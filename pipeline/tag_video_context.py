import os
import re
import pandas as pd

INPUT_FILE = os.path.join("data", "clean_v5.csv")
OUTPUT_FILE = os.path.join("data", "clean_v5_tagged.csv")

# Exact mapping of all 81 unique YouTube video IDs based on their titles
VIDEO_ID_TO_CONTEXT = {
    "-hO-t485nfI": "haul",
    "0Uj56N1FSNo": "anti_consumption",
    "1XD6msqkAUE": "haul",
    "1dgDXkc-lJ8": "other",
    "3APr9AasKIo": "haul",
    "3MDvskB5kew": "haul",
    "50tb2Dotblg": "haul",
    "58--Bxvxb04": "review_comparison",
    "5drKjsPBSLw": "review_comparison",
    "6bs9mv_TIu0": "other",
    "898YWhYDgz4": "other",
    "8hc1pWyD3-g": "size_guide",
    "9nP1eB-_fag": "haul",
    "A6SkEwdjj-8": "review_comparison",
    "E5QJlY9mrxk": "haul",
    "EXnXKhbI4po": "size_guide",
    "Emgn45RApdg": "other",
    "GAAuBX-kOTs": "review_comparison",
    "H3-IvqIjOQs": "review_comparison",
    "H47dQGCvYIk": "haul",
    "HBl_aD-JybI": "haul",
    "HY4jpLXnPUI": "haul",
    "KgGRpd4e-QE": "size_guide",
    "Li81sECrxH0": "size_guide",
    "LpZ06OxW8zw": "other",
    "NMooudFC_nU": "other",
    "NiTfE33-aqQ": "anti_consumption",
    "Nq7qWS0HMyU": "review_comparison",
    "OJlZMOQ9xDk": "anti_consumption",
    "OLWR3Phod0I": "haul",
    "OjM7ne7bezw": "review_comparison",
    "PyRj1hpSXPU": "anti_consumption",
    "Qi_FiM01k3M": "other",
    "RCWeXpdVbeg": "haul",
    "RJJ9l-jLAP8": "haul",
    "RR3QkyD6vS0": "review_comparison",
    "Rbh6Hwlc-So": "haul",
    "UAGE51XUIZg": "review_comparison",
    "Uov6KYO9LPM": "haul",
    "UsTnCO1GrTE": "size_guide",
    "WNGiJs-7Oho": "haul",
    "X3ZEA5ms4qY": "other",
    "XqtVXwHLHvk": "review_comparison",
    "ZEHN6-16d2g": "haul",
    "ZYumjOBhCyA": "other",
    "ZZ25NB-RUdc": "haul",
    "ZjGLr06oU78": "other",
    "Zk0m-U8M4BE": "anti_consumption",
    "ZsuZD4iV4P8": "haul",
    "__737DvZz84": "haul",
    "_uO4qkwmLEU": "other",
    "aLLo5wgXGDc": "anti_consumption",
    "b0FArfw23TU": "haul",
    "bseWza-g9pk": "haul",
    "e-RveOO7mb4": "haul",
    "eXTFjVihjDs": "other",
    "fJp_bpVPuuM": "haul",
    "gd1yPGZgTVA": "haul",
    "hcIqXU6z7h0": "other",
    "htXcUheMxrc": "size_guide",
    "iNy7dZqfzpA": "haul",
    "iabxMFFAt7s": "haul",
    "jxGZnRRyoo8": "review_comparison",
    "k65aOaQItm0": "other",
    "kGvgwTy7K1Y": "haul",
    "kgiewPUxidI": "other",
    "mEo4RxEMitA": "haul",
    "mP33KDhaOWc": "haul",
    "mQtsNLZrc6g": "other",
    "mfDyzuuB7hU": "review_comparison",
    "nYHLXPiNUA8": "haul",
    "okHjO6cXtQI": "review_comparison",
    "p0z6dwVFqwY": "haul",
    "q8VPbXAyld0": "haul",
    "qii3btD9IHs": "other",
    "sdQ0OB75Vvw": "anti_consumption",
    "vy5HNpbnq84": "haul",
    "w8YdtCREa5M": "other",
    "xt9XKzYlIjM": "haul",
    "you6IxDeFRs": "anti_consumption",
    "zR_J12Z3Kxo": "haul"
}

def extract_video_id(url):
    if pd.isna(url):
        return None
    match = re.search(r"v=([a-zA-Z0-9_-]+)", str(url))
    if match:
        return match.group(1)
    return None

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.")
        return

    print(f"Loading {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE, encoding="utf-8")
    
    # Initialize column with default for non-youtube rows
    df["video_context"] = "not_applicable"
    
    # Process YouTube rows
    yt_mask = df["source"] == "youtube"
    
    unmapped_ids = set()
    mapped_count = 0
    
    for idx in df[yt_mask].index:
        url = df.loc[idx, "url"]
        v_id = extract_video_id(url)
        if v_id:
            context = VIDEO_ID_TO_CONTEXT.get(v_id)
            if context:
                df.loc[idx, "video_context"] = context
                mapped_count += 1
            else:
                df.loc[idx, "video_context"] = "other"
                unmapped_ids.add(v_id)
        else:
            df.loc[idx, "video_context"] = "other"
            
    print(f"Mapped {mapped_count} YouTube rows.")
    if unmapped_ids:
        print(f"Warning: Found {len(unmapped_ids)} unmapped video IDs (defaulted to 'other'): {unmapped_ids}")

    # Print the distribution of the categories
    print("\n--- Video Context Category Distribution ---")
    print(df["video_context"].value_counts())
    
    # Save the new tagged dataframe
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\nSaved successfully to {OUTPUT_FILE} (shape: {df.shape})")

if __name__ == "__main__":
    main()
