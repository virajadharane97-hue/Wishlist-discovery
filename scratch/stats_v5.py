import os
import pandas as pd

v5_path = "data/checkpoint_relevance_v5.csv"
if os.path.exists(v5_path):
    df = pd.read_csv(v5_path)
    completed = df[df["relevant"].notna()]
    total_completed = len(completed)
    
    # Recovered from rejected: v4 == NO and v5 == YES
    rec = ((completed["relevant_v4"] == "NO") & (completed["relevant"] == "YES")).sum()
    # Removed from clean: v4 == YES and v5 == NO
    rem = ((completed["relevant_v4"] == "YES") & (completed["relevant"] == "NO")).sum()
    net_change = rec - rem
    
    yes_count = (df["relevant"] == "YES").sum()
    no_count = (df["relevant"] == "NO").sum()
    
    print(f"Total Completed in V5:   {total_completed} / {len(df)}")
    print(f"Rows Recovered from Rejected: {rec}")
    print(f"Rows Removed from Clean:      {rem}")
    print(f"Net Change:                   {net_change:+d}")
    print(f"YES Count (Clean) so far:     {yes_count}")
    print(f"NO Count (Reject) so far:     {no_count}")
    
    print("\n--- Keep Rate per Source (completed only) ---")
    sources = sorted(completed["source"].dropna().unique().tolist())
    for src in sources:
        sub = completed[completed["source"] == src]
        s_total = len(sub)
        s_yes = (sub["relevant"] == "YES").sum()
        s_rate = (s_yes / s_total * 100) if s_total > 0 else 0.0
        print(f" • {src:<12}: {s_yes:>4} / {s_total:<4} ({s_rate:>6.2f}%)")
else:
    print("V5 checkpoint not found.")
