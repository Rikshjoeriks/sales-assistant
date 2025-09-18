# run_pipeline.py
# one-pass, validated pipeline: masterlist + pasted text -> GPT -> validated CSV
import argparse, csv, io, json, pathlib, re
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
    s = text.find(start)
    e = text.rfind(end)
    if s != -1 and e != -1 and e > s:
        return text[s+len(start):e].strip()
    # fallback if model forgot markers (rare)
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

def main():
    ap = argparse.ArgumentParser(description="Spec matcher: masterlist + pasted text -> validated CSV")
    ap.add_argument("--model", required=True, help="Session/Model ID (e.g., MCAFHEV)")
    ap.add_argument("--specfile", required=True, help="Path to pasted text .txt")
    ap.add_argument("--master", required=True, help="Path to masterlist CSV for this model")
    ap.add_argument("--exportdir", default="exports", help="Output directory (default: exports)")
    ap.add_argument("--llm", default="gpt-4o", help="OpenAI model (default: gpt-4o)")
    ap.add_argument("--temperature", type=float, default=0.8, help="LLM temperature (default: 0.8)")
    ap.add_argument("--maxtokens", type=int, default=8000, help="Max tokens to request (default: 8000)")
    args = ap.parse_args()

    model_id = args.model
    spec_path = pathlib.Path(args.specfile)
    master_path = pathlib.Path(args.master)
    export_root = pathlib.Path(args.exportdir) / model_id

    # load inputs
    if not master_path.exists():
        raise SystemExit(f"Masterlist not found: {master_path}")
    master_rows = read_masterlist(master_path)

    if not spec_path.exists():
        raise SystemExit(f"Spec text file not found: {spec_path}")
    scraped = normalize_text(spec_path.read_text(encoding="utf-8", errors="ignore"))

    # cap and log truncation if needed
    export_root.mkdir(parents=True, exist_ok=True)
    if len(scraped) > MAX_SPEC_LEN:
        (export_root / "WARN_truncated.txt").write_text(
            f"Scraped text truncated from {len(scraped)} to {MAX_SPEC_LEN} chars.", encoding="utf-8"
        )
        scraped = scraped[:MAX_SPEC_LEN]

    # build prompt
    prompt_text = pathlib.Path("prompt.txt").read_text(encoding="utf-8")
    system_msg, user_tpl = split_system_user(prompt_text)

    # make INPUT A a numbered list so GPT does not merge items
    scraped_numbered = number_lines(scraped)

    user_msg = build_user_message(user_tpl, model_id, scraped_numbered, master_jsonl(master_rows))
    user_msg = user_msg.replace("<<ROW_COUNT>>", str(len(master_rows)))

    # call LLM
    raw = call_model(system_msg, user_msg, model=args.llm, temperature=args.temperature, max_tokens=args.maxtokens)
    if raw is None:
        raw = ""

    # audit
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (export_root / "audit_user_prompt.txt").write_text(user_msg, encoding="utf-8")
    (export_root / "audit_model_output_raw.txt").write_text(raw, encoding="utf-8")

    # validate + emit CSV
    out_csv = export_root / f"ticksheet_{stamp}.csv"
    validate_and_reemit(master_rows, raw, out_csv, export_root)

    print(f"OK - validated & wrote {out_csv}", flush=True)

if __name__ == "__main__":
    main()
