# Day 1 — Corpus Collection and Filter Validation
**19 August 2026 · Graduation Project: Wishlist → Purchase Conversion (Myntra)**

Read this before any evaluation conversation. Likely evaluator questions are marked **[Q]** with the answer underneath.

**One-line summary of the day:** collected 8,861 public comments across four sources, then built a relevance filter, tested it by hand five times, and measured both its false-positive and false-negative rates before trusting a single number it produced.

---

## 1. What got collected

| Source | Rows | Method | Notes |
|---|---|---|---|
| Play Store — Myntra | 4,000 | `google-play-scraper` | Sampled from 10,000 pulled, seed 42, 10 Jul – 18 Aug 2026 |
| Play Store — AJIO | 496 | same | Competitor comparison line, 6–18 Aug 2026 |
| YouTube batch 1 | 1,567 | Data API v3 | 41 videos, 10 search terms, filtered to 2024+ |
| YouTube batch 2 | 2,724 | Data API v3 | 132 new videos, 15 terms, 4–20 min duration filter |
| Reddit + Quora | 74 | Hand-collected | Reddit API unavailable |
| **Total** | **8,861** | | Zero rows with empty URL |

**[Q] Why 8,861 rows when your own plan targeted 3,000?**
Because raw volume turned out to be a poor proxy for usable data. Play Store looked like the obvious source — nearly half the corpus — but only 0.78% of it discusses deciding whether to buy. Most reviews rate the app, the delivery, or the service. Once I measured that, I went back for more YouTube, which is where pre-purchase reasoning actually lives. The final relevant corpus is roughly 700 comments from 8,861 collected. The gap between those two numbers is the finding.

**[Q] Why is every row required to have a URL?**
So that any quote in the deck can be clicked and verified. A row without provenance cannot be used as evidence, only as filler. I built the column into the first collection script rather than trying to backfill it, and the merge step reports the count of empty URLs — it has been zero throughout.

**[Q] You sampled 4,000 from 10,000 Play Store reviews. Why not use all 10,000?**
The first pull of 4,000 covered only 15 days, which risks a single sale, app update, or outage dominating the corpus. Pulling 10,000 reached back 40 days, and I randomly sampled 4,000 from that wider range with a fixed seed so the sample is reproducible. It trades volume for time coverage, which matters more when the concern is event contamination.

---

## 2. Reddit failed. What I did instead.

Reddit now requires developer registration before API access, and approval was not obtainable inside the project window.

**[Q] You lost your richest source. How did you handle it?**
Three ways. First, I hand-collected from public Reddit and Quora pages — legal, manual, no automation, no login bypass — which yielded 74 rows after cleaning. Second, I doubled down on YouTube, because haul and try-on comment sections are the other place people discuss fit and fabric *before* buying. Third, I stated it as a limitation rather than hiding it. What I did not do was use a third-party scraper like Apify or Octoparse to bypass the API. Those work by scraping pages rather than going through official access, and "I used a scraper to get around Reddit's API" is a weak answer in a project where research method is being graded.

**[Q] Your hand-collected set is tiny. Does it matter?**
It matters disproportionately, in both directions. Those rows survive relevance filtering at 20–28% versus 0.78% for Play Store, and several are the most articulate rows in the corpus. But I found two problems with them, both documented and both consequential — see section 4.

---

## 3. The relevance filter: five iterations

This is the core of the day. The filter separates comments about *deciding to buy* from comments about delivery, refunds, app bugs, and post-purchase satisfaction.

| Version | Change | Keep rate | Why it was rejected |
|---|---|---|---|
| v1 | Base prompt, batch 40 | 26.11% | Hand-check found ~87% false positives on Play Store — keyword matching, not intent |
| v2 | Batch 20, "already purchased = NO" rule | 10.12% | ~40% of kept YouTube rows were pure link requests |
| v3 pilot | Link-request and praise exclusions | 16% (YT) | Still keeping fragments too short to code |
| v3 final | 40-character pre-API length floor | 7.50% | Precision ~80% on pilot. Ran on full corpus. |
| v4 | Same, applied to expanded corpus | 7.50% | Hand-check found **both** false positives and false negatives |
| v5 | Narrowed post-purchase rule + four new exclusions | running | Current |

**[Q] Walk me through how you knew v1 was wrong.**
I extracted 15 kept Play Store rows and read them. Thirteen should have been rejected — things like "nice app for purchasing", "Nice fit, excellent Quality", "Varieties to choose from", "original product only". The pattern was obvious once I looked: the filter was keeping anything containing a shopping-adjacent word — *variety*, *choose*, *fit*, *quality* — regardless of whether a decision was being described. It was doing keyword matching dressed up as classification.

**[Q] What caused that, mechanically?**
Batch size. The pilot at 20 comments per API call classified these correctly; the full run at 40 did not. With more items per call the model gets shallower per item and falls back on surface cues. I reverted to 20 and tightened the prompt with an explicit rule: if the person has already bought and received the item, the answer is NO regardless of what they say about it.

**[Q] Then what went wrong at v2?**
I read 15 kept YouTube rows. Six were pure requests for a purchase link — "link please", "I like the blue, link?", "second kurta link". They express interest but contain no decision content, so there is nothing to code. The filter was right by its own instructions: my prompt said YES to "explicitly describing a purchase not yet made", and a link request qualifies. The rule was mine, not the model's.

**[Q] And v3?**
Adding the link exclusion helped, but a third read showed the filter was keeping fragments too short to carry a codeable blocker — "Price kay rahega", "What about shortss", "First wala order karna hai". Rather than write a fourth prompt, I added a structural fix: a 40-character minimum applied *before* the API call. That removed ~48% of the corpus without spending a single request, and pilot precision came out around 80%.

**[Q] Why a length floor rather than another prompt change?**
Because the problem was not classification, it was the material. YouTube comments are mostly very short, and a two-word comment cannot contain reasoning no matter how well it is classified. Prompt tuning was chasing a data property. I had also iterated three times by then, and each round fixed one failure mode and revealed another — that pattern usually means the fix is in the wrong layer.

---

## 4. The two biases I found in my own research

**[Q] Did you find any problems with your own method?**
Two, both recorded before the affected data entered the corpus.

**Search-term bias.** My initial hand-collection search terms were heavily weighted toward size and fit — which matches the hypothesis I had already stated I expected to win. Since hand-collected rows survive filtering at close to 100%, they are the most influential rows per unit of effort, so this would have inflated confidence-type blockers in the final counts. Approximate split of the 86 collected rows: fit and fabric ~45, price-watching ~10, bookmarking ~6, comparison ~4, occasion **zero**. I rebalanced the search terms across all three hypotheses plus neutral framings and added corrective collection.

**Consequence, stated in my notes:** the hand-collected set cannot be used to compare hypothesis strength. It is treated as depth material for mechanism and workarounds only. All percentages and opportunity scores are computed on the automated corpus, where topic selection was not driven by my prior.

**[Q] That is a significant admission. Why volunteer it?**
Because the alternative is a number I cannot defend. If fit ranks first partly because I searched for fit, the ranking is an artefact of my method, not a finding. The separation — hand-collected for mechanism, automated for counts — is a defensible methodological position. Quietly counting both would not be.

**Content contamination.** Reading the hand-collected set, I found rows that were not user conversation at all: SEO listicles ("Mastering Fashion: Tips and Tricks"), affiliate roundups of blouse retailers, e-commerce marketing copy defining what a wishlist is, and industry commentary on sizing technology. Eleven rows removed, 75 retained. The criterion I applied: the text must report the author's own shopping behaviour, not describe or advise on shopping behaviour in general.

**[Q] Why does that distinction matter?**
Because a copywriter describing what shoppers supposedly do is not a shopper. If one of those rows had contributed a fit-blocker count, I would have been counting marketing copy as user signal.

---

## 5. The false-negative check, and what it found

Four rounds of tuning all pushed in one direction: stricter. Play Store fell from 17.24% to 0.78%. I had never once looked at what was being discarded.

**[Q] How did you check for false negatives?**
By using a set where I already knew the answer. I had hand-picked 74 rows specifically because they were relevant. The filter rejected 57 of them. I read all 57.

**Result: roughly 20 of the 57 were genuinely relevant**, including several of the strongest rows in the corpus:

- *"Size charts said I was a 0. I ended up with a size 6. Why even have a size chart at this point?"*
- *"I ordered a few items during the recent Myntra EORS, and despite all of them being size M, each one fit differently."*
- *"Why don't apps like myntra have a length section? I need 40 inch bust with 24 inch length."*
- *"Women's clothing sizes are not standardized and it suuuucks."*

**[Q] Why did the filter reject those?**
My own rule caused it. I had written "answer NO to any review of an item already purchased and received". Every one of those comments mentions a past purchase — but the point is not the purchase, it is the *general conclusion drawn from it*. "I no longer trust size charts" is a durable belief that shapes every future decision. The rule could not distinguish "the shirt was nice" from "I have stopped believing the information you give me."

**[Q] And the fix?**
I replaced the blunt rule with a test: is the person describing *this item*, or describing *a rule they now follow*? Item only is NO. Rule or belief is YES. I also ran a separate precision check on the newest YouTube batch first, which found the opposite problem — roughly 60% of kept rows were review requests, platform questions, or general anti-consumption advice. So v5 fixes both directions at once. Loosening recall without tightening precision would have made the corpus worse while appearing to improve it.

**[Q] Why check precision before applying the recall fix?**
Because the recall fix loosens the filter. If precision was already weak, loosening would degrade it further and the two effects would be impossible to separate afterwards. Order matters when two corrections push opposite ways.

---

## 6. What broke today

| Failure | What happened | Resolution |
|---|---|---|
| **Pilot sampled wrong** | First relevance pilot took the first 100 rows, all Play Store — the least relevant source. Result was 2%, unrepresentative. | Switched to a stratified sample across sources, seed 42 |
| **`gemini-3.6-flash` unusable** | Free-tier cap of **20 requests per day**, verbatim from the 429 error. 21 batches exhausted a full day. | Switched to `gemini-3.5-flash-lite` |
| **Daily quota, 500 requests** | Confirmed verbatim: `quotaId GenerateRequestsPerDayPerProjectPerModel-FreeTier`, `quotaValue 500`. Consumed across five filter runs plus four pilots. | Checkpointing every batch; runs resume rather than restart |
| **All-or-nothing batch errors** | One malformed response marked all 20 rows in a batch as ERROR — 440 rows lost in one run. | Granular parser: only missing item numbers marked ERROR |
| **Agent lost track of a killed process** | Agent backgrounded a script, I killed it with Ctrl+C, agent waited indefinitely on a dead process and blocked the task queue. | Instructed foreground execution and explicit process-state notes |
| **Wrong Python interpreter** | Agent ran scripts with system Python 3.11 rather than the venv. | Explicit `.venv/Scripts/python.exe` in every task |
| **Seller videos in the corpus** | Two YouTube videos about *starting a clothing business* contributed 378 comments from aspiring sellers, not shoppers. Search term `myntra shopping mistakes` matched loosely. | Dropped both video IDs before classification, saving API calls |
| **SEO rows survived deletion** | One affiliate listicle was still present after the cleaning pass, found later in the rejected-rows review. | Re-verified all removals by string search |

**[Q] You hit API quota limits repeatedly. What did you learn from that?**
Two concrete numbers, both taken verbatim from Google's error responses rather than from documentation: `gemini-3.6-flash` allows 20 requests per day on the free tier, and `gemini-3.5-flash-lite` allows 500, per project per model. That second limit shaped the whole day's architecture — batching, checkpointing every batch, resumable runs, and a hard stop on per-day errors rather than a retry loop, because waiting cannot clear a daily quota. It also carries into the MVP: a deployed prototype on a free-tier key needs a cache and a demo-mode fallback, or grader traffic will exhaust it.

**[Q] I notice you used a second Google Cloud project to get more quota. Explain that.**
Quota is enforced per project per model. The first project's 500 requests were consumed by the filter iterations, so I created a second project to finish the run the same day. The model was held constant at `gemini-3.5-flash-lite` across both, so classification behaviour is identical — only the quota pool differs. I considered waiting for the daily reset instead, which would have cost about eighteen hours and no schedule slack. It is recorded in my artefacts file either way.

---

## 7. Findings that emerged from the raw data

These arrived unprompted, before any coding, and three of them are not covered by my original hypotheses.

**1. Play Store is the wrong place to look.** 4,496 reviews yielded 35 relevant comments — 0.78%. People rate the app, the delivery and the service. Almost nobody writes about the garment they decided not to buy. This confirms a bias I predicted in writing on Day 0 before collecting anything: public comments over-represent loud post-purchase grievance and under-represent quiet pre-purchase hesitation.

**2. The wishlist is being used as a price-monitoring tool.** Multiple independent commenters describe the same routine: save the item, then check at midnight during sale windows. One describes monitoring a 5–10 minute window at the start of an end-of-season sale. Out of scope by constraint — the brief forbids monetary solutions — but it must be measured, because it directly lowers the realistic ceiling on the metric.

**3. Some users believe wishlisting *raises* prices, and avoid the feature because of it.** Three separate comments claim items became more expensive after being saved. One states the workaround plainly: save the link externally and check back manually. This is a trust blocker on the wishlist feature itself. It appears in neither my hypotheses nor the seed codebook.

**4. A user complained that a 70-item wishlist cap was too small**, citing other sites allowing 1,000+ saves. That is not a user saving with 30-day purchase intent. It suggests a heavy-saver segment treating the wishlist as a catalogue.

**5. The dominant workaround is try-offline-then-buy-online.** Stated repeatedly: go to a physical store, try things on, note the sizes and brands, then order online during a sale. Alongside it: *"I always look at the size charts, but the number of times they have been extremely off is laughable."*

**6. One comment describes a complete non-purchase decision** with a reason outside all three hypotheses: intent to buy a camisole, mentally testing it against the existing wardrobe, recalling a similar item bought a year earlier and never worn, and deciding against it. The blocker is anticipated non-use based on a remembered failure.

**[Q] Which of these changes your plan?**
Finding 1 changed my collection strategy mid-day — I stopped adding Play Store data and went back for more YouTube. Findings 3 and 6 are candidate codes the seed codebook would have caused me to miss, which is why the codebook is being built bottom-up from open coding rather than adopted from a template. Finding 2 is measured and then explicitly excluded, because acting on it would breach the no-monetary-incentive constraint.

---

## 8. Where the numbers stand

**Relevant corpus (v4, before the v5 correction): 665 comments**

| Source | Total | Relevant | Keep rate |
|---|---|---|---|
| YouTube | 4,291 | 617 | 14.38% |
| Play Store | 4,496 | 31 | 0.69% |
| Quora | 25 | 7 | 28.00% |
| Reddit | 49 | 10 | 20.41% |

**[Q] Your corpus is 93% YouTube. Is that a problem?**
It is a limitation and it will be stated as one. It is also the honest consequence of measuring rather than assuming: I collected Play Store data first because it looked like the obvious source, then measured its relevance at under 1% and reallocated. A corpus weighted toward the source that actually contains pre-purchase discussion is better than one weighted toward the source with the most rows. The trade-off is that YouTube comments skew toward whatever the video was about, which is why video selection was balanced across hypotheses in the second collection round.

**[Q] Only 665 relevant comments from 8,861. Doesn't that undermine the engine?**
The opposite. A filter that keeps 80% is not filtering. The rejection rate is a credibility figure: it means the engine distinguishes comments about deciding from comments about delivery, and I verified that distinction by hand at five separate stages. What would undermine the engine is 1,585 rows where 80% are noise — which is exactly what v1 produced, and why I did not use it.

---

## 9. Method decisions worth defending

**The classifier is a script, not a chat.** Temperature 0, fixed batch size, checkpointed every batch, one model held constant throughout. This is what makes the counts reproducible and makes a human agreement score computable. Asking an AI assistant to "read these and tell me the themes" would produce numbers that cannot be audited or reproduced.

**Corpus text is never pasted into the coding agent.** The agent writes scripts that read the CSV; it does not see the contents. Thousands of comments written by strangers are untrusted input, and the agent has terminal access.

**Five filter versions preserved, not overwritten.** `clean_v1` through `clean_v5` all exist, alongside the spot-check extracts and the manual notes at each stage. The audit trail is the evidence that the final keep rate was arrived at rather than chosen.

**[Q] Isn't five iterations a sign you did not know what you were doing?**
It is a sign I checked. Each iteration was triggered by reading rows by hand and finding a specific, nameable failure — keyword matching, then link requests, then uncodeable fragments, then a rule of mine that discarded reasoned material. Any of those would have silently corrupted every percentage on the findings slide. The alternative was one pass and a number I could not defend. The cost was about six hours; the alternative cost is a project built on noise.

---

## 10. Artefacts produced today

```
pipeline/collect_playstore.py          Play Store, Myntra, sampled
pipeline/collect_playstore_ajio.py     Play Store, AJIO
pipeline/collect_youtube.py            YouTube batch 1
pipeline/collect_youtube_2.py          YouTube batch 2
pipeline/relevance_filter.py           v5, locked configuration
pipeline/merge_corpus.py               Merge, dedupe, validate

data/raw_all_v2.csv                    8,861 rows, all with URLs
data/clean_v4.csv                      665 relevant comments
data/checkpoint_relevance_v5.csv       In progress
data/spotcheck_*.csv                   Manual verification extracts

notes/first_read.md                    Dated observations and bias notes
artefacts.md                           Every number and link, with provenance
```

**[Q] How do I verify any number in your deck?**
Every figure traces to a file, and every file is either in the repository or listed in `artefacts.md` with the parameters that produced it — model name, temperature, batch size, random seed, date pulled. The seed matters: the Play Store sample used seed 42, so the same 4,000 rows can be regenerated.

---

## 11. The one thing I would do differently

I ran the first relevance pilot on the first 100 rows of the corpus rather than a stratified sample. Because the merge concatenated files in order, that meant testing the filter entirely on Play Store — the least relevant source — and getting a 2% result that told me nothing about YouTube. I caught it and re-piloted across sources, but it cost an hour and produced a number I briefly mistook for a signal.

The general lesson: when a corpus has heterogeneous sources, every sample has to be stratified, and any aggregate figure needs a per-source breakdown next to it or it is not interpretable.
