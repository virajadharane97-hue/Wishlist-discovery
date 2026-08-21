# Wishlist-to-Purchase Conversion Decomposition

## Section 1: The metric

### Numerator
Users who purchased at least one item they had added to their wishlist, within 30 days of adding it.

### Denominator
Users who added at least one item to their wishlist in the same period.

### Five Definition Decisions

#### Q1. Do you count users, or items?
I would count both. A user might save 5 items but purchase only 1.
User-wise it would look like a 100% conversion. Whereas, if we look
at the number of items, the conversion % drops. That is still an
event. So, both. Users will be the primary metric. Items will be
secondary.

#### Q2. If a user deletes a saved item, do they stay in the denominator?
Yes. Every user who saved at least one item stays in the
denominator, regardless of what happens to the item afterwards.
Deletion is an outcome, not an exit. Excluding deleters would let
the metric improve whenever a user gives up, which is the opposite
of what it should measure - and it would allow a feature to game the
number by encouraging deletion. The deletion itself is useful
signal: it marks a leak, and the reason behind it may surface in
research.

#### Q3. User saves a black shirt in size M, buys size L. Same item?
Yes. Match at product level, not variant level - the user wanted
that shirt and bought that shirt. However, the sizing fit issue
gets blindsided in this case. So variant-level data would be needed
separately if fit turns out to be the problem.

#### Q4. A purchase on day 34 doesn't count. What does that rule cost you?
It is still a conversion but just doesn't fit our 30-day window.
The cost is a bias toward cheap, fast purchases. Slow deliberation
concentrates in higher-priced and occasion items, so a 30-day window
may understate the problem precisely where it is largest.
Mitigation: track median days from save to purchase alongside
conversion, so speed effects stay visible even when the purchase
falls outside the window.

#### Q5. The item goes out of stock. Does the user stay in the denominator?
Yes. There is a chance the user might wait for it to get restocked.
Going out of stock is an event that can depict failure of conversion
or leakage. These users should be flagged as a separate cohort.
Stock is a supply problem, not a growth problem, so it stays out of
my solution's scope even though it stays in the metric.

---

## Section 2: The equation

30-Day Conversion = P(intent genuine) x P(comes back | saved) x P(item viable) x P(doubt resolved | comes back) x P(adds to bag | resolved) x P(pays | in bag)

P(event) represents the probability of that specific event or state transition occurring.

---

## Section 3: The five-branch driver tree

### Intent quality
- Purchase intent vs. bookmarking/inspiration
- Occasion-specific saving
- Price-drop monitoring
- Wardrobe/cataloguing habits

### Coming back
- Re-entry triggers and notifications
- Calendar events and trip deadlines
- Wishlist revisit patterns

### Item viability
- Stock availability
- Size availability
- Alternative acquisition channels

### Decision confidence
- Sizing verification (body measurements, size chart reliability, body type projection)
- Material trust (fabric quality, durability, longevity, value for money)
- Product presentation (image and review credibility, social/peer validation)
- Styling appropriateness (occasion coordination, styling recommendations)
- Alternative comparison (shortlisting, deciding between options)

### Checkout
- Return and exchange friction
- Delivery eligibility (PIN code restrictions, delivery times)
- Cart addition and payment processing

---

## Section 4: Evidence attached to branches

| finding | source | branch | figure |
| :--- | :--- | :--- | :--- |
| Intent at save | form Q9, n=20 | intent quality | 25% intended to buy, 30% occasion, 30% comparison, 10% liked not planning, 5% style reference |
| Never-buy items in wishlist | form Q27 | intent quality | estimates range 0 to 30+, several respondents report more than half their list |
| External search before deciding | form Q13 | decision confidence | 16 of 20 (80%) |
| Concrete unanswered question stated | form Q11 | decision confidence | 19 of 20 |
| Size selection is top blocker | engine, excluded corpus n=486 | decision confidence | 22.6% of coded rows, severity 3.38, proximity weight 1.33, opportunity score 101.25, rank 1 under all four weighting schemes |
| Listing incomplete | engine | decision confidence | 22.26% share, second by opportunity score |
| Workaround is asking a trusted person | engine | decision confidence | 26 of 35 stated workarounds on size-selection rows (74.3%) name a creator |
| Peer advising at scale | engine | decision confidence | 203 of 682 comments (29.8%) are people advising others |
| Occasion savers hit styling not sizing | engine | decision confidence | BLOCK_STYLING 56.3% within INTENT_OCCASION versus 7.5% overall, n=16 |
| Acquisition-watch savers hit listing gaps | engine | decision confidence | 90% BLOCK_LISTING_INCOMPLETE, zero size selection, n=10 |

### Terms with no measured evidence

P(comes back | saved) and P(pays | in bag) have no measured figure in this project. Both require platform behavioural data that is not available. They are carried in the equation and left unquantified rather than estimated. This is the same treatment given to kill condition K4, which asks whether most saves are ever revisited and which public comment data cannot answer.

---

## Section 5: Elimination

Decision confidence is the branch pursued. Each branch below is eliminated with a stated reason: Constraint (requires monetary incentive, forbidden by the brief), Scope (not a growth problem), or Signal (the data does not support it as a primary blocker).

### Intent quality — eliminated

Reason: Signal, inverted.

This is measurably the largest leak. Only 5 of 20 respondents saved
with direct purchase intent; 6 saved for comparison and 6 for an
occasion with no near-term deadline. Several respondents estimate
that more than half their wishlist consists of items they will never
buy. One described it as "half shopping list and half reference
folder and the app has no idea which is which."

It is eliminated not because the leak is small, but because intent
quality is detectable rather than changeable. A feature can classify
a save as occasion-driven or inspirational. It cannot convert someone
who saved a lehenga as a style reference, because that user never
intended to buy. Acting on this branch improves measurement, not
conversion.

The finding is therefore relocated rather than discarded: it becomes
a denominator correction in the success metrics. The realistic
ceiling on 30-day conversion is materially below 100%, and any
experiment must segment by intent type before its result is
interpretable — otherwise a feature that works for genuine-intent
users appears flat when averaged against saves that were never going
to convert.

### Coming back — eliminated

Reason: Signal, unmeasurable with available data.

Revisit behaviour requires platform data on session returns, entry
points and time-to-first-revisit. None of this is obtainable from
public comments or a written survey. Kill condition K4 in the project
brief asks whether most saves are ever revisited, and it remains
untested for this reason.

This branch is not dismissed as unimportant. It is upstream of
decision confidence: a user who never returns never reaches the point
of being blocked. It is recorded as an untested precondition and as a
limitation on the eventual result.

### Item viability — eliminated

Reason: Scope.

Stock availability, size availability and catalogue churn are supply
chain problems, not growth problems. The definition decision recorded
in Section 1 Q5 keeps out-of-stock users in the denominator, because
excluding them would hide a real leak, but explicitly places stock
outside the scope of any solution.

Supporting evidence that this is a genuine leak: one respondent
reports a pair of shoes out of stock in their size for months, and
availability questions appear in the corpus. The leak is real. The
lever is not a growth lever.

### Checkout — eliminated

Reason: Signal.

Return friction ranks 12th of 15 blocker codes by opportunity score,
with the lowest proximity weight of any code (0.61) despite the
highest average severity (3.93). It is acute when it occurs but sits
far from the moment a saved item is abandoned. Delivery eligibility
and payment appear in the corpus but almost entirely in post-purchase
grievance rather than pre-purchase hesitation.

The data does not support checkout as the step where wishlisted items
are lost.

---

## Section 6: Illustrative arithmetic
*Illustrative, not platform data.* No figure in this section is
measured against Myntra's systems. Rates grounded in this project's
research are marked (researched); all others are stated assumptions.
The purpose is to locate which step is worth attacking, not to
estimate the size of any effect.

### Baseline funnel, 100 users who save at least one item

| Step | Rate | Users remaining | Basis |
|---|---|---|---|
| Saved at least one item | - | 100.0 | denominator |
| P(intent is genuine) | 55% | 55.0 | (researched) 5 of 20 respondents saved with direct purchase intent, plus 6 of 20 occasion-driven, treated as genuine but slower. Form Q9. |
| P(comes back \| saved) | 60% | 33.0 | assumption. Unmeasured; requires platform data. See Section 5. |
| P(item still viable) | 85% | 28.1 | assumption. In stock, in the user's size, still wanted. |
| P(doubt resolved \| comes back) | 40% | 11.2 | (partly researched) 19 of 20 respondents hold a specific unanswered question and 16 of 20 search outside the app, most without resolving it. Form Q11, Q13. |
| P(adds to bag \| resolved) | 75% | 8.4 | assumption |
| P(pays \| in bag) | 85% | 7.2 | assumption. Unmeasured; requires platform data. |

*Derivation:*
0.55 x 0.60 x 0.85 x 0.40 x 0.75 x 0.85 = *7.15%*

Illustrative baseline conversion: *7.15%*.

### Where the funnel leaks

Two steps account for almost all of the loss.

Intent quality removes 45 of 100 users before any product experience
occurs. Doubt resolution removes 22 of the 33 users who do return -
the single largest proportional drop of any step in the funnel.

Intent quality is eliminated as a lever in Section 5, on the grounds
that it is detectable but not changeable. That leaves doubt
resolution as the largest addressable leak.

### Sensitivity: improving doubt resolution

All other rates held constant.

| P(doubt resolved) | Conversion | Relative change |
|---|---|---|
| 40% (baseline) | 7.15% | - |
| 50% (+10pp) | 8.94% | +25% |
| 60% (+20pp) | 10.73% | +50% |

A 10 percentage point absolute improvement in doubt resolution
produces a 25% relative increase in conversion. This leverage is a
property of the multiplicative structure - a gain on one term
propagates through the whole chain - rather than a claim about the
strength of any particular intervention.

### Why a 10 point improvement is plausible rather than optimistic

Five of 20 respondents describe a blocker that would be removed by a
single artefact: one full-length review photo with the reviewer's
height stated, one video of a real person wearing the item, one
photograph of a bag with a laptop inside it, or two sentences of
measurements from the seller.

Two stated it directly. "One photo. That's the entire blocker and
it's slightly absurd that it doesn't exist." And: "I'm one nudge
away, honestly."

These respondents do not require persuasion, a discount, or a
redesign. They require one specific fact. That is what makes a
double-digit improvement in doubt resolution a reasonable target
rather than an aspirational one.

### Sensitivity to the assumptions

Because the model is multiplicative, the ranking of leaks is more
robust than the absolute output. If P(comes back) were 40% rather
than 60%, baseline conversion falls to 4.77% - but doubt resolution
remains the largest addressable drop, and the relative gain from a
10 point improvement is unchanged at +25%. The conclusion about which
step to attack does not depend on the assumed rates.
The relative gain is in fact invariant to the other assumptions:
because the model is multiplicative, improving one term from 40% to
50% always produces a 25% relative increase, whatever the other five
rates are. Only the absolute conversion figure depends on them

### What this arithmetic cannot claim

The baseline is not Myntra's conversion rate and should not be read
as an estimate of it. Four of the six rates are assumptions, two of
which cannot be measured without platform behavioural data. The model
shows which step is worth attacking given the relative magnitudes the
research supports. It does not predict the effect size of any
intervention. Establishing that requires a controlled experiment,
set out in the success metrics section.
---

## Section 7: Segment

### Segment selected

*Users who search outside the app before deciding on a saved item.*

Defined by an observable behaviour, not by age, gender, city or
category. A user enters this segment when they leave the app to seek
information about something they have saved - a Google search, a
YouTube review, an Instagram tagged-photo scroll, or a message to a
friend or group chat.

Why this segment:

*They have demonstrated intent.* Leaving the app to research an
item is costly and nobody does it for something they do not want.
One respondent spent roughly 30 minutes scrolling a brand's tagged
Instagram photos to find a person of similar height. Another visited
a Zara store specifically to try a size, then ordered the item online
in a different colour, and described this as "slightly ridiculous but
it worked."

*Their blocker is information, not price.* Of the four respondents
who did not search externally, three gave price or need-based answers
to what would make them buy this week: "price to be reduced", "more
saving", "if I am in need then I will buy it". Of the sixteen who did
search, the great majority gave information-based answers. Three
stated unprompted that they did not want a discount, in a question
that had already instructed them to assume constant price.

*The behaviour is already happening at scale.* 16 of 20 respondents
(80%) searched externally. In the corpus, 203 of 682 relevant
comments (29.8%) are people answering each other's product questions,
and 26 of the 35 stated workarounds on size-selection rows name a
creator as the person asked.

*They are addressable without breaching the constraint.* The
solution is to bring inside the product an answer these users are
already leaving to find, which requires no monetary incentive.

### Segment size and assumptions

Directional only.

In this sample: 16 of 20 respondents, 80%. This is a convenience
sample from the author's own network and is not representative, so
the figure indicates that the behaviour is common rather than that it
occurs at this rate on the platform.

The corpus cannot size the segment, because a comment does not tell
you whether its author is a Myntra wishlist user. What the corpus
does show is that the behaviour has scale: 132 of 682 relevant
comments (19.4%) record asking a creator as the workaround.

Assumptions stated: that external search is observable to the
platform in some proxy form - session exit followed by return to the
same product, an in-app search after a wishlist visit, or a share
action - and that the segment is large enough to be worth building
for. Neither is verified here.

### Segments considered and not pursued

*Occasion-driven savers.* A genuinely distinct segment with a
different blocker. Within INTENT_OCCASION, BLOCK_STYLING accounts for
56.3% of blockers against 7.5% across the corpus, and size selection
falls to 6.3%. All 16 of these rows record a workaround, the highest
rate of any intent group. Six of 20 respondents saved for an occasion
or trip.

Not pursued because n=16 in the corpus and 6 in the research is too
small to build on, and because the styling problem needs a different
solution - outfit coordination rather than fit evidence. It is
recorded as the strongest candidate for a second phase.

*Acquisition-watch savers.* Users maintaining a standing want to be
satisfied whenever and wherever the item appears. Their dominant
blocker is BLOCK_LISTING_INCOMPLETE at 90%, with zero size-selection
blockers, the lowest severity of any intent group at 2.30 and the
lowest proximity to purchase at 0.75.

Not pursued because they are furthest from the purchase decision and
their blocker is catalogue completeness rather than confidence.

*Heavy savers.* Four respondents reported saving more than 25 items
in two months. All four had converted more than once in that period.
Heavy saving is therefore not a conversion failure in this sample; it
is a ratio problem, which is why item-level conversion is tracked as
a secondary metric in Section 1 Q1 rather than treated as a segment.

*Price-sensitive savers.* Measured and reported -
INTENT_PRICE_WATCH accounts for 22 corpus rows, and 5 of 20
respondents gave price-led answers. Excluded from scope by the
brief's prohibition on monetary incentives. This is a constraint
exclusion, not a judgement that the group is small.
