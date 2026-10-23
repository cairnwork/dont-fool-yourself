# FACTCHECK：ARTICLE_zh.md 數字核對紀錄（2026-10-23，hmk-lead）

起草：Agy 初稿，後由 hmk-lead 依原文改寫定稿（初稿有誤引，例如把 10/19 的接線盤點當成 10/14 A/B 的內容、把「向量重排 +0.3 pp」與「推式注入 +0.3%」混為一談，已更正）。
核對對象：`~/workspace/knowledge/nexus/` 下原文（簡稱 K/）；非 Agy 總表，總表只當導覽。中文正文不含表格 3,764 字（上限 4,000）。私有題庫名／題號／session 代號：以 grep 檢查 0 筆。

| 文中主張 | 原文位置 | 結果 |
|---|---|---|
| 2/20 起所有「提升」站不住、紀錄真的跑過 | K/research/2026-10-19-measurement-calibration-audit/README.md 結論 | 符合 |
| 133/2,018＝6.6%（5.6–7.8）、7–10%、真實使用 54／獨立審查 27／Core 0 | K/research/2026-10-17-family-false-completion-audit.md | 符合（Core 0 在該檔「Gates (Core 0, CI 9)」） |
| 答案函式 4/23 的 7 個→5/14 的 36 個、5/20 每列 0.9 秒、token 有效 0/24、原始資料遺失 | 校準稽核 README 表第一列 | 符合 |
| NOOP 假模型 12/12 | K/research/2026-10-19-path-performance-feb-oct.md「被推翻的大勝」 | 符合；原文註明只直接證明 value_v1／P16 這組題 |
| 7/11 只有 Nexus 組能重試、慢 3.6 倍、部分失準 | 校準稽核 README 表 | 符合 |
| 同 12 題 ≥10 次、保留題 12 題 ±25 個百分點 | 校準稽核 README 表與「現況」 | 符合（文中省略題集名稱） |
| 6 月 85.7%：裸組寫死解 2 題、驗證 `if True` | 校準稽核 README 表 | 符合 |
| 9/29：23/24 對 16/24、A 組標準答案是受測程式、重算 8/8 對 8/8 | 同上 | 符合 |
| 7/29 Nexus 組 prompt 直接寫答案 | 同上 | 符合 |
| 10/14：P16 12/24 對 11/24；hard_v1 12/20 對 13/20；44 組 42 同；多約 24% token | path-performance 結論 | 符合 |
| 44 列自動修復 0、記憶命中 0、題目設計成看得到的測試會過 | 校準稽核 README 表 10/14 列 | 符合 |
| A2 從 base＋第一次 patch、A0′ 從 base 重抽；只能解讀為整套重試策略 | K/research/2026-10-22-cairnwork-ab-round3-prereg-draft.md §2；K/decisions/council-2026-10-23-cairnwork-ab-strategy/CONSENSUS.md「三方一致」5 | 符合 |
| 4/26 54/54 對 51/54，18 題×3 次，差距全來自同一題 3 次重複、不顯著 | path-performance 末段「查證更正」 | 符合 |
| R8 G2：47.68%→29.74%、302 檔 34.5%、覆蓋率 72.97%、門檻 30%、WATCH→DROP | K/decisions/council-2026-10-22-l2-breakthrough/r8_audit/AUDIT_ZH.md（已讀原文，非只看總表） | 符合 |
| Sonnet 篩選 88 題、合格 11、預估 H 不通過約 7 | round3 prereg §5.2 | 符合（文中寫「預估真錯不到 20 份」） |
| 記憶 76/101 對 BM25 75/101、+1.0 pp、門檻 +10 pp | K/research/2026-10-18-layer1-L2-active-memory/RESULT.md | 符合 |
| 向量比 BM25 +1.48 pp | K/decisions/council-2026-10-22-l2-breakthrough/r7_offline/RESULTS.md | 符合；該檔重測的「省基底 14.18% 對 15% 門檻」文中未用 |
| 檔案定位向量重排 +0.3 pp；BM25 Hit@5 76.3% 中 64.0 pp 來自抄 prompt 路徑 | r6_gates/RESULTS.md（同目錄） | 符合（同檔另處寫 76.7%／64.1%，是不同表；文中用 76.3%／64.0 這組，彼此一致） |
| 偵測器「15/15」對保留語料 53/120（44%） | ~/.claude/skills/nexus-detector-eval/SKILL.md | 符合 |
| 先公布雜湊再解盲、曾忘記而事後補貼；#2721 解盲後偵測器範圍不同（33 對 0） | ~/.claude/skills/blind-custody/SKILL.md §3、§5 | 符合；文中未寫題庫 repo 名 |
| 假模型列有非空 diff 整次作廢 | blind-custody SKILL §2（exit 3） | 符合 |
| A0 與 A3 提示只差一段、32/32；校準 32/32 通過；Gemini 真錯分母預估 <20 故只報方向 | round3 prereg §8.1、§5.2 | 符合 |
| 補遺 1：操作者看過兩列執行狀態欄位、沒看 holdout／評分 | round3 prereg §8.1 補遺 1 | 符合 |
| run2：兩組皆 42.9%（12/28）、延後驗收 28/28 全放行 | K/research/2026-10-22-cairnwork-ab-run2-result.md | 符合 |
| Haiku 實跑 89 題錯 6 題（6/89） | K/research/2026-10-22-cairnwork-filter-mechanism-result.md 表格與第 33 行 | 已核對（表中寫 6／83 為通過 holdout 之外的分母標示，89＝83＋6） |
| 三個問題不互相替代；收件實驗與壓力測試設計；11/16 規則為建議稿 | CONSENSUS.md | 符合 |
| Cairnwork 核心價值不是提高成功率、而是「完成有證據」；不主張提高成功率 | ~/workspace/cairnwork/README.md「定位」節 | 已核對 |

無未核對項目。
