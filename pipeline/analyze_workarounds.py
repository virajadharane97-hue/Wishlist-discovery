import os
import pandas as pd

INPUT_FILE = os.path.join("data", "labelled_v3.csv")

def print_dist(subset, col_name, title):
    print("=" * 80)
    print(f"{title} (Total rows: {len(subset)})")
    print("=" * 80)
    counts = subset[col_name].value_counts(dropna=False)
    pcts = subset[col_name].value_counts(dropna=False, normalize=True) * 100.0
    print(f"{'Category':<25} | {'Count':<7} | {'Percentage':<10}")
    print("-" * 50)
    for idx in counts.index:
        name = str(idx) if pd.notna(idx) else "NaN"
        print(f"{name:<25} | {counts[idx]:<7} | {pcts[idx]:<8.2f}%")
    print("=" * 80 + "\n")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.")
        return

    # Load dataframe
    df = pd.read_csv(INPUT_FILE)
    
    # Excluded corpus only (drop video_context == 'anti_consumption')
    df_ex = df[df["video_context"].astype(str).str.lower().str.strip() != "anti_consumption"].copy()
    
    # Coded rows only (non-null primary_blocker)
    df_coded = df_ex[df_ex["primary_blocker"].notna()].copy()
    
    print("ANALYSIS OF WORKAROUND BEHAVIOR & ROLE (EXCLUDED CORPUS)")
    print("=" * 80)
    print(f"Total rows in Excluded Corpus:       {len(df_ex)}")
    print(f"Coded rows (non-null blocker):      {len(df_coded)}")
    print("=" * 80 + "\n")
    
    print("VERSION A: USING ALL ROWS IN EXCLUDED CORPUS")
    print("*" * 80 + "\n")
    
    # 1. Distribution of external_workaround for intent_code = INTENT_GENUINE
    df_gen = df_ex[df_ex["intent_code"] == "INTENT_GENUINE"]
    print_dist(df_gen, "external_workaround", "1. external_workaround for intent_code = INTENT_GENUINE (All Rows)")
    
    # 2. Distribution of external_workaround for primary_blocker = BLOCK_SIZE_SELECTION
    df_size = df_ex[df_ex["primary_blocker"] == "BLOCK_SIZE_SELECTION"]
    print_dist(df_size, "external_workaround", "2. external_workaround for primary_blocker = BLOCK_SIZE_SELECTION")
    
    # 3. Distribution of role for intent_code = INTENT_GENUINE
    print_dist(df_gen, "role", "3. role for intent_code = INTENT_GENUINE (All Rows)")
    
    # 4. Distribution of role for primary_blocker = BLOCK_SIZE_SELECTION
    print_dist(df_size, "role", "4. role for primary_blocker = BLOCK_SIZE_SELECTION")
    
    print("\nVERSION B: RESTRICTING TO CODED ROWS (NON-NULL PRIMARY_BLOCKER)")
    print("*" * 80 + "\n")
    
    # 1. Distribution of external_workaround for intent_code = INTENT_GENUINE (Coded)
    df_gen_coded = df_coded[df_coded["intent_code"] == "INTENT_GENUINE"]
    print_dist(df_gen_coded, "external_workaround", "1. external_workaround for intent_code = INTENT_GENUINE (Coded Rows)")
    
    # 2. Distribution of external_workaround for primary_blocker = BLOCK_SIZE_SELECTION
    # (This is identical to Version A since primary_blocker is already non-null)
    print_dist(df_size, "external_workaround", "2. external_workaround for primary_blocker = BLOCK_SIZE_SELECTION (Coded Rows)")
    
    # 3. Distribution of role for intent_code = INTENT_GENUINE (Coded)
    print_dist(df_gen_coded, "role", "3. role for intent_code = INTENT_GENUINE (Coded Rows)")
    
    # 4. Distribution of role for primary_blocker = BLOCK_SIZE_SELECTION
    # (This is identical to Version A since primary_blocker is already non-null)
    print_dist(df_size, "role", "4. role for primary_blocker = BLOCK_SIZE_SELECTION (Coded Rows)")

if __name__ == "__main__":
    main()
