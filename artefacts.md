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

# Files
