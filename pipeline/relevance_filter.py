import os
import sys
import time
import re
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

INPUT_FILE = os.path.join("data", "raw_all.csv")
CHECKPOINT_FILE = os.path.join("data", "checkpoint_relevance_v3.csv")
CLEAN_FILE = os.path.join("data", "clean_v3.csv")
REJECTED_FILE = os.path.join("data", "rejected_v3.csv")

BATCH_SIZE = 20
MODEL_NAME = "gemini-3.5-flash-lite"

SYSTEM_INSTRUCTION = """You are classifying text for a study on why shoppers save fashion items but do not buy them. You are looking ONLY for text where someone is deciding, hesitating, or seeking information BEFORE a purchase.

Answer YES only if the text shows one of these:
- Uncertainty or a question about size, fit, fabric, colour, or length that is unresolved
- Comparing two or more specific products or platforms in order to choose between them
- Saving, wishlisting, or postponing a purchase, or discussing items saved and not bought
- Asking someone else for an opinion before buying
- Seeking information in order to decide whether to buy
- Explicitly describing a purchase not yet made

CRITICAL EXCLUSION: Answer NO to comments that only request a purchase link, product name, price, or where to buy, with no stated uncertainty or question about the product itself. Examples that must be NO: 'link please', 'where can I buy this', 'name of the kurta?', 'I like the blue one, link?', 'second one link'. These show interest but contain no decision content.

Answer YES only if the comment contains a specific unresolved question about the product, its fit, its fabric, its suitability, or a comparison between options — even if a link request appears alongside it.

Answer NO for everything else, including:
- Any review of an item already purchased and received, even if it praises or criticises fit, size, quality, or fabric
- Generic praise or criticism of the app, prices, variety, or service
- Generic praise of the items shown in a video, e.g. 'all the suits are beautiful', 'so pretty', with no question attached
- Delivery, refund, return-processing, payment or customer-service issues
- App bugs, UI complaints, or performance issues
- Statements about variety or choice that express satisfaction rather than an unresolved decision

Critical test: if the person has already bought and received the item, the answer is NO regardless of what they say about it. If they are still deciding, the answer is YES.

Return exactly one line per comment:
1: YES
2: NO

Return nothing else."""

api_requests_this_run = 0

def classify_batch_with_retry(client, comments, batch_num, total_batches):
    global api_requests_this_run
    prompt_lines = []
    for idx, comment in enumerate(comments, start=1):
        clean_comment = str(comment).replace("\n", " ").replace("\r", " ").strip()
        prompt_lines.append(f"{idx}. {clean_comment}")
    
    prompt_text = "\n".join(prompt_lines)

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.0
    )

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            api_requests_this_run += 1
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
                print(f"\n==================== [RATE LIMIT 429 VERBATIM ERROR] ====================", file=sys.stderr, flush=True)
                print(err_str, file=sys.stderr, flush=True)
                print(f"=========================================================================\n", file=sys.stderr, flush=True)
                
                if "PerDay" in err_str:
                    print(f"\n[FATAL QUOTA ERROR] PerDay limit encountered. Stopping execution immediately.", file=sys.stderr, flush=True)
                    print(f"API requests made this run before stop: {api_requests_this_run}", file=sys.stderr, flush=True)
                    sys.exit(1)
                else:
                    print(f"[RATE LIMIT 429] Per-minute limit hit. Waiting 60s before retry (Attempt {attempt}/{max_retries})...", file=sys.stderr, flush=True)
                    time.sleep(60)
            else:
                print(f"\n[API ERROR] Batch {batch_num}/{total_batches} failed: Exception Type: {err_type}, Message: {err_str}", file=sys.stderr, flush=True)
                return None, err_type, err_str
        except Exception as e:
            err_str = str(e)
            err_type = type(e).__name__
            print(f"\n[ERROR] Batch {batch_num}/{total_batches} unexpected error: Exception Type: {err_type}, Message: {err_str}", file=sys.stderr, flush=True)
            return None, err_type, err_str

    print(f"\n[ERROR] Batch {batch_num}/{total_batches} failed after {max_retries} retries due to per-minute 429 rate limit.", file=sys.stderr, flush=True)
    return None, "RateLimitError", f"Exceeded max retries ({max_retries}) for per-minute 429 rate limit."

def parse_batch_response(response_text):
    if not response_text:
        return {}

    parsed_answers = {}
    for line in response_text.strip().splitlines():
        match = re.match(r"^\s*(\d+)\s*:\s*(YES|NO)\b", line, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            ans = match.group(2).upper()
            parsed_answers[num] = ans

    return parsed_answers

def is_blank(val):
    if pd.isna(val):
        return True
    s = str(val).strip()
    return s == "" or s == "nan" or s == "None"

def run_relevance_filter(diagnostic=False, pilot=False, pilot3=False, pilot4=False):
    global api_requests_this_run
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.", file=sys.stderr, flush=True)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found.", file=sys.stderr, flush=True)
        sys.exit(1)

    df_all = pd.read_csv(INPUT_FILE, encoding="utf-8")

    if pilot4:
        print("=== RUNNING PILOT 4 PASS (150 YouTube rows, seed 31) ===", flush=True)
        df_target = df_all[df_all["source"] == "youtube"].sample(n=150, random_state=31).reset_index(drop=True)
        df_target["relevant"] = None
        output_checkpoint = os.path.join("data", "pilot4.csv")
    elif pilot3:
        print("=== RUNNING PILOT 3 PASS (100 YouTube rows, seed 21) ===", flush=True)
        df_target = df_all[df_all["source"] == "youtube"].sample(n=100, random_state=21).reset_index(drop=True)
        df_target["relevant"] = None
        output_checkpoint = os.path.join("data", "pilot3.csv")
    elif pilot:
        print("=== RUNNING PILOT PASS (100 rows: 50 play_store, 50 youtube, seed 99) ===", flush=True)
        df_play = df_all[df_all["source"] == "play_store"].sample(n=50, random_state=99)
        df_yt = df_all[df_all["source"] == "youtube"].sample(n=50, random_state=99)
        df_target = pd.concat([df_play, df_yt]).reset_index(drop=True)
        df_target["relevant"] = None
        output_checkpoint = os.path.join("data", "pilot2.csv")
    elif diagnostic:
        print("=== RUNNING DIAGNOSTIC PASS (60 rows starting from row 861) ===", flush=True)
        df_target = df_all.iloc[860:920].copy().reset_index(drop=True)
        df_target["relevant"] = None
        output_checkpoint = os.path.join("data", "diagnostic_test.csv")
    else:
        df_target = df_all
        output_checkpoint = CHECKPOINT_FILE

        # Check for existing checkpoint to resume
        if os.path.exists(CHECKPOINT_FILE):
            try:
                df_ckpt = pd.read_csv(CHECKPOINT_FILE, encoding="utf-8")
                if "doc_id" in df_ckpt.columns and "relevant" in df_ckpt.columns:
                    ckpt_map = df_ckpt.set_index("doc_id")["relevant"].to_dict()
                    df_target["relevant"] = df_target["doc_id"].map(ckpt_map)
                    valid_done = df_target["relevant"].apply(lambda v: not is_blank(v))
                    print(f"Found existing checkpoint '{CHECKPOINT_FILE}'. Resuming: {valid_done.sum()} rows valid (YES/NO), re-processing remaining blank rows...", flush=True)
                else:
                    df_target["relevant"] = None
            except Exception as e:
                print(f"[WARNING] Error reading checkpoint file: {e}. Starting fresh...", flush=True)
                df_target["relevant"] = None
        else:
            df_target["relevant"] = None

    total_rows = len(df_target)

    # Determine indices needing classification (strictly blank/NaN rows)
    unclassified_indices = [idx for idx in df_target.index if is_blank(df_target.loc[idx, "relevant"])]
    initial_classified = total_rows - len(unclassified_indices)

    # Apply minimum length rule (< 40 characters) BEFORE batching / API call on remaining blank rows
    short_removed_count = 0
    for idx in unclassified_indices:
        text_val = str(df_target.loc[idx, "text"])
        if len(text_val) < 40:
            df_target.loc[idx, "relevant"] = "NO"
            short_removed_count += 1

    # Re-evaluate indices that actually need API calls (must be blank and length >= 40)
    api_unclassified_indices = [idx for idx in df_target.index if is_blank(df_target.loc[idx, "relevant"])]

    # Compute overall statistics for length floor
    total_short_rows = sum(1 for idx in df_target.index if len(str(df_target.loc[idx, "text"])) < 40)
    total_api_rows = total_rows - total_short_rows

    print(f"Minimum length filter (< 40 chars) statistics: {total_short_rows} / {total_rows} total rows are under 40 characters and automatically marked NO.")
    print(f"Processing corpus ({total_rows} rows). Remaining to send to API: {len(api_unclassified_indices)} rows...", flush=True)

    num_batches = (len(api_unclassified_indices) + BATCH_SIZE - 1) // BATCH_SIZE
    prev_milestone = initial_classified // 500

    for b in range(num_batches):
        batch_indices = api_unclassified_indices[b * BATCH_SIZE : (b + 1) * BATCH_SIZE]
        batch_comments = df_target.loc[batch_indices, "text"].tolist()

        raw_resp, err_type, err_msg = classify_batch_with_retry(client, batch_comments, b + 1, num_batches)
        parsed = parse_batch_response(raw_resp)

        if len(parsed) != len(batch_comments) or err_type is not None:
            missing_count = len(batch_comments) - len(parsed)
            print(f"\n[BATCH NOTICE] Batch {b + 1}/{num_batches}: Sent {len(batch_comments)} comments, parsed {len(parsed)} answers ({missing_count} missing/ERROR).", flush=True)
            if err_type is not None:
                print(f"Exception Type: {err_type}, Message: {err_msg}", flush=True)

        for item_idx, row_idx in enumerate(batch_indices, start=1):
            val = parsed.get(item_idx, "ERROR")
            df_target.loc[row_idx, "relevant"] = val

        # Progress check
        current_classified = total_rows - sum(1 for idx in df_target.index if is_blank(df_target.loc[idx, "relevant"]))
        current_milestone = current_classified // 500
        if current_milestone > prev_milestone:
            print(f"Progress: {current_milestone * 500} / {total_rows} rows classified... | API Requests this run: {api_requests_this_run}", flush=True)
            prev_milestone = current_milestone
        else:
            print(f"Batch {b + 1}/{num_batches} done ({current_classified}/{total_rows} classified) | API Requests this run: {api_requests_this_run}", flush=True)

        # Save checkpoint after every batch
        os.makedirs(os.path.dirname(output_checkpoint), exist_ok=True)
        df_target.to_csv(output_checkpoint, index=False, encoding="utf-8")

        # Pause 8 seconds between API calls
        if b < num_batches - 1:
            time.sleep(8)

    # Save final output datasets (skip if pilot or diagnostic)
    if not pilot and not pilot3 and not pilot4 and not diagnostic:
        df_clean = df_target[df_target["relevant"] == "YES"].copy()
        df_rejected = df_target[df_target["relevant"] == "NO"].copy()

        df_clean.to_csv(CLEAN_FILE, index=False, encoding="utf-8")
        df_rejected.to_csv(REJECTED_FILE, index=False, encoding="utf-8")

    # Summary Statistics
    total_processed = len(df_target)
    yes_count = (df_target["relevant"] == "YES").sum()
    no_count = (df_target["relevant"] == "NO").sum()
    error_count = (df_target["relevant"] == "ERROR").sum()
    overall_keep_rate = (yes_count / total_processed * 100) if total_processed > 0 else 0.0

    print("\n==========================================================================", flush=True)
    if pilot4:
        print("                        PILOT 4 RUN SUMMARY                               ", flush=True)
    elif pilot3:
        print("                        PILOT 3 RUN SUMMARY                               ", flush=True)
    elif pilot:
        print("                        PILOT RUN SUMMARY                                 ", flush=True)
    else:
        print("                 FULL CORPUS RELEVANCE FILTER SUMMARY                     ", flush=True)
    print("==========================================================================", flush=True)
    print(f"Rows Processed this Run:       {len(unclassified_indices)}", flush=True)
    print(f"Total Requests Made (this run): {api_requests_this_run}", flush=True)
    print(f"Total Processed:    {total_processed}", flush=True)
    print(f"YES Count (Clean):  {yes_count}", flush=True)
    print(f"NO Count (Reject): {no_count}", flush=True)
    print(f"ERROR Count:        {error_count}", flush=True)
    print(f"Overall Keep Rate:  {overall_keep_rate:.2f}%", flush=True)
    print(f"Saved Checkpoint:   {output_checkpoint}", flush=True)

    print("\n--- Keep Rate per Source ---", flush=True)
    print(f"{'Source':<15} | {'Total':<10} | {'YES (Clean)':<12} | {'NO (Reject)':<12} | {'Keep Rate':<10}", flush=True)
    print("-" * 68, flush=True)

    sources = sorted(df_target["source"].dropna().unique().tolist())
    for src in sources:
        sub_src = df_target[df_target["source"] == src]
        s_total = len(sub_src)
        s_yes = (sub_src["relevant"] == "YES").sum()
        s_no = (sub_src["relevant"] == "NO").sum()
        s_rate = (s_yes / s_total * 100) if s_total > 0 else 0.0
        print(f"{src:<15} | {s_total:<10} | {s_yes:<12} | {s_no:<12} | {s_rate:>8.2f}%", flush=True)
    print("==========================================================================", flush=True)

if __name__ == "__main__":
    is_diag = "--diagnostic" in sys.argv
    is_pilot = "--pilot" in sys.argv
    is_pilot3 = "--pilot3" in sys.argv
    is_pilot4 = "--pilot4" in sys.argv
    run_relevance_filter(diagnostic=is_diag, pilot=is_pilot, pilot3=is_pilot3, pilot4=is_pilot4)
