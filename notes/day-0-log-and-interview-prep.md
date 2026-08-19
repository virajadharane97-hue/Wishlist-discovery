# Day 0 — What I Did, Why, and What Broke
**18 August 2026 · Graduation Project: Wishlist → Purchase Conversion (Myntra)**

Read this before any evaluation conversation. Questions an evaluator is likely to ask are marked **[Q]** with the answer underneath.

---

## 1. Scope decisions made today

### Product: Myntra
Chosen over AJIO and Nykaa Fashion on data availability. Myntra has the largest Play Store review pool and the most YouTube haul/try-on content in India, which matters because the discovery engine needs volume to produce defensible percentages.

**[Q] Why Myntra and not Nykaa Fashion?**
Corpus size. The engine's credibility rests on having enough relevant comments to quantify opportunity areas. Nykaa Fashion has a smaller public footprint, which would have forced a thinner corpus and weaker percentages. The problem I am solving is not Myntra-specific — it applies to any fashion marketplace with a wishlist — but the evidence base is strongest for Myntra.

### Timeline: submit 29 August, buffer 30 August
The brief's stated deadline is 4–5 September (it contradicts itself). I set my own deadline five days earlier so that a broken deployment or a slow research response cannot become a missed submission.

---

## 2. The business metric, defined precisely

**30-Day Wishlist-to-Purchase Conversion**

- **Numerator:** users who purchased at least one item they had added to their wishlist, within 30 days of adding it
- **Denominator:** users who added at least one item to their wishlist in the same period
- **Primary:** user-level conversion (the brief says "percentage of users")
- **Secondary:** item-level conversion, which exposes heavy-saver behaviour that user-level counting hides

**[Q] Why track both user-level and item-level?**
Because they tell opposite stories about the same behaviour. A user who saves 5 items and buys 1 is 100% converted at user level and 20% converted at item level. User level is the stated business metric; item level is the diagnostic that reveals whether heavy savers are being served at all.

### The five disputable definitions

A metric is only real if two people can compute it and get the same number. Five things in that formula are genuinely ambiguous. My decisions:

| Question | Decision | The reason that matters |
|---|---|---|
| Users or items? | Both; users primary | Different denominators, different pictures |
| Deleters stay in denominator? | Yes, always | Otherwise the metric improves when users give up |
| Saved size M, bought L — same item? | Yes, product level | But this hides size-switching, so variant data needed separately |
| Purchase on day 34? | Doesn't count | Biases the metric toward cheap, fast purchases |
| Out of stock? | Stays in, flagged separately | Real leak, but supply problem, out of my scope |

**[Q] Your deletion rule — why not exclude users who delete?**
Because that would make the metric gameable. If deleters leave the denominator, any feature that encourages people to clear their wishlist would raise conversion without a single extra purchase. Deletion is an outcome, not an exit — and it is a strong signal, because it marks a user who considered and rejected.

**[Q] What does the 30-day window cost you?**
It systematically undercounts slow deliberation, and slow deliberation is not randomly distributed — it clusters in higher-priced items and occasion wear. So the window may understate the problem precisely in the segment where it is worst. Mitigation: track median days from save to purchase alongside conversion, so speed effects stay visible.

---

## 3. Hypotheses, dated before any data

| ID | Guess | If true, build |
|---|---|---|
| **H1** | **Confidence** — wants it, can't answer one question (fit, fabric, styling) | Helper that answers that question from real review evidence |
| **H2** | **Choice** — saved several similar items, can't pick | Comparison and shortlist tool |
| **H3** | **Timing** — no event, no deadline, no reason to return | Occasion planner, never a price trigger |
| **H0** | **Bookmark** — some saves never carried intent | Nothing, but must be measured |

Plus two propositions that are *not* competing hypotheses:

- **P1 — Revisit is a precondition, not a blocker.** Sits upstream of all three. A user who never returns never reaches the point of being blocked.
- **P2 — Intent may be detectable at save time.** If so, the realistic ceiling on the metric is below 100% and the denominator needs segmenting.

**Out of scope by constraint:** price-watching is probably a large share of wishlist behaviour. It will be measured and reported as `INTENT_PRICE_WATCH`, then excluded, because the brief forbids monetary incentives.

**[Q] Why is revisit a proposition and not a fourth hypothesis?**
Because it does not compete with the other three — it precedes them. Fit, choice and timing are all explanations of why a *present* user fails to convert. If the user never comes back, none of those explanations gets a chance to apply. Treating it as a rival would have implied the four are alternatives, when three of them depend on the fourth.

**[Q] You wrote that you expect H1 to be strongest. Isn't that bias?**
Yes, and that is exactly why it is written down and dated. Naming the prior before collecting data is the only way to later distinguish "the evidence supported H1" from "I steered the analysis toward what I already believed." The kill conditions below are the mechanism that makes the prior falsifiable.

---

## 4. Kill conditions — the part most submissions skip

Written before any data. **Ordering matters: hypotheses first, thresholds second, counting third.** A threshold set after seeing the counts means nothing.

- **K1a — Rank.** H1 dies if confidence-type blockers do not rank first by opportunity score.
- **K1b — Magnitude.** H1 dies if they fall below 2× the even-distribution baseline, even if they rank first. Baseline = 100% ÷ number of blocker codes in the frozen codebook.
- **K2 — Specificity.** H1 dies if respondents who say they are unsure cannot state a concrete unanswered question.
- **K3 — External search.** H1 dies if fewer than half report searching outside the app before deciding.
- **K4 — Upstream override.** If most saves are never revisited, the problem is re-entry, regardless of blocker distribution. This overrides the others.

**Decision rule:** any two of K1a, K1b, K2, K3 fire → abandon H1. K4 fires → overrides everything.

**[Q] Why is K1b a formula rather than a number?**
Because the number of blocker codes is not known yet — the codebook is built bottom-up from open coding, not taken from a template. Hard-coding a percentage today would mean either guessing, or quietly adjusting it later once the counts were visible. The formula fixes the *logic* now and computes the *value* once the codebook is frozen, which preserves the sequence that makes the threshold honest.

**[Q] Walk me through K1b with real numbers.**
With 9 blocker codes, perfectly even distribution gives each code 11.1%. That is the score a code gets from nothing at all. Doubling it gives a 22% threshold. With 12 codes the baseline is 8.3% and the threshold 17%. The purpose is to reject a result where fit "wins" at 11% against choice at 10% — leading a flat field by one point is not a mandate to build, and could reverse on a different sample.

---

## 5. Primary research: the decision I have to defend

**What the brief asks for:** 5–6 user interviews.
**What I am doing:** a structured written form, targeting 12–15 respondents. ~10 responses in on day one.

**Why:** low confidence that respondents would agree to a call within the available window, and no spare days to absorb cancellations.

**[Q] The brief said interviews. Why did you run a form instead?**
A judgement call, and I know what it costs. A form cannot ask "why" a fifth time when an answer surprises me, so root cause depth is weaker than a conversation would give. I mitigated it three ways: a forced three-layer probe on the same item (what stopped you → what don't you know → why can't you answer it), every question anchored to a specific saved item rather than to general behaviour, and a larger n than the brief requires so patterns are countable. I also added an optional opt-in for a follow-up voice call, so anyone willing can go deeper without being pressured up front. The limitation is stated on the deck rather than hidden.

**[Q] How do you get root cause out of a form?**
By staging it. Q10 asks what stopped you — that returns the symptom. Q11 asks what you still don't know, phrased as the exact question you'd ask — that returns the information gap. Q12 asks why you can't answer it and what you already tried — that returns the cause and the workaround. Three fixed layers instead of adaptive probing. Weaker, but not shallow.

**[Q] Why did you ask people to open the app while filling the form?**
Because recall is unreliable and flattering. "What stops you buying wishlisted items" produces "price and size." "Open your wishlist, look at the item you saved most recently, what is it" produces specifics. Every depth question is anchored to a named item for that reason.

**[Q] Why does Q16 say "assume the price stays the same"?**
Because without that constraint roughly half the answers would be "a discount," and the brief forbids a monetary solution. The helper text forces respondents past the easy answer to the non-price reason underneath.

### A decision I made and would make again
I was offered the option of generating six synthetic interview respondents to fill the gap. I declined. Invented research is the single fastest way to fail this project, and more practically, fabricated answers would only reflect what I already expected — which defeats the entire purpose of Part 3.

---

## 6. Tooling and architecture

**Antigravity IDE, agent-assisted mode.** Chosen because I am not a confident Python developer. The agent writes and debugs scripts; I make the analytical decisions.

**The separation that matters:**

| Job | Who does it | Why |
|---|---|---|
| Write the pipeline | Antigravity agent (Gemini) | Code generation, debugging |
| Classify the corpus | A Python script, temperature 0, batched, checkpointed | Must be reproducible and auditable |

**[Q] You used an AI IDE. Did the AI do your analysis?**
No, and the distinction is deliberate. The agent built the collection and classification scripts. The classification itself runs as a scripted API call at temperature 0, batched and checkpointed, so the same input always produces the same label. If I had asked the agent to "read these comments and tell me the themes," the output would be non-reproducible and I could not have computed an agreement score against it. The validation number is the whole credibility of the engine, and it only exists because the classifier is a script rather than a conversation.

**[Q] What did you do about hallucination risk?**
Three things, all built into the classifier spec: temperature 0 so labels are deterministic; a rule that the model returns `null` rather than guessing when a field is not supported by the text; and an evidence quote capped at 12 words that must be the respondent's exact words. Then a human agreement check on a random sample of 100 rows, labelled blind. The MVP adds a further rule — if fewer than five reviews address a question, it returns "not enough reviews to say" rather than an answer.

### Security decisions
- API keys in `.env`, which is in `.gitignore` and verified ignored before the first commit
- Corpus text is never pasted into the agent chat. The agent writes scripts that read the file; it does not see the contents. Scraped internet text is untrusted input, and the agent has terminal access.

**[Q] Why not paste the review data into the AI assistant directly?**
Two reasons. It would make the analysis non-reproducible. And thousands of comments written by strangers are untrusted input — handing them to an agent that can execute terminal commands is a prompt-injection risk with no upside.

---

## 7. What broke today

An honest log. Every one of these cost time and none of them is hidden.

| Failure | What happened | Resolution |
|---|---|---|
| **Antigravity terminal blocked** | Agent could not execute commands — Windows ACL error on NUL | Ran commands manually; agent still wrote all files |
| **Project inside OneDrive** | Path was under OneDrive with a space in the folder name | Moved to `C:\Nextleap\Wishlist-discovery`. OneDrive corrupts git repos and syncs thousands of venv files |
| **Virtual environment broke after move** | venvs hard-code their creation path; pip pointed at the old OneDrive location | Deleted and rebuilt in place |
| **PowerShell syntax errors** | Commands pasted on one line; backslash lost in copy-paste; `pyhton` typo | Ran commands one at a time, used forward slashes |
| **Anthropic API unaffordable** | Paid-only; no budget | Switched to Gemini free tier via AI Studio. Swapped `anthropic` for `google-genai` |
| **Model name retired** | `gemini-2.5-flash` returned 404 — no longer available to new users | Switched to `gemini-3.6-flash`, confirmed working |
| **Reddit API refused** | Developer registration required, approval not obtainable in the window | Reddit and Quora data hand-collected from public pages. Recorded as a stated limitation |
| **Hand-collection yield low** | Only ~10 relevant Reddit comments found on first pass | Searching for the brand rather than the behaviour. Switched to `site:reddit.com` Google queries on the underlying uncertainty, not on "Myntra" |

**[Q] You lost Reddit. Doesn't that weaken your corpus?**
Yes, and it changes what the corpus is good for. Play Store reviews skew toward post-purchase grievances — delivery, refunds, quality. Reddit is where people write about *deciding*, in full sentences, before buying. Losing the API means my richest source is now hand-collected and small. Two consequences I have accounted for: YouTube comments on haul and try-on videos become the most important automated source, because that is where fit and fabric uncertainty gets discussed; and the corpus-bias limitation in my brief becomes more important, not less. It is stated on the deck.

**[Q] Why is your corpus biased, and what do you do about it?**
People post publicly when something went wrong. Almost nobody posts "I didn't buy the kurta because I couldn't tell if the fabric would be see-through" — that thought produces silence and an item that stays saved. So public comments over-represent loud post-purchase grievances and under-represent quiet pre-purchase hesitation, which is exactly where wishlist non-conversion lives. This is the structural reason primary research is needed alongside the corpus, and it is why I expect the two sources to disagree. I predicted that disagreement in writing before collecting anything.

---

## 8. Limitations I am stating, not hiding

1. Written research, not conversational — root cause inferred from staged questions
2. Convenience sample from my own network — not representative
3. No platform data — every baseline is illustrative; prototype validates leading indicators only
4. Corpus bias toward post-purchase grievance (see above)
5. Reddit API unavailable — hand-collected substitute
6. Single-rater validation — one human rater, not two

**[Q] Your sample is small and from your own network. Why should I believe any of this?**
You shouldn't believe it as a population estimate, and I don't present it as one. The written research establishes *mechanism* — how the problem works, what people already do to cope. The corpus establishes *magnitude* — how often it appears across thousands of comments. Every claim on the deck carries both numbers for that reason. Neither source is sufficient alone, and I state what each one cannot do.

---

## 9. Artefacts produced today

```
brief.md                      metric, definitions, hypotheses, kill conditions, limitations
artefacts.md                  running record of every link and number
requirements.txt              pinned dependencies
.gitignore                    protects .env
data/manual_collected.csv     hand-collected Reddit/Quora rows (in progress)
test_key.py                   API verification
```

Two commits, both timestamped 18 August 2026. The commit history is the evidence that hypotheses and thresholds existed before any data.

**[Q] How do I know you didn't pick your solution first and reverse-engineer the research?**
The git history. `brief.md` was committed on 18 August with three competing hypotheses, a stated prior, and five kill conditions including a threshold formula — before a single row of data was collected. The MVP was not chosen until the problem statement was locked. The sequence is verifiable rather than asserted.

---

## 10. The one-line summary of today

Locked the metric with defensible definitions, wrote three competing hypotheses with falsifiable kill conditions, floated primary research, and got the pipeline environment working — while losing the Reddit API and the paid model, and re-planning around both.
