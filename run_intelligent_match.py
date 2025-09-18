#!/usr/bin/env python3
"""
Wrapper to run intelligent matching from the UI
"""

import os
import sys
from intelligent_matcher import intelligent_match

def run_intelligent_match(session_name, llm_model="gpt-4o-mini"):
    """Run intelligent matching for a given session"""
    
    # Set up paths
    session_file = f"sessions/{session_name}_input.txt"
    master_file = f"masterlists/{session_name}.csv"
    output_file = f"exports/{session_name}/intelligent_match_output.csv"
    
    # Validate input files exist
    if not os.path.exists(session_file):
        print(f"Error: Session file not found: {session_file}")
        return False
        
    if not os.path.exists(master_file):
        print(f"Error: Master file not found: {master_file}")
        return False
    
    # Create output directory if needed
    os.makedirs(f"exports/{session_name}", exist_ok=True)
    
    # Read spec text
    with open(session_file, 'r', encoding='utf-8') as f:
        spec_text = f.read()
    
    print(f"Running intelligent matching for {session_name}...")
    print(f"Input text: {len(spec_text)} characters")
    
    # Run intelligent matching
    try:
        intelligent_match(spec_text, master_file, output_file, llm_model)
        print(f"✓ Intelligent matching completed successfully!")
        print(f"✓ Results saved to: {output_file}")
        return True
    except Exception as e:
        print(f"✗ Error during intelligent matching: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_intelligent_match.py <session_name> [llm_model]")
        print("Example: python run_intelligent_match.py MCAFHEV")
        sys.exit(1)
    
    session_name = sys.argv[1]
    llm_model = sys.argv[2] if len(sys.argv) > 2 else "gpt-4o-mini"
    
    success = run_intelligent_match(session_name, llm_model)
    sys.exit(0 if success else 1)
