#!/usr/bin/env python3
# sequential_mega_matcher.py - True sequential dual-language pipeline
# Pipeline: Text Cleanup → Latvian Analysis → English Analysis → 3x Hot Consensus → Final Decision

import argparse, csv, json, pathlib, re, time
from datetime import datetime
from openai import OpenAI
from tqdm import tqdm
from text_normalizer import basic_text_cleanup

def intelligent_match_single_language(spec_text, master_path, language="LV", llm_model="gpt-4o"):
    """Run intelligent matching for a single language"""
    
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
    
    # Create masterlist for matching
    masterlist_text = "\n".join([
        f"{row['nr_code']}: {row['variable_name']}" 
        for row in master_rows if row['is_tt'] == 'N'
    ])
    
    language_instruction = {
        "LV": "Process in Latvian context. Look for Latvian automotive terms and match to Latvian masterlist items.",
        "EN": "Process in English context. Look for English automotive terms and match to English masterlist items."
    }
    
    prompt = f"""You are an automotive specification matching expert working with {language} language.

{language_instruction[language]}

TASK: For each masterlist item, determine if it's mentioned in the specification text.

SPECIFICATION TEXT:
{{spec_text}}

MASTERLIST TO MATCH AGAINST:
{{masterlist}}

RULES:
1. Answer "Yes", "Maybe", or "No" for each masterlist item
2. If "Yes" or "Maybe", provide the EXACT original text snippet that mentions it
3. Use {language} language context for understanding automotive terms
4. Be thorough but conservative - only "Yes" if clearly mentioned
5. Quote the original wording exactly as it appears in the source

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
            temperature=0.2,
            messages=[{"role": "user", "content": prompt.format(spec_text=spec_text, masterlist=masterlist_text)}],
            stream=False
        )
        
        content = response.choices[0].message.content
        return content if content else f"No {language} results"
    except Exception as e:
        print(f"Error in {language} matching: {e}")
        return f"Error in {language} matching"

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

def consensus_match_hot(spec_text, master_rows, llm_model="gpt-4o", progress_callback=None):
    """Run 3x consensus matching with hot temperature (0.5) for variation"""
    
    masterlist_text = "\n".join([
        f"{row['nr_code']}: {row['variable_name']}" 
        for row in master_rows if row['is_tt'] == 'N'
    ])
    
    prompt = """You are an automotive specification consensus validator providing detailed reasoning.

TASK: For each masterlist item, determine if it's mentioned in the specification text and explain your reasoning.

SPECIFICATION TEXT:
{spec_text}

MASTERLIST ITEMS:
{masterlist}

RULES:
1. Answer "Yes", "Maybe", or "No" for each item
2. If "Yes" or "Maybe", provide the EXACT original text snippet from source
3. ALWAYS provide clear reasoning for your decision
4. Be independent - don't be influenced by previous analyses
5. Quote original wording exactly as written

OUTPUT FORMAT:
NR_CODE: Answer | Original_text_snippet | Reasoning_explanation

EXAMPLES:
NR25: Yes | V2L capability mentioned in specifications | Clearly stated V2L feature
NR26: No | | No mention of heat pump technology in the specifications
NR27: Maybe | All-wheel drive system | Could refer to 4WD/AWD but not explicitly stated

CONSENSUS VALIDATION:"""

    client = OpenAI()
    results = []
    
    # Run 3 independent attempts with hot temperature
    for attempt in range(3):
        if progress_callback:
            progress_callback(f"🔥 Consensus attempt {attempt+1}/3")
        
        try:
            response = client.chat.completions.create(
                model=llm_model,
                temperature=0.5,  # Hot temperature for variation
                messages=[{"role": "user", "content": prompt.format(spec_text=spec_text, masterlist=masterlist_text)}],
                stream=False
            )
            
            content = response.choices[0].message.content
            results.append(content if content else f"No results from consensus attempt {attempt+1}")
        except Exception as e:
            results.append(f"Error in consensus attempt {attempt+1}: {e}")
    
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

def sequential_mega_match(spec_text, base_model, output_path, llm_model="gpt-4o", normalize_text=True, progress_callback=None):
    """Sequential MEGA pipeline: LV → EN → 3x Hot Consensus → Final Decision"""
    
    # Initialize progress bar
    progress = tqdm(total=100, desc="🚀 Sequential MEGA", unit="%", 
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
            progress.update(10)  # 10%
        else:
            progress.update(10)
        
        # Setup paths
        master_lv_path = pathlib.Path("masterlists") / f"{base_model}.csv"
        master_en_path = pathlib.Path("masterlists") / f"{base_model}_en.csv"
        
        # Load Latvian masterlist for structure
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
        
        # Step 2: Latvian Analysis
        update_progress("🇱🇻 Latvian analysis")
        lv_results_raw = intelligent_match_single_language(spec_text, master_lv_path, "LV", llm_model)
        lv_results = parse_language_results(lv_results_raw, "LV")
        progress.update(25)  # 40%
        
        # Step 3: English Analysis
        update_progress("🇬🇧 English analysis")
        en_results_raw = intelligent_match_single_language(spec_text, master_en_path, "EN", llm_model)
        en_results = parse_language_results(en_results_raw, "EN")
        progress.update(25)  # 65%
        
        # Step 4: 3x Hot Consensus
        update_progress("🔥 3x Hot consensus")
        consensus_results_raw = consensus_match_hot(spec_text, master_rows, llm_model, update_progress)
        consensus_results = parse_consensus_results(consensus_results_raw, master_rows)
        progress.update(25)  # 90%
        
        # Step 5: Combine results and create final CSV
        update_progress("📊 Final combination")
        
        headers = [
            "Nr Code", "Variable Name", "Is TT", 
            "LV Match", "LV Text", "EN Match", "EN Text", 
            "Consensus Vote", "Consensus Text", "Consensus Reasoning", "Include"
        ]
        
        csv_rows = []
        for row in master_rows:
            nr_code = row['nr_code']
            name = row['variable_name']
            is_tt = row['is_tt']
            
            if is_tt == 'Y':
                # Section header
                csv_rows.append([nr_code, name, is_tt, "", "", "", "", "", "", "", ""])
            else:
                # Feature row
                lv_result = lv_results.get(nr_code, {'answer': 'NO', 'text': ''})
                en_result = en_results.get(nr_code, {'answer': 'NO', 'text': ''})
                consensus_result = consensus_results.get(nr_code, {
                    'answer': 'No', 'text': '', 'votes': '0Y/0M/3N', 'reasoning': ''
                })
                
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
                    auto_tick
                ])
        
        # Save results
        with open(output_path, "w", encoding="utf-8", newline="", errors="replace") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(csv_rows)
        
        # Save audit files
        audit_dir = pathlib.Path(output_path).parent
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        with open(audit_dir / f"sequential_lv_analysis_{timestamp}.txt", "w", encoding="utf-8", errors="replace") as f:
            f.write(lv_results_raw)
        
        with open(audit_dir / f"sequential_en_analysis_{timestamp}.txt", "w", encoding="utf-8", errors="replace") as f:
            f.write(en_results_raw)
        
        with open(audit_dir / f"sequential_consensus_{timestamp}.txt", "w", encoding="utf-8", errors="replace") as f:
            f.write("\n".join([f"=== CONSENSUS ATTEMPT {i+1} ===\n{result}" for i, result in enumerate(consensus_results_raw)]))
        
        progress.update(10)  # 100%
        update_progress("✅ Sequential MEGA Complete")
        progress.close()
        
        print(f"\n🎉 Sequential MEGA Results saved to: {output_path}")
        print(f"🇱🇻 Latvian analysis: {len([r for r in lv_results.values() if r['answer'] in ['YES', 'MAYBE']])} matches")
        print(f"🇬🇧 English analysis: {len([r for r in en_results.values() if r['answer'] in ['YES', 'MAYBE']])} matches")
        print(f"🔥 Hot consensus: {len([r for r in consensus_results.values() if r['answer'] in ['Yes', 'Maybe']])} matches")
        print(f"📊 Processed {len(master_rows)} masterlist items")
        
        return csv_rows
        
    except Exception as e:
        progress.close()
        print(f"\n❌ Error during Sequential MEGA processing: {e}")
        raise

def main():
    ap = argparse.ArgumentParser(description="Sequential MEGA automotive matcher")
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
    output_path = export_dir / f"ticksheet_sequential_mega_{timestamp}.csv"
    
    # Read input
    spec_text = spec_path.read_text(encoding="utf-8")
    
    # Run Sequential MEGA matching
    normalize_text = not args.no_normalize
    results = sequential_mega_match(spec_text, args.model, output_path, args.llm, normalize_text)
    
    print(f"🚀 Sequential MEGA matching complete!")
    print(f"Results: {output_path}")

if __name__ == "__main__":
    main()
