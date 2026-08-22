# MVP scope

**Locked 22 August 2026, after the problem statement.**

## Selected: Wishlist Decision Assistant

A phone-width web prototype. For one saved item, it answers the question standing between the user and the purchase, states how much to trust that answer, and says plainly when it cannot answer at all.

---

## Why this and not the alternatives

Chosen by elimination after the problem statement was locked, not before.

**H2 Choice died.** `BLOCK_CHOICE_COMPARISON` accounts for 4.45% of coded rows, rank 10 of 15, severity 2.38 — the lowest of the top ten. Comparison saving occurs (6 of 20 respondents) but does not block. Those respondents' unanswered questions were about fit, fabric and predictability, not about which item to pick.

**H3 Timing died.** No timing code ranks near the top. Occasion-driven saving is real (6 of 20) but presents as a styling and suitability problem — `BLOCK_STYLING` at 56.3% within `INTENT_OCCASION` against 7.5% overall — not a timing problem. Those users have a deadline; what they lack is confidence.

**H1 Confidence survived all four testable kill conditions.**

### Options considered and rejected

| Option | Why not |
|---|---|
| Size Passport — translate sizes across brands | Strongest conversion logic of any option, because it removes the decision rather than informing it. Rejected because it only works for apparel. Half the research sample holds a non-size question — R12 on shoe suitability, R17 on internal bag dimensions, R11 on durability. Retained on the roadmap. |
| Structured review prompts at point of purchase | Attacks the root cause upstream and would generate exactly the data this MVP needs. Rejected because it delivers nothing to anyone blocked today — a pure cold-start problem. Retained on the roadmap. |
| Ask the buyers, as the whole product | Best conversion logic because it solves the blocker and the return-to-app problem together. Rejected as the core because it is asynchronous and a prototype cannot demonstrate an answer arriving. Retained as one of two fallbacks. |
| On-body visualiser from a user photo | Rejected on evidence and on safety. No respondent asked to see the item on themselves; every one asked to see it on someone else who resembles them. Body-photo upload in a consumer fashion app carries risks that cannot be mitigated in a prototype. |
| Occasion planner | H3 died. |
| Shortlist resolver | H2 died. |

---

## Four answer paths

The path is chosen by what evidence exists, in this order.

**1. A comparable buyer reviewed it** → show their review, with their stated attribute

> **Likely fits you unaltered**
> Based on 6 of 42 reviews — 2 from buyers near your height
> Moderate confidence
> Still unknown: fabric after washing

**2. Reviews answer the question, but comparability is not the axis** → answer from reviews with a count

> **Three reviewers mentioned washing. All three said it kept its shape.**
> Based on 3 of 42 reviews
> Moderate confidence

**3. No usable reviews, but purchase data exists** → aggregate from kept purchases by comparable buyers

> **Buyers like you chose L**
> Of 23 buyers within 2cm of your height who kept the item, 17 chose L.
> No reviews on this item yet.

**4. Nothing available** → say so, and offer a route

> **Uncertain for you**
> 6 reviewers mentioned length — all 5'5" or taller. None near your height.
> At 5'2" their experience may not transfer.

---

## Rules governing path 3

- **Kept purchases only.** Purchases past the return window. Counting returned items would recommend sizes based partly on mistakes.
- **Minimum threshold of 10 comparable kept purchases.** Three buyers is not a pattern.
- **Answers size only.** It says nothing about fabric behaviour, colour accuracy, or whether a laptop fits.

Path 3 is the only path that works on a product with zero reviews, and it is the only one that could not be replicated by any party without first-party purchase data.

---

## Four screens

### Setup — progressive
Height and usual size collected on first use. Any further attribute is requested only when an item requires it, once. A tote asks what size laptop the user carries; activewear asks how they will use it. This keeps first-run setup to two fields.

### Wishlist
Eight saved items. Each shows a badge and, where relevant, the blocking question.

Badges: **✓ ready to buy** · **? needs answers** · **→ ask someone**

The third badge replaces the guide's original *let it go*, which was cut because sorting a wishlist by whether the user still wants the item is intent triage — the branch eliminated in `decomposition.md` Section 5.

### Item sheet
One of the four outputs above. The review count is tappable and opens an evidence drawer showing the actual reviews with each reviewer's stated attribute.

### Action row
```
Buy                    Archive (with undo)
─────────────────────────────────────────
Still need an answer?
  Ask someone you know    →  now
  Ask buyers of this item →  slower, more reliable
```

**Ask someone** produces a message already written — the item, the price, the image, the link, and the question. Copy to clipboard.

**Ask buyers** posts the question to buyers of that item and confirms it has been sent. Asynchronous by nature; the prototype does not fake an answer arriving. One catalogue item carries an already-answered buyer question so the resolved state is visible.

---

## Category-specific matching

The matching attribute is determined by the product type, not fixed.

| Category | Matched on |
|---|---|
| Clothing | Height, build, usual size |
| Footwear | Usual size, foot width, activity |
| Bags | What the buyer carries |
| Activewear | Activity and intensity |

Beauty and skincare are out of scope. The analogous attribute would be skin type, which is legitimate in principle, but beauty accounts for one row of 292 coded comments and zero described items in the research. Building a match dimension on that evidence would be asserting a problem that was not measured.

---

## Evidence for every element

| Element | Evidence |
|---|---|
| Match to a comparable buyer | R7, R8, R13, R14 asked for it directly. R18 performed it by hand — 30 minutes scrolling a brand's tagged photos to find one person of similar height |
| Reviewer's attribute shown alongside | R13: *"Reviews have photos but nobody mentions their height, or if they do they're all 5'6+"* |
| Review count displayed | R16's item had 4 reviews, two of which were photographs of the packet |
| Comparability drives the confidence band | R13 had 6 reviews mentioning length, followed three reviewers' advice, ordered up, and the garment was still too big. Volume without comparability produced a wrong answer |
| "Still unknown" line | 8 of 20 named reviews as the source that failed to answer their question |
| Honest declines | 7 of 20 held a question no review could answer |
| Ask someone, pre-drafted | 4 of 20 already do this. R14 sent *"too much for a mehendi??"* to her sister; R16 sent *"649 cargo, worth risking?"* to a friends group |
| Ask buyers | 203 of 682 corpus comments (29.8%) are people answering each other's product questions. R18 found people in a brand's comments *"asking the same thing with no answers"* |
| Path 3, purchase aggregate | Fills the only gap retrieval cannot reach. R18's brand had no reviews anywhere |

---

## What is deliberately absent

**Anything price-related.** No discounts, coupons, drop alerts or price history. Forbidden by the brief. Measured and reported instead: 5 of 20 gave price-led answers and `INTENT_PRICE_WATCH` accounts for 22 corpus rows. Three respondents stated unprompted that they did not want a discount.

**Occasion and deadline features.** H3 died.

**Comparison between saved items.** H2 died.

**Intent triage.** Eliminated in the decomposition on the grounds that intent is detectable but not changeable.

**Notifications and re-entry prompts.** The coming-back branch was eliminated as unmeasurable with available data.

---

## Who this addresses

The 17 of 20 respondents holding an unanswered question about an item they would consider buying.

Not the 3 who saved with no purchase intent — style reference, or liked without planning to buy. No information changes those, and the only lever that would is price.

Within the 17, the subset blocked by affordability rather than information is also out of reach. R13's *"₹6000+ things I saved when I was feeling rich"*; R17's aspirational bags.

---

## What this MVP does not solve

Stated rather than hidden.

**The fact is not published anywhere — 4 respondents.** If a bag's internal dimensions were never measured, no review contains them. Paths 1 and 2 return nothing; the MVP declines and routes to *ask buyers*, which is the only mechanism that can generate the missing fact.

**The source is not credible — 3 respondents.** Displaying the review count is a partial mitigation. It does not verify that photographs are genuine.

**Nobody has owned it long enough — 2 respondents.** No retrieval system can surface a twelve-month review that does not exist.

---

## Seed catalogue requirements

25 products. Each of these cases must be present:

| Case | Purpose |
|---|---|
| Rich reviews with stated heights or use contexts | Demonstrates path 1 |
| Reviews discussing a non-body attribute — washing, colour, version | Demonstrates path 2 |
| Zero reviews, purchase data present | Demonstrates path 3 |
| Reviews mentioning the attribute, all from dissimilar buyers | Demonstrates path 4 — the R13 case, and the best demo of the product's honesty |
| Zero reviews, no purchase data | Demonstrates the ask-someone and ask-buyers fallbacks |
| One item with an already-answered buyer question | Shows the ask-buyers loop closing |
| At least one bag and one pair of footwear | Proves the mechanism is not apparel-specific |

---

## The objection to answer pre-emptively

*"This is a review filter."*

Partly true and worth conceding. But: a filter returns a list and leaves the synthesis to the user, whereas this returns an answer with its working. Existing filters sort by attributes of the review — rating, recency, helpfulness. This sorts by attributes of the reviewer, matched against the user. A filter cannot tell you it has nothing, and cannot state what it failed to resolve.

The evidence that filters are insufficient is that R18 used them, then left Myntra and spent thirty minutes on Instagram.

And path 3 cannot be reached by filtering at all. *"Buyers within 2cm of your height who kept the item mostly chose L"* does not exist as text anywhere. It requires first-party purchase data.
