#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-run consensus intelligent matcher
Runs intelligent matching multiple times and takes majority vote
"""

import os
import csv
import sys
from collections import defaultdict
from intelligent_matcher import intelligent_match
from feature_dictionary import FeatureDictionary
from tqdm import tqdm

# Force UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def run_consensus_match(session_name, num_runs=3, llm_model="gpt-4o"):
    """Run intelligent matching multiple times and take consensus"""
    
    print(f"Running {num_runs} intelligent matching attempts for consensus...")
    
    # Store all results
    all_results = []
    
    for run_num in range(num_runs):
        print(f"\n=== Run {run_num + 1}/{num_runs} ===")
        
        # Set up paths for this run
        session_file = f"sessions/{session_name}_input.txt"
        master_file = f"masterlists/{session_name}.csv"
        output_file = f"exports/{session_name}/consensus_run_{run_num + 1}.csv"
        
        # Read spec text
        try:
            with open(session_file, 'r', encoding='utf-8', errors='replace') as f:
                spec_text = f.read()
        except Exception as e:
            print(f"Error reading session file {session_file}: {e}")
            continue
        
        # Run intelligent matching
        try:
            intelligent_match(spec_text, master_file, output_file, llm_model)
            
            # Read results
            try:
                with open(output_file, 'r', encoding='utf-8', errors='replace') as f:
                    reader = csv.DictReader(f)
                    run_results = list(reader)
                    all_results.append(run_results)
                    print(f"Run {run_num + 1} completed: {len(run_results)} results")
            except Exception as e:
                print(f"Error reading results from {output_file}: {e}")
                continue
                
        except Exception as e:
            print(f"Run {run_num + 1} failed: {e}")
            continue
    
    if not all_results:
        print("All runs failed!")
        return False
    
    print(f"\n=== Creating Consensus from {len(all_results)} runs ===")
    
    # Create consensus
    consensus_results = []
    for i in range(len(all_results[0])):  # For each row
        nr_code = all_results[0][i]['Nr Code']
        variable_name = all_results[0][i]['Variable Name']
        is_tt = all_results[0][i]['Is TT']
        
        # Collect votes for this row
        match_votes = []
        text_votes = []
        reason_votes = []
        
        for run_results in all_results:
            if i < len(run_results):
                match_votes.append(run_results[i]['Match (Yes/No/Maybe)'])
                text_votes.append(run_results[i]['Matching Text'])
                reason_votes.append(run_results[i]['LLM_Reason'])
        
        # Take majority vote for match
        match_counts = defaultdict(int)
        for vote in match_votes:
            match_counts[vote] += 1
        
        consensus_match = max(match_counts.items(), key=lambda x: x[1])[0]
        confidence = match_counts[consensus_match] / len(match_votes)
        
        # For text and reason, use the one from the majority match vote
        consensus_text = ""
        consensus_reason = ""
        
        for run_results in all_results:
            if i < len(run_results) and run_results[i]['Match (Yes/No/Maybe)'] == consensus_match:
                if run_results[i]['Matching Text']:
                    consensus_text = run_results[i]['Matching Text']
                if run_results[i]['LLM_Reason']:
                    consensus_reason = run_results[i]['LLM_Reason']
                break
        
        # Add confidence info to reason
        if consensus_reason:
            consensus_reason += f" (Confidence: {confidence:.0%} - {match_counts[consensus_match]}/{len(match_votes)} votes)"
        
        consensus_results.append({
            'Nr Code': nr_code,
            'Variable Name': variable_name,
            'Is TT': is_tt,
            'Match (Yes/No/Maybe)': consensus_match,
            'Matching Text': consensus_text,
            'LLM_Reason': consensus_reason
        })
    
    # Save consensus results
    consensus_file = f"exports/{session_name}/consensus_intelligent_match.csv"
    os.makedirs(f"exports/{session_name}", exist_ok=True)
    
    try:
        with open(consensus_file, 'w', encoding='utf-8', newline='', errors='replace') as f:
            writer = csv.DictWriter(f, fieldnames=['Nr Code', 'Variable Name', 'Is TT', 'Match (Yes/No/Maybe)', 'Matching Text', 'LLM_Reason'])
            writer.writeheader()
            writer.writerows(consensus_results)
        
        print(f"✓ Consensus results saved to: {consensus_file}")
    except Exception as e:
        print(f"Error saving consensus results: {e}")
        return False
    
    # Print summary
    matches = sum(1 for r in consensus_results if r['Match (Yes/No/Maybe)'] in ['Yes', 'Maybe'])
    print(f"✓ Found {matches} matches with consensus agreement")
    
    # Add results to feature dictionary
    try:
        fd = FeatureDictionary()
        imported_count = fd.import_from_csv(consensus_file, session_name, "consensus_match")
        print(f"✓ Added {imported_count} features to dictionary")
    except Exception as e:
        print(f"Warning: Could not update feature dictionary: {e}")
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-run consensus intelligent matcher")
    parser.add_argument("session_name", help="Session/model name")
    parser.add_argument("num_runs", type=int, nargs='?', default=3, help="Number of runs (default: 3)")
    parser.add_argument("--llm", default="gpt-4o", help="LLM model to use (default: gpt-4o)")
    
    args = parser.parse_args()
    
    success = run_consensus_match(args.session_name, args.num_runs, args.llm)
    sys.exit(0 if success else 1)
