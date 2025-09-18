#!/usr/bin/env python3
# mega_matcher.py - Ultimate automotive feature matching pipeline
# Combines: Dual-language processing + Intelligent matching + 3x Consensus + Text normalization

import argparse, csv, json, pathlib, re, time
from datetime import datetime
from openai import OpenAI
from tqdm import tqdm
from text_normalizer import normalize_spec_text
from intelligent_matcher import extract_features_from_text, parse_extracted_features, match_to_masterlist, parse_matching_results

def extract_features_bilingual(text, llm_model="gpt-4o"):
    """Extract features in both English and Latvian"""
    
    prompt = """You are a bilingual automotive feature extraction expert.

TASK: Extract all car features from the input text in BOTH English and Latvian.

INPUT TEXT:
{text}

OUTPUT: For each feature, provide both English and Latvian versions:
- English feature | Latvian feature | Exact text from input | Category

Categories: Engine, Transmission, Safety, Lighting, Interior, Exterior, Technology, Other

EXAMPLE:
- All-wheel drive | Pilna piedziņa | All-wheel drive (AWD) system | Transmission
- LED headlights | LED priekšējie lukturi | LED headlights with adaptive lighting | Lighting
- Heated mirrors | Sildāmi spoguļi | Electric heated mirrors | Exterior

EXTRACTED FEATURES (EN | LV | TEXT | CATEGORY):"""

    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model=llm_model,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt.format(text=text)}],
            stream=False
        )
        
        content = response.choices[0].message.content
        return content if content else "No features extracted"
    except Exception as e:
        print(f"Error in bilingual feature extraction: {e}")
        return "Error extracting features"

def parse_bilingual_features(extracted_text):
    """Parse bilingual extracted features into structured data"""
    features = []
    for line in extracted_text.split('\n'):
        line = line.strip()
        if line.startswith('-') and '|' in line:
            parts = line[1:].split('|')
            if len(parts) >= 4:
                en_name = parts[0].strip()
                lv_name = parts[1].strip()
                exact_text = parts[2].strip()
                category = parts[3].strip()
                features.append({
                    'en_name': en_name,
                    'lv_name': lv_name,
                    'text': exact_text,
                    'category': category
                })
    return features

def match_bilingual_to_masterlist(features, master_rows, llm_model="gpt-4o"):
    """Match extracted features to masterlist in both languages"""
    
    # Create bilingual feature database
    feature_db = "\n".join([
        f"- EN: {f['en_name']} | LV: {f['lv_name']} | TEXT: {f['text']}" 
        for f in features
    ])
    
    # Create masterlist for matching
    masterlist_text = "\n".join([
        f"{row['nr_code']}: {row['variable_name']}" 
        for row in master_rows if row['is_tt'] == 'N'
    ])
    
    prompt = """You are a bilingual automotive feature matching expert.

TASK: Match extracted bilingual features to specific masterlist items.

EXTRACTED FEATURES (EN | LV | TEXT):
{features}

MASTERLIST TO MATCH AGAINST:
{masterlist}

RULES:
1. Each masterlist item gets either ONE matched feature or "No match"
2. Consider BOTH English and Latvian feature names for matching
3. Use the most appropriate language match for each masterlist item
4. Don't reuse the same extracted feature for multiple masterlist items
5. Be conservative - prefer "No match" over wrong matches

OUTPUT FORMAT (one line per masterlist item):
NR_CODE: Match_status | Language_used | Feature_name | Exact_text | Reason

EXAMPLES:
NR24: MATCH | EN | All-wheel drive | All-wheel drive (AWD) system | AWD matches 4X4 pilna laika
NR25: MATCH | LV | Automātiskā ātrumkārba | Automatic transmission with 8-speed CVT | Latvian term better match
NR26: NO_MATCH | | | | No equivalent found in either language

BILINGUAL MATCHING RESULTS:"""

    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model=llm_model,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt.format(features=feature_db, masterlist=masterlist_text)}],
            stream=False
        )
        
        content = response.choices[0].message.content
        return content if content else "No matching results"
    except Exception as e:
        print(f"Error in bilingual matching: {e}")
        return "Error in matching"

def consensus_match_3x(spec_text, master_rows, llm_model="gpt-4o"):
    """Run 3x consensus matching for validation"""
    
    prompt = """You are an automotive specification matching expert.

TASK: For each masterlist item, determine if it's mentioned in the specification text.

SPECIFICATION TEXT:
{spec_text}

MASTERLIST ITEMS:
{masterlist}

RULES:
1. Answer "Yes", "No", or "Maybe" for each item
2. If "Yes" or "Maybe", provide the exact text snippet that mentions it
3. Be thorough but conservative - only "Yes" if clearly mentioned

OUTPUT FORMAT:
NR_CODE: Answer | Text_snippet | Reason

MATCHING RESULTS:"""

    masterlist_text = "\n".join([
        f"{row['nr_code']}: {row['variable_name']}" 
        for row in master_rows if row['is_tt'] == 'N'
    ])
    
    client = OpenAI()
    results = []
    
    # Run 3 independent attempts
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=llm_model,
                temperature=0.1 + (attempt * 0.1),  # Slightly different temperatures
                messages=[{"role": "user", "content": prompt.format(spec_text=spec_text, masterlist=masterlist_text)}],
                stream=False
            )
            
            content = response.choices[0].message.content
            results.append(content if content else f"No results from attempt {attempt+1}")
        except Exception as e:
            results.append(f"Error in attempt {attempt+1}: {e}")
    
    return results

def parse_consensus_results(consensus_results, master_rows):
    """Parse and combine 3x consensus results"""
    all_votes = {}
    
    # Parse each consensus attempt
    for i, result_text in enumerate(consensus_results):
        for line in result_text.split('\n'):
            line = line.strip()
            if ':' in line and '|' in line:
                nr_code = line.split(':')[0].strip()
                rest = line.split(':', 1)[1].strip()
                parts = rest.split('|')
                
                if len(parts) >= 3:
                    answer = parts[0].strip().upper()
                    text_snippet = parts[1].strip()
                    reason = parts[2].strip()
                    
                    if nr_code not in all_votes:
                        all_votes[nr_code] = []
                    
                    all_votes[nr_code].append({
                        'attempt': i + 1,
                        'answer': answer,
                        'text': text_snippet,
                        'reason': reason
                    })
    
    # Calculate consensus
    consensus_results = {}
    for nr_code, votes in all_votes.items():
        yes_count = sum(1 for v in votes if v['answer'] == 'YES')
        maybe_count = sum(1 for v in votes if v['answer'] == 'MAYBE')
        no_count = sum(1 for v in votes if v['answer'] == 'NO')
        
        # Consensus logic
        if yes_count >= 2:
            final_answer = "Yes"
        elif yes_count + maybe_count >= 2:
            final_answer = "Maybe"
        else:
            final_answer = "No"
        
        # Get best text snippet and reason
        best_vote = next((v for v in votes if v['answer'] == 'YES'), 
                        next((v for v in votes if v['answer'] == 'MAYBE'), votes[0] if votes else None))
        
        consensus_results[nr_code] = {
            'answer': final_answer,
            'text': best_vote['text'] if best_vote else "",
            'reason': f"Consensus: {yes_count}Y/{maybe_count}M/{no_count}N - {best_vote['reason'] if best_vote else 'No reasoning'}",
            'votes': f"{yes_count}/{maybe_count}/{no_count}"
        }
    
    return consensus_results

def combine_all_results(bilingual_results, consensus_results, master_rows):
    """Combine bilingual intelligent matching with consensus results"""
    
    # Parse bilingual results
    bilingual_matches = {}
    for line in bilingual_results.split('\n'):
        line = line.strip()
        if ':' in line and '|' in line:
            nr_code = line.split(':')[0].strip()
            rest = line.split(':', 1)[1].strip()
            parts = rest.split('|')
            
            if len(parts) >= 5:
                status = parts[0].strip()
                language = parts[1].strip()
                feature_name = parts[2].strip()
                exact_text = parts[3].strip()
                reason = parts[4].strip()
                
                bilingual_matches[nr_code] = {
                    'status': status,
                    'language': language,
                    'feature': feature_name,
                    'text': exact_text,
                    'reason': reason
                }
    
    # Create final combined CSV rows
    csv_rows = []
    for row in master_rows:
        nr_code = row['nr_code']
        name = row['variable_name']
        is_tt = row['is_tt']
        
        if is_tt == 'Y':
            # Section header
            csv_rows.append([nr_code, name, is_tt, "", "", "", "", "", "", "", "", "", ""])
        else:
            # Feature row - combine intelligent and consensus results
            
            # Bilingual intelligent match
            bi_match = bilingual_matches.get(nr_code, {})
            intelligent_match = "Yes" if bi_match.get('status', '').upper() == 'MATCH' else "No"
            intelligent_text = bi_match.get('text', '')
            intelligent_reason = f"{bi_match.get('language', 'EN')}: {bi_match.get('reason', 'not found')}"
            
            # Consensus match
            consensus = consensus_results.get(nr_code, {})
            consensus_match = consensus.get('answer', 'No')
            consensus_text = consensus.get('text', '')
            consensus_reason = consensus.get('reason', 'not mentioned')
            
            # Final decision (combine both methods)
            if intelligent_match == "Yes" and consensus_match in ["Yes", "Maybe"]:
                final_match = "Yes"
            elif intelligent_match == "Yes" or consensus_match == "Yes":
                final_match = "Maybe"  
            else:
                final_match = "No"
            
            # Choose best text snippet
            final_text = intelligent_text if intelligent_text else consensus_text
            language_used = bi_match.get('language', 'EN')
            
            csv_rows.append([
                nr_code, name, is_tt, 
                intelligent_match, consensus_match, final_match,
                intelligent_text, consensus_text, final_text,
                language_used, intelligent_reason, consensus_reason, 
                f"Combined: I:{intelligent_match}/C:{consensus_match} = {final_match} ({language_used})"
            ])
    
    return csv_rows

def mega_match(spec_text, master_path, output_path, llm_model="gpt-4o", normalize_text=True):
    """Ultimate matching pipeline with all techniques combined"""
    
    # Initialize progress bar
    progress = tqdm(total=100, desc="🚀 MEGA Spec Matching", unit="%", 
                   bar_format='{desc}: {percentage:3.0f}%|{bar}| {n}/{total} [{elapsed}<{remaining}]')
    
    try:
        # Load masterlist
        progress.set_description("📋 Loading masterlist")
        with open(master_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            master_rows = []
            for row in reader:
                master_rows.append({
                    'nr_code': row['Nr Code'].strip(),
                    'variable_name': row['Variable Name'].strip(),
                    'is_tt': row.get('Is TT', 'N').strip().upper()
                })
        progress.update(5)  # 5%
        
        # Step 1: Normalize text (CONSERVATIVE - basic cleanup only)
        if normalize_text:
            progress.set_description("🧹 Normalizing text (safe)")
            # Force safe mode - NO GPT organization at all
            from text_normalizer import basic_text_cleanup
            spec_text = basic_text_cleanup(spec_text)
            progress.update(10)  # 15%
        else:
            progress.update(10)  # Skip normalization
        
        # Step 2: Bilingual feature extraction
        progress.set_description("🌍 Bilingual feature extraction")
        bilingual_features_raw = extract_features_bilingual(spec_text, llm_model)
        bilingual_features = parse_bilingual_features(bilingual_features_raw)
        progress.update(20)  # 35%
        
        # Step 3: Bilingual intelligent matching
        progress.set_description("🧠 Bilingual intelligent matching")
        bilingual_matching = match_bilingual_to_masterlist(bilingual_features, master_rows, llm_model)
        progress.update(20)  # 55%
        
        # Step 4: 3x Consensus matching
        progress.set_description("🎯 3x Consensus matching")
        consensus_results_raw = consensus_match_3x(spec_text, master_rows, llm_model)
        consensus_results = parse_consensus_results(consensus_results_raw, master_rows)
        progress.update(20)  # 75%
        
        # Step 5: Combine all results
        progress.set_description("🔄 Combining results")
        csv_rows = combine_all_results(bilingual_matching, consensus_results, master_rows)
        progress.update(15)  # 90%
        
        # Save results
        progress.set_description("💾 Saving mega results")
        mega_headers = [
            "Nr Code", "Variable Name", "Is TT", 
            "Intelligent Match", "Consensus Match", "Final Match",
            "Intelligent Text", "Consensus Text", "Final Text",
            "Language Used", "Intelligent Reason", "Consensus Reason", "Combined Reason"
        ]
        
        with open(output_path, "w", encoding="utf-8", newline="", errors="replace") as f:
            writer = csv.writer(f)
            writer.writerow(mega_headers)
            writer.writerows(csv_rows)
        
        # Save audit files
        from pathlib import Path
        audit_dir = Path(output_path).parent
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        if normalize_text:
            with open(audit_dir / f"mega_normalized_text_{timestamp}.txt", "w", encoding="utf-8", errors="replace") as f:
                f.write(spec_text)
        
        with open(audit_dir / f"mega_bilingual_features_{timestamp}.txt", "w", encoding="utf-8", errors="replace") as f:
            f.write(bilingual_features_raw)
        
        with open(audit_dir / f"mega_bilingual_matching_{timestamp}.txt", "w", encoding="utf-8", errors="replace") as f:
            f.write(bilingual_matching)
        
        with open(audit_dir / f"mega_consensus_results_{timestamp}.txt", "w", encoding="utf-8", errors="replace") as f:
            f.write("\n".join([f"=== ATTEMPT {i+1} ===\n{result}" for i, result in enumerate(consensus_results_raw)]))
        
        progress.update(10)  # 100%
        progress.set_description("✅ MEGA Complete")
        progress.close()
        
        print(f"\n🎉 MEGA Results saved to: {output_path}")
        print(f"🌍 Bilingual features extracted: {len(bilingual_features)}")
        print(f"🎯 Consensus validations: 3x attempts")
        print(f"📊 Processed {len(master_rows)} masterlist items")
        if normalize_text:
            print(f"🧹 Text normalized: {len(spec_text)} characters")
        
        return csv_rows
        
    except Exception as e:
        progress.close()
        print(f"\n❌ Error during MEGA processing: {e}")
        raise

def main():
    ap = argparse.ArgumentParser(description="MEGA automotive feature matcher - Ultimate pipeline")
    ap.add_argument("--model", required=True, help="Model ID")
    ap.add_argument("--specfile", required=True, help="Input text file")
    ap.add_argument("--master", required=True, help="Masterlist CSV")
    ap.add_argument("--exportdir", default="exports", help="Output directory")
    ap.add_argument("--llm", default="gpt-4o", help="LLM model")
    ap.add_argument("--no-normalize", action="store_true", help="Skip text normalization")
    args = ap.parse_args()
    
    # Setup paths
    spec_path = pathlib.Path(args.specfile)
    master_path = pathlib.Path(args.master)
    export_dir = pathlib.Path(args.exportdir) / args.model
    export_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = export_dir / f"ticksheet_mega_{timestamp}.csv"
    
    # Read input
    spec_text = spec_path.read_text(encoding="utf-8")
    
    # Run MEGA matching
    normalize_text = not args.no_normalize
    results = mega_match(spec_text, master_path, output_path, args.llm, normalize_text)
    
    print(f"🚀 MEGA matching complete!")
    print(f"Results: {output_path}")

if __name__ == "__main__":
    main()
