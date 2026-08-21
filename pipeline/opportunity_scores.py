import os
import pandas as pd

INPUT_FILE = os.path.join("data", "labelled_v3.csv")
OUTPUT_FILE = os.path.join("data", "opportunity_scores.csv")

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

GROUPED_CODES = ["BLOCK_ANTICIPATED_NONUSE", "BLOCK_WARDROBE_SATURATION"]

def compute_stats(df, codes, total_coded):
    results = {}
    for code in codes:
        if isinstance(code, list) or isinstance(code, tuple):
            df_c = df[df["primary_blocker"].isin(code)]
            code_name = " + ".join(code)
        else:
            df_c = df[df["primary_blocker"] == code]
            code_name = code
        
        count = len(df_c)
        share_pct = (count / total_coded * 100.0) if total_coded > 0 else 0.0
        
        # Severity calculation
        if count > 0:
            avg_severity = df_c["severity_1_5"].dropna().mean()
            if pd.isna(avg_severity):
                avg_severity = 0.0
        else:
            avg_severity = 0.0
            
        # Proximity weight calculation
        low_count = (df_c["conversion_proximity"].astype(str).str.lower().str.strip() == "low").sum()
        med_count = (df_c["conversion_proximity"].astype(str).str.lower().str.strip() == "medium").sum()
        high_count = (df_c["conversion_proximity"].astype(str).str.lower().str.strip() == "high").sum()
        
        total_prox = low_count + med_count + high_count
        if total_prox > 0:
            avg_proximity_weight = (0.5 * low_count + 1.0 * med_count + 1.5 * high_count) / total_prox
        else:
            avg_proximity_weight = 0.0
            
        opp_score = share_pct * avg_severity * avg_proximity_weight
        
        results[code_name] = {
            "count": count,
            "share": share_pct,
            "severity": avg_severity,
            "prox_weight": avg_proximity_weight,
            "opp_score": opp_score,
            "proximity_mix": (low_count, med_count, high_count)
        }
    return results

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.")
        return

    # Load dataframe
    df = pd.read_csv(INPUT_FILE)
    
    # Clean severity data
    df["severity_1_5"] = pd.to_numeric(df["severity_1_5"], errors="coerce")
    
    # Define excluded corpus
    df_excl = df[df["video_context"].astype(str).str.lower().str.strip() != "anti_consumption"]
    
    # Calculate totals
    total_rows_full = len(df)
    total_coded_full = df["primary_blocker"].notna().sum()
    
    total_rows_excl = len(df_excl)
    total_coded_excl = df_excl["primary_blocker"].notna().sum()
    
    print("=" * 80)
    print("OPPORTUNITY SCORE PIPELINE RUN")
    print("=" * 80)
    print(f"(a) Full Corpus:      {total_rows_full} total rows, {total_coded_full} coded rows (denominator)")
    print(f"(b) Excluded Corpus:  {total_rows_excl} total rows, {total_coded_excl} coded rows (denominator)")
    print("=" * 80)
    
    # Compute for both
    stats_full = compute_stats(df, BLOCKER_CODES, total_coded_full)
    stats_excl = compute_stats(df_excl, BLOCKER_CODES, total_coded_excl)
    
    # Build dataframe for output
    rows = []
    for code in BLOCKER_CODES:
        sf = stats_full[code]
        se = stats_excl[code]
        rows.append({
            "code": code,
            "count_full": sf["count"],
            "share_full": sf["share"],
            "severity_full": sf["severity"],
            "prox_weight_full": sf["prox_weight"],
            "opp_score_full": sf["opp_score"],
            "count_excl": se["count"],
            "share_excl": se["share"],
            "severity_excl": se["severity"],
            "prox_weight_excl": se["prox_weight"],
            "opp_score_excl": se["opp_score"],
        })
        
    df_results = pd.DataFrame(rows)
    
    # Compute ranks
    df_results["opp_rank_full"] = df_results["opp_score_full"].rank(ascending=False, method="min").astype(int)
    df_results["opp_rank_excl"] = df_results["opp_score_excl"].rank(ascending=False, method="min").astype(int)
    
    # Compute share change in percentage points
    df_results["share_change_pp"] = df_results["share_excl"] - df_results["share_full"]
    
    # Save CSV
    df_results.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved opportunity scores successfully to {OUTPUT_FILE}\n")
    
    # 1. Print full table sorted by opp_score_full descending
    df_sorted = df_results.sort_values(by="opp_score_full", ascending=False)
    
    print("FULL TABLE (Sorted by opp_score_full descending):")
    print(f"{'Code':<30} | {'Cnt (F)':<7} | {'Shr (F)%':<8} | {'Sev (F)':<7} | {'PrxW(F)':<7} | {'Opp (F)':<7} || {'Cnt (E)':<7} | {'Shr (E)%':<8} | {'Sev (E)':<7} | {'PrxW(E)':<7} | {'Opp (E)':<7} | {'Rk(F)':<5} | {'Rk(E)':<5} | {'Chg(pp)':<7}")
    print("-" * 155)
    for _, row in df_sorted.iterrows():
        print(
            f"{row['code']:<30} | "
            f"{int(row['count_full']):<7} | "
            f"{row['share_full']:<8.2f} | "
            f"{row['severity_full']:<7.2f} | "
            f"{row['prox_weight_full']:<7.2f} | "
            f"{row['opp_score_full']:<7.2f} || "
            f"{int(row['count_excl']):<7} | "
            f"{row['share_excl']:<8.2f} | "
            f"{row['severity_excl']:<7.2f} | "
            f"{row['prox_weight_excl']:<7.2f} | "
            f"{row['opp_score_excl']:<7.2f} | "
            f"{int(row['opp_rank_full']):<5} | "
            f"{int(row['opp_rank_excl']):<5} | "
            f"{row['share_change_pp']:<+7.2f}"
        )
    print("=" * 155)
    
    # 2. FLAG list of any code where abs(share_change_pp) > 5
    flags = df_results[df_results["share_change_pp"].abs() > 5.0]
    print("\nFLAGS (abs(share_change_pp) > 5 percentage points):")
    if len(flags) == 0:
        print("None")
    else:
        print(f"{'Code':<30} | {'Share Full %':<14} | {'Share Excl %':<14} | {'Change (pp)':<12}")
        print("-" * 75)
        for _, row in flags.iterrows():
            print(f"{row['code']:<30} | {row['share_full']:<14.2f} | {row['share_excl']:<14.2f} | {row['share_change_pp']:<+12.2f}")
    print("=" * 75)
    
    # 3. Top 3 codes by opp_score_full and by opp_score_excl side by side
    top_3_full = df_results.sort_values(by="opp_score_full", ascending=False).head(3)
    top_3_excl = df_results.sort_values(by="opp_score_excl", ascending=False).head(3)
    
    print("\nTOP 3 CODES COMPARISON (Side-by-side):")
    print(f"{'Rank':<5} | {'Top by opp_score_full':<32} | {'Score (F)':<9} || {'Top by opp_score_excl':<32} | {'Score (E)':<9}")
    print("-" * 95)
    for r in range(3):
        row_f = top_3_full.iloc[r]
        row_e = top_3_excl.iloc[r]
        print(
            f"{r+1:<5} | "
            f"{row_f['code']:<32} | "
            f"{row_f['opp_score_full']:<9.2f} || "
            f"{row_e['code']:<32} | "
            f"{row_e['opp_score_excl']:<9.2f}"
        )
    print("=" * 95)
    
    # 4. Grouped calculation for BLOCK_ANTICIPATED_NONUSE + BLOCK_WARDROBE_SATURATION
    group_stats_full = compute_stats(df, [GROUPED_CODES], total_coded_full)
    group_stats_excl = compute_stats(df_excl, [GROUPED_CODES], total_coded_excl)
    
    gname = " + ".join(GROUPED_CODES)
    gf = group_stats_full[gname]
    ge = group_stats_excl[gname]
    g_chg = ge["share"] - gf["share"]
    
    print("\nGROUPED FIGURE (BLOCK_ANTICIPATED_NONUSE + BLOCK_WARDROBE_SATURATION):")
    print("-" * 120)
    print(f"Full Corpus:     Count = {gf['count']}, Share = {gf['share']:.2f}%, Avg Severity = {gf['severity']:.2f}, Proximity Wt = {gf['prox_weight']:.2f}, Opportunity Score = {gf['opp_score']:.2f}")
    print(f"Excluded Corpus: Count = {ge['count']}, Share = {ge['share']:.2f}%, Avg Severity = {ge['severity']:.2f}, Proximity Wt = {ge['prox_weight']:.2f}, Opportunity Score = {ge['opp_score']:.2f}")
    print(f"Share Change:    {g_chg:+.2f} pp")
    print("=" * 120)
    print("\n")
    
    # Run the sensitivity analysis check
    run_sensitivity_check(df_excl, total_coded_excl)

def run_sensitivity_check(df_excl, total_coded_excl):
    # Four schemes:
    # A: low=0.5, med=1.0, high=1.5  (baseline)
    # B: low=1.0, med=1.0, high=1.0  (proximity ignored)
    # C: low=0.25, med=1.0, high=2.0 (proximity weighted heavily)
    # D: share only (severity and proximity both ignored)
    
    results = []
    
    for code in BLOCKER_CODES:
        df_c = df_excl[df_excl["primary_blocker"] == code]
        count = len(df_c)
        share_pct = (count / total_coded_excl * 100.0) if total_coded_excl > 0 else 0.0
        
        # Severity
        if count > 0:
            avg_severity = df_c["severity_1_5"].dropna().mean()
            if pd.isna(avg_severity):
                avg_severity = 0.0
        else:
            avg_severity = 0.0
            
        # Proximity low/med/high counts
        low_count = (df_c["conversion_proximity"].astype(str).str.lower().str.strip() == "low").sum()
        med_count = (df_c["conversion_proximity"].astype(str).str.lower().str.strip() == "medium").sum()
        high_count = (df_c["conversion_proximity"].astype(str).str.lower().str.strip() == "high").sum()
        total_prox = low_count + med_count + high_count
        
        # Scheme A: baseline (0.5, 1.0, 1.5)
        if total_prox > 0:
            prox_wt_A = (0.5 * low_count + 1.0 * med_count + 1.5 * high_count) / total_prox
        else:
            prox_wt_A = 0.0
        score_A = share_pct * avg_severity * prox_wt_A
        
        # Scheme B: proximity ignored (1.0, 1.0, 1.0)
        if total_prox > 0:
            prox_wt_B = (1.0 * low_count + 1.0 * med_count + 1.0 * high_count) / total_prox
        else:
            prox_wt_B = 0.0
        score_B = share_pct * avg_severity * prox_wt_B
        
        # Scheme C: proximity heavily weighted (0.25, 1.0, 2.0)
        if total_prox > 0:
            prox_wt_C = (0.25 * low_count + 1.0 * med_count + 2.0 * high_count) / total_prox
        else:
            prox_wt_C = 0.0
        score_C = share_pct * avg_severity * prox_wt_C
        
        # Scheme D: share only (severity and proximity both ignored)
        score_D = share_pct
        
        results.append({
            "code": code,
            "score_A": score_A,
            "score_B": score_B,
            "score_C": score_C,
            "score_D": score_D,
        })
        
    df_sens = pd.DataFrame(results)
    
    # Compute Ranks (Standard descending order, min rank)
    df_sens["rank_A"] = df_sens["score_A"].rank(ascending=False, method="min").astype(int)
    df_sens["rank_B"] = df_sens["score_B"].rank(ascending=False, method="min").astype(int)
    df_sens["rank_C"] = df_sens["score_C"].rank(ascending=False, method="min").astype(int)
    df_sens["rank_D"] = df_sens["score_D"].rank(ascending=False, method="min").astype(int)
    
    # Save to data/sensitivity_check.csv
    sens_output_file = os.path.join("data", "sensitivity_check.csv")
    df_sens.to_csv(sens_output_file, index=False)
    print(f"Saved sensitivity check successfully to {sens_output_file}\n")
    
    # Print Top 5 for each scheme
    print("=" * 80)
    print("SENSITIVITY ANALYSIS: TOP 5 CODES BY SCHEME")
    print("=" * 80)
    
    schemes = [
        ("A", "Baseline (low=0.5, med=1.0, high=1.5)", "score_A", "rank_A"),
        ("B", "Proximity Ignored (low=1.0, med=1.0, high=1.0)", "score_B", "rank_B"),
        ("C", "Proximity Weighted Heavily (low=0.25, med=1.0, high=2.0)", "score_C", "rank_C"),
        ("D", "Share Only (Severity & Proximity Ignored)", "score_D", "rank_D")
    ]
    
    for letter, desc, score_col, rank_col in schemes:
        print(f"\nScheme {letter}: {desc}")
        print(f"{'Rank':<5} | {'Code':<30} | {'Score':<10}")
        print("-" * 50)
        df_sorted = df_sens.sort_values(by=score_col, ascending=False).head(5)
        for idx, row in df_sorted.iterrows():
            print(f"{int(row[rank_col]):<5} | {row['code']:<30} | {row[score_col]:<10.2f}")
            
    # Find codes in top 3 under ALL four schemes
    top_3_A = set(df_sens[df_sens["rank_A"] <= 3]["code"])
    top_3_B = set(df_sens[df_sens["rank_B"] <= 3]["code"])
    top_3_C = set(df_sens[df_sens["rank_C"] <= 3]["code"])
    top_3_D = set(df_sens[df_sens["rank_D"] <= 3]["code"])
    
    all_four = top_3_A.intersection(top_3_B).intersection(top_3_C).intersection(top_3_D)
    
    print("\n" + "=" * 80)
    print("CODES APPEARING IN THE TOP 3 UNDER ALL FOUR SCHEMES:")
    print("=" * 80)
    if len(all_four) == 0:
        print("None")
    else:
        for code in sorted(all_four):
            print(f"- {code}")
    print("=" * 80)

if __name__ == "__main__":
    main()

