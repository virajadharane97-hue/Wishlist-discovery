import os
import sys
import pandas as pd
from google_play_scraper import Sort, reviews

PACKAGE_ID = "com.ril.ajio"
TARGET_COUNT = 500
OUTPUT_FILE = os.path.join("data", "raw_play_ajio.csv")

def collect_reviews():
    print(f"Starting Google Play Store review collection for AJIO ('{PACKAGE_ID}')...", flush=True)
    print(f"Target: {TARGET_COUNT} valid reviews (lang='en', country='in', sort=NEWEST)", flush=True)

    collected_rows = []
    seen_texts = set()
    continuation_token = None
    batch_size = 200

    os.makedirs("data", exist_ok=True)

    try:
        while len(collected_rows) < TARGET_COUNT:
            count_to_fetch = min(batch_size, TARGET_COUNT - len(collected_rows) + 200)

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

            prev_progress_milestone = len(collected_rows) // 100

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
                    "platform_mentioned": "ajio",
                    "text": raw_text,
                    "url": url
                })

                current_progress_milestone = len(collected_rows) // 100
                if current_progress_milestone > prev_progress_milestone:
                    print(f"Progress: {current_progress_milestone * 100} / {TARGET_COUNT} rows collected...", flush=True)
                    prev_progress_milestone = current_progress_milestone

                if len(collected_rows) >= TARGET_COUNT:
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

    df = pd.DataFrame(collected_rows)
    df["doc_id"] = [f"play_ajio_{i+1:04d}" for i in range(len(df))]
    df = df[["doc_id", "source", "date", "platform_mentioned", "text", "url"]]

    # Save to CSV UTF-8
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    total_rows = len(df)
    dates = [d for d in df["date"].dropna() if d]
    earliest_date = min(dates) if dates else "N/A"
    latest_date = max(dates) if dates else "N/A"

    print("\n--- Collection Summary ---", flush=True)
    print(f"Total rows saved: {total_rows}", flush=True)
    print(f"Date range: {earliest_date} to {latest_date}", flush=True)
    print(f"File saved to: {OUTPUT_FILE}", flush=True)

if __name__ == "__main__":
    collect_reviews()
