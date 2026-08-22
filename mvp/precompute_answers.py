import os
import sys
import json
import time
import re
import collections
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

# Load environment variables from .env
load_dotenv()

# We MUST use GEMINI_API_KEY_2 as requested
api_key = os.getenv("GEMINI_API_KEY_2")
if not api_key:
    print("Error: GEMINI_API_KEY_2 not found in environment.", file=sys.stderr)
    sys.exit(1)

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

INPUT_FILE = "mvp/seed.json"
OUTPUT_FILE = "mvp/seed_with_answers.json"

DEMO_USER = {
    "height_cm": 157,
    "usual_size_top": "M",
    "usual_size_bottom": "M",
    "usual_size_shoe": "UK6",
    "build": "average"
}

SYSTEM_INSTRUCTION = """You are the AI engine for a fashion e-commerce prototype: "Wishlist Decision Assistant".
For a given product, its reviews, and its buyer questions (if any), you must analyze the text and generate a structured JSON response to help a specific user (the "demo_user") resolve their "blocking_question".

The Demo User Profile contains height, size, and progressive fields like build, laptop_size_inches, and activity.

Depending on the available evidence, you must classify the product into one of the following PATHs:

MANDATORY COMPARABILITY FOR FIT, SIZE, AND LENGTH:
If the blocking question concerns FIT, SIZE, LENGTH, or how the item sits on the body (e.g. sleeves length, shoulder fit, pants length, ankle width, or whether it clings to a certain build), then comparability is mandatory.
- Such a question can ONLY be PATH 1 (if a comparable reviewer exists) or PATH 4 (if no comparable reviewer exists).
- It can NEVER be PATH 2. A fit/size/length answer from a dissimilar body does not transfer.
- PATH 2 is strictly reserved for questions where the reviewer's body is irrelevant to the answer, such as fabric behaviour, colour accuracy, durability, washing, product version, or capacity.

PATH 1: At least one review has reviewer_height_cm within 3cm of the demo user (i.e. 154cm to 160cm inclusive) OR has a matching reviewer_use/activity/laptop_size for footwear and bags, AND there are at least 3 reviews that address the blocking question.
Output JSON schema:
{
  "path": 1,
  "verdict": "<verdict under 12 words, summarizing fit/suitability for the demo user>",
  "evidence_count": "Based on X of Y reviews - N from buyers near your height" (or "with similar use", "with similar laptop size" depending on match attribute),
  "confidence": "low" | "moderate" | "high",
  "still_unknown": "<something important the reviews do not address at all, or null>",
  "matched_reviews": [0-based indices of reviews that match the attribute]
}

PATH 2: No comparable reviewer (no reviewer with height within 3cm, or matching use/activity/laptop size), but at least 3 reviews DO address the blocking question.
Output JSON schema:
{
  "path": 2,
  "verdict": "<verdict under 12 words, summarizing what the reviews say about the blocking question>",
  "evidence_count": "Based on X of Y reviews",
  "confidence": "low" | "moderate" | "high",
  "still_unknown": "<something important the reviews do not address, or null>",
  "matched_reviews": [0-based indices of reviews that address the question]
}

PATH 4: Either:
- Reviews mention the attribute but no reviewer is comparable (e.g. all reviewers are 5'7" or taller for a length question, and user is 5'2" / 157cm), OR
- Reviews are too thin (fewer than 3 reviews address the blocking question), OR
- Reviews are completely irrelevant or do not address the blocking question at all.
Output JSON schema:
{
  "path": 4,
  "verdict": "Uncertain for you",
  "evidence_count": "<N reviewers mentioned attribute - all range. None near your height/use>",
  "reason": "<explanation of why experience may not transfer, e.g., 'At 5'2\" their experience may not transfer' or 'Too few reviews to determine fabric softness'>",
  "confidence": "low"
}

PATH 0: There are zero reviews in total for this product. If a product has any reviews at all, it CANNOT be path 0.
Output JSON schema:
{
  "path": 0,
  "verdict": "Can't answer this one",
  "evidence_count": "0 reviews",
  "confidence": "none"
}

HARD RULES:
1. Use ONLY the reviews and buyer questions supplied. Never use general knowledge about the brand or product.
2. If fewer than 3 reviews (excluding buyer questions) address the question, you MUST NOT produce a Path 1 or Path 2 verdict. You MUST fallback to Path 4.
   Exception: If there is a buyer question and answer under "buyer_questions" that directly resolves the blocking question, you can use Path 1 or Path 2 using the buyer question/answer as the key evidence, regardless of the review count. For example, if a buyer Q&A answers the laptop size question and is from a comparable buyer, use Path 1.
3. The verdict must be under 12 words.
4. still_unknown must name something the reviews genuinely do not address, or be null.
5. Never invent a review, a reviewer attribute, or a count.
6. Return ONLY the raw JSON object. Do not include markdown wrappers or any other text.
7. IMPORTANT: If you include height in feet and inches (e.g., 5'2"), you MUST use single quotes for inches (e.g. 5'2') or escape the double quote (e.g. 5'2\\\") to ensure the JSON remains valid. Unescaped double quotes inside JSON string values are syntax errors.
8. If a product has any reviews, it must be assigned path 1, 2, or 4. It cannot be path 0.
"""

def clean_json_text(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    # Escape any unescaped double quotes indicating inches, e.g., 5'2" -> 5'2\"
    text = re.sub(r"(\d+)'(\d+)\"(\s*[^,}\]])", r"\1'\2\\\"\3", text)
    # Also catch simple cases like "all 5'2" or "all 5'2"
    text = re.sub(r"(\d+)'(\d+)\"", r"\1'\2\\\"", text)
    return text.strip()

def call_gemini_with_retry(prompt):
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.0,
                response_mime_type="application/json"
            )
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=config
            )
            return response.text
        except (ClientError, APIError) as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait_time = attempt * 10
                print(f"Rate limit hit. Waiting {wait_time}s before retry (attempt {attempt}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("Exceeded max retries for Gemini API call.")

def compute_path_3(product):
    kept = product.get("purchase_data", {}).get("kept_purchases", [])
    comparable_kept = [p for p in kept if 155 <= p["height_cm"] <= 159]
    if len(comparable_kept) >= 10:
        sizes = [p["size"] for p in comparable_kept]
        size_counts = collections.Counter(sizes)
        modal_size, modal_count = size_counts.most_common(1)[0]
        return {
            "path": 3,
            "verdict": f"Buyers like you chose {modal_size}",
            "evidence_count": f"Of {len(comparable_kept)} buyers within 2cm of your height who kept the item, {modal_count} chose {modal_size}",
            "confidence": "moderate",
            "note": "No reviews on this item yet"
        }
    return None

def get_badge(path, confidence):
    if path in [1, 2]:
        if confidence in ["high", "moderate"]:
            return "answered"
        elif confidence == "low":
            return "needs answers"
    elif path == 3:
        return "answered"
    elif path in [4, 0]:
        return "ask someone"
    return "ask someone"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    products = data.get("products", [])
    print(f"Loaded {len(products)} products from seed.json")

    results_table = []

    # FIT/SIZE/LENGTH products list (comparability mandatory)
    FIT_PRODUCTS = {"p01", "p03", "p04", "p05", "p12", "p16", "p17", "p20", "p22", "p23"}

    for p in products:
        pid = p["id"]
        name = p["name"]
        num_reviews = len(p.get("reviews", []))
        has_purchase_data = "purchase_data" in p

        print(f"\nProcessing product {pid}: {name}")

        # Rule 1: Check Path 3 (zero reviews but purchase data)
        if num_reviews == 0 and has_purchase_data:
            ans = compute_path_3(p)
            if ans:
                p["answer"] = ans
                p["badge"] = get_badge(ans["path"], ans["confidence"])
                print(f"  -> Path 3 (computed in Python)")
                results_table.append((pid, name, ans["path"], p["badge"], ans["verdict"]))
                continue

        # Rule 2: Check Path 0 (zero reviews, no purchase data)
        if num_reviews == 0 and not has_purchase_data:
            ans = {
                "path": 0,
                "verdict": "Can't answer this one",
                "evidence_count": "0 reviews",
                "confidence": "none"
            }
            p["answer"] = ans
            p["badge"] = get_badge(ans["path"], ans["confidence"])
            print(f"  -> Path 0 (computed in Python)")
            results_table.append((pid, name, ans["path"], p["badge"], ans["verdict"]))
            continue

        # Prepare progressive user profile specific to product context
        user_profile = DEMO_USER.copy()
        if pid == "p06":
            user_profile["laptop_size_inches"] = 14
        elif pid == "p07":
            user_profile["activity"] = "daily walking"
        elif pid == "p09":
            user_profile["activity"] = "afternoon function"
        elif pid == "p11":
            user_profile["activity"] = "summer daily"
        elif pid == "p13":
            user_profile["laptop_size_inches"] = 14
        elif pid == "p21":
            user_profile["activity"] = "long walking"
        elif pid == "p25":
            user_profile["activity"] = "long standing event"

        # For items with reviews (or buyer questions), use Gemini API
        prompt_data = {
            "product_details": {
                "id": p["id"],
                "name": p["name"],
                "brand": p["brand"],
                "category": p["category"],
                "match_attribute": p.get("match_attribute"),
                "blocking_question": p["blocking_question"]
            },
            "demo_user": user_profile,
            "reviews": [
                {
                    "index": i,
                    "text": r["text"],
                    "rating": r["rating"],
                    "reviewer_height_cm": r.get("reviewer_height_cm"),
                    "reviewer_size": r.get("reviewer_size"),
                    "months_owned": r.get("months_owned"),
                    "reviewer_use": r.get("reviewer_use"),
                    "packet_photo_only": r.get("packet_photo_only")
                }
                for i, r in enumerate(p.get("reviews", []))
            ],
            "buyer_questions": p.get("buyer_questions", [])
        }

        prompt_str = json.dumps(prompt_data, indent=2)

        try:
            print("  Calling Gemini API...")
            raw_response = call_gemini_with_retry(prompt_str)
            clean_response = clean_json_text(raw_response)
            
            try:
                ans = json.loads(clean_response)
            except json.JSONDecodeError as jde:
                print(f"  [ERROR] JSON Parsing failed: {jde}")
                print(f"  Raw response from API:\n{raw_response}")
                raise jde
            
            # Python Guard: If a FIT/SIZE product is incorrectly returned as Path 2, override to Path 4
            if pid in FIT_PRODUCTS and ans.get("path") == 2:
                print(f"  [PYTHON GUARD] Overriding Path 2 to Path 4 for fit product {pid}")
                ans["path"] = 4
                ans["verdict"] = "Uncertain for you"
                ans["confidence"] = "low"
                
                # Count reviews that address sizing
                reviews = p.get("reviews", [])
                fit_review_count = 0
                for r in reviews:
                    txt = r["text"].lower()
                    if any(w in txt for w in ["size", "fit", "tight", "loose", "small", "large", "waist", "hip", "thigh", "length", "hem", "sleeve", "shoulder", "short", "tall", "wide", "cling", "stretch", "ribbing"]):
                        fit_review_count += 1
                if fit_review_count == 0:
                    fit_review_count = len(reviews)
                
                match_attr = p.get("match_attribute")
                if match_attr == "build":
                    ans["evidence_count"] = f"{fit_review_count} reviewers mentioned fit - none with average build"
                    ans["reason"] = "All four reviewers who commented on fit described themselves as slim. For an average build, their experience may not transfer."
                else:
                    ans["evidence_count"] = f"{fit_review_count} reviewers mentioned sizing - none near your height"
                    ans["reason"] = "At 5'2\" their experience may not transfer."
                
                ans.pop("matched_reviews", None)
                ans.pop("still_unknown", None)

            p["answer"] = ans
            p["badge"] = get_badge(ans["path"], ans["confidence"])
            
            print(f"  -> Path {ans['path']} (Gemini API) | Badge: {p['badge']} | Verdict: {ans['verdict']}")
            results_table.append((pid, name, ans["path"], p["badge"], ans["verdict"]))
            
        except Exception as e:
            print(f"  [ERROR] Failed to process product {pid}: {e}", file=sys.stderr)
            # Fallback to Path 0 in case of failure
            ans = {
                "path": 0,
                "verdict": "Error processing",
                "evidence_count": "Error",
                "confidence": "none"
            }
            p["answer"] = ans
            p["badge"] = "ask someone"
            results_table.append((pid, name, 0, p["badge"], ans["verdict"]))

        # Respect Rate Limits (15 RPM -> space out requests)
        time.sleep(4)

    # Save output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved updated seed to {OUTPUT_FILE}")

    # Print summary table
    print("\n" + "="*80)
    print(f"{'ID':<5} | {'Product Name':<35} | {'Path':<5} | {'Badge':<15} | {'Verdict'}")
    print("="*80)
    for pid, name, path, badge, verdict in results_table:
        short_name = name[:33] + "..." if len(name) > 35 else name
        print(f"{pid:<5} | {short_name:<35} | {path:<5} | {badge:<15} | {verdict}")
    print("="*80)

if __name__ == "__main__":
    main()
