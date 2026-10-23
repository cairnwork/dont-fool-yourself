# How to Run an A/B on an Agent Tool Without Fooling Yourself

We build engineering tools for AI agents. Over eight months we measured many times that "this tool makes the model stronger." On 2026-10-19 we went back and audited the calibration, and the verdict was ugly: from 2/20 to that day, every number that claimed an improvement did not hold up after calibration, while the claims of "no improvement" were mostly accurate (measurement-calibration-audit/README.md). The records were real runs. What was wrong was the way we measured, not fabrication (same file).

Another number from the same period is even less comfortable. A 2026-10-17 audit of 2,018 merged PRs across 11 repos confirmed a lower bound of 133/2,018 = 6.6% (interval 5.6-7.8) for PRs that claimed to be done but were not, with an estimate of 7-10%. How strict the governance rules were showed no visible relationship to that rate. What caught these PRs was real use (54), independent review (27), and almost nothing from automated gates (2026-10-17-family-false-completion-audit.md).

Both are the same problem: you say "it's done" or "it got stronger," and why should you believe yourself? This article covers how we got fooled and the checks we added afterwards.

## 1. How our own numbers fooled us

**1. Hand-written answers for only one arm.** The April-May A/Bs showed big wins, 24/24 against 5-16/24. A development agent had hand-written answer functions problem by problem, growing from 7 on 4/23 to 36 on 5/14. Only the arm with the tool under test could use them, and they were counted as solves. The 5/20 run took 0.9 seconds per row with 0/24 effective tokens, and the raw data was not kept (measurement-calibration-audit/README.md). On 2026-10-16 we swapped in a NOOP fake model that does nothing, ran the same problem set, and it still scored 12/12 (2026-10-19-path-performance-feb-oct.md).

**2. Hidden-test feedback for only one arm.** In the same batch of evaluations, only the arm with the tool under test received hidden-test feedback. In one 7/11 run only that arm could retry, so its conclusion "no improvement, 3.6x slower" is only partly accurate (measurement-calibration-audit/README.md).

**3. Problems tuned along the way.** The same 12 problems were run at least 10 times and adjusted between runs. The person who wrote the problems was the person tuning the code. In the end only 12 genuinely unseen held-out problems remained, enough to see only large differences of about +/-25 percentage points (measurement-calibration-audit/README.md).

**4. Wrong scoring.** The June 85.7% came from a hard-coded script: the bare arm was hard-coded to solve 2 problems, verification was written as `if True`, and the model was never called. The 9/29 hybrid experiment, 23/24 against 16/24, used a gold answer produced by the program under test; recomputed under the rules sealed in advance, it was 8/8 against 8/8 (measurement-calibration-audit/README.md). In the 7/29 three-arm calibration, the prompt of the Nexus arm literally contained the answer (same file).

**5. A fair A/B with the capabilities under test switched off.** On 2026-10-14 we finally ran a same-model A/B with symmetric conditions: P16 was 12/24 against 11/24, hard_v1 was 12/20 against 13/20, 42 of 44 pairs had identical outcomes, and the tool arm used about 24% more tokens. We called it a tie (2026-10-19-path-performance-feb-oct.md). But for the sake of fairness the tool's capabilities had been turned off: 44 rows with 0 automatic repairs, 0 memory hits, and problems designed so that "the visible tests pass," so nothing ever escalated (measurement-calibration-audit/README.md). That tie measured "the wiring was not connected," not "it does not help." We then reported it as "it is useless," a miscalibration in the opposite direction (same file).

**6. A2 and A0' with different starting points.** The third-round pre-registration wanted to separate the effect of feedback from the effect of drawing a second attempt. A2 continued from "base + first patch" with failure feedback, while the control A0' was redrawn from base, which changed two variables at once. The 10/23 council review pointed this out. Conclusion: in the Gemini round, A2 - A0' can only be read as the effect of the whole retry strategy, and this goes into the limitations (2026-10-22-cairnwork-ab-round3-prereg-draft.md, council-2026-10-23-cairnwork-ab-strategy/CONSENSUS.md).

**7. Drawing conclusions from too small a denominator.** The 4/26 result of 54/54 against 51/54 was 18 problems times 3 runs, and the whole gap came from the 3 repeats of a single problem, which is not significant (2026-10-19-path-performance-feb-oct.md). The R8 sub-agent offloading claimed a 47.68% net saving. An independent audit found that 302 runs (34.5%) of sub-agents had no target files at all, and the script gave them 100% recall for free. After removing them, coverage was 72.97% and the net saving 29.74%, below the 30% bar, and the verdict moved from WATCH to DROP (r8_audit/AUDIT_ZH.md). The third round had the same issue: Sonnet screening of 88 problems left only 11 qualifying, and the expected number of true failures was below 20 (2026-10-22-cairnwork-ab-round3-prereg-draft.md).

**8. Small effects that stack up.** Memory replay scored 76/101 against the BM25 baseline's 75/101, only +1.0 pp, while the bar set in advance was +10 pp. Vector retrieval beat zero-cost BM25 by +1.48 pp. Vector re-ranking for file localization added +0.3 pp (2026-10-18-layer1-L2-active-memory/RESULT.md, r7_offline/RESULTS.md, r6_gates/RESULTS.md). Each is tiny, and summed they look like "steady progress." What protected us was judging each mechanism against its own pre-set bar and never adding them up. One more warning: BM25 file localization had a Hit@5 of 76.3%, of which 64.0 percentage points came merely from copying paths already written in the prompt (r6_gates/RESULTS.md). The baseline itself has to be taken apart first.

## 2. The check for each trap

| Trap | Check | Source |
|---|---|---|
| 1, 4: the score is not measured from the model | Run a fake-model arm; it must pass 0 held-out problems; if a fake-model row has a non-empty diff, the whole run is void | measurement-calibration-audit/README.md; blind-custody SKILL |
| 2, 5: arms differ in information or capability | Zero-model prompt diff: compare the actual prompts of both arms character by character before the run; only pre-registered differences are allowed (example: A0 and A3 differ only by one file list, confirmed on 32/32 problems) | 2026-10-22-cairnwork-ab-round2-prereg-draft.md; round3 freeze record |
| 3: problems tuned or already exposed | Freeze the problem-set hash; record each problem's fix date and the model cutoff and stratify by them; ask the custodian to compare against the exposed bank; the worker sees no URLs and no post-fix history | round2, round3 prereg |
| 4: the scorer is wrong | Calibrate before the run: the reference solution must pass, "base plus one comment line" must fail | round3 freeze record (32/32 passed) |
| 5: capabilities switched off | Prove the wiring first, then measure: show row by row "it ran, it produced output, downstream used it"; anything that fails stays out of the measurement | measurement-calibration-audit/README.md |
| 6: different starting points | Fork from the same start: control arm and treatment arm start from the same patch | CONSENSUS.md |
| 7: denominator too small | Write the bar in advance: denominator < 20 is judged "insufficient information," report direction only; no adding problems after the freeze | round2, round3 prereg |
| 8: small effects stacking | Set a bar per mechanism in advance (for example +10 pp), judge each on its own, never sum | RESULT.md etc. |
| Changing the rules afterwards | Frozen fields; an addendum may only be filed before any formal scoring is seen | round3 prereg |
| Measuring yourself | Separate who builds, who measures, who approves; independent recomputation before publishing; publish hashes before unblinding, and unblind once | blind-custody SKILL; round2 prereg |
| A detector grading itself | The implementer's own positives count only as a development set: we once reported "15/15 caught," and on a blind-written held-out corpus it was 53/120 (44%) | nexus-detector-eval SKILL |

Three more details. **Unblinding needs a gate**: publish the hashes of the candidate set and the analysis reports first, then unblind. Once we forgot, posted them late, and said so (blind-custody SKILL). **Asymmetries found afterwards are labelled post-hoc**: after unblinding in #2721 we found that the detectors scanned different scopes in the two arms (NEXUS 33 hits, BARE 0), while the task text itself was identical. It was handled as a limitation or sensitivity analysis and marked "post-hoc" (blind-custody SKILL). **Record what the operator saw**: addendum 1 of the third round states that the operator looked at the execution-status fields of two rows to decide where to stop, and did not look at the holdout or any scoring (round3 prereg).

## 3. One-page checklist

- [ ] Freeze: problem set, tests, prompt templates, model versions and harness commit all have hashes and do not change after the run starts.
- [ ] Zero-model prompt diff: both arms' prompts compared character by character; only pre-registered differences remain.
- [ ] Fake-model arm: 0 held-out problems pass.
- [ ] Scores come from the model: no hard-coded answers, no shortcut that skips the model.
- [ ] Both arms get symmetric information: hidden-test feedback, number of retries and tool permissions are the same.
- [ ] The capability under test really ran (it executed, produced output, and downstream used it).
- [ ] Scorer calibrated: the reference solution passes, the known-bad solution fails.
- [ ] Problems unseen: not written by the person tuning the code; exposure and model cutoff reported by stratum.
- [ ] Control and treatment start from the same point, and only one variable changes at a time.
- [ ] Denominator bar and "insufficient information" written in advance; no problems added after the freeze.
- [ ] Each mechanism judged against its own bar; small effects are not summed; the baseline is taken apart first.
- [ ] Scorers cannot see the arm; hashes are published first, then unblind once.
- [ ] Addenda are filed only before any formal scoring is seen, and who saw what is recorded.
- [ ] Build, measure and approve are separate roles; recompute independently before publishing.
- [ ] The report states only what was measured; what was not measured is written as "not supported this round."

## 4. How we do it now

These checks are now how Cairnwork is measured. Cairnwork is the delivery-verification layer for AI coding agents that we turned out of Nexus. Its core value is not raising the success rate but "completion with evidence" (Cairnwork README, "Positioning" section). Its A/B follows the rules above, and the third-round pre-registration looks like this: the same problem and the same model are run once, the resulting patch is evaluated under several policies at once, and every patch is fully scored whether or not it is delivered, so false blocks can be measured; the tests are written by three authors who cannot see each other's work; the freeze record contains hashes, seeds and model versions; and the expected number of true failures for Gemini is below 20, so we wrote in advance that we would report direction only and draw no conclusion (2026-10-22-cairnwork-ab-round3-prereg-draft.md).

The second-round result reminds us not to get complacent: both arms had a delivery precision of 42.9% (12/28), and the deferred acceptance let all 28/28 through, blocking nothing (2026-10-22-cairnwork-ab-run2-result.md). The 10/23 council concluded that this A/B measures only "the deferred hidden-test filter" and not "completion with evidence" (CONSENSUS.md). One reason is that on small bugs the model rarely errs to begin with: Haiku was wrong on only 6 of 89 problems (2026-10-22-cairnwork-filter-mechanism-result.md), so a tie is structural. Catching errors, trustworthy evidence, and benefit to the receiving maintainer are three separate questions, and passing one cannot pass the other two (CONSENSUS.md).

So we are adding two experiments that use no worker quota: an intake experiment (reusing patches that were already scored; the control arm sees the PR diff plus ordinary public CI, and the treatment arm sees the diff plus scope locking and offline-verifiable receipts, without per-problem hidden-test results, since otherwise we would be measuring "someone wrote the answer sheet first"), and an anti-false-completion stress test (offline replay of historical false completions and hand-made patches that tamper with tests). The decision rule is a proposal: if the denominator is still insufficient, admit that the claim does not hold and change direction rather than extend the contest (CONSENSUS.md).

If you build tools that "deliver" anything on behalf of an agent or an AI PR, take a look at Cairnwork. What it blocks and what it cannot block are measured with these same rules, and the results are published whether they are good or bad.
