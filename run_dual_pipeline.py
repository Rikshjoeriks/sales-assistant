# run_dual_pipeline.py
# Dual-language pipeline: Run Latvian first, then English, merge results
import argparse, csv, io, json, pathlib, re, subprocess, sys
from datetime import datetime
from openai import OpenAI
import httpx

ALLOWED_MATCH = {"Yes", "No", "Maybe", ""}  # empty only for TT rows
MAX_SPEC_LEN = 80000  # chars; safety cap for huge brochures

def number_lines(s: str) -> str:
    # Turn lines into 1), 2), … to force GPT to treat each as separate.
    lines = s.split("\n")
    return "\n".join(f"{i+1}) {ln}" for i, ln in enumerate(lines))

def read_masterlist(path: pathlib.Path):
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        rdr = csv.DictReader(f)
        required = {"Nr Code", "Variable Name"}
        missing = required - set(rdr.fieldnames or [])
        if missing:
            raise SystemExit(f"Masterlist missing columns: {missing}. Expected at least: {required}")
        for line in rdr:
            nr = (line.get("Nr Code") or "").strip()
            name = (line.get("Variable Name") or "").strip()
            is_tt = (line.get("Is TT") or "N").strip().upper() or "N"
            if not nr and not name:
                continue
            if is_tt not in {"Y","N"}:
                is_tt = "N"
            rows.append({"nr_code": nr, "variable_name": name, "is_tt": is_tt})
    if not rows:
        raise SystemExit("Masterlist appears empty.")
    return rows

def read_csv_results(path: pathlib.Path):
    """Read existing results CSV and return as list of rows (excluding header)"""
    if not path.exists():
        return []
    
    with open(path, encoding="utf-8", newline="") as f:
        rdr = csv.reader(f)
        rows = list(rdr)
    
    # Skip header if present
    if rows and any("Nr Code" in str(cell) for cell in rows[0]):
        rows = rows[1:]
    
    return rows

def master_jsonl(rows):
    # model consumes one object per line
    return "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)

def normalize_text(s: str) -> str:
    # Keep one feature per line; normalize whitespace per line.
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for raw in s.split("\n"):
        line = re.sub(r"\s+", " ", raw).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)

def split_system_user(prompt_text: str):
    parts = re.split(r"\nUSER\n", prompt_text, maxsplit=1)
    if len(parts) != 2 or not parts[0].startswith("SYSTEM"):
        raise SystemExit("prompt.txt must start with 'SYSTEM' and include a single 'USER' separator.")
    system_msg = parts[0].replace("SYSTEM", "", 1).strip()
    user_tpl = parts[1]
    return system_msg, user_tpl

def build_user_message(user_tpl: str, session_id: str, scraped_text: str, master_rows_jsonl: str):
    return (user_tpl
            .replace("<<SESSION_ID>>", session_id)
            .replace("<<<SCRAPED_TEXT>>>", scraped_text)
            .replace("<<<MASTER_ROWS_JSONL>>>", master_rows_jsonl))

def call_model(system_msg: str, user_msg: str, model: str, temperature: float, max_tokens: int):
    client = OpenAI()  # requires OPENAI_API_KEY in your environment
    try:
        resp = client.chat.completions.create(
            model=model,
            temperature=temperature,  # balanced fuzziness for synonyms
            top_p=1.0,
            messages=[
                {"role":"system","content": system_msg},
                {"role":"user","content": user_msg},
            ],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content
    except httpx.ConnectError:
        raise SystemExit("Network error: cannot reach api.openai.com (DNS/proxy/VPN). Set HTTPS_PROXY or check your connection.")

def extract_between_markers(text: str, start="BEGIN_CSV", end="END_CSV"):
    # First try official markers
    s = text.find(start)
    e = text.rfind(end)
    if s != -1 and e != -1 and e > s:
        return text[s+len(start):e].strip()
    
    # Fallback: look for markdown code blocks
    import re
    # Look for ```csv or ```plaintext or ``` followed by CSV-like content
    markdown_patterns = [
        r'```(?:csv|plaintext)?\s*\n(.*?)\n```',
        r'```\s*\n(.*?)\n```'
    ]
    
    for pattern in markdown_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            # Check if it looks like CSV (has commas and quotes)
            if ',' in content and ('NR' in content or 'Nr' in content):
                return content
    
    # Final fallback if model forgot markers (rare)
    return text.strip()

def validate_and_reemit(master_rows, model_text: str, out_path: pathlib.Path, audit_dir: pathlib.Path):
    raw = extract_between_markers(model_text)

    # parse model output safely
    rdr = csv.reader(io.StringIO(raw))
    out_rows = [row for row in rdr if any(cell.strip() for cell in row)]
    master_len = len(master_rows)

    # Drop accidental header row from model, if present
    if out_rows and any(h.lower().startswith("nr code") for h in out_rows[0]):
        out_rows = out_rows[1:]

    if len(out_rows) != master_len:
        # Coerce: truncate or pad with empty rows, and log
        with open(audit_dir / "WARN_row_coercion.txt", "a", encoding="utf-8") as wf:
            wf.write(f"Model rows={len(out_rows)} vs master rows={master_len}. Coercing to master length.\n")
        if len(out_rows) > master_len:
            out_rows = out_rows[:master_len]
        else:
            # pad with default values for clarity
            pad = []
            for mrow in master_rows[len(out_rows):]:
                # Always trust master for first 3 columns
                nr, name, is_tt = mrow["nr_code"], mrow["variable_name"], mrow["is_tt"]
                if is_tt == "Y":
                    match, snippet, reason = "", "", ""
                else:
                    match, snippet, reason = "No", "", "not stated"
                pad.append([nr, name, is_tt, match, snippet, reason])
            out_rows = out_rows + pad

    cleaned = []
    for idx, (mrow, out) in enumerate(zip(master_rows, out_rows)):
        out = (out + [""]*6)[:6]
        # Always trust master for the first 3 columns, ignore model's versions to avoid drift
        nr, name, is_tt = mrow["nr_code"], mrow["variable_name"], mrow["is_tt"]
        match, snippet, reason = [c.strip() for c in out[3:6]]
        
        # Fix for GPT outputting blank values - ensure non-TT rows have proper defaults
        if is_tt == "N" and not (match or snippet or reason):
            match, snippet, reason = "No", "", "not stated"
        # If match is empty but we have other fields, default match to No
        if is_tt == "N" and not match:
            match = "No"
        # If reason is empty for non-TT, provide default
        if is_tt == "N" and not reason:
            reason = "not stated"
            
        # If padded row (all blank), default to No / not stated for review
        if not match and not snippet and not reason and is_tt != "Y":
            match, reason = "No", "not stated"

        if is_tt == "Y":
            match, snippet, reason = "", "", ""
        else:
            # normalize label
            if match not in (ALLOWED_MATCH - {""}):
                low = match.lower()
                if "yes" in low: match = "Yes"
                elif "no" in low: match = "No"
                elif "maybe" in low or "partial" in low or "unclear" in low: match = "Maybe"
                else:
                    match = "Maybe"
                    if not reason:
                        reason = "label coerced"
            # clip snippet
            if len(snippet) > 140:
                snippet = snippet[:137] + "..."
        cleaned.append([nr, name, is_tt, match, snippet, reason])

    # re-emit with header for Excel convenience
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Nr Code","Variable Name","Is TT","Match (Yes/No/Maybe)","Matching Text","LLM_Reason"])
        w.writerows(cleaned)

def create_dual_language_output(lv_rows, en_rows, master_rows):
    """
    Create dual-language output format with separate columns for each language.
    Output format: [Nr Code, Variable Name, Is TT, LV Match, EN Match, Final Match, Include, LV Text, EN Text, LV Reason, EN Reason]
    """
    # Ensure all arrays have the same length
    max_len = len(master_rows)
    
    # Pad or truncate to match master length
    lv_rows = (lv_rows + [[""]*6 for _ in range(max_len)])[:max_len]
    en_rows = (en_rows + [[""]*6 for _ in range(max_len)])[:max_len]
    
    dual_results = []
    match_priority = {"Yes": 3, "Maybe": 2, "No": 1, "": 0}
    
    for i, (lv_row, en_row, master_row) in enumerate(zip(lv_rows, en_rows, master_rows)):
        # Ensure all rows have 6 columns
        lv_row = (lv_row + [""]*6)[:6]
        en_row = (en_row + [""]*6)[:6]
        
        # Get master data
        nr, name, is_tt = master_row["nr_code"], master_row["variable_name"], master_row["is_tt"]
        
        if is_tt == "Y":
            # Title rows - no matching
            dual_results.append([nr, name, is_tt, "", "", "", "No", "", "", "", ""])
            continue
        
        # Extract individual language results
        lv_match = lv_row[3] if len(lv_row) > 3 else ""
        lv_snippet = lv_row[4] if len(lv_row) > 4 else ""
        lv_reason = lv_row[5] if len(lv_row) > 5 else ""
        
        en_match = en_row[3] if len(en_row) > 3 else ""
        en_snippet = en_row[4] if len(en_row) > 4 else ""
        en_reason = en_row[5] if len(en_row) > 5 else ""
        
        # Clean up any language prefixes that might already exist
        lv_reason = lv_reason.replace("LV: ", "").replace("EN: ", "") if lv_reason else ""
        en_reason = en_reason.replace("LV: ", "").replace("EN: ", "") if en_reason else ""
        
        # Determine final match based on priority
        lv_priority = match_priority.get(lv_match, 0)
        en_priority = match_priority.get(en_match, 0)
        
        if lv_priority > en_priority:
            final_match = lv_match
        elif en_priority > lv_priority:
            final_match = en_match
        else:
            # Same priority level - prefer the one with more evidence
            lv_evidence = len(lv_snippet.strip())
            en_evidence = len(en_snippet.strip())
            
            if lv_evidence >= en_evidence and lv_match:
                final_match = lv_match
            elif en_match:
                final_match = en_match
            else:
                final_match = "No"
        
        # Default include to "No" unless there's a match
        include = "Yes" if final_match in ["Yes", "Maybe"] else "No"
        
        # Create dual-language row
        dual_results.append([
            nr, name, is_tt, 
            lv_match, en_match, final_match, 
            include, 
            lv_snippet, en_snippet, 
            lv_reason, en_reason
        ])
    
    return dual_results

def merge_latvian_english_results(lv_rows, en_rows, master_rows):
    """
    Legacy merge function for backwards compatibility.
    Creates simple merged results (old format).
    """
    dual_results = create_dual_language_output(lv_rows, en_rows, master_rows)
    
    # Convert dual format to old merged format
    merged = []
    for row in dual_results:
        nr, name, is_tt, lv_match, en_match, final_match, include, lv_text, en_text, lv_reason, en_reason = row
        
        if is_tt == "Y":
            merged.append([nr, name, is_tt, "", "", ""])
            continue
            
        # Use final match and pick the best evidence
        if final_match == lv_match and lv_text:
            final_text, final_reason = lv_text, f"LV: {lv_reason}"
        elif final_match == en_match and en_text:
            final_text, final_reason = en_text, f"EN: {en_reason}"
        elif lv_text:
            final_text, final_reason = lv_text, f"LV: {lv_reason}"
        elif en_text:
            final_text, final_reason = en_text, f"EN: {en_reason}"
        else:
            final_text, final_reason = "", "not found in either language"
            
        merged.append([nr, name, is_tt, final_match, final_text, final_reason])
    
    return merged

def run_single_language(model_id: str, spec_path: pathlib.Path, master_path: pathlib.Path, 
                       prompt_path: pathlib.Path, export_root: pathlib.Path, 
                       language_suffix: str, llm_model: str, temperature: float, max_tokens: int):
    """Run pipeline for a single language and return the output CSV path"""
    
    # Load inputs
    if not master_path.exists():
        raise SystemExit(f"Masterlist not found: {master_path}")
    master_rows = read_masterlist(master_path)

    if not spec_path.exists():
        raise SystemExit(f"Spec text file not found: {spec_path}")
    scraped = normalize_text(spec_path.read_text(encoding="utf-8", errors="ignore"))

    # Cap and log truncation if needed
    if len(scraped) > MAX_SPEC_LEN:
        (export_root / f"WARN_truncated_{language_suffix}.txt").write_text(
            f"Scraped text truncated from {len(scraped)} to {MAX_SPEC_LEN} chars.", encoding="utf-8"
        )
        scraped = scraped[:MAX_SPEC_LEN]

    # Build prompt
    if not prompt_path.exists():
        raise SystemExit(f"Prompt file not found: {prompt_path}")
    prompt_text = prompt_path.read_text(encoding="utf-8")
    system_msg, user_tpl = split_system_user(prompt_text)

    # Make INPUT A a numbered list so GPT does not merge items
    scraped_numbered = number_lines(scraped)
    user_msg = build_user_message(user_tpl, f"{model_id}_{language_suffix}", scraped_numbered, master_jsonl(master_rows))

    # Call LLM
    print(f"Calling {llm_model} for {language_suffix} recognition...", flush=True)
    raw = call_model(system_msg, user_msg, model=llm_model, temperature=temperature, max_tokens=max_tokens)
    if raw is None:
        raw = ""

    # Audit
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (export_root / f"audit_user_prompt_{language_suffix}.txt").write_text(user_msg, encoding="utf-8")
    (export_root / f"audit_model_output_raw_{language_suffix}.txt").write_text(raw, encoding="utf-8")

    # Validate + emit CSV
    out_csv = export_root / f"ticksheet_{language_suffix}_{stamp}.csv"
    validate_and_reemit(master_rows, raw, out_csv, export_root)
    
    print(f"Completed {language_suffix} processing -> {out_csv}", flush=True)
    return out_csv

def main():
    ap = argparse.ArgumentParser(description="Dual-language spec matcher: Latvian + English -> merged CSV")
    ap.add_argument("--model", required=True, help="Session/Model ID (e.g., MCAFHEV)")
    ap.add_argument("--specfile", required=True, help="Path to pasted text .txt")
    ap.add_argument("--master-lv", required=True, help="Path to Latvian masterlist CSV")
    ap.add_argument("--master-en", required=True, help="Path to English masterlist CSV")
    ap.add_argument("--prompt-lv", default="prompt.txt", help="Path to Latvian prompt file")
    ap.add_argument("--prompt-en", default="prompt_en.txt", help="Path to English prompt file")
    ap.add_argument("--exportdir", default="exports", help="Output directory (default: exports)")
    ap.add_argument("--llm", default="gpt-4o-mini", help="OpenAI model (default: gpt-4o-mini)")
    ap.add_argument("--temperature", type=float, default=0.8, help="LLM temperature (default: 0.8)")
    ap.add_argument("--maxtokens", type=int, default=8000, help="Max tokens to request (default: 8000)")
    args = ap.parse_args()

    model_id = args.model
    spec_path = pathlib.Path(args.specfile)
    master_lv_path = pathlib.Path(args.master_lv)
    master_en_path = pathlib.Path(args.master_en)
    prompt_lv_path = pathlib.Path(args.prompt_lv)
    prompt_en_path = pathlib.Path(args.prompt_en)
    export_root = pathlib.Path(args.exportdir) / model_id

    export_root.mkdir(parents=True, exist_ok=True)

    # Run Latvian pipeline first
    print("=== Running Latvian Recognition ===", flush=True)
    lv_csv_path = run_single_language(
        model_id, spec_path, master_lv_path, prompt_lv_path, 
        export_root, "LV", args.llm, args.temperature, args.maxtokens
    )

    # Run English pipeline second
    print("=== Running English Recognition ===", flush=True)
    en_csv_path = run_single_language(
        model_id, spec_path, master_en_path, prompt_en_path, 
        export_root, "EN", args.llm, args.temperature, args.maxtokens
    )

    # Load results for merging
    print("=== Creating Dual Language Output ===", flush=True)
    lv_rows = read_csv_results(lv_csv_path)
    en_rows = read_csv_results(en_csv_path)
    master_rows = read_masterlist(master_lv_path)  # Use LV master as reference for structure

    # Create dual-language results
    dual_rows = create_dual_language_output(lv_rows, en_rows, master_rows)

    # Save dual-language results
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dual_csv = export_root / f"ticksheet_dual_{stamp}.csv"
    
    with open(dual_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Nr Code","Variable Name","Is TT","LV Match","EN Match","Final Match","Include","LV Text","EN Text","LV Reason","EN Reason"])
        w.writerows(dual_rows)

    print(f"=== Complete ===", flush=True)
    print(f"Latvian results: {lv_csv_path}", flush=True)
    print(f"English results: {en_csv_path}", flush=True)
    print(f"Dual-language results: {dual_csv}", flush=True)

if __name__ == "__main__":
    main()
