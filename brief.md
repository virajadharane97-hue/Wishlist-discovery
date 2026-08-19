# Project Brief
*Date written: 18 August 2026*
*Written before any data was collected.*

Product chosen: Myntra

## 1. The business metric

*30-Day Wishlist-to-Purchase Conversion*

Numerator: Users who purchased at least one item they had added to
their wishlist, within 30 days of adding it.

Denominator: Users who added at least one item to their wishlist in
the same period.

Primary metric: user-level conversion, as stated in the brief.
Secondary metric: item-level conversion, which exposes heavy-saver
behaviour that user-level counting hides.

Constraint from the brief: no monetary incentives in the solution.
No discounts, coupons, cashback, points, or price-drop alerts.
"Users wait for a sale" is a valid finding. It can never be my
solution.

## 2. Five definition decisions

*Q1. Do you count users, or items?*

I would count both. A user might save 5 items but purchase only 1.
User-wise it would look like a 100% conversion. Whereas, if we look
at the number of items, the conversion % drops. That is still an
event. So, both. Users will be the primary metric. Items will be
secondary.

**Q2. If a user deletes a saved item, do they stay in the
denominator?**

Yes. Every user who saved at least one item stays in the
denominator, regardless of what happens to the item afterwards.
Deletion is an outcome, not an exit. Excluding deleters would let
the metric improve whenever a user gives up, which is the opposite
of what it should measure — and it would allow a feature to game the
number by encouraging deletion. The deletion itself is useful
signal: it marks a leak, and the reason behind it may surface in
research.

*Q3. User saves a black shirt in size M, buys size L. Same item?*

Yes. Match at product level, not variant level — the user wanted
that shirt and bought that shirt. However, the sizing fit issue
gets blindsided in this case. So variant-level data would be needed
separately if fit turns out to be the problem.

**Q4. A purchase on day 34 doesn't count. What does that rule cost
you?**

It is still a conversion but just doesn't fit our 30-day window.
The cost is a bias toward cheap, fast purchases. Slow deliberation
concentrates in higher-priced and occasion items, so a 30-day window
may understate the problem precisely where it is largest.
Mitigation: track median days from save to purchase alongside
conversion, so speed effects stay visible even when the purchase
falls outside the window.

**Q5. The item goes out of stock. Does the user stay in the
denominator?**

Yes. There is a chance the user might wait for it to get restocked.
Going out of stock is an event that can depict failure of conversion
or leakage. These users should be flagged as a separate cohort.
Stock is a supply problem, not a growth problem, so it stays out of
my solution's scope even though it stays in the metric.

## 3. Hypotheses

Written 18 August 2026, before any data was collected.

*H1 — Confidence.* The user wants the item but cannot answer one
question about it: will it fit, is the fabric good, what would I
wear it with. The save carries real intent, blocked by missing
information.
→ If true, build: a helper that answers that one question using
real review evidence.

*H2 — Choice.* The user saved several similar items and cannot
decide between them. Real intent, blocked by comparison difficulty.
→ If true, build: a comparison and shortlist tool.

*H3 — Timing.* The user has no event, no deadline, and no reason
to come back today. Real intent, with no trigger.
→ If true, build: an occasion planner that brings the user back
with a reason, never with a price.

*H0 — Bookmark.* Some share of saves never carried purchase intent
at all. Not a problem to solve, but it must be measured, because it
changes the denominator and therefore the realistic ceiling on the
metric.

*My prior, recorded before any data:* I expect H1 to be strongest,
based on personal experience and on the trade-offs I identified in
the five definition decisions above — particularly Q3, where
size-switching behaviour suggests fit is a live problem. I am
recording this so I can check later whether the data changed my
mind, or whether I steered the data toward what I already believed.

*Two additional propositions, not competing hypotheses:*

*P1 — Revisit is a precondition, not a blocker.* Users who re-open
their wishlist convert at a higher rate than those who do not. This
sits upstream of H1, H2 and H3: a user who never returns never
reaches the point of being blocked. If the data shows that most
saves are never revisited, the confidence, choice and timing
explanations all become secondary to a re-entry problem. To be
checked early.

*P2 — Intent may be detectable at the point of saving.* H0 says
some saves carry no purchase intent. The stronger version is that
intent type can be inferred at save time — occasion, comparison,
inspiration, price-watch. If so, the realistic ceiling on the metric
is lower than 100%, and the denominator needs segmenting before any
result is judged.

*Out of scope by constraint:* Price-sensitive saving is likely a
large share of wishlist behaviour. I will measure and report it as
INTENT_PRICE_WATCH, but the brief forbids monetary incentives, so it
cannot become my solution. Measured, reported, excluded.

## 4. Kill conditions

These conditions were written before any data was collected. The
ordering matters: hypotheses first, thresholds second, counting
third. Setting a threshold after seeing the counts would make it
meaningless.

*K1a — Rank.* H1 dies if confidence-type blockers (fit, fabric,
styling, body projection, or their equivalents in my final codebook)
do not rank first by opportunity score.

*K1b — Magnitude.* H1 dies if confidence-type blockers fall below
2x the even-distribution baseline, even if they rank first.

Baseline = 100% divided by the number of blocker codes in the frozen
codebook. The codebook is built bottom-up from open coding, so the
code count is not known at the time of writing. Worked examples: 9
blocker codes gives a baseline of 11.1% and a threshold of 22%; 12
blocker codes gives 8.3% and a threshold of 17%.

The exact threshold will be computed and recorded once the codebook
is frozen, and before any counting begins.

Rationale: ranking first is not sufficient. A theme leading a flat
distribution by one or two points is not a mandate to build, and
could reverse on a different sample.

*K2 — Specificity.* H1 dies if respondents who say they are unsure
about a saved item cannot state a specific unanswered question when
asked directly. Vague dissatisfaction ("just not sure", "didn't feel
like it") is not an information gap. Concrete questions ("will this
be see-through", "is the length short on someone my height") are.
Measured on form question 11.

*K3 — External search.* H1 dies if fewer than half of respondents
report looking for information outside the app before deciding (form
question 13). If users do not search elsewhere, the unmet
information need H1 depends on is not real, and there is no
workaround for the solution to absorb.

*K4 — Upstream check on P1.* If the data shows that most saves are
never revisited, the problem sits upstream of all three hypotheses.
A helper that answers questions is useless to a user who never
returns. In that case I pursue re-entry, regardless of what the
blocker distribution says.

*Decision rule.* If any two of K1a, K1b, K2 or K3 fire, I abandon
H1 and pursue whichever of H2 or H3 the evidence supports. If K4
fires, it overrides all of them.

## 5. Known limitations, recorded up front

1. *Written research, not conversational.* Primary research is a
structured form, not interviews. Root cause is inferred from staged
questions (Q10 to Q12) rather than live follow-up. Depth is
therefore limited compared to a conversation, and I cannot probe an
unexpected answer.

2. *Convenience sample.* Respondents come from my own network. Not
representative of Myntra's user base. Next step would be a larger
survey with recruited respondents.

3. *No platform data.* I have no access to Myntra's transaction or
behavioural data. Every baseline figure in this project is
illustrative and labelled as such. The prototype can validate
leading indicators only. Causal proof needs a controlled experiment.

4. *Corpus bias.* Public comments over-represent loud
post-purchase grievances (delivery, refunds, quality) and
under-represent quiet pre-purchase hesitation. Wishlist
non-conversion lives almost entirely in the second category. People
post publicly when something went wrong; they stay silent when they
simply did not buy. This is the main reason primary research is
needed alongside the corpus, and it is why I expect the two sources
to disagree.

5. 5. *Reddit API unavailable.* Reddit developer access could not be
obtained on 18 August 2026. Reddit and Quora data are hand-collected
from public pages instead. Corpus composition: Play Store 4,496
rows (5.3% relevance), YouTube 1,567 rows (47.1% relevance),
hand-collected 51 rows (~100% relevance). The hand-collected source
is the smallest but densest, and Play Store contributes the majority
of raw volume while contributing least to the relevant corpus.

6. *Single-rater validation.* The classifier reliability check
compares machine labels against one human rater. A second independent rater would give a stronger agreement estimate.


## 6. Predictions checked against data

*Limitation 4, checked 19 August 2026.* The brief predicted that
public comments would over-represent post-purchase grievance and
under-represent pre-purchase hesitation. Measured relevance rates
after filtering confirm this: Play Store 5.3%, YouTube 47.1%,
hand-collected Reddit/Quora ~100%. Play Store reviews rate the app
and the delivery, not the decision. This was predicted before
collection and measured after, and it is why YouTube carries the
analysis despite contributing only 26% of raw rows.