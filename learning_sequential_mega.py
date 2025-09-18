#!/usr/bin/env python3
# learning_sequential_mega.py - Sequential MEGA with learning dictionary integration

import argparse, csv, json, pathlib, re, time
from datetime import datetime
from openai import OpenAI
from tqdm import tqdm
from text_normalizer import basic_text_cleanup
from enhanced_dictionary import LearningDictionary

def intelligent_match_with_learning(spec_text, master_path, language="LV", llm_model="gpt-4o", learning_dict=None):
    """Enhanced intelligent matching that uses learned knowledge"""
    
    # Load masterlist
    with open(master_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        master_rows = []
        for row in reader:
            master_rows.append({
                'nr_code': row['Nr Code'].strip(),
                'variable_name': row['Variable Name'].strip(),
                'is_tt': row.get('Is TT', 'N').strip().upper()
            })
    
    # Pre-check with learning dictionary
    learned_suggestions = {}
    if learning_dict:
        print(f"   🧠 Checking learned knowledge for {language}...")
        for text_snippet in spec_text.split('\n'):
            if text_snippet.strip():
                learned_matches = learning_dict.get_learned_matches(text_snippet, language, threshold=0.6)
                for match in learned_matches:
                    nr_code = match['nr_code']
                    if nr_code not in learned_suggestions:
                        learned_suggestions[nr_code] = []
                    learned_suggestions[nr_code].append({
                        'text': text_snippet.strip(),
                        'confidence': match['confidence'],
                        'type': match['match_type'],
                        'learned_from': match['learned_text']
                    })
    
    # Create masterlist for GPT matching
    masterlist_text = "\n".join([
        f"{row['nr_code']}: {row['variable_name']}" 
        for row in master_rows if row['is_tt'] == 'N'
    ])
    
    language_instruction = {
        "LV": "Process in Latvian context. Look for Latvian automotive terms and match to Latvian masterlist items.",
        "EN": "Process in English context. Look for English automotive terms and match to English masterlist items."
    }
    
    # Build enhanced prompt with learned knowledge
    learned_hints = ""
    if learned_suggestions:
        learned_hints = "\n\nLEARNED KNOWLEDGE HINTS:\n"
        for nr_code, suggestions in learned_suggestions.items():
            best_suggestion = max(suggestions, key=lambda x: x['confidence'])
            learned_hints += f"{nr_code}: Previous match found - '{best_suggestion['text']}' (confidence: {best_suggestion['confidence']:.1f})\n"
        learned_hints += "\nUse this learned knowledge to improve accuracy, but still analyze the current text independently.\n"
    
    prompt = f"""You are an automotive specification matching expert working with {language} language.

{language_instruction[language]}

TASK: For each masterlist item, determine if it's mentioned in the specification text.

SPECIFICATION TEXT:
{{spec_text}}

MASTERLIST TO MATCH AGAINST:
{{masterlist}}

{learned_hints}

RULES:
1. Answer "Yes", "Maybe", or "No" for each masterlist item
2. If "Yes" or "Maybe", provide the EXACT original text snippet that mentions it
3. Use {language} language context for understanding automotive terms
4. Consider learned knowledge hints but verify with current text
5. Be thorough but conservative - only "Yes" if clearly mentioned
6. Quote the original wording exactly as it appears in the source

OUTPUT FORMAT:
NR_CODE: Answer | Original_text_snippet

EXAMPLES:
NR25: Yes | V2L capability mentioned in specifications
NR26: No | 
NR27: Maybe | All-wheel drive system (could be 4WD/AWD)

MATCHING RESULTS:"""

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=llm_model,
            temperature=0.1,  # Lower temperature for more consistent results with learned knowledge
            messages=[{"role": "user", "content": prompt.format(spec_text=spec_text, masterlist=masterlist_text)}]
        )
        
        content = response.choices[0].message.content
        return content if content else f"No {language} results", learned_suggestions
    except Exception as e:
        print(f"Error in {language} matching: {e}")
        return f"Error in {language} matching", learned_suggestions

def consensus_match_with_learning(spec_text, master_rows, llm_model="gpt-4o", progress_callback=None, learning_dict=None):
    """Enhanced consensus matching with learning integration"""
    
    masterlist_text = "\n".join([
        f"{row['nr_code']}: {row['variable_name']}" 
        for row in master_rows if row['is_tt'] == 'N'
    ])
    
    # Get learned knowledge for all relevant codes
    learned_context = ""
    if learning_dict:
        stats = learning_dict.get_learning_stats()
        learned_context = f"\n\nLEARNED KNOWLEDGE AVAILABLE:\n- {stats['learned_features']} verified features\n- {stats['learned_patterns']} patterns\n- {stats['covered_codes']} codes with knowledge\n\nUse this knowledge to improve accuracy.\n"
    
    prompt = f"""You are an automotive specification consensus validator with access to learned knowledge.

TASK: For each masterlist item, determine if it's mentioned in the specification text and explain your reasoning.

SPECIFICATION TEXT:
{{spec_text}}

MASTERLIST ITEMS:
{{masterlist}}

{learned_context}

RULES:
1. Answer "Yes", "Maybe", or "No" for each item
2. If "Yes" or "Maybe", provide the EXACT original text snippet from source
3. ALWAYS provide clear reasoning for your decision
4. Be independent - don't be influenced by previous analyses
5. Quote original wording exactly as written
6. Consider learned patterns but verify with current text

OUTPUT FORMAT:
NR_CODE: Answer | Original_text_snippet | Reasoning_explanation

CONSENSUS VALIDATION:"""

    client = OpenAI()
    results = []
    
    # Run 3 independent attempts with learning-informed temperature
    for attempt in range(3):
        if progress_callback:
            progress_callback(f"🔥 Consensus attempt {attempt+1}/3 (with learning)")
        
        try:
            response = client.chat.completions.create(
                model=llm_model,
                temperature=0.3 + (attempt * 0.1),  # Gradually increase temperature
                messages=[{"role": "user", "content": prompt.format(spec_text=spec_text, masterlist=masterlist_text)}]
            )
            
            content = response.choices[0].message.content
            results.append(content if content else f"No results from consensus attempt {attempt+1}")
        except Exception as e:
            results.append(f"Error in consensus attempt {attempt+1}: {e}")
    
    return results

def learning_sequential_mega_match(spec_text, base_model, output_path, llm_model="gpt-4o", normalize_text=True, progress_callback=None):
    """Enhanced Sequential MEGA with learning dictionary integration"""
    
    # Initialize learning dictionary
    learning_dict = LearningDictionary()
    stats = learning_dict.get_learning_stats()
    
    # Initialize progress bar
    progress = tqdm(total=100, desc="🧠 Learning Sequential MEGA", unit="%", 
                   bar_format='{desc}: {percentage:3.0f}%|{bar}| {n}/{total} [{elapsed}<{remaining}]')
    
    def update_progress(description):
        if progress_callback:
            progress_callback(description)
        progress.set_description(description)
    
    try:
        # Step 1: Text normalization (safe mode only)
        if normalize_text:
            update_progress("🧹 Text cleanup (safe)")
            spec_text = basic_text_cleanup(spec_text)
            progress.update(8)  # 8%
        else:
            progress.update(8)
        
        # Learning status
        update_progress(f"🧠 Loading learned knowledge ({stats['learned_features']} features)")
        progress.update(2)  # 10%
        
        # Setup paths
        master_lv_path = pathlib.Path("masterlists") / f"{base_model}.csv"
        master_en_path = pathlib.Path("masterlists") / f"{base_model}_en.csv"
        
        # Load masterlist structure
        with open(master_lv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            master_rows = []
            for row in reader:
                master_rows.append({
                    'nr_code': row['Nr Code'].strip(),
                    'variable_name': row['Variable Name'].strip(),
                    'is_tt': row.get('Is TT', 'N').strip().upper()
                })
        
        progress.update(5)  # 15%
        
        # Step 2: Enhanced Latvian Analysis with Learning
        update_progress("🇱🇻 Latvian analysis (with learning)")
        lv_results_raw, lv_learned = intelligent_match_with_learning(spec_text, master_lv_path, "LV", llm_model, learning_dict)
        lv_results = parse_language_results(lv_results_raw, "LV")
        progress.update(25)  # 40%
        
        # Step 3: Enhanced English Analysis with Learning
        update_progress("🇬🇧 English analysis (with learning)")
        en_results_raw, en_learned = intelligent_match_with_learning(spec_text, master_en_path, "EN", llm_model, learning_dict)
        en_results = parse_language_results(en_results_raw, "EN")
        progress.update(25)  # 65%
        
        # Step 4: Enhanced Consensus with Learning
        update_progress("🔥 3x Hot consensus (with learning)")
        consensus_results_raw = consensus_match_with_learning(spec_text, master_rows, llm_model, update_progress, learning_dict)
        consensus_results = parse_consensus_results(consensus_results_raw, master_rows)
        progress.update(25)  # 90%
        
        # Step 5: Combine results with learning annotations
        update_progress("📊 Final combination (with learning)")
        
        headers = [
            "Nr Code", "Variable Name", "Is TT", 
            "LV Match", "LV Text", "EN Match", "EN Text", 
            "Consensus Vote", "Consensus Text", "Consensus Reasoning", 
            "Learning Applied", "Include"
        ]
        
        csv_rows = []
        learning_applied_count = 0
        
        for row in master_rows:
            nr_code = row['nr_code']
            name = row['variable_name']
            is_tt = row['is_tt']
            
            if is_tt == 'Y':
                # Section header
                csv_rows.append([nr_code, name, is_tt, "", "", "", "", "", "", "", "", ""])
            else:
                # Feature row
                lv_result = lv_results.get(nr_code, {'answer': 'NO', 'text': ''})
                en_result = en_results.get(nr_code, {'answer': 'NO', 'text': ''})
                consensus_result = consensus_results.get(nr_code, {
                    'answer': 'No', 'text': '', 'votes': '0Y/0M/3N', 'reasoning': ''
                })
                
                # Check if learning was applied
                learning_applied = ""
                if nr_code in lv_learned or nr_code in en_learned:
                    learning_applied_count += 1
                    lv_learned_info = lv_learned.get(nr_code, [])
                    en_learned_info = en_learned.get(nr_code, [])
                    
                    applied_info = []
                    for info in lv_learned_info + en_learned_info:
                        applied_info.append(f"{info['type']}:{info['confidence']:.1f}")
                    learning_applied = "; ".join(applied_info)
                
                # Convert to Yes/Maybe/No format
                lv_match = "Yes" if lv_result['answer'] == 'YES' else "Maybe" if lv_result['answer'] == 'MAYBE' else "No"
                en_match = "Yes" if en_result['answer'] == 'YES' else "Maybe" if en_result['answer'] == 'MAYBE' else "No"
                
                # Auto-tick logic: tick if ANY method says Yes or Maybe
                auto_tick = "☑" if any([
                    lv_match in ["Yes", "Maybe"],
                    en_match in ["Yes", "Maybe"], 
                    consensus_result['answer'] in ["Yes", "Maybe"]
                ]) else "☐"
                
                csv_rows.append([
                    nr_code, name, is_tt,
                    lv_match, lv_result['text'],
                    en_match, en_result['text'],
                    f"{consensus_result['answer']} ({consensus_result['votes']})", 
                    consensus_result['text'],
                    consensus_result['reasoning'],
                    learning_applied,
                    auto_tick
                ])
        
        # Save results
        with open(output_path, "w", encoding="utf-8", newline="", errors="replace") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(csv_rows)
        
        # Save audit files with learning information
        audit_dir = pathlib.Path(output_path).parent
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        with open(audit_dir / f"learning_lv_analysis_{timestamp}.txt", "w", encoding="utf-8", errors="replace") as f:
            f.write(f"=== LEARNED KNOWLEDGE APPLIED ===\n{json.dumps(lv_learned, indent=2, ensure_ascii=False)}\n\n")
            f.write(lv_results_raw)
        
        with open(audit_dir / f"learning_en_analysis_{timestamp}.txt", "w", encoding="utf-8", errors="replace") as f:
            f.write(f"=== LEARNED KNOWLEDGE APPLIED ===\n{json.dumps(en_learned, indent=2, ensure_ascii=False)}\n\n")
            f.write(en_results_raw)
        
        with open(audit_dir / f"learning_consensus_{timestamp}.txt", "w", encoding="utf-8", errors="replace") as f:
            f.write(f"=== LEARNING STATS ===\n{json.dumps(stats, indent=2)}\n\n")
            f.write("\n".join([f"=== CONSENSUS ATTEMPT {i+1} ===\n{result}" for i, result in enumerate(consensus_results_raw)]))
        
        progress.update(10)  # 100%
        update_progress("✅ Learning Sequential MEGA Complete")
        progress.close()
        
        print(f"\n🎉 Learning Sequential MEGA Results saved to: {output_path}")
        print(f"🇱🇻 Latvian analysis: {len([r for r in lv_results.values() if r['answer'] in ['YES', 'MAYBE']])} matches")
        print(f"🇬🇧 English analysis: {len([r for r in en_results.values() if r['answer'] in ['YES', 'MAYBE']])} matches")
        print(f"🔥 Hot consensus: {len([r for r in consensus_results.values() if r['answer'] in ['Yes', 'Maybe']])} matches")
        print(f"🧠 Learning applied: {learning_applied_count} features")
        print(f"📊 Knowledge base: {stats['learned_features']} features, {stats['covered_codes']} codes")
        
        return csv_rows
        
    except Exception as e:
        progress.close()
        print(f"\n❌ Error during Learning Sequential MEGA processing: {e}")
        raise

def parse_language_results(result_text, language="LV"):
    """Parse single language matching results"""
    results = {}
    
    for line in result_text.split('\n'):
        line = line.strip()
        if ':' in line and '|' in line:
            nr_code = line.split(':')[0].strip()
            rest = line.split(':', 1)[1].strip()
            parts = rest.split('|')
            
            if len(parts) >= 2:
                answer = parts[0].strip().upper()
                text_snippet = parts[1].strip()
                
                results[nr_code] = {
                    'answer': answer,
                    'text': text_snippet if answer in ['YES', 'MAYBE'] else ""
                }
    
    return results

def parse_consensus_results(consensus_results, master_rows):
    """Parse and combine 3x consensus results with voting and reasoning"""
    all_votes = {}
    
    # Parse each consensus attempt
    for i, result_text in enumerate(consensus_results):
        for line in result_text.split('\n'):
            line = line.strip()
            if ':' in line and '|' in line:
                nr_code = line.split(':')[0].strip()
                rest = line.split(':', 1)[1].strip()
                parts = rest.split('|')
                
                if len(parts) >= 2:
                    answer = parts[0].strip().upper()
                    text_snippet = parts[1].strip() if len(parts) > 1 else ""
                    reasoning = parts[2].strip() if len(parts) > 2 else ""
                    
                    if nr_code not in all_votes:
                        all_votes[nr_code] = []
                    
                    all_votes[nr_code].append({
                        'attempt': i + 1,
                        'answer': answer,
                        'text': text_snippet if answer in ['YES', 'MAYBE'] else "",
                        'reasoning': reasoning
                    })
    
    # Calculate consensus with vote counting and reasoning
    consensus_results = {}
    for nr_code, votes in all_votes.items():
        yes_count = sum(1 for v in votes if v['answer'] == 'YES')
        maybe_count = sum(1 for v in votes if v['answer'] == 'MAYBE')
        no_count = sum(1 for v in votes if v['answer'] == 'NO')
        
        # Consensus logic: 3/3 Yes = Yes, 1-2/3 Yes = Maybe, 0/3 Yes = No
        if yes_count == 3:
            final_answer = "Yes"
        elif yes_count >= 1:
            final_answer = "Maybe"
        else:
            final_answer = "No"
        
        # Get best text snippet and reasoning
        best_vote = next((v for v in votes if v['answer'] == 'YES'), 
                        next((v for v in votes if v['answer'] == 'MAYBE'), 
                            next((v for v in votes if v['reasoning']), None)))
        
        # Combine reasoning from all votes
        all_reasoning = [v['reasoning'] for v in votes if v['reasoning']]
        combined_reasoning = "; ".join(all_reasoning) if all_reasoning else ""
        
        consensus_results[nr_code] = {
            'answer': final_answer,
            'text': best_vote['text'] if best_vote else "",
            'votes': f"{yes_count}Y/{maybe_count}M/{no_count}N",
            'reasoning': combined_reasoning
        }
    
    return consensus_results

def main():
    ap = argparse.ArgumentParser(description="Learning Sequential MEGA automotive matcher")
    ap.add_argument("--model", required=True, help="Base model ID (will find both .csv and _en.csv)")
    ap.add_argument("--specfile", required=True, help="Input text file")
    ap.add_argument("--exportdir", default="exports", help="Output directory")
    ap.add_argument("--llm", default="gpt-4o", help="LLM model")
    ap.add_argument("--no-normalize", action="store_true", help="Skip text normalization")
    args = ap.parse_args()
    
    # Setup paths
    spec_path = pathlib.Path(args.specfile)
    export_dir = pathlib.Path(args.exportdir) / args.model
    export_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = export_dir / f"ticksheet_learning_mega_{timestamp}.csv"
    
    # Read input
    spec_text = spec_path.read_text(encoding="utf-8")
    
    # Run Learning Sequential MEGA matching
    normalize_text = not args.no_normalize
    results = learning_sequential_mega_match(spec_text, args.model, output_path, args.llm, normalize_text)
    
    print(f"🧠 Learning Sequential MEGA matching complete!")
    print(f"Results: {output_path}")

if __name__ == "__main__":
    main()
