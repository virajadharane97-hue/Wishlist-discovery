# AI Findings Report: Wishlist Discovery

This report outlines key findings, limitations, and exclusions based on the qualitative analysis of user comments in the fashion wishlist and shopping corpus.

## Key Findings

1. **Corpus Funnel:** Out of 8,861 raw comments collected across platforms, only 7.7% (682) passed relevance filtering, with the Play Store contributing 4,496 raw comments but yielding only 29 relevant rows.
2. **Top Blocker:** Size selection is the top blocker in the excluded corpus, representing 22.6% of coded rows (66 rows) with an opportunity score of 101.25, a severity of 3.38, and a proximity weight of 1.33.
3. **Irreconcilable Information:** The core sizing blocker is not ignorance of one's body dimensions but the difficulty of reconciling conflicting brand data, as one shopper complained, "which single number is the one I use to order" (yt_0785).
4. **Creator Workaround:** Faced with sizing blockers, 74.3% of users who recorded a workaround (26 of 35) turned to creators for advice, while 64 of the 66 size-selection rows represented a "seeking" role, asking queries like "meeso par mai 5 fit 3 inch ki hu" (I'm 5'3" — Meesho) (yt_0989).
5. **Peer Resolution:** Indicating that peer resolution already happens at scale, 29.8% of the relevant corpus (203 of 682 comments) consists of users advising each other, for example warning that "rayon h to thoda shrink hoga" (it's rayon, so it'll shrink a bit) (yt_0639).
6. **Occasion Segment:** Occasion-driven savers represent a distinct segment where `BLOCK_STYLING` jumps to 56.3% of blockers (compared to 7.5% overall) and 100% of the 16 users recorded workarounds, asking questions such as "smjh nhi aa rha kaise style kru" (I can't work out how to style it) (yt2_0677).

---

## Limitations

* **Platform Bias:** The relevant corpus is heavily biased, with 88% of rows originating from YouTube, while the Play Store contributed only a 0.65% relevance rate, predominantly app, delivery and service reviews, based on manual inspection of sampled rows.
* **Collection Artefacts:** Approximately 29% of the original relevant corpus came from decluttering and anti-consumption videos; to mitigate this, all metrics were computed twice and anti-consumption sources were excluded, which caused `BLOCK_WARDROBE_SATURATION` to drop from 37 rows to just 4.
* **Labeling Ambiguity:** Human-machine agreement was low at 36% (kappa 0.289), but because two independent human raters agreed with each other on only 46.7% of rows (kappa 0.413), it indicates the ambiguity lies in the codebook definitions rather than the raters.
* **Category Contamination:** `BLOCK_DURABILITY_VALUE` absorbed general price complaints instead of focusing purely on value-for-money, overstating its rank (7.19%, rank 5) and understating `INTENT_PRICE_WATCH` (22 rows).
* **Indicative Counts:** Counts and scores are indicative rather than statistically definitive; no conclusions are drawn from share differences under 3 percentage points.

---

## Why the Lower-Ranked Areas are Lower

### `BLOCK_LISTING_INCOMPLETE`
`BLOCK_LISTING_INCOMPLETE` ranks second because although its share (22.26%) is comparable to size selection (22.60%), its severity (2.62 vs 3.38) and proximity weight (1.07 vs 1.33) are lower.

### `BLOCK_FABRIC_QUALITY`
`BLOCK_FABRIC_QUALITY` ranks third (opportunity score 26.29) because it has a significantly lower share (10.62% vs 22.60% for size selection), a lower severity (2.74 vs 3.38), and a lower proximity weight (0.90 vs 1.33).

### `BLOCK_STYLING`
`BLOCK_STYLING` ranks fourth (opportunity score 18.52) because its share (7.53% vs 22.60%), severity (2.77 vs 3.38), and proximity weight (0.89 vs 1.33) are all lower than size selection.

---

## What This Rules Out

* **`BLOCK_WARDROBE_SATURATION` & `BLOCK_ANTICIPATED_NONUSE`:** These are ruled out as genuine customer blockers because they are collection artefacts of YouTube decluttering and anti-consumption videos, shrinking to negligible shares (1.37% and 0.34%) in the excluded corpus.
* **`INTENT_ACQUISITION_WATCH`:** This segment is ruled out as out of scope due to its small size (n=10) and the fact that it contains zero size-selection blockers, focusing instead on long-term availability tracking.
* **Price-driven Saving:** Saving items purely to wait for a discount (`INTENT_PRICE_WATCH`) is ruled out by the baseline business constraint against monetary incentives, meaning we do not design wishlist discovery interventions around pricing or discounts.
