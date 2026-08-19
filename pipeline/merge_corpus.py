import os
import sys
import pandas as pd

REQUIRED_COLUMNS = ["doc_id", "source", "date", "platform_mentioned", "text", "url"]

FILES_TO_MERGE = [
    os.path.join("data", "raw_play_myntra.csv"),
    os.path.join("data", "raw_play_ajio.csv"),
    os.path.join("data", "raw_youtube.csv"),
    os.path.join("data", "manual_collected.csv"),
]

OUTPUT_FILE = os.path.join("data", "raw_all.csv")

def normalize_date(val):
    if pd.isna(val) or not str(val).strip():
        return ""
    val_str = str(val).strip()
    try:
        return pd.to_datetime(val_str, format="%d-%b-%y").strftime("%Y-%m-%d")
    except Exception:
        pass
    try:
        return pd.to_datetime(val_str).strftime("%Y-%m-%d")
    except Exception:
        return val_str[:10]

def load_and_prep_file(file_path):
    if not os.path.exists(file_path):
        print(f"[WARNING] File '{file_path}' does not exist. Skipping...", flush=True)
        return None

    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except Exception as e:
        print(f"[WARNING] Error reading '{file_path}': {e}. Skipping...", flush=True)
        return None

    # Handle common schema mismatches gracefully (e.g. manual_collected.csv)
    if "doc id" in df.columns:
        df.rename(columns={"doc id": "doc_id"}, inplace=True)
    if "platform" in df.columns:
        df.rename(columns={"platform": "platform_mentioned"}, inplace=True)

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        print(f"[WARNING] File '{file_path}' missing columns {missing_cols}. Skipping...", flush=True)
        return None

    # Standardize data formats
    df["date"] = df["date"].apply(normalize_date)
    df["platform_mentioned"] = df["platform_mentioned"].astype(str).str.strip().str.lower()
    df["text"] = df["text"].astype(str)
    df["url"] = df["url"].astype(str)

    return df[REQUIRED_COLUMNS]

def merge_corpus():
    print("Starting corpus merge process...", flush=True)

    loaded_dfs = []
    for filepath in FILES_TO_MERGE:
        df = load_and_prep_file(filepath)
        if df is not None and not df.empty:
            loaded_dfs.append(df)

    if not loaded_dfs:
        print("Error: No data files loaded.", file=sys.stderr, flush=True)
        sys.exit(1)

    merged_df = pd.concat(loaded_dfs, ignore_index=True)
    total_before = len(merged_df)

    # Calculate initial stats per source
    sources_before = merged_df["source"].value_counts().to_dict()

    # Count empty URLs before filtering
    empty_url_count_before = (merged_df["url"].isna() | (merged_df["url"].str.strip() == "") | (merged_df["url"] == "nan")).sum()

    # Step 2: Drop rows with empty text or empty url
    merged_df = merged_df[~merged_df["text"].isna() & (merged_df["text"].str.strip() != "") & (merged_df["text"] != "nan")]
    merged_df = merged_df[~merged_df["url"].isna() & (merged_df["url"].str.strip() != "") & (merged_df["url"] != "nan")]

    # Step 3: Drop rows where text is under 15 characters
    merged_df["text_clean"] = merged_df["text"].str.strip()
    merged_df = merged_df[merged_df["text_clean"].str.len() >= 15]

    # Step 4: Drop exact duplicate text across the whole merged set (keeping first occurrence)
    total_before_dedup = len(merged_df)
    merged_df = merged_df.drop_duplicates(subset=["text_clean"], keep="first")
    merged_df.drop(columns=["text_clean"], inplace=True)
    total_after = len(merged_df)
    duplicates_removed = total_before_dedup - total_after

    # Save to data/raw_all.csv
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    merged_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    # Post-filter stats per source
    sources_after = merged_df["source"].value_counts().to_dict()
    empty_url_count_after = (merged_df["url"].isna() | (merged_df["url"].str.strip() == "") | (merged_df["url"] == "nan")).sum()

    # Calculate date range per source
    date_ranges = {}
    all_sources = sorted(list(set(list(sources_before.keys()) + list(sources_after.keys()))))
    for src in all_sources:
        src_dates = merged_df[merged_df["source"] == src]["date"].dropna().tolist()
        src_dates = [d for d in src_dates if d]
        if src_dates:
            date_ranges[src] = f"{min(src_dates)} to {max(src_dates)}"
        else:
            date_ranges[src] = "N/A"

    all_dates = [d for d in merged_df["date"].dropna().tolist() if d]
    overall_date_range = f"{min(all_dates)} to {max(all_dates)}" if all_dates else "N/A"

    print("\n==========================================================================", flush=True)
    print("                      MERGED CORPUS SUMMARY TABLE                         ", flush=True)
    print("==========================================================================", flush=True)
    print(f"{'Source':<15} | {'Rows Before':<12} | {'Rows After':<12} | {'Date Range':<25}", flush=True)
    print("-" * 74, flush=True)

    for src in all_sources:
        before_cnt = sources_before.get(src, 0)
        after_cnt = sources_after.get(src, 0)
        d_range = date_ranges.get(src, "N/A")
        print(f"{src:<15} | {before_cnt:<12} | {after_cnt:<12} | {d_range:<25}", flush=True)

    print("-" * 74, flush=True)
    print(f"Total Rows Before Filter/Dedup: {total_before}", flush=True)
    print(f"Total Rows After Filter/Dedup:  {total_after}", flush=True)
    print(f"Duplicates Removed:             {duplicates_removed}", flush=True)
    print(f"Overall Date Range:             {overall_date_range}", flush=True)
    print(f"Rows with Empty URL (Final):    {empty_url_count_after}", flush=True)
    print(f"Output Saved To:                {OUTPUT_FILE}", flush=True)
    print("==========================================================================", flush=True)

if __name__ == "__main__":
    merge_corpus()
