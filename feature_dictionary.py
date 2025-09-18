#!/usr/bin/env python3
"""
Feature Dictionary System
Tracks all processed features for reference and learning
"""

import json
import csv
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib

class FeatureDictionary:
    """Comprehensive feature tracking and reference system"""
    
    def __init__(self, db_path="feature_dictionary.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for feature storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main features table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text_hash TEXT UNIQUE,
                original_text TEXT,
                language TEXT,
                model_name TEXT,
                matched_code TEXT,
                matched_name TEXT,
                match_status TEXT,
                confidence REAL,
                reasoning TEXT,
                method TEXT,
                timestamp TEXT,
                user_verified BOOLEAN DEFAULT FALSE,
                user_correction TEXT
            )
        ''')
        
        # Sessions table for tracking processing runs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT,
                model_name TEXT,
                method TEXT,
                start_time TEXT,
                end_time TEXT,
                total_features INTEGER,
                matches_found INTEGER,
                success_rate REAL
            )
        ''')
        
        # Statistics table for analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value REAL,
                date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_text(self, text):
        """Create consistent hash for text deduplication"""
        return hashlib.md5(text.lower().strip().encode('utf-8')).hexdigest()
    
    def normalize_text(self, text):
        """Normalize text for similarity comparison"""
        import re
        # Remove extra whitespace, punctuation, convert to lowercase
        normalized = re.sub(r'[^\w\s]', ' ', text.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two texts using Jaccard similarity"""
        words1 = set(self.normalize_text(text1).split())
        words2 = set(self.normalize_text(text2).split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return intersection / union if union > 0 else 0.0
    
    def find_similar_features(self, text, similarity_threshold=0.8):
        """Find existing features similar to the given text"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT text_hash, original_text, matched_code, matched_name, confidence FROM features')
        existing_features = cursor.fetchall()
        conn.close()
        
        similar_features = []
        for hash_val, existing_text, code, name, conf in existing_features:
            similarity = self.calculate_similarity(text, existing_text)
            if similarity >= similarity_threshold:
                similar_features.append({
                    'hash': hash_val,
                    'text': existing_text,
                    'code': code,
                    'name': name,
                    'confidence': conf,
                    'similarity': similarity
                })
        
        return sorted(similar_features, key=lambda x: x['similarity'], reverse=True)
    
    def add_feature(self, original_text, language, model_name, matched_code="", 
                   matched_name="", match_status="No", confidence=0.0, 
                   reasoning="", method="manual", check_similarity=True):
        """Add a processed feature to the dictionary with smart deduplication"""
        
        # Check for similar features first
        if check_similarity:
            similar = self.find_similar_features(original_text, similarity_threshold=0.85)
            
            if similar:
                best_match = similar[0]
                print(f"⚠️  Similar feature exists ({best_match['similarity']:.0%} match):")
                print(f"   New: {original_text[:60]}...")
                print(f"   Existing: {best_match['text'][:60]}...")
                
                # If very similar (>95%), skip adding
                if best_match['similarity'] > 0.95:
                    print(f"   ⏭️  Skipping (too similar)")
                    return False
                
                # If similar but different model, still add but note it
                if best_match['similarity'] > 0.85:
                    reasoning = f"Similar to existing feature (similarity: {best_match['similarity']:.0%}). {reasoning}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        text_hash = self.hash_text(original_text)
        timestamp = datetime.now().isoformat()
        
        # Check if exact duplicate exists
        cursor.execute('SELECT COUNT(*) FROM features WHERE text_hash = ?', (text_hash,))
        if cursor.fetchone()[0] > 0:
            print(f"   ⏭️  Exact duplicate exists, skipping: {original_text[:50]}...")
            conn.close()
            return False
        
        # Insert new feature
        cursor.execute('''
            INSERT INTO features 
            (text_hash, original_text, language, model_name, matched_code, 
             matched_name, match_status, confidence, reasoning, method, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (text_hash, original_text, language, model_name, matched_code,
              matched_name, match_status, confidence, reasoning, method, timestamp))
        
        conn.commit()
        conn.close()
        return True
    
    def import_from_csv(self, csv_path, model_name, method="smart_match", check_similarity=True):
        """Import features from a processed CSV file with smart deduplication"""
        print(f"Importing features from {csv_path}...")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            added_count = 0
            skipped_count = 0
            
            for row in reader:
                # Extract data from CSV
                matched_code = row.get('Nr Code', '')
                matched_name = row.get('Variable Name', '')
                match_status = row.get('Match (Yes/No/Maybe)', 'No')
                matching_text = row.get('Matching Text', '')
                reasoning = row.get('LLM_Reason', '')
                
                # Parse confidence from reasoning if available
                confidence = 0.0
                if 'Confidence:' in reasoning:
                    try:
                        conf_part = reasoning.split('Confidence:')[1].split('%')[0].strip()
                        confidence = float(conf_part) / 100.0
                    except:
                        confidence = 0.5 if match_status == 'Yes' else 0.0
                
                # Only add if there's actual matching text
                if matching_text and matching_text.strip():
                    added = self.add_feature(
                        original_text=matching_text,
                        language="auto",  # Could be detected later
                        model_name=model_name,
                        matched_code=matched_code,
                        matched_name=matched_name,
                        match_status=match_status,
                        confidence=confidence,
                        reasoning=reasoning,
                        method=method,
                        check_similarity=check_similarity
                    )
                    
                    if added:
                        added_count += 1
                    else:
                        skipped_count += 1
        
        print(f"✓ Added {added_count} new features, skipped {skipped_count} duplicates/similar")
        return added_count
    
    def search_features(self, query, limit=50):
        """Search features by text content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, original_text, model_name, matched_code, matched_name, 
                   match_status, confidence, reasoning, timestamp, user_verified
            FROM features 
            WHERE original_text LIKE ? OR matched_name LIKE ?
            ORDER BY confidence DESC, timestamp DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'text': row[1],
                'model': row[2],
                'code': row[3],
                'name': row[4],
                'status': row[5],
                'confidence': row[6],
                'reasoning': row[7],
                'timestamp': row[8],
                'user_verified': row[9]
            }
            for row in results
        ]
    
    def mark_as_verified(self, feature_id, is_verified=True, correction=None):
        """Mark a feature as user-verified with optional correction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE features 
            SET user_verified = ?, user_correction = ?
            WHERE id = ?
        ''', (is_verified, correction, feature_id))
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    def delete_feature(self, feature_id):
        """Delete a feature from the dictionary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM features WHERE id = ?', (feature_id,))
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    def update_feature(self, feature_id, matched_code=None, matched_name=None, 
                      match_status=None, confidence=None, reasoning=None):
        """Update specific fields of a feature"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if matched_code is not None:
            updates.append("matched_code = ?")
            params.append(matched_code)
        if matched_name is not None:
            updates.append("matched_name = ?")
            params.append(matched_name)
        if match_status is not None:
            updates.append("match_status = ?")
            params.append(match_status)
        if confidence is not None:
            updates.append("confidence = ?")
            params.append(confidence)
        if reasoning is not None:
            updates.append("reasoning = ?")
            params.append(reasoning)
        
        if not updates:
            conn.close()
            return False
        
        params.append(feature_id)
        query = f"UPDATE features SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    def get_feature_by_id(self, feature_id):
        """Get a specific feature by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, text_hash, original_text, language, model_name, 
                   matched_code, matched_name, match_status, confidence, 
                   reasoning, method, timestamp, user_verified, user_correction
            FROM features WHERE id = ?
        ''', (feature_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'text_hash': row[1],
                'text': row[2],
                'language': row[3],
                'model': row[4],
                'code': row[5],
                'name': row[6],
                'status': row[7],
                'confidence': row[8],
                'reasoning': row[9],
                'method': row[10],
                'timestamp': row[11],
                'user_verified': row[12],
                'user_correction': row[13]
            }
        return None
    
    def get_similar_features(self, text, threshold=0.7, limit=10):
        """Find features similar to given text"""
        # Simple similarity based on common words
        words = set(text.lower().split())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT original_text, matched_code, matched_name, match_status, 
                   confidence, reasoning
            FROM features 
            WHERE match_status = 'Yes'
            ORDER BY confidence DESC
        ''')
        
        results = []
        for row in cursor.fetchall():
            other_words = set(row[0].lower().split())
            overlap = len(words.intersection(other_words))
            total = len(words.union(other_words))
            similarity = overlap / total if total > 0 else 0
            
            if similarity >= threshold:
                results.append({
                    'text': row[0],
                    'code': row[1],
                    'name': row[2],
                    'status': row[3],
                    'confidence': row[4],
                    'reasoning': row[5],
                    'similarity': similarity
                })
        
        conn.close()
        return sorted(results, key=lambda x: x['similarity'], reverse=True)[:limit]
    
    def get_statistics(self):
        """Get processing statistics with duplicate analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total features
        cursor.execute('SELECT COUNT(*) FROM features')
        total_features = cursor.fetchone()[0]
        
        # Match success rate
        cursor.execute("SELECT COUNT(*) FROM features WHERE match_status = 'Yes'")
        successful_matches = cursor.fetchone()[0]
        
        # Average confidence
        cursor.execute("SELECT AVG(confidence) FROM features WHERE match_status = 'Yes'")
        avg_confidence = cursor.fetchone()[0] or 0
        
        # Features by model
        cursor.execute('''
            SELECT model_name, COUNT(*), 
                   SUM(CASE WHEN match_status = 'Yes' THEN 1 ELSE 0 END)
            FROM features 
            GROUP BY model_name
        ''')
        by_model = cursor.fetchall()
        
        # Potential duplicates analysis
        cursor.execute('SELECT original_text FROM features')
        all_texts = [row[0] for row in cursor.fetchall()]
        
        # Find potential duplicates (similarity > 0.8)
        potential_duplicates = 0
        for i, text1 in enumerate(all_texts):
            for text2 in all_texts[i+1:]:
                if self.calculate_similarity(text1, text2) > 0.8:
                    potential_duplicates += 1
        
        conn.close()
        
        return {
            'total_features': total_features,
            'successful_matches': successful_matches,
            'success_rate': successful_matches / total_features if total_features > 0 else 0,
            'average_confidence': avg_confidence,
            'potential_duplicates': potential_duplicates,
            'by_model': {row[0]: {'total': row[1], 'matches': row[2]} for row in by_model}
        }
    
    def export_to_json(self, output_path="feature_dictionary.json"):
        """Export entire dictionary to JSON for backup"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM features ORDER BY timestamp DESC')
        features = cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Convert to list of dictionaries
        feature_list = [dict(zip(columns, row)) for row in features]
        
        conn.close()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'export_date': datetime.now().isoformat(),
                'total_features': len(feature_list),
                'features': feature_list
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported {len(feature_list)} features to {output_path}")
        return output_path

def main():
    """Command line interface for feature dictionary"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Feature Dictionary Management")
    parser.add_argument('action', choices=['add', 'import', 'search', 'stats', 'export', 'duplicates'])
    parser.add_argument('--file', help="CSV file to import")
    parser.add_argument('--text', help="Feature text to add")
    parser.add_argument('--model', help="Model name for import/add")
    parser.add_argument('--matched', help="Matched name for add")
    parser.add_argument('--query', help="Search query")
    parser.add_argument('--output', help="Output file for export")
    parser.add_argument('--threshold', type=float, default=0.8, help="Similarity threshold for duplicates")
    
    args = parser.parse_args()
    
    fd = FeatureDictionary()
    
    if args.action == 'add' and args.text and args.model and args.matched:
        success = fd.add_feature(args.text, args.model, args.matched)
        if success:
            print(f"✅ Added feature: {args.text[:50]}...")
        else:
            print(f"⚠️  Skipped similar feature: {args.text[:50]}...")
    
    elif args.action == 'import' and args.file and args.model:
        fd.import_from_csv(args.file, args.model)
    
    elif args.action == 'search' and args.query:
        results = fd.search_features(args.query)
        print(f"\nFound {len(results)} features matching '{args.query}':")
        for i, result in enumerate(results[:10], 1):
            print(f"{i}. {result['text']} -> {result['name']} ({result['status']}, {result['confidence']:.0%})")
    
    elif args.action == 'stats':
        stats = fd.get_statistics()
        print(f"\n📊 Feature Dictionary Statistics:")
        print(f"Total Features: {stats['total_features']}")
        print(f"Successful Matches: {stats['successful_matches']}")
        print(f"Success Rate: {stats['success_rate']:.1%}")
        print(f"Average Confidence: {stats['average_confidence']:.1%}")
        print(f"Potential Duplicates: {stats['potential_duplicates']}")
        print(f"\nBy Model:")
        for model, data in stats['by_model'].items():
            rate = data['matches'] / data['total'] if data['total'] > 0 else 0
            print(f"  {model}: {data['matches']}/{data['total']} ({rate:.1%})")
    
    elif args.action == 'export':
        output = args.output or "feature_dictionary.json"
        fd.export_to_json(output)
    
    elif args.action == 'duplicates':
        # Find and display similar features
        threshold = args.threshold
        print(f"\n🔍 Finding features with >{threshold:.0%} similarity...")
        
        conn = sqlite3.connect(fd.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT original_text, model_name, matched_name FROM features')
        all_features = cursor.fetchall()
        conn.close()
        
        duplicates_found = 0
        for i, (text1, model1, name1) in enumerate(all_features):
            for text2, model2, name2 in all_features[i+1:]:
                similarity = fd.calculate_similarity(text1, text2)
                if similarity > threshold:
                    duplicates_found += 1
                    print(f"\n{duplicates_found}. Similarity: {similarity:.0%}")
                    print(f"   A: {text1[:60]}... ({model1} -> {name1})")
                    print(f"   B: {text2[:60]}... ({model2} -> {name2})")
        
        if duplicates_found == 0:
            print(f"✅ No similar features found above {threshold:.0%} threshold")
        else:
            print(f"\n⚠️  Found {duplicates_found} similar feature pairs")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
