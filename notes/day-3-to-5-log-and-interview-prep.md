# Days 3–5 — Quantification, the Engine, and the Metric Tree
**21 August 2026 · Graduation Project: Wishlist → Purchase Conversion (Myntra)**

Likely evaluator questions are marked **[Q]** with the answer underneath.

**Summary of the three days:** ranked the opportunity areas and tested whether the ranking survives its own assumptions, caught and excluded one false finding, built and deployed the discovery engine as a public link, read all 20 research responses, and decomposed the business metric into a driver tree with four eliminated branches and a locked segment.

---

## 1. The opportunity score — how it works and what it can claim

**The formula:**

```
Opportunity score = share (%) × average severity × average proximity weight
```

Where share is the code's count divided by rows carrying any blocker, severity is the 1–5 rating averaged across those rows, and proximity weights are low 0.5, medium 1.0, high 1.5.

**[Q] Where does this formula come from? Did you design it?**
It's an adaptation of standard reach-impact-leverage prioritisation — the RICE family. Share is reach, severity is impact, and proximity is leverage on the specific metric being moved. I did not invent the structure; I adapted it to rank qualitative codes rather than solution candidates.

**[Q] RICE is Reach × Impact × Confidence ÷ Effort. Where are your confidence and effort terms?**
Deliberately absent, for different reasons.

Confidence in RICE captures how sure you are that a solution will deliver. I'm ranking *problems*, not solutions, so there is no solution to be confident about yet. Proximity replaces it: how close the blocker sits to the purchase decision, which is the analogous question when the object being ranked is a problem rather than a feature.

Effort is absent because effort belongs to solutions too. A problem doesn't have an effort cost. Adding an effort term at this stage would smuggle a solution assumption into a problem ranking.

**[Q] Why multiplicative rather than additive?**
Because addition lets one strong dimension mask a near-zero one. A blocker appearing in 40% of comments that blocks nobody would still score well under addition. Multiplication requires all three: reach, bite, and closeness to the decision. A zero on any dimension zeroes the score, which is the correct behaviour.

**[Q] What can this number actually claim?**
It is **ordinal, not cardinal.** An opportunity score of 101.25 has no unit and no meaning in isolation — it is a percentage multiplied by two ordinal scales. Only the comparison means anything: 101.25 ranks above 62.25. I never present a score as a magnitude, only as a rank.

**[Q] The proximity weights look arbitrary. Aren't they?**
They are. 0.5, 1.0 and 1.5 have no empirical basis; they encode a belief that closeness to the decision matters, not a measured relationship. Which is why I tested whether the ranking depends on them.

I recomputed the ranking under four weighting schemes: baseline, proximity ignored entirely (all weights 1.0), proximity weighted heavily (0.25 / 1.0 / 2.0), and raw share alone with severity and proximity both discarded.

**BLOCK_SIZE_SELECTION ranks first under all four.** The same three codes hold the top three positions under all four. The ranking is not an artefact of the weighting choice.

**[Q] Is there any caveat to that result?**
Yes, and it's worth stating. Under raw share alone, size selection (22.60%) and listing incomplete (22.26%) are nearly tied. It's severity (3.38 vs 2.62) and proximity (1.33 vs 1.07) that separate them. So the weighting doesn't change *which* codes matter, but it does widen the gap between first and second. I would not claim a clean win on share alone.

**[Q] Both severity and proximity are model-assigned. Doesn't classifier error propagate into the score?**
It does, and that's a real limitation given 36% human-machine agreement. Three mitigations: the ranking is stable across three independent codebook versions; no conclusion rests on a gap smaller than about 3 percentage points; and every finding is cross-checked against primary research collected separately, with only doubly-supported findings reported.

---

## 2. Dual counting — a false finding caught before it reached a slide

**[Q] Talk me through something you found and then discarded.**
`BLOCK_WARDROBE_SATURATION`. During open coding, anticipated non-use and wardrobe saturation together produced about 20 of 124 raw labels, rivalling fit. After the codebook was sharpened, wardrobe saturation nearly tripled from 14 rows to 37 and ranked third by opportunity score.

Then the dual count fired. Every frequency and score was computed twice — once on the full corpus of 682 relevant comments, once excluding rows from anti-consumption and decluttering videos, which made up 196 rows or 29% of the corpus.

`BLOCK_WARDROBE_SATURATION` fell from 37 rows to 4. Share dropped from 9.84% to 1.37%, a swing of 8.47 percentage points, and its rank went from 3rd to 13th. **33 of 37 rows came from videos about buying less.**

Grouped with anticipated non-use, the collapse is larger: 55 rows to 5, a swing of 12.92 points.

**[Q] So what was it?**
An artefact of my own search terms. Three of fifteen terms in my second YouTube collection round pulled decluttering content, and a duration filter I set to favour reasoned comments also favoured that genre. If I had reported it, "wardrobe saturation is the third-largest blocker" would have meant "I searched for videos about buying less and found people worried about buying too much."

**[Q] Why did you set up the dual count in advance rather than after seeing the results?**
Because a check designed after seeing a result is designed to confirm it. The flag threshold — any code moving more than 5 percentage points between the two counts — was written into the artefacts file before the counts were run. Exactly one code tripped it, and it was the one I had predicted would.

Every other code moved less than 2 points, and the top two ranks are identical in both views. The ranking is robust to the exclusion.

---

## 3. Cross-tabs — and recognising when a result is circular

**[Q] How did you find your segment?**
Cross-tabulating the blocker distribution against every available grouping variable and looking for the largest gap rather than the largest number. Most of what came back was unusable, and recognising why mattered more than the numbers.

The largest gaps in the table were things like `information_sought = fabric` correlating with `BLOCK_FABRIC_QUALITY` at +71 percentage points. **That is the same judgement recorded twice by the same model in one pass.** It is an internal consistency check, not a segment gap. Worth one line as exactly that — the classifier's blocker and information-need fields agree on 67–82% of rows — and then out of the segment analysis.

Similarly, `video_context = size_guide` correlating with size selection at +50 points reflects the video's topic, not a user segment.

**[Q] What survived?**
Two things. `INTENT_OCCASION` shows `BLOCK_STYLING` at 56.3% against 7.5% overall, with size selection falling to 6.3% — a genuinely different problem for a different motivation. And comments naming Myntra specifically show *fewer* sizing complaints, 9.1% against 22.6%, consistent with brand-directed comments being grievance rather than deliberation.

**[Q] Your corpus can't segment by user, can it?**
No, and that's an important limitation. Public comments carry no save volume, no purchase history, no demographics. `video_context` segments by content topic; `platform_mentioned` segments by who is being complained about. Neither is a user segment. My guide is explicit that a segment must be defined by behaviour, and the corpus cannot supply that. The segment had to come from the research data, where save volume, conversion history, category mix and price tier are all recorded.

---

## 4. The engine — what it is for and how it will be used

**[Q] What is the discovery engine actually for?**
Three things, in order of weight. It is a deliverable in its own right — the brief asks for a link where the workflow can be tested, not a description of one. It is the evidence base for the findings slides, so a grader can verify any number. And it is the demonstration that this went beyond summarisation and sentiment analysis, which the brief explicitly requires: the method tab carries the funnel, the validation scores and the sensitivity result.

**[Q] Isn't the engine the same thing as your MVP?**
No, and they have different audiences. The engine is a research instrument that answers *why* people don't buy; nobody shopping for a kurta would open it. The MVP is a product that *fixes* the one problem identified. Two links, two audiences, two deliverables. The engine is the argument; the MVP is the conclusion.

**[Q] How would a grader use it?**
Realistically in about three minutes: land on the findings tab, register that there are real counts, maybe read a quote and click one source link, paste something into the live classifier to see whether it works, and read the method tab if thorough. The live classifier is the credibility test — a dashboard of charts could be static, but a classifier that responds to their input proves the pipeline is real.

**[Q] Why does the sidebar have a corpus view toggle?**
Because 29% of the relevant corpus came from anti-consumption videos, and that inflated two codes substantially — wardrobe saturation from 4 rows to 37, rank 13 to rank 3. The toggle lets a grader switch between the full corpus and the corpus with that source removed, and see for themselves that the top-two ranking is identical either way.

It's in the app rather than in a footnote for two reasons. It converts a limitation I would otherwise have to be trusted on into something testable in one click. And it demonstrates that I found my own collection bias before anyone else did, which is a stronger signal than not having the bias.

The excluded view is the default, because that is the view the findings are based on.

---

## 5. Reading the five charts

**Metric cards.** Raw comments collected 8,861. Relevant after filtering 682. Coded rows — 292 in the excluded view, 376 in the full corpus. Top blocker share. The coded-rows figure depends only on the corpus toggle, not on the tab's own filters; that separation had to be fixed as a bug, because a filter selection was silently corrupting a number in the method section.

**Chart 1 — blocker frequency.** Horizontal bars, counts labelled, sorted descending. The top code is orange, everything else dark blue, so the leader is identifiable without relying on colour alone. **The denominator is coded rows, not all relevant rows.** That choice was committed before counting and matters: on coded rows size selection is 22.6% and clears the 13.33% threshold; on all 682 relevant rows it is 10.0% and would not. The threshold baseline was derived on the same basis, so the two are internally consistent — but the denominator is labelled, because a reader will ask.

**Chart 2 — opportunity score scatter.** Share on x, average severity on y, bubble size proportional to opportunity score, quadrant lines at the medians. Size selection sits alone in the top-right: high share, high severity, largest bubble. The chart's purpose is to show that its lead is not a single-dimension artefact. Return friction is the instructive opposite — highest severity of any code at 3.93, but the lowest proximity at 0.61. Acute but distant.

**Chart 3 — co-occurrence heatmap.** Primary blocker against secondary blocker. The "None" column dominates because most comments carry a single identifiable blocker; only 46 of 682 rows have a secondary code. The reading is that these blockers largely appear alone rather than in clusters, which is why the codes can be ranked independently.

**Chart 4 — blocker share by intent.** Restricted to the three intent codes with n≥10, one colour each. Two things to read: occasion savers show styling at 56% where the corpus average is 7.5%, and acquisition-watch savers show listing gaps at 90% with zero size-selection blockers. The tallest bar on the chart is the grey one, and the caption names it, because a caption that points away from the most visually dominant element misleads.

**Chart 5 — intent distribution.** Genuine intent dominates in the corpus, but the smaller codes matter more than their size suggests: price-watching, simulated ownership and acquisition-watch together represent saves that were never going to convert within 30 days. That sets a ceiling on the business metric and belongs in the measurement plan rather than the feature.

---

## 6. The metric decomposition

**The equation:**

```
30-Day Conversion = P(intent genuine)
                  × P(comes back | saved)
                  × P(item viable)
                  × P(doubt resolved | comes back)
                  × P(adds to bag | resolved)
                  × P(pays | in bag)
```

**[Q] Why decompose at all?**
Because one percentage hides six sequential steps, and a solution has to attach to a step. Without the decomposition I could say "conversion is low"; with it I can say which step leaks and, more usefully, which leaks I have chosen not to address.

**[Q] Which branch are you pursuing?**
Decision confidence. Size selection ranks first by opportunity score, has the highest proximity weight of any code at 1.33, and clears the pre-registered magnitude threshold. Independently, 16 of 20 research respondents searched outside the app before deciding, and 19 of 20 could state a specific unanswered question.

**[Q] Your own data says intent quality is the bigger leak. Why aren't you solving that?**
You're right that it's bigger. Only 5 of 20 respondents saved with direct purchase intent — 6 saved for comparison, 6 for an occasion with no near-term deadline, 3 with no intention to buy at all. Several respondents estimate more than half their wishlist consists of items they will never buy.

But intent quality is detectable, not changeable. A feature can classify a save as occasion-driven or inspirational. It cannot convert someone who saved a lehenga as a style reference, because they never wanted it. Acting on that branch improves measurement, not conversion.

**Intent quality is a ceiling, not a lever.** So it doesn't get discarded — it gets relocated into the success metrics as a denominator correction. The realistic ceiling on 30-day conversion is materially below 100%, and any experiment must segment by intent type before its result is interpretable. Otherwise a feature that works for genuine-intent users appears flat when averaged against saves that were never going to convert.

**[Q] Couldn't you nudge intent at the point of saving?**
You could try, and two things argue against it. It adds friction to the one action in the flow that currently has none, and saves are the denominator — so a prompt that reduces saving improves the ratio without improving the business. And the honest levers for converting genuinely low-intent saves are mostly promotional, which the brief forbids.

Whereas decision confidence has a workaround users already perform at their own cost. One respondent spent about 30 minutes scrolling a brand's tagged Instagram photos to find someone of similar height. Absorbing an existing behaviour is a better bet than manufacturing a new one.

**[Q] What about the other branches?**
Each is eliminated with a stated reason. Coming back: Signal, but unmeasurable — revisit behaviour needs platform data I don't have, which is also why kill condition K4 remains untested rather than passed. Item viability: Scope — stock and size availability are supply problems, and while out-of-stock users stay in the denominator, stock isn't a growth lever. Checkout: Signal — return friction ranks 12th of 15 by opportunity score with the lowest proximity weight of any code, and delivery and payment appear almost entirely in post-purchase grievance.

**[Q] Where is your illustrative funnel from?**
Six rates multiplied. One is researched — P(intent genuine) at 55%, from 5 of 20 direct-intent plus 6 of 20 occasion-driven saves. One is partly researched — P(doubt resolved) at 40%, grounded in 19 of 20 holding an unanswered question and 16 of 20 searching externally without resolving it. The other four are stated assumptions, two of which cannot be measured without platform data.

0.55 × 0.60 × 0.85 × 0.40 × 0.75 × 0.85 = **7.15%**

Every figure is labelled illustrative. The baseline is not Myntra's conversion rate and shouldn't be read as an estimate of it.

**[Q] Then what is the point of the model?**
Locating the leak, not sizing it. Intent quality removes 45 of 100 users; doubt resolution removes 22 of the 33 who return, which is the largest proportional drop of any step. Since intent quality is eliminated as a lever, doubt resolution is the largest addressable leak.

**[Q] Your assumptions could be wrong. Doesn't that invalidate the conclusion?**
The absolute number, yes. The conclusion, no — and this is testable. If P(comes back) were 40% rather than 60%, baseline conversion falls from 7.15% to 4.77%. But the relative gain from a 10-point improvement in doubt resolution is **unchanged at +25%**.

That invariance is a property of the multiplicative structure: improving one term from 40% to 50% always produces a 25% relative increase, whatever the other five rates are. So my central claim rests on no invented number at all. Only the absolute conversion figure depends on the assumptions.

---

## 7. The segment

**Users who search outside the app before deciding on a saved item.**

**[Q] Why that segment?**
Four reasons, all evidenced.

They have demonstrated intent — leaving the app to research an item is costly and nobody does it for something they don't want. One respondent visited a Zara store specifically to try a size, then ordered online in a different colour, and described this as "slightly ridiculous but it worked."

Their blocker is information, not price. Of the four respondents who searched nowhere, three gave price or need-led answers to what would make them buy. Of the sixteen who did search, the majority gave information-led answers, and three stated unprompted that they did not want a discount — in a question that had already told them to assume constant price.

The behaviour is already happening at scale: 16 of 20 respondents searched externally, and in the corpus 203 of 682 comments are people answering each other's product questions.

And they are addressable without breaching the constraint, because the solution brings inside the product an answer these users are already leaving to find.

**[Q] Is that a behavioural segment or a demographic one?**
Behavioural, and deliberately so. It is defined by an observable action — leaving the app to seek information about a saved item. It contains no reference to age, gender, city or category. The behaviour is also self-selecting for intent, which means the qualification and the signal are the same thing.

**[Q] How large is it?**
I can't size it honestly, and I say so. 16 of 20 in a convenience sample from my own network indicates the behaviour is common, not that it occurs at 80% on the platform. The corpus can't size it either, because a comment doesn't tell you whether its author uses a Myntra wishlist. What the corpus shows is scale: 132 of 682 relevant comments record asking a creator as the workaround.

**[Q] What did you consider and reject?**
Occasion-driven savers — a genuinely distinct segment where styling accounts for 56.3% of blockers against 7.5% overall, and where all 16 corpus rows record a workaround. Rejected on sample size, and because the styling problem needs outfit coordination rather than fit evidence. It is the strongest candidate for a second phase.

Acquisition-watch savers — furthest from purchase, lowest severity at 2.30, lowest proximity at 0.75, and their blocker is catalogue completeness rather than confidence.

Heavy savers — four respondents reported saving more than 25 items in two months, and **all four had converted more than once.** Heavy saving is not a conversion failure in this sample; it's a ratio problem, which is why item-level conversion is a secondary metric rather than a segment.

Price-sensitive savers — measured and reported, then excluded by the brief's prohibition on monetary incentives. A constraint exclusion, not a judgement that the group is small.

---

## 8. The research read, n=20

**[Q] What did the research actually tell you that the corpus couldn't?**
The mechanism. The corpus says size selection is the most frequent blocker. The research says *why* it can't be resolved, and the answer is sharper than "size charts are unreliable."

Respondents describe information that exists but answers a different question than the one they hold. Reviews report appearance on arrival; the decision requires fit on a body like theirs, fabric in use, and durability over time. In their words: "nobody mentions their height, or if they do they're all 5'6+." And: "There are 11 reviews and all of them are about how pretty it looks, not one person says whether they were sweating in it."

**This is a mismatch, not an absence.** Which explains why more information hasn't fixed the problem.

**[Q] Anything that surprised you?**
Five respondents describe a blocker that would be removed by a single artefact — one full-length review photo with the reviewer's height stated, one video, one photograph of a bag with a laptop inside, or two sentences of measurements. Two put it directly: "One photo. That's the entire blocker and it's slightly absurd that it doesn't exist." And: "I'm one nudge away, honestly."

These are not users needing persuasion. They need one fact.

**[Q] Did all four kill conditions hold?**
Three tested and passed, one untestable. K1a — a confidence-type code ranks first by opportunity score. K1b — it clears the 13.33% magnitude threshold at 22.6%. K2 — 19 of 20 respondents stated a specific unanswered question, against a condition that would have fired on vague dissatisfaction. K3 — 16 of 20 searched externally, against a 50% threshold. K4 asks whether most saves are ever revisited, which public comment data cannot answer; it is recorded as untested rather than passed.

---

## 9. What broke, across these three days

| Failure | Cause | Fix |
|---|---|---|
| **pyarrow broken** | Streamlit needs `<25`; an unpinned reinstall pulled 25.0.1 | Pinned `pyarrow<25` in requirements |
| **"undefined" above every chart** | Caption variable passed with no value | Real captions stating each chart's message |
| **Chart 4 colour collision** | Five series, three-colour palette — two pairs shared a colour | Restricted to three intents with n≥10 |
| **Material icon names as text** | Font-family override included `button`; Streamlit's sidebar control is a button whose arrow is a Material Icons ligature | Removed `button` from the selector |
| **Invisible sidebar text in dark mode** | CSS assumed a light background | Pinned light theme in `.streamlit/config.toml` |
| **Deployed app crashed on import** | `google-genai` missing from requirements; installed locally by hand on Day 0 and the file edit never stuck | Rewrote requirements, removed stale `anthropic` |
| **Tab 4 funnel corrupted by Tab 1 filters** | Method-section metric read from the filtered dataframe | Decoupled from tab filters |
| **Fabricated causal claims in the findings file** | Agent supplied plausible mechanisms not present in the data | Deleted; replaced with measured figures only |

**[Q] Which of these is most instructive?**
The missing `google-genai` requirement, because it was invisible locally. The package was installed by hand, so the app worked on my machine and failed the moment it ran anywhere else. It only surfaced because I deployed an empty shell early and then deployed again with real content. Deploying twice is what caught it.

**[Q] You mentioned fabricated causal claims. Explain.**
The agent writing my findings file produced sentences like "users rarely express active fabric concerns at the final decision point, instead relying on general reviews or simply buying and returning the item." Plausible, readable, and entirely unsupported — I never measured when concerns arise relative to the decision, nor whether buy-and-return is a fabric strategy.

I removed every such claim and replaced each with the measured comparison only: this code ranks lower because its share is 10.62% against 22.60%, its severity 2.74 against 3.38, its proximity 0.90 against 1.33. Less readable, defensible.

The general rule I now give the agent: state measured relationships only, and never supply a mechanism the data doesn't contain.

**[Q] Anything you got wrong in your own analysis?**
Yes. When counting behaviours from free-text responses, I initially used keyword matching — counting any mention of "review" in an answer, for instance. That inflated several counts, because it counted people saying they *read* reviews as if they'd said reviews *failed* them. Reading each response individually gave materially different numbers.

The lesson is that free-text behaviour counts require a stated counting rule and a list of which respondents were counted, so the boundary decisions are visible. Structured-field counts — checkboxes, single-selects — need none of that, and those are the counts I lead with.

---

## 10. Artefacts produced

```
research/ai_findings.md            Six findings, limitations, exclusions
research/decomposition.md          Metric, tree, elimination, funnel, segment
research/validation.md             Agreement scores and diagnosis
data/opportunity_scores.csv        Dual-counted, full and excluded
data/sensitivity_check.csv         Four weighting schemes
data/cross_tabs.csv                Blocker against six variables
data/gap_table.csv                 Ranked gaps, min group size 15
data/evidence.csv                  Quotes with source URLs
data/intent_blocker.csv            Blocker profile by intent code
app.py                             Four-tab engine, deployed
.streamlit/config.toml             Pinned light theme
```

**Deliverable 1 is live:** a public Streamlit link, four tabs, verified on desktop and mobile in a private window, no login, with a demo-mode fallback so a grader never sees a traceback.

---

## 11. The two things I would raise unprompted

**The corpus is 93% YouTube.** Play Store contributed half the raw rows and 0.65% of the relevant ones. That's a real limitation, and it's also the honest consequence of measuring rather than assuming: I collected Play Store first because it looked like the obvious source, measured its relevance, and reallocated collection effort to where the pre-purchase discussion actually lives.

**One blocker code is contaminated.** `BLOCK_DURABILITY_VALUE` is absorbing general price complaints — four of its five highest-severity quotes are about prices rising rather than durability. It sits at rank 5, outside the top two the analysis rests on, and the codebook was frozen before counting, so I reported it as a limitation rather than reopening the codebook. The consequence is that durability is overstated and price-watching understated, and I'd rather state that than have it found.
