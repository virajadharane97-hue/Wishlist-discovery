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

# Files
