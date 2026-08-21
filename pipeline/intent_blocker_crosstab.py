import os
import pandas as pd

INPUT_FILE = os.path.join("data", "labelled_v3.csv")
OUTPUT_FILE = os.path.join("data", "intent_blocker.csv")

BLOCKER_CODES = [
    "BLOCK_SIZE_SELECTION",
    "BLOCK_CHART_UNRELIABLE",
    "BLOCK_BODY_PROJECTION",
    "BLOCK_LISTING_INCOMPLETE",
    "BLOCK_FABRIC_QUALITY",
    "BLOCK_DURABILITY_VALUE",
    "BLOCK_IMAGE_DISTRUST",
    "BLOCK_REVIEW_DISTRUST",
    "BLOCK_AUTHENTICITY",
    "BLOCK_ANTICIPATED_NONUSE",
    "BLOCK_WARDROBE_SATURATION",
    "BLOCK_STYLING",
    "BLOCK_CHOICE_COMPARISON",
    "BLOCK_SOCIAL_VALIDATION",
    "BLOCK_RETURN_FRICTION"
]

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.")
        return

    # Load dataframe
    df = pd.read_csv(INPUT_FILE)
    
    # 1. Filter: EXCLUDED corpus only (drop video_context == 'anti_consumption')
    df_filtered = df[df["video_context"].astype(str).str.lower().str.strip() != "anti_consumption"]
    
    # 2. Keep only rows with non-null primary_blocker
    df_coded = df_filtered[df_filtered["primary_blocker"].notna()].copy()
    
    # Get intent code counts to find those with n >= 10
    intent_counts = df_coded["intent_code"].value_counts(dropna=True)
    valid_intents = intent_counts[intent_counts >= 10].index.tolist()
    
    print("=" * 80)
    print("INTENT VS BLOCKER ANALYSIS")
    print("=" * 80)
    print(f"Intents with n >= 10 in Excluded Coded Corpus: {valid_intents}")
    print("=" * 80)
    
    # Proximity mapping
    prox_map = {"low": 0.5, "medium": 1.0, "high": 1.5}
    
    # Build the final table
    results = []
    
    for intent in valid_intents:
        df_intent = df_coded[df_coded["intent_code"] == intent]
        n_total = len(df_intent)
        
        # Severity
        df_intent["severity_1_5"] = pd.to_numeric(df_intent["severity_1_5"], errors="coerce")
        mean_severity = df_intent["severity_1_5"].dropna().mean()
        if pd.isna(mean_severity):
            mean_severity = 0.0
            
        # Proximity weight
        prox_series = df_intent["conversion_proximity"].astype(str).str.lower().str.strip().map(prox_map)
        mean_prox_weight = prox_series.dropna().mean()
        if pd.isna(mean_prox_weight):
            mean_prox_weight = 0.0
            
        # Workarounds (not null and not 'none')
        workaround_mask = df_intent["external_workaround"].notna() & (
            df_intent["external_workaround"].astype(str).str.lower().str.strip() != "none"
        )
        workaround_cnt = workaround_mask.sum()
        
        # Blocker code counts and shares
        row_data = {
            "intent_code": intent,
            "total_count": n_total,
            "mean_severity": mean_severity,
            "mean_prox_weight": mean_prox_weight,
            "workaround_count": workaround_cnt
        }
        
        for code in BLOCKER_CODES:
            cnt_code = (df_intent["primary_blocker"] == code).sum()
            share_code = (cnt_code / n_total * 100.0) if n_total > 0 else 0.0
            row_data[f"count_{code}"] = cnt_code
            row_data[f"share_{code}"] = share_code
            
        results.append(row_data)
        
    df_output = pd.DataFrame(results)
    
    # Reorder columns to have counts and shares clearly
    col_order = ["intent_code", "total_count", "mean_severity", "mean_prox_weight", "workaround_count"]
    for code in BLOCKER_CODES:
        col_order.append(f"count_{code}")
        col_order.append(f"share_{code}")
        
    df_output = df_output[col_order]
    
    # Save CSV
    df_output.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved intent-blocker analysis to {OUTPUT_FILE}\n")
    
    # Print focused output
    for intent in valid_intents:
        df_intent = df_coded[df_coded["intent_code"] == intent]
        n_total = len(df_intent)
        
        row_res = df_output[df_output["intent_code"] == intent].iloc[0]
        
        print(f"Intent Code: {intent} (n = {n_total})")
        print("-" * 80)
        print(f"Mean Severity:          {row_res['mean_severity']:.2f}")
        print(f"Mean Proximity Weight:  {row_res['mean_prox_weight']:.2f}")
        print(f"Workaround Count:       {row_res['workaround_count']} (out of {n_total})")
        print("\nAll Blocker Shares:")
        
        # Sort blocker codes by count descending for printing
        blocker_shares = []
        for code in BLOCKER_CODES:
            cnt = int(row_res[f"count_{code}"])
            sh = row_res[f"share_{code}"]
            blocker_shares.append((code, cnt, sh))
            
        # Sort descending by share/count
        blocker_shares_sorted = sorted(blocker_shares, key=lambda x: x[2], reverse=True)
        
        print(f"{'Blocker Code':<30} | {'Count':<7} | {'Share %':<8}")
        print("-" * 50)
        for code, cnt, sh in blocker_shares_sorted:
            if cnt > 0:
                print(f"{code:<30} | {cnt:<7} | {sh:<8.2f}")
                
        # Top 3 blockers
        print("\nTop 3 Blocker Codes:")
        for r in range(min(3, len(blocker_shares_sorted))):
            code, cnt, sh = blocker_shares_sorted[r]
            print(f"  {r+1}. {code} ({cnt} count, {sh:.2f}%)")
        print("=" * 80)

if __name__ == "__main__":
    main()
