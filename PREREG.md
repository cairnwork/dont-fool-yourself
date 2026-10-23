# PREREG: <title of the measurement>   (status: DRAFT | FROZEN <date>)

Rules of this document: before FROZEN, anyone may edit. After FROZEN, the only allowed change is a dated entry in section 9 (Addenda), filed before anyone has seen any formal score. Anything else voids the run and needs a new run directory and a new PREREG.

## 1. Question and claim boundary
- Question(s), one sentence each (Q1, Q2 ...):
- The claim applies ONLY to: <task type, models, time window>. It does not extend to: <list>.
- If a sample is selected (screened, filtered), say so in every sentence that quotes its result, and report the unselected (random) stratum next to it.

## 2. Arms (same problem, same model, same scorer)
| Arm | Exactly what differs from the control | Starts from |
|---|---|---|
| A0 control | nothing | base |
| A1 | <one change> | <same start as control> |
- One variable per comparison. A retry arm and its control must start from the SAME point (same patch, same context); if they cannot, write the confound into section 8 now.
- Zero-model prompt diff (run `python3 symcheck.py armA armB`): only differences registered here are allowed: <list>.
- Fake-model arm (a model that does nothing): must pass 0 held-out problems. Non-empty output from it voids the run.
- Capability under test: show, row by row, that it executed, produced output, and downstream used it. Otherwise the result measures "not wired", not "no help".

## 3. Problems
- Source, selection rule, random seed and its origin (a value fixed before selection):
- Exposure: public or private? Record fix date and model cutoff per problem and report by stratum.
- Who wrote problems, hidden tests and the holdout (three people or agents who cannot see each other's work, and none of them tunes the tool under test):
- Scorer calibration before the run: reference solution passes, known-bad solution fails.

## 4. Metrics and thresholds (written before any run)
| Metric | Definition | Pass bar | Denominator minimum |
|---|---|---|---|
| Primary | | point estimate >= X and one-sided 95% lower bound >= Y | n >= 20 |
- Each mechanism is judged against its own bar. Small effects are never summed across mechanisms.
- Take the baseline apart first (how much of its score is trivially available, such as paths already written in the prompt).

## 5. Three-way verdict (per model, never pooled)
- SUPPORTED: primary bar met with denominator >= minimum.
- NOT SUPPORTED THIS ROUND: denominator >= minimum and the bar is not met.
- INSUFFICIENT INFORMATION: denominator < minimum or interval crosses the boundary. Report direction only, draw no conclusion, add no problems after the freeze, and do not describe a change of direction as a validated new claim.

## 6. Denominator rule
- Minimum n for every verdict: <20>. Estimate it BEFORE freezing from dry runs; if the estimate is below the minimum, add problems before the freeze, or state now that the verdict will probably be INSUFFICIENT INFORMATION.
- Excluded or replaced problems: record which, why, and the order position used for replacement.

## 7. Blinding, unblinding, independent check
- Scorers see only de-identified output, never the arm.
- Arm map held by someone who does not analyse. Before unblinding, publish hashes of the candidate set and of every analysis script. Unblind once, when the stated condition holds: <condition>.
- Anything found asymmetric after unblinding is labelled post-hoc and reported as a limitation or sensitivity analysis.
- Independent recomputation by someone who neither built the pipeline nor scored, before any number is published.
- Roles (builder / measurer / approver, all different):

## 8. Known limitations (written now, not after)
-

## 9. Freeze record and addenda
### Frozen fields (fill at freeze, then do not change)
- Problem set hash:
- Test hashes (all three sets):
- Harness commit:
- Prompt template hashes (per arm):
- Model ids and CLI versions:
- Seed and its origin commit:
- Analysis script hashes:
### Addenda (dated; each must state "filed before any formal scoring was seen" and what the operator looked at)
- <date> Addendum 1:
