# One-page checklist: A/B for agent tools (see docs/ARTICLE_en.md for the evidence behind each line)

- [ ] **Freeze**: problem set, tests, prompt templates, model versions, harness commit all hashed; nothing changes after the run starts.
- [ ] **Zero-model prompt diff** (`python3 symcheck.py`): only pre-registered differences remain.
- [ ] **Fake-model arm**: 0 held-out problems pass.
- [ ] **Scores come from the model**: no hard-coded answers, no shortcut that skips the model.
- [ ] **Symmetric information**: hidden-test feedback, retries, tool permissions are the same in both arms.
- [ ] **Capability really ran**: executed, produced output, downstream used it.
- [ ] **Scorer calibrated**: reference solution passes, known-bad solution fails.
- [ ] **Problems unseen**: not written by the person tuning the tool; exposure and model cutoff reported by stratum.
- [ ] **Same start, one variable**: control and treatment start from the same point.
- [ ] **Denominator bar** and "insufficient information" written in advance; no problems added after the freeze.
- [ ] **Per-mechanism bar**: small effects are not summed; the baseline is taken apart first.
- [ ] **Blind scoring**; publish hashes first; unblind once.
- [ ] **Addenda only before formal scores are seen**; record who looked at what.
- [ ] **Build / measure / approve are different roles**; recompute independently before publishing.
- [ ] **Report only what was measured**; write "not supported this round" when it is.

# 一頁檢查清單（中文）
凍結（雜湊）／零模型提示比對／假模型臂 0 題通過／分數來自模型／兩組資訊對稱／能力真的有跑／評分器校準／題目沒看過／同起點只改一個變因／分母門檻事先寫／每個機制各自對門檻／盲評、先公布雜湊再一次解盲／補遺只在看到評分前／做量批准分開、公開前獨立重算／只寫量到的。
