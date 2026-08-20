import os
import re
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build

def main():
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in .env")
        return

    df = pd.read_csv("data/clean_v5.csv")
    yt = df[df["source"] == "youtube"]
    video_ids = set()
    for url in yt["url"].dropna():
        match = re.search(r"v=([a-zA-Z0-9_-]+)", str(url))
        if match:
            video_ids.add(match.group(1))

    video_ids = sorted(list(video_ids))
    print(f"Fetching titles for {len(video_ids)} video IDs...")

    youtube = build("youtube", "v3", developerKey=api_key)
    
    # Batch request in chunks of 50
    video_details = {}
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        try:
            request = youtube.videos().list(
                part="snippet",
                id=",".join(chunk)
            )
            response = request.execute()
            for item in response.get("items", []):
                v_id = item["id"]
                title = item["snippet"]["title"]
                video_details[v_id] = title
        except Exception as e:
            print(f"Error fetching chunk {i}: {e}")

    with open("scratch/video_titles.txt", "w", encoding="utf-8") as f:
        for v_id in video_ids:
            title = video_details.get(v_id, "UNKNOWN")
            f.write(f"{v_id} | {title}\n")
    print("Titles written to scratch/video_titles.txt successfully!")

if __name__ == "__main__":
    main()
