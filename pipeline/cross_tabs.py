import os
import pandas as pd
import numpy as np

INPUT_FILE = os.path.join("data", "labelled_v3.csv")
CROSS_TABS_FILE = os.path.join("data", "cross_tabs.csv")
GAP_TABLE_FILE = os.path.join("data", "gap_table.csv")

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

GROUP_VARIABLES = [
    "video_context",
    "platform_mentioned",
    "intent_code",
    "role",
    "information_sought",
    "external_workaround"
]

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.")
        return

    # Load dataframe
    df = pd.read_csv(INPUT_FILE)
    
    # 1. Filter: EXCLUDED corpus only (drop video_context == 'anti_consumption')
    # Use case-insensitive check and stripping to be robust
    df_filtered = df[df["video_context"].astype(str).str.lower().str.strip() != "anti_consumption"]
    
    # 2. Keep only rows with non-null primary_blocker
    df_coded = df_filtered[df_filtered["primary_blocker"].notna()].copy()
    
    # Verify the denominator is 292
    n_denominator = len(df_coded)
    print("=" * 80)
    print("CROSS-TABULATIONS AND GAP ANALYSIS")
    print("=" * 80)
    print(f"Total rows in Excluded Corpus: {len(df_filtered)}")
    print(f"Coded rows (denominator):       {n_denominator}")
    print("=" * 80)
    
    # Calculate overall shares for blocker codes in the excluded corpus
    overall_shares = {}
    for code in BLOCKER_CODES:
        count_overall = (df_coded["primary_blocker"] == code).sum()
        overall_shares[code] = (count_overall / n_denominator * 100.0) if n_denominator > 0 else 0.0

    # We will accumulate tidy data for cross_tabs.csv
    crosstab_rows = []
    
    # We will accumulate data for gap_table.csv
    gap_rows = []

    for var in GROUP_VARIABLES:
        print(f"\nCROSS-TABULATION: primary_blocker vs {var}")
        print("-" * 80)
        
        # Drop rows where the grouping variable is NaN for this cross-tab print
        df_var = df_coded[df_coded[var].notna()]
        
        # Calculate counts
        ct_count = pd.crosstab(df_var[var], df_var["primary_blocker"])
        # Ensure all 15 blocker codes are columns
        for code in BLOCKER_CODES:
            if code not in ct_count.columns:
                ct_count[code] = 0
        ct_count = ct_count[BLOCKER_CODES] # Reorder columns
        
        # Calculate row percentages (row sums to 100%)
        ct_pct = pd.crosstab(df_var[var], df_var["primary_blocker"], normalize="index") * 100.0
        for code in BLOCKER_CODES:
            if code not in ct_pct.columns:
                ct_pct[code] = 0.0
        ct_pct = ct_pct[BLOCKER_CODES] # Reorder columns
        
        # Print counts
        print("COUNTS:")
        print(ct_count.to_string())
        print("\nROW PERCENTAGES (%):")
        print(ct_pct.round(2).to_string())
        print("-" * 80)
        
        # Accumulate in tidy format for the CSV
        for val in ct_count.index:
            row_total = ct_count.loc[val].sum()
            for code in BLOCKER_CODES:
                count_val = ct_count.loc[val, code]
                pct_val = ct_pct.loc[val, code]
                crosstab_rows.append({
                    "variable": var,
                    "group_value": val,
                    "code": code,
                    "count": count_val,
                    "row_percentage": pct_val
                })
                
            # Also calculate gaps if the group size is >= 15
            if row_total >= 15:
                for code in BLOCKER_CODES:
                    share_in_group = ct_pct.loc[val, code]
                    share_in_overall = overall_shares[code]
                    gap_pp = share_in_group - share_in_overall
                    gap_rows.append({
                        "group_variable": var,
                        "group_value": val,
                        "group_size": row_total,
                        "code": code,
                        "share_in_group": share_in_group,
                        "share_in_overall": share_in_overall,
                        "gap_pp": gap_pp
                    })
                    
    # Save the cross-tabs tidy data
    df_ct_out = pd.DataFrame(crosstab_rows)
    df_ct_out.to_csv(CROSS_TABS_FILE, index=False)
    print(f"\nSaved cross-tabulations tidy data to {CROSS_TABS_FILE}")
    
    # Process and save the gap table
    df_gap = pd.DataFrame(gap_rows)
    
    # Sort by absolute gap descending
    df_gap["abs_gap_pp"] = df_gap["gap_pp"].abs()
    df_gap_sorted = df_gap.sort_values(by="abs_gap_pp", ascending=False).drop(columns=["abs_gap_pp"])
    
    df_gap_sorted.to_csv(GAP_TABLE_FILE, index=False)
    print(f"Saved gap analysis to {GAP_TABLE_FILE}\n")
    
    # Print the top 20 gaps
    print("=" * 110)
    print("TOP 20 LARGEST GAPS (by absolute gap_pp descending, group size >= 15):")
    print("=" * 110)
    print(f"{'Group Variable':<20} | {'Group Value':<20} | {'Size':<6} | {'Code':<30} | {'Grp Share%':<10} | {'Ovr Share%':<10} | {'Gap (pp)':<9}")
    print("-" * 110)
    
    top_20 = df_gap_sorted.head(20)
    for _, row in top_20.iterrows():
        print(
            f"{row['group_variable']:<20} | "
            f"{str(row['group_value']):<20} | "
            f"{int(row['group_size']):<6} | "
            f"{row['code']:<30} | "
            f"{row['share_in_group']:<10.2f} | "
            f"{row['share_in_overall']:<10.2f} | "
            f"{row['gap_pp']:+9.2f}"
        )
    print("=" * 110)

if __name__ == "__main__":
    main()
