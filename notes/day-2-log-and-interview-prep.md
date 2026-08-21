# Day 2 — Codebook, Classification, and Validation
**20 August 2026 · Graduation Project: Wishlist → Purchase Conversion (Myntra)**

Likely evaluator questions are marked **[Q]** with the answer underneath.

**One-line summary:** built a codebook bottom-up from the data, classified 682 comments three times, hand-labelled 150 rows blind to check the machine, found agreement was poor, diagnosed why, fixed it, and re-measured. Both pre-registered kill conditions on the corpus passed. H1 survives.

---

## 1. Reading the research responses first

Before touching the corpus, I read all 13 form responses and counted two things. This was deliberate: two of my four kill conditions are measured on research data, and I wanted that read before the corpus numbers could influence how I interpreted it.

**K3 — external search.** 9 of 13 respondents looked for information outside the app before deciding. Threshold was 50%. **K3 does not fire.**
Sources named: Google 7, YouTube 5, asked a friend or family member 5, checked another app 5, Reddit 2, Instagram 2, physical store 1.

**K2 — specificity.** 8 of 13 gave a specific, answerable information requirement. **K2 does not fire.**

**[Q] What did the research actually say people needed?**
Not manufacturer information. Evidence from other customers similar to themselves. The phrasing was consistent and unprompted: "someone with a similar body type", "several normal customers", "someone whose judgement I trust", "people who have actually used the bag for a few months", "someone around my height". One respondent reduced it to a single sentence: if someone in the reviews posted a full-length photo and mentioned they were around my height, that's genuinely it.

**[Q] That sounds like it refines your hypothesis rather than confirming it.**
It does, and that is the more useful outcome. H1 as I wrote it says the user cannot answer one question about the item. The data says something sharper: they cannot find a person similar enough to themselves whose experience is credible. That is a similarity-qualified social proof gap, not a generic information gap. A size chart does not solve it. Surfacing reviews from people matching the user's body, height and use case does. That distinction changes what gets built.

**[Q] Did anyone say they just wanted a discount?**
5 of 13 gave price-related answers, which is measured and reported. More interesting: **3 respondents explicitly said they did not need a lower price**, unprompted, in a question that already instructed them to assume the price stays constant. "I don't necessarily need a lower price." "I don't need a discount; I just want to know that it's the right type of shoe." That is direct support for a non-monetary solution, volunteered rather than elicited.

---

## 2. Building the codebook bottom-up

**Process:** 200 rows sampled from the relevant corpus (seed 55, stratified by source). The model was asked, for each comment, what the person is unable to resolve, and to invent a short label for it. No predefined category list was supplied and no hypothesis was mentioned in the prompt.

**Result:** 124 unique invented labels, every one at frequency 1. The merging into codes was human work.

**[Q] Why not start from a template list of categories?**
Because I would only ever have found what the template's author expected. Three things in my final codebook are absent from the seed list in my own execution guide: distrust that the wishlist itself raises prices, the wishlist as a deferral tool that increases desire rather than dampening it, and anticipated non-use based on a remembered unworn purchase. None of those would have surfaced top-down. I used the seed list only as a gap check after building my own.

**Final codebook:** 15 blocker codes, 6 intent codes, plus a `role` field. Each code carries a definition, a use-when rule, a do-not-use-when rule, and an example.

**[Q] Walk me through one non-obvious decision.**
I split fit four ways rather than keeping it as one code: size selection, chart unreliability, body projection, and listing incompleteness. Each implies a different product response. Missing chart data means adding a field. Chart distrust means surfacing peer evidence instead of manufacturer data. Body projection means showing people of similar build. Size selection means a recommender. A single combined "fit" code would have produced a large number pointing at nothing buildable.

The cost was real: splitting reduced each part, creating a live risk that no single fit code would clear my own magnitude threshold. I made the split knowing it worked against the hypothesis I expected to win.

**[Q] Anything you added because of testing?**
Two things, from hand-testing the draft codebook on 20 fresh rows not in the open-coding sample. One row described maintaining a list of wanted items and watching for them to turn up while thrifting — not a blocker, not price-watching, not any existing intent code. That became `INTENT_ACQUISITION_WATCH`. Another row was someone answering a stranger's sizing question rather than asking one. That became the `role` field, `seeking` or `advising`, because peer advice is the resolution mechanism and it should be counted without polluting the blocker distribution.

---

## 3. The threshold, set before counting

**[Q] How do I know you didn't pick a threshold that your favoured hypothesis would clear?**
Because the threshold is a formula, written before any data existed, and its value was computed and recorded the moment the codebook was frozen — before the classifier ran.

The formula, from my Day 0 brief: baseline = 100% ÷ number of blocker codes; threshold = 2 × baseline. With 15 blocker codes that is 6.67% and 13.33%. Both figures are in the frozen `codebook.json` and in `artefacts.md`, timestamped before the first classification run.

**[Q] Why 2× the baseline?**
Because ranking first is not sufficient. With 15 codes, an even spread gives each code 6.67% from nothing at all. A code leading a flat distribution by one or two points is not a mandate to build and could reverse on a different sample. Doubling the baseline is the bar I set for a theme being dominant rather than merely present.

**[Q] You also split "confidence" across six codes. Doesn't that let you group them to guarantee a win?**
That is exactly the loophole I closed in advance, and it is recorded in the codebook. Grouping six of fifteen codes as "my hypothesis" would make the test nearly impossible to fail, which defeats the purpose of writing a kill condition. So the resolution, recorded before counting: **the rank test is evaluated at individual code level, not group level.** Group shares are reported alongside, clearly labelled as grouped, and are not used to decide whether the hypothesis survives.

---

## 4. The classifier

**Configuration:** one model held constant, temperature 0, batches of 20, checkpointed every batch, definitions read verbatim from the frozen codebook rather than paraphrased into the prompt.

**Hard rules in the system prompt:** use only what the text says; return null rather than guessing; never invent a code name; evidence quote under 12 words and verbatim.

**[Q] How did you handle hallucination?**
Three layers. Temperature 0 for determinism. A null-rather-than-guess rule. And a **post-hoc deterministic check** rather than trusting the model to comply: after classification, every evidence quote is tested as a contiguous substring of its source text after whitespace normalisation. Any quote that fails is set to null and flagged.

That check caught a real failure. One pilot row had merged two non-contiguous sentences from different parts of a comment into a single quote that read as continuous speech. Both fragments were genuine; the combination was fabricated. Across the full corpus, **26 of 682 quotes failed the check and were discarded — 3.8%.** That is a measured hallucination rate on a specific failure mode, not an assertion that the model behaves well.

**[Q] Why a post-hoc check rather than a better prompt?**
Because a prompt instruction is a request and a substring test is a guarantee. The check catches every instance rather than most, and it produces a number I can put on a slide.

**[Q] Any data integrity issues?**
Two, both recorded. One row failed JSON parsing because the source comment contained nested double quotes. It was re-sent individually with the quote marks sanitised, same prompt and temperature; the label is the model's output, not hand-assigned. One row returned a code name with a casing deviation from the frozen codebook, corrected to match. Across 682 rows there were zero invented code names.

**[Q] Is the classifier deterministic?**
Not entirely, and this is worth stating. Two pilot runs on the same 100-row sample at temperature 0 produced slightly different distributions — one code moved from 6 to 9, another from 7 to 5. Temperature 0 reduces but does not eliminate variance. The operational consequence, which I applied throughout: **no conclusion rests on a difference of less than about 3 percentage points between codes.**

---

## 5. Validation — the part that went badly, and what it found

**Method:** 100 rows (seed 99) then 50 fresh rows (seed 202), hand-labelled by me, blind. No machine labels visible, no video-source information visible, codebook definitions only.

**[Q] Why hide the video source as well as the labels?**
Because knowing a comment came from a decluttering video would nudge me toward the wardrobe-saturation code. Blind has to mean blind on everything that could steer the rater.

### The results

| Codebook version | Sample | Agreement | Cohen's kappa |
|---|---|---|---|
| v1.0 | n=100 | 49% | 0.409 |
| v1.0 | n=50 | 32% | 0.256 |
| v1.1 | n=50 | 28% | 0.205 |
| v1.2 | n=50 | 36% | 0.289 |
| v1.2, excluding 16 structurally disputed rows | n=34 | **52.9%** | — |

**The bar is 70% agreement and kappa above 0.6. This fails it.**

**[Q] So your classifier does not work?**
That is not what the data says, and the distinction matters. Disagreement was not spread across the taxonomy — it was concentrated in **one construct**. On 16 of 50 rows I coded social validation, because the person was delegating the decision to a trusted creator. The machine coded the substantive uncertainty underneath: size, fabric, styling.

Both readings are defensible. **The codebook conflated two dimensions:** what the user cannot resolve, and how they are trying to resolve it. A human labelling the resolution mechanism and a machine labelling the uncertainty will disagree on the code while agreeing on the substance.

**[Q] How do you know that is the explanation and not just a broken classifier?**
Because I tested it. Version 1.2 separated the dimensions: substantive uncertainty stays in `primary_blocker`, delegation moves to `external_workaround` with `creator` added as a permitted value. After that change, **11 of the 16 disputed rows carry `external_workaround = "creator"`.** The classifier was detecting the behaviour all along and filing it in a different column.

And the arithmetic confirms the concentration: excluding those 16 rows, agreement is 52.9%. The entire gap is one construct.

**[Q] Version 1.1 made things worse. Why?**
Because I tried to fix it by widening the social validation definition, which was the wrong layer. You cannot sharpen your way out of a category error. Agreement fell from 32% to 28%. That failure is what told me the problem was structural rather than definitional, and it is why v1.2 restructured rather than reworded.

**[Q] What do you actually claim, then?**
That reported blocker shares are **indicative, not precise**, with three mitigations. First, no conclusion rests on a gap smaller than about 3 percentage points. Second, the ranking of the top three codes was stable across all three codebook versions, so the headline finding does not depend on which version is used. Third, every finding is cross-checked against primary research, and only findings supported by both sources are reported.

**[Q] Would you do anything differently?**
Yes — I would have modelled the two dimensions separately from the start. In hindsight the signal was there in my own research: respondents described both *what* they could not resolve and *who* they would ask. I built a taxonomy that could only capture the first.

I have also sent 30 of the same rows to a second independent rater, because single-rater validation cannot distinguish codebook ambiguity from rater idiosyncrasy. That is 30 minutes of someone else's time and it converts a stated limitation into a measured one.

---

## 6. Both corpus kill conditions passed

On coded rows (n=376 in v1.2), as pre-committed:

| Code | Share |
|---|---|
| **BLOCK_SIZE_SELECTION** | **18.1%** |
| BLOCK_LISTING_INCOMPLETE | 18.6% |
| BLOCK_FABRIC_QUALITY | 9.0% |
| BLOCK_WARDROBE_SATURATION | 9.8% |

Stability of the top three across versions:

| Code | v1.0 | v1.1 | v1.2 |
|---|---|---|---|
| BLOCK_SIZE_SELECTION | 80 | 68 | 68 |
| BLOCK_LISTING_INCOMPLETE | 65 | 59 | 70 |
| BLOCK_FABRIC_QUALITY | 63 | 45 | 34 |

**Rank test:** a confidence-type code ranks first. Does not fire.
**Magnitude test:** clears the 13.33% threshold. Does not fire.
**H1 survives**, on the corpus and on the research data independently.

**[Q] Your denominator is coded rows, not all relevant rows. Isn't that convenient?**
It is the denominator I committed to before counting, and the baseline was derived on the same basis, so it is internally consistent. But the choice matters and I state it: on coded rows size selection is 18.1% and clears the bar; on all 682 relevant rows it is 10.0% and would not. Anyone reading the findings slide should know which denominator is in use, so it is labelled.

**[Q] One kill condition you have not tested.**
K4, which asks whether most saves are ever revisited. Public comments cannot answer that — revisit behaviour is platform data I do not have. It is recorded as untested rather than presented as passed.

---

## 7. Findings the classification produced

**1. 203 of 682 comments are people advising others**, not describing their own problem. That is 30% of the relevant corpus being peer-to-peer help. It is direct evidence at scale for the workaround the research described, and it is only visible because the `role` field was added after hand-testing the codebook.

**2. Intent is not uniformly genuine.** 364 genuine, 26 occasion, 22 price-watching, 21 inspiration, 17 acquisition-watch, 9 simulated ownership. Roughly 13% of coded intent is a mode that was never going to convert on this platform within 30 days. That lowers the realistic ceiling on the business metric and means the denominator needs segmenting before any experiment result is judged.

**3. Wardrobe saturation nearly tripled** after the definition fix, from 14 rows to 37. No-buy challenges and "I don't know how to stop shopping" are a real blocker rather than noise. Combined with anticipated non-use, the group is 55 rows.

**4. Social validation as a standalone blocker fell to zero** in v1.2 — correctly. It was never a blocker type. It is a resolution mechanism, and it is now counted as one.

**[Q] The wardrobe-saturation finding worries me. Didn't you collect data from anti-shopping videos?**
Yes, and that is exactly the right question. **29% of my relevant corpus comes from anti-consumption and decluttering videos**, the largest single video category, and their comment sections discuss buying less by construction. Three of fifteen search terms in my second collection round pulled that content.

This is documented as a collection bias with a specific mitigation: every frequency, share and opportunity score is computed twice — full corpus at n=682, and excluding anti-consumption rows at n=486 — and reported side by side. A finding that appears only in the full-corpus version is an artefact of my search terms, not a discovery. The corpus composition table goes on the findings slide rather than being buried.

**[Q] One place your corpus and your research disagree.**
Social validation. Asking a friend or family member appears in **5 of 13 research responses** but is almost absent as a standalone blocker in 682 public comments. People do not post publicly that they are waiting for their sister's opinion; they just wait. This is the structural corpus bias I predicted in writing on Day 0 before collecting anything: public comments over-represent loud post-purchase grievance and under-represent quiet pre-purchase hesitation. It is the reason primary research is needed alongside the corpus rather than instead of it.

---

## 8. Artefacts produced today

```
data/codebook.json                v1.2, definitions, use rules, thresholds
data/open_coding_raw.csv          124 invented labels from 200 rows
data/labelled.csv                 v1.0 classification, 682 rows
data/labelled_v2.csv              v1.1 classification
data/labelled_v3.csv              v1.2 classification, current
data/human_label_task.csv         100 rows, hand-labelled blind
data/human_label_50.csv           50 fresh rows, hand-labelled blind
data/rater2_task.csv              30 rows, sent to a second rater
research/validation.md            Agreement scores, diagnosis, limitations
notes/pending_tasks.md            Carry-forward instructions
```

All three classifier versions preserved rather than overwritten. The progression is the evidence that the final numbers were arrived at rather than chosen.

**[Q] Why keep three versions?**
Because the improvement is a claim, and a claim needs evidence. With all three preserved, plus the blind human labels and the disagreement analysis, anyone can verify that agreement went 32% to 28% to 36% and see exactly which rows moved and why.

---

## 9. The one thing I would flag unprompted

My agreement score is 36% against a 70% bar. That is the weakest number in this project and I would rather raise it than have it found.

What I would say about it: the disagreement is concentrated in a single construct, the cause is diagnosed and evidenced rather than guessed, the fix moved 11 of 16 disputed rows into the correct field, the headline ranking is stable across three independent codebook versions, and every reported finding is corroborated by primary research collected separately. A second rater is in progress to test whether the residual gap is codebook ambiguity or my own idiosyncrasy.

What I would not say: that the classifier is reliable. It is reliable enough to rank themes and not precise enough to quantify them tightly, and that is how the findings are presented.
