import os
import sys
import time
import re
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

INPUT_FILE = os.path.join("data", "clean_v5_tagged.csv")
BATCH_SIZE = 20
MODEL_NAME = "gemini-3.5-flash-lite"

api_requests_this_run = 0

def is_blank(val):
    if pd.isna(val):
        return True
    s = str(val).strip()
    return s == "" or s == "nan" or s == "None"

def format_code(c):
    lines = [f"Code: {c['code']}", f"Definition: {c['definition']}"]
    if "use_when" in c:
        lines.append(f"Use When: {c['use_when']}")
    if "do_not_use_when" in c:
        lines.append(f"Do Not Use When: {c['do_not_use_when']}")
    return "\n".join(lines)

def classify_batch_with_retry(client, comments, system_instruction, batch_num, total_batches):
    global api_requests_this_run
    prompt_lines = []
    for idx, comment in enumerate(comments, start=1):
        clean_comment = str(comment).replace("\n", " ").replace("\r", " ").strip()
        prompt_lines.append(f"{idx}. {clean_comment}")
    
    prompt_text = "\n".join(prompt_lines)

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.0
    )

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            api_requests_this_run += 1
            print(f"API Request #{api_requests_this_run} sent for batch {batch_num}/{total_batches}...", flush=True)
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt_text,
                config=config
            )
            return response.text, None, None
        except (ClientError, APIError) as e:
            err_str = str(e)
            err_type = type(e).__name__
            is_429 = getattr(e, "code", None) == 429 or getattr(e, "status_code", None) == 429 or "429" in err_str or "RESOURCE_EXHAUSTED" in err_str
            if is_429:
                if "PerDay" in err_str:
                    print(f"\n[FATAL QUOTA ERROR] PerDay limit encountered. Stopping execution immediately.", file=sys.stderr, flush=True)
                    return None, "PerDayQuotaError", err_str
                else:
                    print(f"[RATE LIMIT 429] Per-minute limit hit. Waiting 60s before retry (Attempt {attempt}/{max_retries})...", file=sys.stderr, flush=True)
                    time.sleep(60)
            else:
                print(f"[API ERROR] Batch {batch_num}/{total_batches} failed: Exception Type: {err_type}, Message: {err_str}", file=sys.stderr, flush=True)
                return None, err_type, err_str
        except Exception as e:
            err_str = str(e)
            err_type = type(e).__name__
            print(f"[ERROR] Batch {batch_num}/{total_batches} unexpected error: Exception Type: {err_type}, Message: {err_str}", file=sys.stderr, flush=True)
            return None, err_type, err_str

    print(f"[ERROR] Batch {batch_num}/{total_batches} failed after {max_retries} retries.", file=sys.stderr, flush=True)
    return None, "RateLimitError", f"Exceeded max retries ({max_retries}) for per-minute 429 rate limit."

def parse_json_response(response_text):
    if not response_text:
        return {}

    parsed_answers = {}
    clean_resp = response_text.strip()
    # Remove markdown formatting if present
    clean_resp = re.sub(r"^```(?:json)?\s*", "", clean_resp, flags=re.IGNORECASE)
    clean_resp = re.sub(r"\s*```$", "", clean_resp)
    clean_resp = clean_resp.strip()
    
    try:
        data = json.loads(clean_resp)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "n" in item:
                    try:
                        n = int(item["n"])
                        parsed_answers[n] = item
                    except (ValueError, TypeError):
                        pass
    except Exception:
        # Regex extraction fallback if array is malformed
        matches = re.findall(r"\{[^{}]*\}", clean_resp)
        for m in matches:
            try:
                item = json.loads(m)
                if isinstance(item, dict) and "n" in item:
                    try:
                        n = int(item["n"])
                        parsed_answers[n] = item
                    except (ValueError, TypeError):
                        pass
            except Exception:
                pass
                
    return parsed_answers

def clean_for_console(s):
    if s is None:
        return "None"
    return str(s).encode('ascii', 'backslashreplace').decode('ascii')

def run_validation(df_classified, codebook):
    valid_blockers = {c["code"] for c in codebook["blocker_codes"]}
    valid_intents = {c["code"] for c in codebook["intent_codes"]}
    
    valid_blockers.update([None, "null", "", "NaN"])
    valid_intents.update([None, "null", "", "NaN"])

    # Rows processed, API requests, ERROR count
    total_rows = len(df_classified)
    error_count = (df_classified["role"] == "ERROR").sum()
    
    print("\n==========================================================================", flush=True)
    print("                      CLASSIFICATION SUMMARY                              ", flush=True)
    print("==========================================================================", flush=True)
    print(f"Rows processed:       {total_rows}", flush=True)
    print(f"API requests made:    {api_requests_this_run}", flush=True)
    print(f"ERROR count:          {error_count}", flush=True)

    # Frequency of every primary_blocker including null
    print("\n--- Frequency of every primary_blocker ---", flush=True)
    pb_counts = df_classified["primary_blocker"].value_counts(dropna=False)
    for pb, cnt in pb_counts.items():
        print(f"  {clean_for_console(pb)}: {cnt}", flush=True)

    # Frequency of every secondary_blocker including null
    print("\n--- Frequency of every secondary_blocker ---", flush=True)
    sb_counts = df_classified["secondary_blocker"].value_counts(dropna=False)
    for sb, cnt in sb_counts.items():
        print(f"  {clean_for_console(sb)}: {cnt}", flush=True)

    # Frequency of every intent_code including null
    print("\n--- Frequency of every intent_code ---", flush=True)
    it_counts = df_classified["intent_code"].value_counts(dropna=False)
    for it, cnt in it_counts.items():
        print(f"  {clean_for_console(it)}: {cnt}", flush=True)

    # Role distribution
    print("\n--- Role distribution ---", flush=True)
    role_counts = df_classified["role"].value_counts(dropna=False)
    for role, cnt in role_counts.items():
        print(f"  {clean_for_console(role)}: {cnt}", flush=True)

    # Count of invalidated quotes
    invalidated_count = (df_classified["quote_valid"] == False).sum()
    print(f"\nCount of invalidated quotes: {invalidated_count}", flush=True)

    # Any invented code names
    invented_codes = []
    for idx, row in df_classified.iterrows():
        pb = row["primary_blocker"]
        sb = row["secondary_blocker"]
        it = row["intent_code"]
        
        if not is_blank(pb) and str(pb).strip().lower() != "null" and pb not in valid_blockers:
            invented_codes.append((row["doc_id"], "primary_blocker", pb))
        if not is_blank(sb) and str(sb).strip().lower() != "null" and sb not in valid_blockers:
            invented_codes.append((row["doc_id"], "secondary_blocker", sb))
        if not is_blank(it) and str(it).strip().lower() != "null" and it not in valid_intents:
            invented_codes.append((row["doc_id"], "intent_code", it))
            
    print("\n--- Invented Code Names (Not in Codebook) ---", flush=True)
    if invented_codes:
        for doc_id, field, code in invented_codes:
            print(f"  - {clean_for_console(doc_id)} | Field: {clean_for_console(field)} | Code: {clean_for_console(code)}", flush=True)
    else:
        print("  None found.", flush=True)

    # Count of rows where primary_blocker is null but role is "seeking"
    cond = (df_classified["primary_blocker"].apply(lambda v: is_blank(v) or str(v).strip().lower() == "null")) & (df_classified["role"] == "seeking")
    count_null_pb_seeking = cond.sum()
    print(f"\nCount of rows where primary_blocker is null but role is 'seeking': {count_null_pb_seeking}", flush=True)
    print("==========================================================================", flush=True)

def normalize_text(s):
    if pd.isna(s):
        return ""
    s = str(s).strip()
    s = re.sub(r"\s+", " ", s)
    return s

def main():
    global api_requests_this_run
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY_2") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: Gemini API key not found in environment.", file=sys.stderr, flush=True)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    is_pilot = "--pilot" in sys.argv
    
    if not os.path.exists("data/codebook.json"):
        print("Error: data/codebook.json not found.", file=sys.stderr, flush=True)
        sys.exit(1)

    with open("data/codebook.json", "r", encoding="utf-8") as f:
        codebook = json.load(f)

    # Format blocker and intent definitions for system prompt
    blocker_defs = []
    for c in codebook["blocker_codes"]:
        blocker_defs.append(format_code(c))
    blocker_text = "\n\n".join(blocker_defs)

    intent_defs = []
    for c in codebook["intent_codes"]:
        lines = [f"Code: {c['code']}", f"Definition: {c['definition']}"]
        if "use_when" in c:
            lines.append(f"Use When: {c['use_when']}")
        if "do_not_use_when" in c:
            lines.append(f"Do Not Use When: {c['do_not_use_when']}")
        intent_defs.append("\n".join(lines))
    intent_text = "\n\n".join(intent_defs)

    SYSTEM_INSTRUCTION = f"""You are classifying a fashion shopping wishlist study corpus. For each comment, determine the role, intent, purchase stage, blockers, and details.

Here is the Codebook of Blocker Codes:
{blocker_text}

Here is the Codebook of Intent Codes:
{intent_text}

For each comment, return exactly this JSON structure:
{{
  "n": 1,
  "role": "seeking | advising | null",
  "intent_code": "one INTENT_* code or null",
  "primary_blocker": "one BLOCK_* code or null",
  "secondary_blocker": "one BLOCK_* code or null",
  "purchase_stage": "discovery | consideration | saved | comparison | decision | cart | post_purchase",
  "unresolved_question": "the question they still cannot answer, or null",
  "information_sought": "size | fit | fabric | styling | reviews | social_proof | alternatives | durability | authenticity | null",
  "external_workaround": "google | youtube | instagram | reddit | friends | creator | offline_store | tailor | thrift | none | null",
  "conversion_proximity": "low | medium | high",
  "severity_1_5": 3,
  "confidence_1_5": 4,
  "evidence_quote": "max 12 words, exact words from the text only"
}}

Hard rules:
- Use only what the text says. Never infer beyond it.
- Return null rather than guessing when a field is not supported.
- Never invent a code name. Only codes from the Codebook above.
- evidence_quote must be verbatim from the input, under 12 words.
- role is "advising" when the person is answering someone else's question rather than describing their own uncertainty.
- If no blocker applies, primary_blocker is null. Do not force a code.
- ROLE RULE: When role is 'advising' — the person is sharing a strategy, answering someone else's question, or giving general advice — primary_blocker must be null unless they also describe their own current unresolved uncertainty about a specific item. Their advice may still carry an intent_code and an external_workaround value.
- CONTENT REQUEST RULE: Comments asking a creator to make a video, do a haul, review a product, or cover a topic are not purchase blockers. Set primary_blocker to null. Examples: 'please make a video on shirts', 'plz bna de suit guide pe', 'do polos next'.

Return a JSON array of objects, one corresponding to each numbered comment (e.g. n matches the comment number). Return nothing else."""

    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.", file=sys.stderr, flush=True)
        sys.exit(1)

    df_all = pd.read_csv(INPUT_FILE, encoding="utf-8")

    # Define targets and checkpoints
    if is_pilot:
        print("=== RUNNING PILOT CLASSIFICATION PASS (100 rows, seed 66) ===", flush=True)
        df_target = df_all.sample(n=100, random_state=66).reset_index(drop=True)
        output_file = os.path.join("data", "pilot_classify.csv")
        checkpoint_file = os.path.join("data", "pilot_classify.csv")
    else:
        print("=== RUNNING FULL CORPUS CLASSIFICATION PASS ===", flush=True)
        df_target = df_all.copy()
        output_file = os.path.join("data", "labelled_v3.csv")
        checkpoint_file = os.path.join("data", "checkpoint_classify_v3.csv")

    # Initialize classification columns if not existing
    FIELDS = [
        "role", "intent_code", "primary_blocker", "secondary_blocker", 
        "purchase_stage", "unresolved_question", "information_sought", 
        "external_workaround", "conversion_proximity", "severity_1_5", 
        "confidence_1_5", "evidence_quote", "quote_valid"
    ]
    for field in FIELDS:
        if field not in df_target.columns:
            df_target[field] = None

    # Load existing checkpoint to resume
    if os.path.exists(checkpoint_file):
        try:
            df_ckpt = pd.read_csv(checkpoint_file, encoding="utf-8")
            if "doc_id" in df_ckpt.columns:
                # Ensure quote_valid exists in loaded df_ckpt
                if "quote_valid" not in df_ckpt.columns:
                    df_ckpt["quote_valid"] = None
                ckpt_map = df_ckpt.set_index("doc_id")[FIELDS].to_dict("index")
                for idx, row in df_target.iterrows():
                    d_id = row["doc_id"]
                    if d_id in ckpt_map:
                        for field in FIELDS:
                            df_target.at[idx, field] = ckpt_map[d_id][field]
                valid_done = df_target["quote_valid"].apply(lambda q: q is True or q is False)
                print(f"Resuming classification: {valid_done.sum()} / {len(df_target)} rows already classified.", flush=True)
        except Exception as e:
            print(f"[WARNING] Error reading checkpoint file: {e}. Starting fresh...", flush=True)

    unclassified_indices = [idx for idx in df_target.index if df_target.loc[idx, "quote_valid"] is None]
    
    if len(unclassified_indices) == 0:
        print("All rows already classified. Running validation statistics directly.", flush=True)
    else:
        print(f"Processing {len(unclassified_indices)} unclassified rows in batches of {BATCH_SIZE}...", flush=True)
        
        num_batches = (len(unclassified_indices) + BATCH_SIZE - 1) // BATCH_SIZE
        
        for b in range(num_batches):
            batch_indices = unclassified_indices[b * BATCH_SIZE : (b + 1) * BATCH_SIZE]
            batch_comments = df_target.loc[batch_indices, "text"].tolist()

            raw_resp, err_type, err_msg = classify_batch_with_retry(
                client, batch_comments, SYSTEM_INSTRUCTION, b + 1, num_batches
            )
            
            if err_type == "PerDayQuotaError":
                print("\n[FATAL] PerDay limit reached. Preserving checkpoint and exiting.", flush=True)
                break
                
            parsed = parse_json_response(raw_resp)
            
            # Map parsed JSON objects back to dataframe rows
            for item_idx, row_idx in enumerate(batch_indices, start=1):
                item_data = parsed.get(item_idx)
                if item_data and isinstance(item_data, dict):
                    for field in FIELDS[:-1]: # Map role, intent_code, blockers, etc. (excluding quote_valid)
                        val = item_data.get(field, None)
                        df_target.at[row_idx, field] = val
                    
                    # Verbatim quote check and normalization
                    quote = df_target.at[row_idx, "evidence_quote"]
                    text = df_target.at[row_idx, "text"]
                    if is_blank(quote) or str(quote).strip().lower() in ["null", "error"]:
                        df_target.at[row_idx, "quote_valid"] = True
                    else:
                        q_norm = normalize_text(quote)
                        t_norm = normalize_text(text)
                        if q_norm.lower() in t_norm.lower():
                            df_target.at[row_idx, "quote_valid"] = True
                        else:
                            df_target.at[row_idx, "evidence_quote"] = None
                            df_target.at[row_idx, "quote_valid"] = False
                else:
                    # JSON parse fail for this specific row
                    for field in FIELDS[:-1]:
                        df_target.at[row_idx, field] = "ERROR"
                    df_target.at[row_idx, "quote_valid"] = True
            
            # Checkpoint save after every batch
            df_target.to_csv(checkpoint_file, index=False, encoding="utf-8")
            print(f"Batch {b+1}/{num_batches} done and checkpointed. | Requests: {api_requests_this_run}", flush=True)

            if b < num_batches - 1:
                time.sleep(8)

    # Perform post-classification verbatim validation step globally
    invalidated_count = 0
    for idx, row in df_target.iterrows():
        quote = row.get("evidence_quote")
        text = row.get("text")
        
        # If already flagged as invalid (False), increment count
        if df_target.at[idx, "quote_valid"] is False:
            invalidated_count += 1
            continue
            
        if is_blank(quote) or str(quote).strip().lower() in ["null", "error"]:
            df_target.at[idx, "quote_valid"] = True
            continue
            
        q_norm = normalize_text(quote)
        t_norm = normalize_text(text)
        
        if q_norm.lower() in t_norm.lower():
            df_target.at[idx, "quote_valid"] = True
        else:
            df_target.at[idx, "evidence_quote"] = None
            df_target.at[idx, "quote_valid"] = False
            invalidated_count += 1
            
    print(f"\nVerbatim Quote Validation: {invalidated_count} quotes were invalidated and set to null.")

    # Save final completed classification if fully done
    is_fully_done = df_target["quote_valid"].apply(lambda q: q is True or q is False).sum() == len(df_target)
    if is_fully_done:
        df_target.to_csv(output_file, index=False, encoding="utf-8")
        print(f"\nClassification successfully complete! Final file saved to {output_file}", flush=True)

    # Run validation checks on the target dataframe
    run_validation(df_target, codebook)

if __name__ == "__main__":
    main()
