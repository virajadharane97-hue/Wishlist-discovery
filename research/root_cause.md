# Root cause chain

From the observed symptom down to a cause a product can act on. Each link cites the evidence that supports it. Corpus figures are from the excluded corpus, n=486, 292 coded rows. Research figures are from 20 written responses.

---

## The chain

**Symptom.** The item stays in the wishlist and is not bought within 30 days.

**Because** the user holds one unresolved question about the item.

> 19 of 20 respondents could state a specific question when asked directly. `BLOCK_SIZE_SELECTION` ranks first of 15 blocker codes at 22.6% of coded rows, with the highest severity (3.38) and the highest proximity to purchase (1.33) of any code, and ranks first under all four weighting schemes tested.

**Because** the information available to them does not answer that question.

> 8 of 20 named reviews as the source that failed them. R14: *"There are 11 reviews and all of them are about how pretty it looks, not one person says whether they were sweating in it."* R13: *"someone asked about length but the answer was just 'true to size' which means nothing."*

**Because** reviews report what an item looks like on arrival, while the question is about how it will perform for this specific person, over time, in their particular use.

> The search strings users type carry the qualifier explicitly: *"myntra cargo pants honest review"*, *"[bag] long term review"*, *"[shoe model] walking review"*, *"hidesign [model] laptop fit review"*. R10: *"Most reviews are written immediately after delivery and say things like 'good quality' without explaining what that means."* R12: *"I couldn't find a review from someone doing the same kind of activity as me."*

**Because** the review system collects a star rating and free text at the point of delivery, with no structured field for the reviewer's body, their use case, or how long they have owned the item.

> 4 of 20 said the reference bodies available are never close enough to transfer. R13: *"Reviews have photos but nobody mentions their height, or if they do they're all 5'6+."* R7: *"The size chart gives measurements but doesn't really tell me how the pants fit on an actual body... people have different body types and many haven't mentioned their height or measurements."*

**Because** reviews are designed to signal product quality in aggregate, not to answer an individual's specific question.

---

## Where the chain stops, and why

The final link is the root. It is a design property of the review system rather than a user failing or a gap in the data, and everything above it follows from it.

It also explains what a competing account cannot: **why more information has not fixed the problem.** Reviews exist. Photographs exist. Size charts exist. Users read all of them — 11 of 20 consult the size chart, 7 of 20 read reviews looking for size information, 6 of 20 examine customer photographs. Volume is not the constraint. Shape is. Aggregate signal cannot answer an individual question however much of it accumulates.

---

## What this makes buildable

A root cause is only useful if a product can act on it. This one can be acted on in a specific way: **the reviews that contain the answer often already exist, but the person who needs them cannot find them.**

You cannot make reviewers write differently at scale. You can find the review that already answers a given user's question and put it in front of them.

That is precisely what respondents described wanting, and what several did by hand at real cost:

- R13: *"If someone in the reviews posted a full length photo and mentioned they were around my height. That's genuinely it."*
- R17: *"If I could see a photo of the bag with a laptop inside it. One photo. That's the entire blocker and it's slightly absurd that it doesn't exist."*
- R18: went through a brand's tagged Instagram photos, found one person who stated they were 5'10 wearing M, ordered M at 5'11 — *"Took me about 30 minutes of scrolling to figure that out."*

---

## Two competing chains considered and rejected

### "Because size charts are unreliable"

Supported by the data — 4 of 20 describe cross-brand inconsistency, and `BLOCK_CHART_UNRELIABLE` accounts for 4.79% of coded rows. But it stops one level too high.

It cannot explain why a user who uses the chart correctly still fails. R13 measured herself with a tape, compared against the chart, found she was between M and L, read the reviews sorted by size, found three reviewers saying the item ran small, ordered L on that basis, and it was too big. She returned it and abandoned the item.

Chart unreliability is a symptom of the same root: the chart is aggregate data being asked an individual question.

### "Because users do not trust the information"

Also supported — 4 of 20 doubt the imagery, and `BLOCK_IMAGE_DISTRUST` accounts for 5.48% of coded rows. R16: *"Meesho photos are all clearly stolen from other websites... So I don't trust the photos at all."*

But distrust is a response to information that has repeatedly failed them, not the cause of the failure. Reversing the order would imply the fix is reassurance, when the evidence says the fix is relevance. Respondents do not ask to be persuaded; they ask for one specific fact.

---

## A note on where a reasonable reader might stop the chain earlier

The third link — that reviews answer a different question than the one the user holds — could itself be treated as the root, with the fourth link read as an explanation of why rather than a further cause.

Both stopping points are defensible. The fourth link is retained because it names a specific, changeable mechanism: the absence of structured fields for body, use case and ownership duration at the point of review collection. That is more actionable than the third link alone, which describes the mismatch without locating it.
