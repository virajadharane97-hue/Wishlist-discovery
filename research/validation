# Classifier validation

Method: 100 rows (seed 99) and 50 fresh rows (seed 202) hand-labelled
blind, no machine labels visible, using codebook definitions only.
Single rater.

## Results
| Codebook | Sample | Agreement | Cohen's kappa |
|---|---|---|---|
| v1.0 | n=100 | 49% | 0.409 |
| v1.0 | n=50 | 32% | 0.256 |
| v1.1 | n=50 | 28% | 0.205 |
| v1.2 | n=50 | 36% | 0.289 |

Excluding the 16 rows where the disagreement was structural (below):
v1.2 agreement 52.9%.

## Diagnosis
Disagreement is concentrated in one construct, not spread across the
taxonomy. On 16 of 50 rows the human coded BLOCK_SOCIAL_VALIDATION —
the user is delegating the decision to a trusted creator — while the
machine coded the substantive uncertainty underneath (size, fabric,
styling).

Both readings are defensible. The codebook conflated two dimensions:
WHAT the user cannot resolve, and HOW they are attempting to resolve
it. v1.2 separated them: substantive uncertainty in primary_blocker,
delegation in external_workaround. After that change, 11 of the 16
disputed rows carry external_workaround = "creator", confirming the
classifier detects the behaviour but files it elsewhere.

## Conclusion
Agreement of 36% (kappa 0.289) is below the 0.6 threshold. Reported
blocker shares are therefore indicative, not precise. Three
mitigations: (1) no conclusion rests on a difference of less than
about 3 percentage points between codes; (2) the ranking of the top
three codes was stable across all three codebook versions; (3) all
findings are cross-checked against primary research, and only
findings supported by both sources are reported.

Limitation: single rater. A second independent rater would give a
stronger estimate and would test whether the residual disagreement is
codebook ambiguity or rater idiosyncrasy.

## Second rater (n=30, independent, blind)

| Pair | Agreement | Cohen's kappa |
|---|---|---|
| Rater 1 vs Rater 2 | 46.7% | 0.413 |
| Rater 1 vs Machine | 40.0% | 0.325 |
| Rater 2 vs Machine | 26.7% | 0.241 |
| All three concordant | 5 of 30 | — |

Two human raters using identical definitions, blind and independently,
agreed on 46.7% of rows (kappa 0.413). This establishes that the
residual disagreement is codebook ambiguity rather than rater
idiosyncrasy: a 15-way taxonomy applied to short, multilingual,
often-fragmentary comments is inherently unstable.

The two humans agreed with each other more than either agreed with the
machine, indicating the classifier is a systematic outlier rather than
that all three are labelling randomly.

Null usage diverged sharply: machine 12 of 30, rater 1 five, rater 2
zero. Rater 2 assigned a code to every row despite instructions that
blank was a valid answer. Null-boundary behaviour is the second
largest source of disagreement after the social-validation construct.

### Convergent finding
Both human raters independently coded a large share of rows as social
validation — 6 of 30 and 8 of 30 — while the machine coded zero.
Rater 2 had no knowledge that this code was contested. Combined with
the classifier's own external_workaround field (creator on 132 of 682
rows, 19%) and the role field (advising on 203 of 682, 30%), and with
8 of 14 research respondents asking for peer or trusted-source
evidence, four independent sources identify the same behaviour:
users delegate the decision to a person they consider similar or
credible.

This behaviour is therefore reported as a workaround and a solution
requirement, not as a blocker code.