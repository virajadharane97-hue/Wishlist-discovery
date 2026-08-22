import json

INPUT_FILE = "mvp/seed_with_answers.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# FIX 1: Update p23 evidence_count
for p in data["products"]:
    if p["id"] == "p23":
        p["answer"]["evidence_count"] = "2 reviewers mentioned sleeves, both 165-168cm. None near your height."
        print("Updated p23 evidence_count")
        
# FIX 2: Update p22 reason
for p in data["products"]:
    if p["id"] == "p22":
        p["answer"]["reason"] = "All four reviewers who commented on fit described themselves as slim. For an average build, their experience may not transfer."
        print("Updated p22 reason")

# Convert to string to perform global height notation replacement (FIX 3)
json_str = json.dumps(data, indent=2, ensure_ascii=False)

# Standardise height notation (replace 5'2' with 5'2")
# In Python json.dumps, double quotes inside strings are escaped as \", so we look for 5'2' and replace with 5'2\"
json_str = json_str.replace("5'2'", '5\'2\\"')

with open(INPUT_FILE, "w", encoding="utf-8") as f:
    f.write(json_str)
print("Standardised 5'2' heights to 5'2\"")

# Reload and print targeted outputs
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data_updated = json.load(f)
    
targets = ["p04", "p05", "p09", "p17", "p22", "p23"]
output_dict = {p["id"]: p["answer"] for p in data_updated["products"] if p["id"] in targets}
print("\nTargeted answer objects:")
print(json.dumps(output_dict, indent=2))
