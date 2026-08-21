import os
import sys
import pandas as pd

# Reconfigure stdout to use UTF-8 encoding on Windows to prevent UnicodeEncodeError
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

INPUT_FILE = os.path.join("data", "labelled_v3.csv")
OUTPUT_FILE = os.path.join("data", "evidence.csv")

TARGET_CODES = [
    "BLOCK_SIZE_SELECTION",
    "BLOCK_LISTING_INCOMPLETE",
    "BLOCK_FABRIC_QUALITY",
    "BLOCK_STYLING",
    "BLOCK_DURABILITY_VALUE",
    "BLOCK_BODY_PROJECTION"
]

def get_word_count(quote):
    if pd.isna(quote):
        return 0
    return len(str(quote).strip().split())

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.")
        return

    # Load dataframe
    df = pd.read_csv(INPUT_FILE)
    
    # 1. Filter: EXCLUDED corpus only (drop video_context == 'anti_consumption')
    df_filtered = df[df["video_context"].astype(str).str.lower().str.strip() != "anti_consumption"].copy()
    
    # 2. Filter: quote_valid == True
    df_filtered["quote_valid_bool"] = df_filtered["quote_valid"].astype(str).str.lower().str.strip().isin(["true", "1", "yes"])
    df_valid_quotes = df_filtered[df_filtered["quote_valid_bool"]].copy()
    
    # Ensure severity is numeric
    df_valid_quotes["severity_1_5"] = pd.to_numeric(df_valid_quotes["severity_1_5"], errors="coerce")
    
    # Calculate word count of evidence_quote
    df_valid_quotes["quote_word_count"] = df_valid_quotes["evidence_quote"].apply(get_word_count)
    
    # Exclude rows where evidence_quote is under 4 words
    df_valid_quotes = df_valid_quotes[df_valid_quotes["quote_word_count"] >= 4].copy()
    
    evidence_rows = []
    
    print("=" * 120)
    print("REGENERATING EVIDENCE QUOTES FOR KEY BLOCKERS (8 rows per code, word count >= 4)")
    print("=" * 120)
    
    for code in TARGET_CODES:
        df_code = df_valid_quotes[df_valid_quotes["primary_blocker"] == code].copy()
        
        # Sort by severity descending, then quote word count descending
        df_code_sorted = df_code.sort_values(by=["severity_1_5", "quote_word_count"], ascending=[False, False])
        
        # Get top 8
        top_8 = df_code_sorted.head(8)
        
        print(f"\nBlocker Code: {code} (Matches found: {len(df_code_sorted)}, Selected: {len(top_8)})")
        print("-" * 120)
        
        for _, row in top_8.iterrows():
            evidence_rows.append({
                "code": code,
                "doc_id": row["doc_id"],
                "source": row["source"],
                "evidence_quote": row["evidence_quote"],
                "severity_1_5": row["severity_1_5"],
                "information_sought": row["information_sought"],
                "external_workaround": row["external_workaround"],
                "url": row["url"],
                "text": row["text"]
            })
            
            # Print quote details for reading
            quote_text = str(row["evidence_quote"]).replace("\n", " ").strip()
            full_text = str(row["text"]).replace("\n", " ").strip()
            print(f"[{row['doc_id']}] Severity: {row['severity_1_5']} | Words: {row['quote_word_count']} | Workaround: {row['external_workaround']}")
            print(f"Quote:     \"{quote_text}\"")
            print(f"Full Text: \"{full_text}\"")
            print(f"URL:       {row['url']}")
            print("-" * 60)
            
    # Save to CSV
    df_evidence = pd.DataFrame(evidence_rows)
    df_evidence.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved evidence quotes successfully to {OUTPUT_FILE} (Total rows: {len(df_evidence)})")
    print("=" * 120)

if __name__ == "__main__":
    main()
