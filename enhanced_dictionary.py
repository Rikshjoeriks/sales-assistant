#!/usr/bin/env python3
# enhanced_dictionary.py - Enhanced learning dictionary system for spec matcher

import json
import sqlite3
from datetime import datetime
from pathlib import Path
import re

class LearningDictionary:
    """Enhanced dictionary that learns from user corrections and improves matching"""
    
    def __init__(self, db_path="learning_dictionary.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize enhanced learning database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Learned features table - stores verified correct matches
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT,
                normalized_text TEXT,
                nr_code TEXT,
                variable_name TEXT,
                language TEXT,
                model_name TEXT,
                match_method TEXT,
                confidence REAL,
                user_verified BOOLEAN DEFAULT TRUE,
                verification_date TEXT,
                usage_count INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 1.0
            )
        ''')
        
        # Pattern library - stores learned text patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_text TEXT,
                pattern_type TEXT,
                nr_code TEXT,
                variable_name TEXT,
                language TEXT,
                confidence REAL,
                usage_count INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 1.0,
                created_date TEXT
            )
        ''')
        
        # Negative examples - stores what NOT to match
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS negative_examples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT,
                nr_code TEXT,
                variable_name TEXT,
                reason TEXT,
                created_date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def learn_from_results(self, results_data, model_name):
        """Learn from user-verified results (ticked items are correct)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        learned_count = 0
        negative_count = 0
        
        for row in results_data:
            # Handle current 9-column UI format: [nr_code, var_name, lv_match, en_match, final_match, include, lv_text, en_text, reasoning]
            if len(row) < 6:
                continue
                
            nr_code, var_name = row[0], row[1]
            
            # Skip if no nr_code (empty rows)
            if not nr_code:
                continue
                
            # Determine if this is a section header by checking if var_name contains typical header patterns
            # Section headers typically don't have match data
            is_section_header = (
                len(row[2:5]) == 3 and all(x == "" for x in row[2:5]) or  # All matches empty
                "—" in var_name or "–" in var_name  # Contains em-dash or en-dash (common in headers)
            )
            
            if is_section_header:
                continue
                
            # Extract data from 9-column format
            lv_match = row[2] if len(row) > 2 else ""
            en_match = row[3] if len(row) > 3 else ""
            final_match = row[4] if len(row) > 4 else ""
            include = row[5] if len(row) > 5 else ""
            lv_text = row[6] if len(row) > 6 else ""
            en_text = row[7] if len(row) > 7 else ""
            reasoning = row[8] if len(row) > 8 else ""
            
            # If user ticked it (include = ☑), it's a positive example
            if include == "☑":
                # Learn from LV text if available
                if lv_text and lv_match in ["Yes", "Maybe"]:
                    self._add_learned_feature(lv_text, nr_code, var_name, "LV", model_name, "sequential_mega", cursor)
                    learned_count += 1
                
                # Learn from EN text if available  
                if en_text and en_match in ["Yes", "Maybe"]:
                    self._add_learned_feature(en_text, nr_code, var_name, "EN", model_name, "sequential_mega", cursor)
                    learned_count += 1
            
            # If user unticked it but system said Yes, it's a negative example
            elif include == "☐" and final_match == "Yes":
                if lv_text:
                    self._add_negative_example(lv_text, nr_code, var_name, "False positive - user rejected", cursor)
                    negative_count += 1
                if en_text:
                    self._add_negative_example(en_text, nr_code, var_name, "False positive - user rejected", cursor)
                    negative_count += 1
        
        conn.commit()
        conn.close()
        
        return learned_count, negative_count
    
    def _add_learned_feature(self, text, nr_code, var_name, language, model_name, method, cursor):
        """Add a verified positive example"""
        normalized_text = self._normalize_text(text)
        timestamp = datetime.now().isoformat()
        
        # Check if already exists and update usage count
        cursor.execute('''
            SELECT id, usage_count FROM learned_features 
            WHERE normalized_text = ? AND nr_code = ? AND language = ?
        ''', (normalized_text, nr_code, language))
        
        existing = cursor.fetchone()
        if existing:
            cursor.execute('''
                UPDATE learned_features 
                SET usage_count = usage_count + 1, verification_date = ?
                WHERE id = ?
            ''', (timestamp, existing[0]))
        else:
            cursor.execute('''
                INSERT INTO learned_features 
                (original_text, normalized_text, nr_code, variable_name, language, 
                 model_name, match_method, confidence, verification_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (text, normalized_text, nr_code, var_name, language, model_name, method, 1.0, timestamp))
        
        # Extract and learn patterns
        self._extract_patterns(text, nr_code, var_name, language, cursor)
    
    def _add_negative_example(self, text, nr_code, var_name, reason, cursor):
        """Add a negative example (what NOT to match)"""
        timestamp = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO negative_examples (original_text, nr_code, variable_name, reason, created_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (text, nr_code, var_name, reason, timestamp))
    
    def _extract_patterns(self, text, nr_code, var_name, language, cursor):
        """Extract useful patterns from learned text"""
        patterns = []
        
        # Extract key automotive terms
        auto_terms = re.findall(r'\b(?:electric|elektris|sildām|heated|automatic|automātis|4WD|AWD|V2L|heat pump|siltumsūkn)\w*\b', text, re.IGNORECASE)
        for term in auto_terms:
            patterns.append((term.lower(), "automotive_term"))
        
        # Extract technical specifications
        tech_specs = re.findall(r'\b\d+(?:\.\d+)?\s*(?:kW|hp|km/h|mm|kg|V|A|kWh)\b', text, re.IGNORECASE)
        for spec in tech_specs:
            patterns.append((spec, "technical_spec"))
        
        # Add patterns to database
        timestamp = datetime.now().isoformat()
        for pattern, pattern_type in patterns:
            cursor.execute('''
                INSERT OR IGNORE INTO learned_patterns 
                (pattern_text, pattern_type, nr_code, variable_name, language, confidence, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (pattern, pattern_type, nr_code, var_name, language, 0.8, timestamp))
    
    def _normalize_text(self, text):
        """Normalize text for better matching"""
        # Remove extra whitespace, lowercase
        normalized = re.sub(r'\s+', ' ', text.strip().lower())
        # Remove common punctuation
        normalized = re.sub(r'[.,;:!?"]', '', normalized)
        return normalized
    
    def get_learned_matches(self, text, language="LV", threshold=0.7):
        """Get learned matches for given text"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        normalized_text = self._normalize_text(text)
        
        # Direct matches
        cursor.execute('''
            SELECT nr_code, variable_name, confidence, usage_count, success_rate, original_text
            FROM learned_features 
            WHERE language = ? AND (
                normalized_text = ? OR 
                normalized_text LIKE ? OR
                ? LIKE '%' || normalized_text || '%'
            )
            ORDER BY success_rate DESC, usage_count DESC
        ''', (language, normalized_text, f"%{normalized_text}%", normalized_text))
        
        direct_matches = cursor.fetchall()
        
        # Pattern matches
        cursor.execute('''
            SELECT lp.nr_code, lp.variable_name, lp.confidence, lp.pattern_text
            FROM learned_patterns lp
            WHERE lp.language = ? AND ? LIKE '%' || lp.pattern_text || '%'
            ORDER BY lp.confidence DESC, lp.usage_count DESC
        ''', (language, text.lower()))
        
        pattern_matches = cursor.fetchall()
        
        conn.close()
        
        # Combine and rank results
        results = []
        
        for nr_code, var_name, conf, usage, success, orig_text in direct_matches:
            results.append({
                'nr_code': nr_code,
                'variable_name': var_name,
                'confidence': conf * success,
                'match_type': 'direct',
                'usage_count': usage,
                'learned_text': orig_text
            })
        
        for nr_code, var_name, conf, pattern in pattern_matches:
            results.append({
                'nr_code': nr_code,
                'variable_name': var_name,
                'confidence': conf * 0.8,  # Lower confidence for pattern matches
                'match_type': 'pattern',
                'pattern': pattern,
                'learned_text': f"Pattern: {pattern}"
            })
        
        # Filter by threshold and remove duplicates
        filtered_results = []
        seen_codes = set()
        
        for result in sorted(results, key=lambda x: x['confidence'], reverse=True):
            if result['confidence'] >= threshold and result['nr_code'] not in seen_codes:
                filtered_results.append(result)
                seen_codes.add(result['nr_code'])
        
        return filtered_results
    
    def check_negative_examples(self, text, nr_code):
        """Check if text is a known negative example for this code"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        normalized_text = self._normalize_text(text)
        
        cursor.execute('''
            SELECT reason FROM negative_examples 
            WHERE nr_code = ? AND (
                LOWER(original_text) = ? OR
                LOWER(original_text) LIKE ? OR
                ? LIKE '%' || LOWER(original_text) || '%'
            )
        ''', (nr_code, normalized_text, f"%{normalized_text}%", normalized_text))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_learning_stats(self):
        """Get statistics about learned knowledge"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM learned_features')
        learned_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM learned_patterns')  
        pattern_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM negative_examples')
        negative_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT nr_code) FROM learned_features')
        covered_codes = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'learned_features': learned_count,
            'learned_patterns': pattern_count,
            'negative_examples': negative_count,
            'covered_codes': covered_codes
        }
    
    def export_learned_knowledge(self, output_path="learned_knowledge.json"):
        """Export learned knowledge for backup/sharing"""
        conn = sqlite3.connect(self.db_path)
        
        # Get all learned data
        features_df = conn.execute('SELECT * FROM learned_features').fetchall()
        patterns_df = conn.execute('SELECT * FROM learned_patterns').fetchall()
        negatives_df = conn.execute('SELECT * FROM negative_examples').fetchall()
        
        conn.close()
        
        knowledge = {
            'learned_features': features_df,
            'learned_patterns': patterns_df,
            'negative_examples': negatives_df,
            'export_date': datetime.now().isoformat(),
            'stats': self.get_learning_stats()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, indent=2, ensure_ascii=False)
        
        return output_path
