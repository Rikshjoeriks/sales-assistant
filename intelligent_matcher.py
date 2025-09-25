#!/usr/bin/env python3
# intelligent_matcher.py - Smart feature matching system
# Extracts features from text, then matches them to correct masterlist positions

import argparse, csv, json, pathlib, re, time
from datetime import datetime
from openai import OpenAI
from tqdm import tqdm
from text_normalizer import normalize_spec_text

def extract_features_from_text(text, llm_model="gpt-4o"):
    """First pass: Extract all automotive features from the input text"""
    
    prompt = """You are an automotive feature extraction expert.

TASK: Extract all car features mentioned in the input text.

INPUT TEXT:
{text}

OUTPUT: List each feature on a separate line in this format:
- Feature name | Exact text from input | Category

Categories: Engine, Transmission, Safety, Lighting, Interior, Exterior, Technology, Other

EXAMPLE:
- All-wheel drive | All-wheel drive (AWD) system | Transmission
- LED headlights | LED headlights with adaptive lighting | Lighting
- Heated mirrors | Electric heated mirrors | Exterior

EXTRACTED FEATURES:"""

    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model=llm_model,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt.format(text=text)}],
            stream=False
        )
        
        # Safely extract content from response
        try:
            content = response.choices[0].message.content
            return content if content else "No features extracted"
        except (AttributeError, IndexError, TypeError) as e:
            return f"Invalid API response structure: {str(e)}"
            
    except Exception as e:
        print(f"Error in feature extraction: {e}")
        return f"Error extracting features: {str(e)}"

def parse_extracted_features(extracted_text):
    """Parse the extracted features into structured data"""
    features = []
    for line in extracted_text.split('\n'):
        line = line.strip()
        if line.startswith('-') and '|' in line:
            parts = line[1:].split('|')
            if len(parts) >= 3:
                feature_name = parts[0].strip()
                exact_text = parts[1].strip()
                category = parts[2].strip()
                features.append({
                    'name': feature_name,
                    'text': exact_text,
                    'category': category
                })
    return features

def match_to_masterlist(features, master_rows, llm_model="gpt-4o"):
    """Second pass: Match extracted features to specific masterlist items"""
    
    # Create feature database
    feature_db = "\n".join([f"- {f['name']}: {f['text']}" for f in features])
    
    # Create masterlist for matching
    masterlist_text = "\n".join([
        f"{row['nr_code']}: {row['variable_name']}" 
        for row in master_rows if row['is_tt'] == 'N'
    ])
    
    prompt = """You are an automotive feature matching expert.

TASK: Match extracted features to specific masterlist items.

EXTRACTED FEATURES FROM TEXT:
{features}

MASTERLIST TO MATCH AGAINST:
{masterlist}

RULES:
1. Each masterlist item should get either ONE matched feature or "No match"
2. Don't use the same extracted feature for multiple masterlist items
3. Only match if they represent the same automotive component
4. Be conservative - prefer "No match" over wrong matches

OUTPUT FORMAT (one line per masterlist item):
NR_CODE: Match_status | Feature_name | Exact_text | Reason

EXAMPLES:
NR24: MATCH | All-wheel drive | All-wheel drive (AWD) system | AWD = 4X4 pilna laika
NR25: NO_MATCH | | | No equivalent transmission feature found
NR26: MATCH | Automatic transmission | Automatic transmission with 8-speed CVT | Automatic transmission matches

MATCHING RESULTS:"""

    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model=llm_model,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt.format(features=feature_db, masterlist=masterlist_text)}],
            stream=False
        )
        
        # Safely extract content from response
        try:
            content = response.choices[0].message.content
            return content if content else "No matching results"
        except (AttributeError, IndexError, TypeError) as e:
            return f"Invalid API response structure: {str(e)}"
            
    except Exception as e:
        print(f"Error in matching: {e}")
        return f"Error in matching: {str(e)}"

def parse_matching_results(matching_text, master_rows):
    """Parse the matching results and create final CSV rows"""
    results = {}
    
    # Parse matching results
    for line in matching_text.split('\n'):
        line = line.strip()
        if ':' in line and '|' in line:
            nr_code = line.split(':')[0].strip()
            rest = line.split(':', 1)[1].strip()
            parts = rest.split('|')
            
            if len(parts) >= 4:
                status = parts[0].strip()
                feature_name = parts[1].strip()
                exact_text = parts[2].strip()
                reason = parts[3].strip()
                
                results[nr_code] = {
                    'status': status,
                    'feature_name': feature_name,
                    'exact_text': exact_text,
                    'reason': reason
                }
    
    # Create final CSV rows
    csv_rows = []
    for row in master_rows:
        nr_code = row['nr_code']
        name = row['variable_name']
        is_tt = row['is_tt']
        
        if is_tt == 'Y':
            # Section header
            csv_rows.append([nr_code, name, is_tt, "", "", ""])
        else:
            # Feature row
            if nr_code in results and results[nr_code]['status'].upper() == 'MATCH':
                match = "Yes"
                text = results[nr_code]['exact_text']
                reason = results[nr_code]['reason']
            else:
                match = "No"
                text = ""
                reason = "not mentioned" if nr_code not in results else results[nr_code]['reason']
            
            csv_rows.append([nr_code, name, is_tt, match, text, reason])
    
    return csv_rows

def intelligent_match(spec_text, master_path, output_path, llm_model="gpt-4o", normalize_text=True):
    """Main intelligent matching pipeline with progress tracking"""
    
    # Initialize progress bar
    progress = tqdm(total=100, desc="🚀 Spec Matching", unit="%", 
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
        
        # Step 0: Normalize text (new step) - SAFE mode only
        if normalize_text:
            progress.set_description("🧹 Normalizing text (safe)")
            # Force safe mode - basic cleanup only, NO GPT
            from text_normalizer import basic_text_cleanup
            spec_text = basic_text_cleanup(spec_text)
            progress.update(15)  # 20%
        else:
            progress.update(15)  # Skip normalization, go to 20%
        
        # Step 1: Extract features
        progress.set_description("🔍 Extracting features")
        extracted = extract_features_from_text(spec_text, llm_model)
        if not extracted:
            extracted = "No features extracted"
        progress.update(25)  # 45%
        
        # Step 2: Parse features
        progress.set_description("⚙️ Parsing features")
        features = parse_extracted_features(extracted)
        progress.update(15)  # 60%
        
        # Step 3: Match to masterlist
        progress.set_description("🎯 Matching to masterlist")
        matching_results = match_to_masterlist(features, master_rows, llm_model)
        if not matching_results:
            matching_results = "No matching results"
        progress.update(25)  # 85%
        
        # Step 4: Create final results
        progress.set_description("📊 Creating results")
        csv_rows = parse_matching_results(matching_results, master_rows)
        progress.update(10)  # 95%
        
        # Save results
        progress.set_description("💾 Saving files")
        with open(output_path, "w", encoding="utf-8", newline="", errors="replace") as f:
            writer = csv.writer(f)
            writer.writerow(["Nr Code", "Variable Name", "Is TT", "Match (Yes/No/Maybe)", "Matching Text", "LLM_Reason"])
            writer.writerows(csv_rows)
        
        # Save audit files (including normalized text)
        from pathlib import Path
        audit_dir = Path(output_path).parent
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Save normalized text
        if normalize_text:
            with open(audit_dir / f"audit_normalized_text_{timestamp}.txt", "w", encoding="utf-8", errors="replace") as f:
                f.write(spec_text)
        
        with open(audit_dir / f"audit_extracted_features_{timestamp}.txt", "w", encoding="utf-8", errors="replace") as f:
            f.write(extracted)
        
        with open(audit_dir / f"audit_matching_results_{timestamp}.txt", "w", encoding="utf-8", errors="replace") as f:
            f.write(matching_results)
        
        progress.update(5)  # 100%
        progress.set_description("✅ Complete")
        progress.close()
        
        print(f"\n🎉 Results saved to: {output_path}")
        print(f"📊 Processed {len(features)} features from {len(master_rows)} masterlist items")
        if normalize_text:
            print(f"🧹 Text normalized: {len(spec_text)} characters")
        
        return csv_rows
        
    except Exception as e:
        progress.close()
        print(f"\n❌ Error during processing: {e}")
        raise

def main():
    ap = argparse.ArgumentParser(description="Intelligent automotive feature matcher")
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
    output_path = export_dir / f"ticksheet_intelligent_{timestamp}.csv"
    
    # Read input
    spec_text = spec_path.read_text(encoding="utf-8")
    
    # Run intelligent matching with or without normalization
    normalize_text = not args.no_normalize
    results = intelligent_match(spec_text, master_path, output_path, args.llm, normalize_text)
    
    print(f"Intelligent matching complete!")
    print(f"Results: {output_path}")

if __name__ == "__main__":
    main()
