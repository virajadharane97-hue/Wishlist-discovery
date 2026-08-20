import os
import sys
import time
import re
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

INPUT_FILE = os.path.join("data", "clean_v5.csv")
OUTPUT_FILE = os.path.join("data", "open_coding_raw.csv")
BATCH_SIZE = 20
MODEL_NAME = "gemini-3.5-flash-lite"

SYSTEM_INSTRUCTION = """For each numbered comment below, answer two things:

1. What is this person uncertain about, hesitating over, or unable to
resolve? Describe it in your own words, under 15 words. If nothing,
write NONE.

2. Invent a short label for that problem, in the form of a few words
joined by underscores, for example unsure_size_across_brands.

Do not use any predefined list of categories. Invent labels from what
the text actually says.

Return one line per comment:
1 | description | invented_label
2 | NONE | NONE

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

def parse_batch_response(response_text):
    if not response_text:
        return {}

    parsed_answers = {}
    for line in response_text.strip().splitlines():
        parts = line.split("|")
        if len(parts) >= 3:
            num_part = parts[0].strip()
            num_part = re.sub(r"[^\d]", "", num_part)
            if num_part.isdigit():
                idx = int(num_part)
                desc = parts[1].strip()
                label = parts[2].strip()
                parsed_answers[idx] = (desc, label)
    return parsed_answers

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY_2") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: Gemini API key not found in environment or .env file.", file=sys.stderr, flush=True)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found.", file=sys.stderr, flush=True)
        sys.exit(1)

    df_clean = pd.read_csv(INPUT_FILE, encoding="utf-8")
    
    # 1. Stratify proportionally by source
    total_count = len(df_clean)
    sample_size = 200
    
    sources = df_clean["source"].unique()
    sample_dfs = []
    
    # Pre-calculate counts to handle potential rounding issues
    allocations = {}
    for src in sources:
        src_df = df_clean[df_clean["source"] == src]
        allocations[src] = round((len(src_df) / total_count) * sample_size)
    
    # Adjust to sum exactly to sample_size (200) if rounding causes off-by-one or two
    current_sum = sum(allocations.values())
    if current_sum != sample_size:
        diff = sample_size - current_sum
        largest_src = max(allocations, key=allocations.get)
        allocations[largest_src] += diff
        
    print("Stratified sample allocation from clean_v5.csv:")
    for src, alloc in allocations.items():
        print(f"  - {src}: {alloc} rows")
        src_df = df_clean[df_clean["source"] == src]
        sampled_src = src_df.sample(n=alloc, random_state=55)
        sample_dfs.append(sampled_src)
        
    df_sample = pd.concat(sample_dfs).reset_index(drop=True)
    print(f"Total sampled rows: {len(df_sample)}")

    # Add columns for coding
    df_sample["description"] = None
    df_sample["invented_label"] = None

    num_batches = (len(df_sample) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Starting API coding process in {num_batches} batches of {BATCH_SIZE}...")

    for b in range(num_batches):
        batch_indices = list(range(b * BATCH_SIZE, min((b + 1) * BATCH_SIZE, len(df_sample))))
        batch_comments = df_sample.loc[batch_indices, "text"].tolist()

        raw_resp, err_type, err_msg = classify_batch_with_retry(client, batch_comments, b + 1, num_batches)
        parsed = parse_batch_response(raw_resp)

        if len(parsed) != len(batch_comments):
            print(f"[WARNING] Batch {b + 1}/{num_batches}: Sent {len(batch_comments)} comments, parsed {len(parsed)} answers.")

        for item_idx, row_idx in enumerate(batch_indices, start=1):
            desc, label = parsed.get(item_idx, ("ERROR", "ERROR"))
            df_sample.loc[row_idx, "description"] = desc
            df_sample.loc[row_idx, "invented_label"] = label

        # Pause 8 seconds between API calls to control rate limits
        if b < num_batches - 1:
            time.sleep(8)

    # Save to output file
    df_output = df_sample[["doc_id", "source", "text", "description", "invented_label"]]
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df_output.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\nRaw open coding output saved to {OUTPUT_FILE}")

    # Analysis and printing
    total_processed = len(df_output)
    
    # Calculate count of NONE (case-insensitive checking)
    none_count = df_output["invented_label"].astype(str).str.strip().str.upper().eq("NONE").sum()
    
    # Value counts of invented_label
    label_counts = df_output["invented_label"].value_counts()

    print("\n" + "="*50)
    print("                 OPEN CODING RESULTS SUMMARY      ")
    print("="*50)
    print(f"Total Rows Processed:  {total_processed}")
    print(f"Count of NONE Labels:  {none_count}")
    print("\n--- Unique Invented Labels and Frequencies (Descending) ---")
    print(f"{'Invented Label':<35} | {'Frequency':<10}")
    print("-" * 50)
    for lbl, freq in label_counts.items():
        print(f"{str(lbl):<35} | {freq:<10}")
    print("="*50)

if __name__ == "__main__":
    main()
