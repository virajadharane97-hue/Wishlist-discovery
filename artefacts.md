# Links

# Numbers
-Model used for all classification: gemini- 3.6-flash
-gemini free tier (AI Studio), key created 18 Aug2026

## Numbers
- Play Store (Myntra): 4,000 sampled from 10,000 pulled
- Date range: 2026-07-10 to 2026-08-18 (40 days)
- Package ID: com.myntra.android, lang=en, country=in
- Random seed: 42
- Pulled: 19 Aug 2026

- Play Store (AJIO): 500 rows, 2026-08-06 to 2026-08-18
- Package ID: com.ril.ajio

## Corpus (Day 1, 19 Aug 2026)
- Total: 6,070 rows
- Play Store: 4,496 (Myntra 4,000 + AJIO 496), 10 Jul – 18 Aug 2026
- YouTube: 1,567 comments, 41 videos, 22 May 2024 – 19 Aug 2026
- Reddit/Quora hand-collected: 7
- Duplicates removed: 4
- Rows with empty URL: 0
- Myntra sample: 4,000 drawn from 10,000, seed 42
- YouTube filtered to comments from 2024-01-01 onward
- Hand-collected (Reddit/Quora): 86 collected, 8 removed as SEO or
  industry content, 78 retained
- Removal criterion: text must report the author's own shopping
  behaviour, not describe or advise on shopping behaviour in general

# Markdown
-- Model: gemini-3.5-flash-lite (all classification)
- gemini-3.6-flash abandoned: free-tier cap of 20 requests/day.
  Verified via 429 RESOURCE_EXHAUSTED, quotaValue 20.
- Batch size 40, 8s pacing, 142 requests for 6,070 rows

## API quota constraints (observed, verbatim from 429 responses)
- gemini-3.6-flash: 20 requests/day, free tier. Unusable for bulk.
- gemini-3.5-flash-lite: 500 requests/day, free tier.
  quotaId GenerateRequestsPerDayPerProjectPerModel-FreeTier
- Limit is per project per model. Resets midnight Pacific = 12:30 pm IST.
- Today's 500 consumed across: 4 pilots, v1 full run (142 req),
  v2 full run (304 req), v3 partial (30 req).

  - Free-tier quota is 500 requests/day per project per model. The
  first project's quota was exhausted during filter iteration
  (v1 142 requests, v2 304, v3 30, plus pilots). A second Google
  Cloud project was created to complete the run.
- Model held constant at gemini-3.5-flash-lite across both projects,
  so classification behaviour is unchanged. Only the quota pool
  differs.

## Relevance filter iterations (19 Aug 2026)
- v1: batch 40, base prompt. 26.11% keep (1,585). Manual spot-check
  found ~87% false positives on Play Store — keyword matching, not
  intent. Rejected.
- v2: batch 20, stricter prompt with "already purchased = NO" rule.
  10.12% keep (614). Spot-check found ~40% of kept YouTube rows were
  pure link requests. Rejected.
- v3 pilot: added link-request and generic-praise exclusions.
  16% YouTube keep. Still keeping fragments too short to code.
- v3 final: added 40-character pre-API length floor. Pilot precision
  ~80% on 17 kept rows. LOCKED.
- Model: gemini-3.5-flash-lite, temperature 0, batch 20 throughout

- v4: 665 YES (7.50%). Manual check of 74 hand-picked rows found
  57 rejected, ~20 of them genuinely relevant. Separate check of 25
  new-batch YES rows found ~10 usable. Both false negatives and
  false positives present.
- v5: two prompt changes. Post-purchase rule narrowed to allow
  general conclusions drawn from past experience. Added exclusions
  for review requests, platform questions, return/exchange problems,
  and general anti-consumption advice.

  ## 20aug2026
 ## Relevance filter final (v5), 20 Aug 2026
- 8,861 raw → 682 relevant. Keep rate 7.70%. Zero errors.
- YouTube 615 (14.33%), Play Store 29 (0.65%),
  Reddit 27 (55.10%), Quora 11 (44.00%)
- Model: gemini-3.5-flash-lite, temp 0, batch 20, 8s pacing,
  40-character pre-API length floor
- Total API requests across all v5 runs: 298

## Filter validation
- Five iterations, each triggered by a hand check of retained or
  rejected rows. All versions preserved (clean_v1 to clean_v5).
- v4 → v5: 126 false negatives recovered, 157 false positives
  removed, net -31. Roughly 280 of 682 rows differ from v4.
- Recall validated on hand-picked rows: 17 YES in v4 → 38 YES in v5.
  Every row manually identified as wrongly rejected was recovered.
- Final precision check (n=25, stratified 15 YouTube / 8
  hand-collected / 2 Play Store, seed 77): ~15 of 25 carry codeable
  decision content, approx 60%. Remaining rows are short questions
  and platform queries that pass relevance but will not attract a
  blocker code, so they do not enter the counts.

## Quota constraints (verbatim from 429 responses)
- gemini-3.6-flash: 20 requests/day free tier. Unusable for bulk.
- gemini-3.5-flash-lite: 500 requests/day, per project per model.
  quotaId GenerateRequestsPerDayPerProjectPerModel-FreeTier
- Daily reset confirmed at 12:30 pm IST (midnight Pacific), observed
  20 Aug 2026.
- Two Google Cloud projects used. Model held constant across both,
  so classification behaviour is unchanged; only the quota pool
  differs.

  ## Corpus composition by video context (n=682)
- anti_consumption    196   28.7%
- haul                145   21.3%
- review_comparison   142   20.8%
- other                72   10.6%
- not_applicable       67    9.8%
- size_guide           60    8.8%

## Codebook frozen 20 Aug 2026
- 15 blocker codes, 5 intent codes
- Built bottom-up from 124 raw labels via open coding on 200 rows
  (seed 55), then merged. Seed codebook used only as a gap check.

## K1b threshold, computed before counting
- 15 blocker codes
- Baseline = 100 ÷ 15 = 6.67%
- Threshold = 2 × baseline = 13.33%
- H1 dies if no confidence-type blocker code reaches 13.33% of
  coded rows, even if one ranks first.

## K1a resolution, decided before counting
- K1a is evaluated at INDIVIDUAL CODE level, not group level.
- H1 survives only if one of these ranks first by opportunity score:
  BLOCK_SIZE_SELECTION, BLOCK_CHART_UNRELIABLE,
  BLOCK_BODY_PROJECTION, BLOCK_LISTING_INCOMPLETE,
  BLOCK_FABRIC_QUALITY, BLOCK_DURABILITY_VALUE
- Group-level shares will be reported alongside, labelled as
  grouped, and will NOT be used to decide whether H1 survives.
- Reason: grouping 6 of 15 codes as "my hypothesis" would make the
  test nearly impossible to fail, which defeats the purpose of a
  kill condition.

  ## Classifier (20 Aug 2026)
- Model gemini-3.5-flash-lite, temperature 0, batch 20, 8s pacing
- Codebook: data/codebook.json v1.0, frozen 20 Aug, 15 blocker codes,
  6 intent codes, role field
- Post-hoc verbatim validation: evidence_quote must be a contiguous
  substring of the source after whitespace normalisation, else set to
  null and quote_valid = False

### Known variance
Two pilot runs on the same 100-row sample (seed 66) at temperature 0
produced slightly different blocker distributions — DURABILITY 6 vs 9,
STYLING 7 vs 5, ANTICIPATED_NONUSE 2 vs 1. Temperature 0 reduces but
does not eliminate model variance. All reported shares should be read
as approximate to within a few percentage points, and no conclusion
should rest on a difference of less than about 3 points between codes.

### Classifier data integrity
- 1 row (yt_1054) failed JSON parsing due to nested double quotes in
  the source text. Re-sent individually with quote marks sanitised,
  same prompt and temperature. Label is the model's output, not
  hand-assigned.
- 1 row (play_ajio_0460) returned BLOCK_FABric_QUALITY, a casing
  deviation from the frozen codebook. Corrected to
  BLOCK_FABRIC_QUALITY. No invented code names across 682 rows.
- 18 of 682 evidence quotes failed the verbatim substring check and
  were set to null (2.6%).

  ## Classification distributions (v1.2, n=682)

### Workaround
- creator: 132 (19.4%)
- none: 137
- offline_store: 13
- friends: 8
- thrift: 8
- youtube: 7
- google: 4
- reddit: 2, tailor: 2, other: 3
- null: 366

### Role
- seeking: 461 (67.6%)
- advising: 203 (29.8%)
- null: 18

### Information sought
- size: 124 (37% of rows where a need was identified)
- styling: 60
- fabric: 52
- alternatives: 33
- fit: 27
- durability: 18
- reviews: 9
- authenticity: 9
- null: 350

## Links
- AI Discovery Engine: https://wishlist-discovery-lrfjnwcual42uzaat9po84.streamlit.app/
- GitHub: https://github.com/virajadharane97-hue/Wishlist-discovery
- Deployed 21 Aug 2026, shell only. Content added Day 4.

## Opportunity score formula
opportunity_score = share (as %) × avg_severity × avg_proximity_weight

Where:
- share = count / total rows with a non-null primary_blocker
- avg_severity = mean of severity_1_5 for rows carrying that code
- proximity weights: low = 0.5, medium = 1.0, high = 1.5

The proximity weights are a judgement, not a measured value. They
encode the assumption that a blocker sitting closer to the purchase
decision matters more than one sitting further away. Stated as a
judgement on the findings slide.

Computed twice: full corpus (n=682) and excluding
video_context = anti_consumption (n=486). Any code whose share moves
more than 5 percentage points between the two is flagged as
potentially an artefact of corpus composition.

## Opportunity ranking (excluded corpus, n=486, 292 coded rows)
| Code | Count | Share | Severity | Prox wt | Score |
|---|---|---|---|---|---|
| BLOCK_SIZE_SELECTION | 66 | 22.60% | 3.38 | 1.33 | 101.25 |
| BLOCK_LISTING_INCOMPLETE | 65 | 22.26% | 2.62 | 1.07 | 62.25 |
| BLOCK_FABRIC_QUALITY | 31 | 10.62% | 2.74 | 0.90 | 26.29 |
| BLOCK_STYLING | 22 | 7.53% | 2.77 | 0.89 | 18.52 |
| BLOCK_DURABILITY_VALUE | 21 | 7.19% | 3.05 | 0.76 | 16.70 |

Full corpus (n=682, 376 coded) figures in
data/opportunity_scores.csv.

## Sensitivity check on the opportunity formula
Ranking recomputed on the excluded corpus (n=486) under four
weighting schemes:
  A. baseline (0.5 / 1.0 / 1.5)
  B. proximity ignored (1.0 / 1.0 / 1.0)
  C. proximity weighted heavily (0.25 / 1.0 / 2.0)
  D. raw share only

BLOCK_SIZE_SELECTION ranks first under all four schemes.
BLOCK_SIZE_SELECTION, BLOCK_LISTING_INCOMPLETE and
BLOCK_FABRIC_QUALITY occupy the top three under all four.

Note: on raw share alone (D), size selection and listing incomplete
are close — 22.60% vs 22.26%. Severity (3.38 vs 2.62) and proximity
(1.33 vs 1.07) are what separate them. So the weighting does not
change which codes matter, but it does widen the gap between first
and second.

Conclusion: the ranking is not an artefact of the weighting choice.

## Workaround behaviour (excluded corpus)

BLOCK_SIZE_SELECTION, n=66:
- creator 26 (39.4%), none 8 (12.1%), youtube 1 (1.5%),
  not stated 31 (47.0%)
- Of rows where a workaround was stated (n=35): creator 74.3%,
  none 22.9%, youtube 2.9%
- role: seeking 64 (97.0%), advising 0

INTENT_GENUINE, n=222 coded rows:
- creator 80 (36.0%), none 33 (14.9%), youtube 4, friends 4,
  offline_store 3, reddit 1, not stated 97
- role: seeking 219 (98.7%)

Interpretation: users blocked on size selection overwhelmingly
resolve it by asking a person they consider credible, not by
consulting size charts or measuring themselves. Null values mean the
workaround was not stated in the comment, not that none exists, so
the 74.3% figure is computed on rows where a workaround was recorded.

## Links
- AI Discovery Engine (Deliverable 1):
  https://wishlist-discovery-lrfjnwcual42uzaat9po84.streamlit.app/
- GitHub: https://github.com/virajadharane97-hue/Wishlist-discovery
- Deployed and verified 21 Aug 2026 on desktop and mobile, private
  window, no login. Four tabs: findings with five charts, evidence
  with clickable source links, live classifier with demo-mode
  fallback, method and validation.
- Theme pinned to light in .streamlit/config.toml so the
  colour-blind-safe palette is not inverted by device dark mode.
  - Live classifier verified on the deployed app: a substantive comment
  returns a real classification; empty input falls back to the saved
  example with a warning rather than an error.

# Files
