import json, random
random.seed(42)

# ---------------------------------------------------------------
# SYNTHETIC DEMO DATA. Not real reviews, not real products.
# Reviewer heights, use contexts and ownership durations are the
# structured fields the MVP depends on and that real review systems
# do not collect. That absence is the problem being solved.
# ---------------------------------------------------------------

DEMO_USER = {
    "name": "Demo user",
    "height_cm": 157,          # 5'2"
    "usual_size_top": "M",
    "usual_size_bottom": "M",
    "usual_size_shoe": "UK6",
    "build": "average",
    "laptop_size_inches": None,   # asked progressively
    "activity": None              # asked progressively
}

def rv(text, rating, h=None, size=None, months=1, use=None, kept=True, packet_only=False):
    return {"text": text, "rating": rating, "reviewer_height_cm": h,
            "reviewer_size": size, "months_owned": months,
            "reviewer_use": use, "kept": kept, "packet_photo_only": packet_only}

products = []

# ============ PATH 1: comparable buyers exist, apparel ============
products.append({
 "id":"p01","name":"Olive wide-leg high-waist trousers","brand":"Anouk",
 "category":"apparel_bottom","price":1699,"colour_block":"#6B7C3A",
 "match_attribute":"height",
 "blocking_question":"Will the length work on me at 5'2\", or will I need it altered?",
 "size_chart":{"S":{"waist_in":28,"hip_in":36,"inseam_in":30},
               "M":{"waist_in":30,"hip_in":38,"inseam_in":30},
               "L":{"waist_in":32,"hip_in":40,"inseam_in":30}},
 "demo_case":"path_1",
 "reviews":[
   rv("I'm 5'2 and the length was perfect without altering, sits right at the ankle.",5,157,"M",2),
   rv("At 5'3 these needed about an inch taken off, wearable with heels otherwise.",4,160,"M",1),
   rv("Fabric is thicker than expected which is good, holds shape.",4,168,"L",3),
   rv("Waist runs slightly small, I sized up.",3,165,"L",1),
   rv("Colour is exactly as shown. Very happy.",5,170,"M",1),
   rv("Too long on me but I'm short so expected that.",3,152,"S",1),
   rv("Good for office. Comfortable all day.",4,163,"M",4),
   rv("Delivery was quick, packaging fine.",4,None,"M",1),
 ]})

# ============ PATH 2: non-body attribute, washing ============
products.append({
 "id":"p02","name":"Blue oversized cotton T-shirt","brand":"Roadster",
 "category":"apparel_top","price":599,"colour_block":"#3B6EA5",
 "match_attribute":"height",
 "blocking_question":"Will the fabric stay soft after a few washes or lose its shape?",
 "size_chart":{"M":{"chest_in":40},"L":{"chest_in":42},"XL":{"chest_in":44}},
 "demo_case":"path_2",
 "reviews":[
   rv("Washed it six times now, no shrinking and the shape held.",5,None,"L",5),
   rv("Three months in, still soft. Colour faded very slightly.",4,None,"M",3),
   rv("After four washes the neckline is still fine, no stretching.",4,None,"L",4),
   rv("Comfortable, exactly the oversized fit I wanted.",5,172,"L",1),
   rv("Bit see-through in bright light but fine indoors.",3,None,"M",1),
   rv("Good value at this price.",4,None,"M",1),
 ]})

# ============ PATH 3: zero reviews, purchase data present ============
products.append({
 "id":"p03","name":"Rust corduroy boxy overshirt","brand":"Independent label",
 "category":"apparel_top","price":3200,"colour_block":"#A15B34",
 "match_attribute":"height",
 "blocking_question":"If I'm normally an M, what would I be in this brand?",
 "size_chart":None,
 "demo_case":"path_3",
 "reviews":[],
 "purchase_data":{
   "kept_purchases":[
     {"height_cm":156,"size":"L"},{"height_cm":157,"size":"L"},
     {"height_cm":158,"size":"L"},{"height_cm":155,"size":"L"},
     {"height_cm":157,"size":"M"},{"height_cm":158,"size":"L"},
     {"height_cm":156,"size":"L"},{"height_cm":159,"size":"L"},
     {"height_cm":155,"size":"M"},{"height_cm":157,"size":"L"},
     {"height_cm":158,"size":"L"},{"height_cm":156,"size":"L"},
     {"height_cm":159,"size":"L"},{"height_cm":157,"size":"L"},
     {"height_cm":155,"size":"L"},{"height_cm":158,"size":"M"},
     {"height_cm":156,"size":"L"},{"height_cm":157,"size":"L"},
     {"height_cm":170,"size":"L"},{"height_cm":172,"size":"XL"},
     {"height_cm":168,"size":"L"},{"height_cm":175,"size":"XL"},
     {"height_cm":165,"size":"L"}
   ],
   "returned_purchases":[
     {"height_cm":157,"size":"M"},{"height_cm":156,"size":"M"},
     {"height_cm":158,"size":"M"}
   ]}})

# ============ PATH 4: the R13 case — reviews mention it, none comparable ============
products.append({
 "id":"p04","name":"Black straight-fit cargo pants","brand":"Myntra label",
 "category":"apparel_bottom","price":1599,"colour_block":"#2B2B2B",
 "match_attribute":"height",
 "blocking_question":"Will these fit around the waist and thighs, or should I size up?",
 "size_chart":{"M":{"waist_in":30,"hip_in":38},"L":{"waist_in":32,"hip_in":40}},
 "demo_case":"path_4",
 "reviews":[
   rv("Runs small, I sized up and it was right.",4,170,"L",1),
   rv("Definitely size up, the waist is tight.",3,173,"L",1),
   rv("I went one size larger based on other reviews, good decision.",4,168,"L",2),
   rv("Thigh area is snug if you have muscular legs.",3,175,"XL",1),
   rv("Length was good on me, I'm on the taller side.",4,172,"L",1),
   rv("Fabric quality is decent for the price.",4,169,"L",3),
   rv("Nice colour, true black not washed out.",5,None,"M",1),
 ]})

# ============ ASK-SOMEONE / ASK-BUYERS: nothing at all ============
products.append({
 "id":"p05","name":"Chocolate satin midi dress","brand":"Instagram brand",
 "category":"apparel_top","price":2450,"colour_block":"#5C4033",
 "match_attribute":"height",
 "blocking_question":"Does it look and fit like it does in the brand's video?",
 "size_chart":None,
 "demo_case":"no_evidence",
 "reviews":[]})

# ============ ANSWERED BUYER QUESTION: shows the loop closing ============
products.append({
 "id":"p06","name":"Tan leather tote bag","brand":"Hidesign",
 "category":"bag","price":8900,"colour_block":"#B4794A",
 "match_attribute":"laptop_size_inches",
 "blocking_question":"Will a 14-inch laptop fit flat inside without forcing it?",
 "size_chart":{"one_size":{"external_w_cm":38,"external_h_cm":30,"external_d_cm":12}},
 "demo_case":"answered_buyer_question",
 "buyer_questions":[
   {"question":"Will a 14-inch MacBook fit flat inside?",
    "answer":"Yes, mine goes in flat. Slightly snug at the corners but no forcing.",
    "answered_by":"Verified buyer, owned 7 months","answered_days_ago":3}],
 "reviews":[
   rv("Beautiful bag, looks premium in person.",5,None,None,1),
   rv("Leather has softened nicely over six months.",5,None,None,6),
   rv("Straps are comfortable even when full.",4,None,None,4),
   rv("Colour is slightly darker than the photos.",4,None,None,2),
 ]})

# ============ FOOTWEAR: use-case matching, proves not apparel-only ============
products.append({
 "id":"p07","name":"Dark green running shoes","brand":"Asics",
 "category":"footwear","price":3800,"colour_block":"#2E5D4B",
 "match_attribute":"activity",
 "blocking_question":"Are these comfortable for long walks and light running, or mainly casual?",
 "size_chart":{"UK5":{"cm":23},"UK6":{"cm":24},"UK7":{"cm":25}},
 "demo_case":"path_1_use",
 "reviews":[
   rv("I walk 5km daily in these, no complaints after four months.",5,None,"UK6",4,use="daily walking"),
   rv("Used them for light jogging twice a week, cushioning holds up.",4,None,"UK7",3,use="light running"),
   rv("Bought for the gym, fine for treadmill but not for lifting.",4,None,"UK8",2,use="gym"),
   rv("Mainly wear them casually, very comfortable.",5,None,"UK6",1,use="casual"),
   rv("Sole started wearing after two months of running.",3,None,"UK9",2,use="running"),
   rv("Sizing is true, no need to size up.",4,None,"UK6",1,use="casual"),
 ]})

# ============ THIN REVIEWS, PACKET PHOTOS: the R16 case ============
products.append({
 "id":"p08","name":"Grey baggy cargo pants","brand":"Meesho seller",
 "category":"apparel_bottom","price":649,"colour_block":"#7E8287",
 "match_attribute":"height",
 "blocking_question":"Is the fabric the thin shiny type or actual cotton canvas?",
 "size_chart":{"M":{"waist_in":30},"L":{"waist_in":32}},
 "demo_case":"thin_reviews",
 "reviews":[
   rv("ok",3,None,"M",1),
   rv("received",4,None,"L",1,packet_only=True),
   rv("nice",4,None,"M",1,packet_only=True),
   rv("Fabric is a bit shiny, not what I expected from the photos.",2,None,"L",1),
 ]})

# ============ OCCASION ITEM: R14's case ============
products.append({
 "id":"p09","name":"Maroon Anarkali kurta set with gota work","brand":"Libas",
 "category":"apparel_top","price":4299,"colour_block":"#7B2D3B",
 "match_attribute":"use",
 "blocking_question":"Will the inner lining make this too hot for a 4-hour afternoon function?",
 "size_chart":{"M":{"bust_in":38},"L":{"bust_in":40}},
 "demo_case":"path_4_use",
 "reviews":[
   rv("Gorgeous, the gota work is delicate and well done.",5,None,"M",1),
   rv("Wore it to an evening reception, lots of compliments.",5,None,"L",1,use="evening event"),
   rv("Colour is rich, exactly as shown.",5,None,"M",1),
   rv("Slightly long, I had it hemmed.",4,155,"M",1),
   rv("The dupatta is thinner than expected.",3,None,"L",1),
   rv("Good quality stitching for the price.",4,None,"M",2),
   rv("Fits well, no alterations needed.",4,165,"L",1),
   rv("Beautiful for festive occasions.",5,None,"M",1),
   rv("Lining is soft, comfortable to wear.",4,None,"M",1),
   rv("Packaging was lovely, felt premium.",5,None,"L",1),
   rv("Would buy again in another colour.",5,None,"M",2),
 ]})

# ============ Remaining catalogue: ordinary items, varied cases ============
filler = [
 ("p10","Pastel green embroidered kurta set","W","apparel_top",2400,"#A8C3A0","height",
  "Is the actual colour the same as in the pictures?","path_2",[
   rv("Colour is slightly more mint than the photo shows.",4,None,"M",1),
   rv("Embroidery looks good in person, better than expected.",5,None,"L",1),
   rv("Lighting in the listing makes it look brighter.",3,None,"M",1),
   rv("True to the photos on my screen.",4,None,"M",1),
   rv("Fabric is comfortable for summer.",4,162,"M",2),
  ]),
 ("p11","Linen saree, natural beige","Fabindia","apparel_top",1200,"#D8CBB3","use",
  "Will linen be comfortable in humid weather?","path_2",[
   rv("Wore it through a Chennai summer, breathable throughout.",5,None,None,3,use="summer daily"),
   rv("Creases quickly but that is linen.",4,None,None,2),
   rv("Light and easy to drape.",4,None,None,1),
   rv("Needed starching to hold shape.",3,None,None,1),
  ]),
 ("p12","Red three-piece suit set","Anouk","apparel_top",1324,"#9B2226","height",
  "Will the shoulders be too tight at my size?","path_1",[
   rv("I'm 5'2 and the M fitted well across the shoulders.",5,157,"M",1),
   rv("At 5'1 the length was slightly long.",4,155,"M",1),
   rv("Shoulders run narrow, size up if broad.",3,168,"L",1),
   rv("Good fit overall, comfortable.",4,160,"M",2),
   rv("Colour is deeper than shown.",4,None,"L",1),
  ]),
 ("p13","Black structured shoulder bag","Independent brand","bag",4200,"#1F1F1F","laptop_size_inches",
  "Will it hold up well with daily use?","path_2",[
   rv("Eight months of daily commuting, corners are wearing slightly.",4,None,None,8),
   rv("Six months in and still looks new.",5,None,None,6),
   rv("Structure held up better than I expected.",5,None,None,5),
   rv("Hardware started tarnishing after three months.",3,None,None,3),
   rv("Looks professional, good for office.",5,None,None,1),
  ]),
 ("p14","Asics running shoes, current model","Asics","footwear",4500,"#4A5D75","activity",
  "Is this the same model as last year or did the sole change?","no_evidence",[
   rv("Comfortable, no issues.",4,None,"UK8",1),
   rv("Good grip.",4,None,"UK7",1),
  ]),
 ("p15","White fitted crew-neck tee","Uniqlo","apparel_top",790,"#F2F2F2","height",
  "Is it see-through?","path_2",[
   rv("Slightly sheer in direct sunlight, fine otherwise.",4,None,"M",1),
   rv("Not see-through at all for me.",5,None,"L",1),
   rv("Thin fabric, I wear a camisole under it.",3,None,"M",2),
   rv("Held shape after many washes.",5,None,"M",6),
   rv("Good basic, would rebuy.",5,None,"L",3),
  ]),
 ("p16","Wide-leg denim jeans, mid blue","Levis","apparel_bottom",2999,"#4A6382","height",
  "How much length will I lose if I hem them at 5'2\"?","path_1",[
   rv("I'm 5'2 and took off two inches, sits perfectly now.",5,157,"M",2),
   rv("At 5'3 I hemmed one and a half inches.",4,160,"M",1),
   rv("No alteration needed at 5'8.",5,173,"L",1),
   rv("Denim is stiff at first, softens after two washes.",4,None,"M",3),
   rv("True to size at the waist.",4,None,"L",1),
   rv("Colour bled slightly in the first wash.",3,None,"M",1),
  ]),
 ("p17","Cotton palazzo trousers, mustard","W","apparel_bottom",1099,"#C99A2E","height",
  "Are they too wide at the ankle for someone short?","path_4",[
   rv("Very flowy, I like the drape. I'm 5'7.",5,170,"M",1),
   rv("At 5'8 these are elegant.",5,173,"L",1),
   rv("Wide but manageable, I'm 5'9.",4,175,"L",1),
   rv("Nice fabric for summer.",4,None,"M",2),
  ]),
 ("p18","Faux-leather crossbody bag","Accessorize","bag",1899,"#3A2E28","laptop_size_inches",
  "Will an A5 notebook and a water bottle both fit?","no_evidence",[
   rv("Cute bag, good for evenings.",4,None,None,1),
   rv("Strap is adjustable which helps.",4,None,None,2),
 ]),
 ("p19","Chunky knit cardigan, oatmeal","H&M","apparel_top",2199,"#D6C7AC","height",
  "Does it pill after washing?","path_2",[
   rv("Pilled under the arms after four washes.",3,None,"M",4),
   rv("Five months in, minor pilling but acceptable.",4,None,"L",5),
   rv("No pilling at all, I hand wash.",5,None,"M",3),
   rv("Warm and soft, good for Delhi winter.",5,None,"L",2),
   rv("Sleeves are long, I'm 5'3.",4,160,"M",1),
  ]),
 ("p20","Pleated midi skirt, navy","Vero Moda","apparel_bottom",1799,"#25344F","height",
  "Where will it fall on me at 5'2\"?","path_1",[
   rv("Hits mid-calf on me, I'm 5'2.",4,157,"M",1),
   rv("Below the knee at 5'4.",5,163,"M",1),
   rv("Just above the ankle at 5'0.",4,152,"S",1),
   rv("Pleats hold well after washing.",5,None,"M",3),
   rv("Waistband is comfortable.",4,None,"L",1),
 ]),
 ("p21","Canvas sneakers, off-white","Converse","footwear",3299,"#EDE8DC","activity",
  "Do they hurt on long walking days?","path_1_use",[
   rv("Walked around Rome for a week, no blisters.",5,None,"UK6",2,use="long walking"),
   rv("Fine for short trips, sore after 10km.",3,None,"UK7",1,use="long walking"),
   rv("Good for daily college wear.",4,None,"UK5",4,use="casual"),
   rv("Needed a week to break in.",4,None,"UK6",1,use="casual"),
 ]),
 ("p22","Ribbed bodycon dress, black","Zara","apparel_top",2590,"#1A1A1A","build",
  "Is the ribbing forgiving or does it cling?","path_4",[
   rv("Clings but in a flattering way, I'm slim.",4,None,"S",1,use=None),
   rv("Very stretchy, comfortable.",5,None,"M",1),
   rv("Shows every line, size up if unsure.",3,None,"M",1),
   rv("Good quality ribbing, thick fabric.",5,None,"S",2),
 ]),
 ("p23","Formal shirt, light blue","Van Heusen","apparel_top",1499,"#A9C4DA","height",
  "Are the sleeves long enough for someone tall?","path_4",[
   rv("Sleeves are fine at 5'6.",4,168,"M",1),
   rv("Good fit at 5'5.",4,165,"M",2),
   rv("Collar is well structured.",5,None,"L",1),
   rv("Wrinkles easily, needs ironing.",3,None,"M",1),
 ]),
 ("p24","Silk-blend scarf, teal print","Fabindia","apparel_top",899,"#1F6E6E","use",
  "Is the print as vivid in person?","path_2",[
   rv("More muted than the photo but still lovely.",4,None,None,1),
   rv("Print is accurate on my screen.",5,None,None,1),
   rv("Silk feels good, drapes nicely.",5,None,None,2),
 ]),
 ("p25","Block-heel sandals, tan","Metro","footwear",2199,"#C08552","activity",
  "Can I stand in these for a four-hour function?","path_1_use",[
   rv("Stood through a whole wedding, feet were fine.",5,None,"UK6",1,use="long standing event"),
   rv("Comfortable for three hours, then sore.",4,None,"UK7",2,use="long standing event"),
   rv("Heel height is manageable.",4,None,"UK5",1,use="casual"),
   rv("Strap rubbed on the first wear.",3,None,"UK6",1,use="casual"),
 ]),
]

for pid,name,brand,cat,price,colour,attr,q,case,revs in filler:
    products.append({"id":pid,"name":name,"brand":brand,"category":cat,
        "price":price,"colour_block":colour,"match_attribute":attr,
        "blocking_question":q,"size_chart":None,"demo_case":case,"reviews":revs})

out = {
  "_disclaimer":("SYNTHETIC DEMO DATA. Products, brands, prices, reviews and "
    "purchase records are invented for prototype demonstration. Not affiliated "
    "with Myntra or any brand named. Reviewer height, use context and ownership "
    "duration are structured fields that real review systems do not collect; "
    "their absence is the problem this prototype addresses."),
  "demo_user": DEMO_USER,
  "products": products
}

with open('/home/claude/mvp/seed.json','w',encoding='utf-8') as f:
    json.dump(out,f,indent=2,ensure_ascii=False)

# ---- verification ----
print("products:",len(products))
from collections import Counter
print("\ndemo cases:")
for k,v in Counter(p['demo_case'] for p in products).items(): print(f"  {k}: {v}")
print("\ncategories:")
for k,v in Counter(p['category'] for p in products).items(): print(f"  {k}: {v}")
print("\ntotal reviews:",sum(len(p['reviews']) for p in products))
print("reviews with height stated:",sum(1 for p in products for r in p['reviews'] if r['reviewer_height_cm']))
print("reviews with use stated:",sum(1 for p in products for r in p['reviews'] if r['reviewer_use']))
print("products with zero reviews:",sum(1 for p in products if len(p['reviews'])==0))
print("products with purchase data:",sum(1 for p in products if 'purchase_data' in p))
print("products with answered buyer question:",sum(1 for p in products if 'buyer_questions' in p))
