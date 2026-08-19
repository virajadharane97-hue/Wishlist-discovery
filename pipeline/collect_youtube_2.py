import os
import sys
import re
import html
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SEARCH_TERMS = [
    "myntra fabric quality honest review",
    "myntra kurti quality review",
    "online clothes fabric disappointment india",
    "myntra vs ajio vs meesho comparison",
    "comparing online fashion sites india",
    "wedding shopping online india clothes",
    "festive outfit shopping online india",
    "diwali shopping haul online india",
    "online shopping clothes experience india",
    "why i stopped buying clothes online",
    "myntra shopping mistakes",
    "online shopping tips india clothes",
    "honest myntra review not sponsored",
    "online fashion shopping problems india",
    "myntra return exchange experience",
]

OUTPUT_FILE = os.path.join("data", "raw_youtube_2.csv")
EXISTING_YOUTUBE_FILE = os.path.join("data", "raw_youtube.csv")

def get_platform_mentioned(text):
    text_lower = text.lower()
    keywords = ["myntra", "ajio", "nykaa", "meesho"]
    matches = []
    for kw in keywords:
        pos = text_lower.find(kw)
        if pos != -1:
            matches.append((pos, kw))
    if not matches:
        return "none"
    matches.sort(key=lambda x: x[0])
    return matches[0][1]

def save_dataframe(rows, file_path):
    df = pd.DataFrame(rows)
    df["doc_id"] = [f"yt2_{i+1:04d}" for i in range(len(df))]
    df = df[["doc_id", "source", "date", "platform_mentioned", "text", "url"]]
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False, encoding="utf-8")
    return df

def collect_youtube_comments_v2():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in .env file.", file=sys.stderr, flush=True)
        sys.exit(1)

    # Load existing processed video IDs to avoid duplicates
    existing_video_ids = set()
    if os.path.exists(EXISTING_YOUTUBE_FILE):
        try:
            df_ex = pd.read_csv(EXISTING_YOUTUBE_FILE)
            if "url" in df_ex.columns:
                for url in df_ex["url"].dropna():
                    match = re.search(r"v=([a-zA-Z0-9_-]+)", str(url))
                    if match:
                        existing_video_ids.add(match.group(1))
            print(f"Loaded {len(existing_video_ids)} already processed video IDs from {EXISTING_YOUTUBE_FILE} for deduplication.", flush=True)
        except Exception as e:
            print(f"Warning: Could not read existing videos from {EXISTING_YOUTUBE_FILE}: {e}", flush=True)

    print("Initializing YouTube Data API v3 client...", flush=True)
    youtube = build("youtube", "v3", developerKey=api_key)

    unique_videos = []
    seen_video_ids = set()
    skipped_duplicates_count = 0

    print(f"Searching for videos across {len(SEARCH_TERMS)} terms (top 10 each, duration: medium 4-20m)...", flush=True)

    try:
        for term in SEARCH_TERMS:
            request = youtube.search().list(
                q=term,
                part="snippet",
                type="video",
                relevanceLanguage="en",
                regionCode="IN",
                videoDuration="medium",  # Filter to videos between 4 and 20 minutes
                maxResults=10
            )
            response = request.execute()

            for item in response.get("items", []):
                v_id = item["id"]["videoId"]
                v_title = html.unescape(item["snippet"]["title"])
                if v_id in existing_video_ids:
                    skipped_duplicates_count += 1
                    continue
                if v_id not in seen_video_ids:
                    seen_video_ids.add(v_id)
                    unique_videos.append({"id": v_id, "title": v_title, "term": term})
                else:
                    skipped_duplicates_count += 1

    except HttpError as e:
        if e.resp.status == 403 or "quotaExceeded" in str(e):
            print(f"\n[QUOTA EXCEEDED] YouTube API quota exceeded during video search: {e}", file=sys.stderr, flush=True)
        else:
            print(f"\n[API ERROR] YouTube API error during search: {e}", file=sys.stderr, flush=True)
        if not unique_videos:
            print("No videos discovered before error occurred.", file=sys.stderr, flush=True)
            sys.exit(1)

    print(f"Discovered {len(unique_videos)} unique videos to process. Skipped {skipped_duplicates_count} duplicate/processed videos.\n", flush=True)

    collected_rows = []
    seen_texts = set()
    video_breakdown = {}
    last_checkpoint_count = 0
    quota_exceeded = False

    for idx, v_info in enumerate(unique_videos, start=1):
        v_id = v_info["id"]
        v_title = v_info["title"]
        video_comments_before = len(collected_rows)

        print(f"[{idx}/{len(unique_videos)}] Scraping video: '{v_title}' (ID: {v_id})...", flush=True)

        top_threads_count = 0
        next_page_token = None

        try:
            while top_threads_count < 300:
                threads_request = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=v_id,
                    maxResults=min(100, 300 - top_threads_count),
                    textFormat="plainText",
                    pageToken=next_page_token
                )
                threads_response = threads_request.execute()

                items = threads_response.get("items", [])
                if not items:
                    break

                for item in items:
                    top_threads_count += 1

                    # Top level comment
                    top_comment_item = item["snippet"]["topLevelComment"]
                    c_id = top_comment_item["id"]
                    c_snippet = top_comment_item["snippet"]
                    raw_text = c_snippet.get("textDisplay") or c_snippet.get("textOriginal") or ""
                    clean_text = html.unescape(raw_text).strip()

                    pub_at = c_snippet.get("publishedAt") or ""
                    date_str = pub_at[:10] if pub_at else ""

                    # Only comments published on or after 2024-01-01
                    if date_str and date_str < "2024-01-01":
                        continue

                    # Drop comments under 40 characters and drop exact duplicates
                    if len(clean_text) >= 40 and clean_text not in seen_texts:
                        seen_texts.add(clean_text)
                        collected_rows.append({
                            "source": "youtube",
                            "date": date_str,
                            "platform_mentioned": get_platform_mentioned(clean_text),
                            "text": clean_text,
                            "url": f"https://www.youtube.com/watch?v={v_id}&lc={c_id}"
                        })

                    # Replies handling
                    total_replies = item["snippet"].get("totalReplyCount", 0)
                    embedded_replies = item.get("replies", {}).get("comments", [])
                    seen_reply_ids = set()

                    for r in embedded_replies:
                        r_id = r["id"]
                        seen_reply_ids.add(r_id)
                        r_snippet = r["snippet"]
                        r_raw_text = r_snippet.get("textDisplay") or r_snippet.get("textOriginal") or ""
                        r_clean_text = html.unescape(r_raw_text).strip()
                        r_pub_at = r_snippet.get("publishedAt") or ""
                        r_date_str = r_pub_at[:10] if r_pub_at else ""

                        if r_date_str and r_date_str < "2024-01-01":
                            continue

                        # Drop replies under 40 characters and drop duplicates
                        if len(r_clean_text) >= 40 and r_clean_text not in seen_texts:
                            seen_texts.add(r_clean_text)
                            collected_rows.append({
                                "source": "youtube",
                                "date": r_date_str,
                                "platform_mentioned": get_platform_mentioned(r_clean_text),
                                "text": r_clean_text,
                                "url": f"https://www.youtube.com/watch?v={v_id}&lc={r_id}"
                            })

                    # If more replies exist than embedded, fetch remaining via comments().list
                    if total_replies > len(embedded_replies):
                        try:
                            r_next_token = None
                            while True:
                                replies_req = youtube.comments().list(
                                    part="snippet",
                                    parentId=c_id,
                                    maxResults=100,
                                    textFormat="plainText",
                                    pageToken=r_next_token
                                )
                                replies_res = replies_req.execute()
                                r_items = replies_res.get("items", [])
                                for r in r_items:
                                    r_id = r["id"]
                                    if r_id in seen_reply_ids:
                                        continue
                                    seen_reply_ids.add(r_id)
                                    r_snippet = r["snippet"]
                                    r_raw_text = r_snippet.get("textDisplay") or r_snippet.get("textOriginal") or ""
                                    r_clean_text = html.unescape(r_raw_text).strip()
                                    r_pub_at = r_snippet.get("publishedAt") or ""
                                    r_date_str = r_pub_at[:10] if r_pub_at else ""

                                    if r_date_str and r_date_str < "2024-01-01":
                                        continue

                                    # Drop comments under 40 characters and drop duplicates
                                    if len(r_clean_text) >= 40 and r_clean_text not in seen_texts:
                                        seen_texts.add(r_clean_text)
                                        collected_rows.append({
                                            "source": "youtube",
                                            "date": r_date_str,
                                            "platform_mentioned": get_platform_mentioned(r_clean_text),
                                            "text": r_clean_text,
                                            "url": f"https://www.youtube.com/watch?v={v_id}&lc={r_id}"
                                        })

                                r_next_token = replies_res.get("nextPageToken")
                                if not r_next_token:
                                    break
                        except HttpError as reply_err:
                            if reply_err.resp.status == 403 or "quotaExceeded" in str(reply_err):
                                raise reply_err
                            pass

                    # Save checkpoint every 500 comments
                    if len(collected_rows) - last_checkpoint_count >= 500:
                        save_dataframe(collected_rows, OUTPUT_FILE)
                        last_checkpoint_count = len(collected_rows)
                        print(f"  [CHECKPOINT] Saved {len(collected_rows)} comments to {OUTPUT_FILE}", flush=True)

                    if top_threads_count >= 300:
                        break

                next_page_token = threads_response.get("nextPageToken")
                if not next_page_token:
                    break

        except HttpError as e:
            if e.resp.status == 403 or "quotaExceeded" in str(e):
                print(f"\n[QUOTA EXCEEDED] YouTube API quota limit reached: {e}", file=sys.stderr, flush=True)
                quota_exceeded = True
            else:
                print(f"\n[API ERROR] Error processing video {v_id}: {e}", file=sys.stderr, flush=True)

        video_added = len(collected_rows) - video_comments_before
        video_breakdown[f"{v_title} ({v_id})"] = video_added
        print(f"  -> Added {video_added} valid comments from this video. (Total so far: {len(collected_rows)})", flush=True)

        if quota_exceeded:
            print("Stopping video processing due to quota limit. Saving collected data...", flush=True)
            break

    if not collected_rows:
        print("Error: No comments collected.", file=sys.stderr, flush=True)
        sys.exit(1)

    # Save final DataFrame
    df_final = save_dataframe(collected_rows, OUTPUT_FILE)

    dates = [d for d in df_final["date"].dropna() if d]
    earliest_date = min(dates) if dates else "N/A"
    latest_date = max(dates) if dates else "N/A"

    print("\n==========================================", flush=True)
    print("      YOUTUBE V2 COLLECTION SUMMARY       ", flush=True)
    print("==========================================", flush=True)
    print(f"Total comments collected: {len(df_final)}", flush=True)
    print(f"Total videos processed:   {len(video_breakdown)}", flush=True)
    print(f"Videos skipped (dup/prev):{skipped_duplicates_count}", flush=True)
    print(f"Date range:               {earliest_date} to {latest_date}", flush=True)
    print(f"Output saved to:          {OUTPUT_FILE}", flush=True)

    print("\n--- Per-Video Breakdown ---", flush=True)
    for v_name, count in video_breakdown.items():
        print(f" • {v_name}: {count} comments", flush=True)

if __name__ == "__main__":
    collect_youtube_comments_v2()
