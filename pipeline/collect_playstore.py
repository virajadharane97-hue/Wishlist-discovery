import os
import sys
import pandas as pd
from google_play_scraper import Sort, reviews

PACKAGE_ID = "com.myntra.android"
FULL_TARGET_COUNT = 10000
SAMPLE_TARGET_COUNT = 4000
RANDOM_SEED = 42

FULL_OUTPUT_FILE = os.path.join("data", "raw_play_myntra_full.csv")
SAMPLE_OUTPUT_FILE = os.path.join("data", "raw_play_myntra.csv")

def collect_reviews():
    print(f"Starting Google Play Store review collection for '{PACKAGE_ID}'...", flush=True)
    print(f"Target: {FULL_TARGET_COUNT} valid reviews (lang='en', country='in', sort=NEWEST)", flush=True)

    collected_rows = []
    seen_texts = set()
    continuation_token = None
    batch_size = 200

    os.makedirs("data", exist_ok=True)

    try:
        while len(collected_rows) < FULL_TARGET_COUNT:
            count_to_fetch = min(batch_size, FULL_TARGET_COUNT - len(collected_rows) + 500)

            result, continuation_token = reviews(
                PACKAGE_ID,
                lang="en",
                country="in",
                sort=Sort.NEWEST,
                count=count_to_fetch,
                continuation_token=continuation_token
            )

            if not result:
                print("No more results returned from Google Play Store.", flush=True)
                break

            prev_progress_milestone = len(collected_rows) // 500

            for rev in result:
                raw_text = rev.get("content") or ""
                text_clean = raw_text.strip()

                # Filter rule 1: Drop rows where text is under 15 characters
                if len(text_clean) < 15:
                    continue

                # Filter rule 2: Drop exact duplicate text
                if text_clean in seen_texts:
                    continue

                seen_texts.add(text_clean)

                # Format review date to ISO YYYY-MM-DD
                rev_date = rev.get("at")
                if rev_date:
                    date_str = rev_date.strftime("%Y-%m-%d")
                else:
                    date_str = ""

                # Construct review URL
                review_id = rev.get("reviewId") or ""
                url = f"https://play.google.com/store/apps/details?id={PACKAGE_ID}&reviewId={review_id}"

                collected_rows.append({
                    "source": "play_store",
                    "date": date_str,
                    "platform_mentioned": "myntra",
                    "text": raw_text,
                    "url": url
                })

                current_progress_milestone = len(collected_rows) // 500
                if current_progress_milestone > prev_progress_milestone:
                    print(f"Progress: {current_progress_milestone * 500} / {FULL_TARGET_COUNT} rows collected...", flush=True)
                    prev_progress_milestone = current_progress_milestone

                if len(collected_rows) >= FULL_TARGET_COUNT:
                    break

            if not continuation_token:
                print("No continuation token returned; stopping pagination.", flush=True)
                break

    except Exception as e:
        print(f"Error occurred while fetching reviews: {str(e)}", file=sys.stderr, flush=True)
        raise e

    if not collected_rows:
        print("Error: No reviews collected.", file=sys.stderr, flush=True)
        sys.exit(1)

    # Prepare full DataFrame
    df_full = pd.DataFrame(collected_rows)
    df_full["doc_id"] = [f"play_myntra_{i+1:04d}" for i in range(len(df_full))]
    df_full = df_full[["doc_id", "source", "date", "platform_mentioned", "text", "url"]]

    # Save full dataset
    df_full.to_csv(FULL_OUTPUT_FILE, index=False, encoding="utf-8")

    # Sample 4000 reproducibly with fixed seed
    sample_size = min(SAMPLE_TARGET_COUNT, len(df_full))
    df_sample = df_full.sample(n=sample_size, random_state=RANDOM_SEED).copy()
    df_sample["doc_id"] = [f"play_myntra_{i+1:04d}" for i in range(len(df_sample))]
    df_sample = df_sample[["doc_id", "source", "date", "platform_mentioned", "text", "url"]]

    # Save sampled dataset
    df_sample.to_csv(SAMPLE_OUTPUT_FILE, index=False, encoding="utf-8")

    # Summary statistics
    total_pulled = len(df_full)
    
    dates_full = [d for d in df_full["date"].dropna() if d]
    earliest_full = min(dates_full) if dates_full else "N/A"
    latest_full = max(dates_full) if dates_full else "N/A"

    dates_sample = [d for d in df_sample["date"].dropna() if d]
    earliest_sample = min(dates_sample) if dates_sample else "N/A"
    latest_sample = max(dates_sample) if dates_sample else "N/A"

    print("\n--- Collection Summary ---", flush=True)
    print(f"Total pulled: {total_pulled}", flush=True)
    print(f"Date range of full set: {earliest_full} to {latest_full}", flush=True)
    print(f"Date range of sample: {earliest_sample} to {latest_sample}", flush=True)
    print(f"Full dataset saved: {len(df_full)} rows -> {FULL_OUTPUT_FILE}", flush=True)
    print(f"Sampled dataset saved: {len(df_sample)} rows -> {SAMPLE_OUTPUT_FILE}", flush=True)

if __name__ == "__main__":
    collect_reviews()
