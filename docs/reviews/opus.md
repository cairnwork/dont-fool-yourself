# Opus 獨立審查（2026-10-23）摘要
驗證：乾淨 venv 安裝、pytest 19 全過；真實全量 scan 4.5 秒（README 的「約 3 秒」偏樂觀）；message.id 去重正確；脈絡長度＝in＋cw＋cr 分桶正確；輸出無 prompt／路徑／email；無網路呼叫；dont-fool-yourself unittest 9 全過；抽查 25+ 個數字全對；中英一致；LICENSE 與 Cairnwork 連結正確。

| # | 專案 | 檔案:行 | 問題 | 嚴重度 | 修法 |
|---|---|---|---|---|---|
| 1 | token-autopsy | src/token_autopsy/default_prices.json:4-7 | 所有 opus／fable 都套 $15/$75（cache read $1.5）。實際：Opus 5.5 $4/$20（read $0.20）、Opus 4.8／4.6 $5/$25、Fable 5.1 $10/$50（read $0.25）、Sonnet 5.5 $2/$10、Haiku 5.5 $0.10/$0.50。日誌 83% 費用是 opus-5-5，總額高估約 4.8 倍（$55,312 → $11,541） | 高 | 價目依版本細分（opus-5-5、opus-4-8…），預設表放前面；正確價目檔在 scratchpad p.json |
| 2 | token-autopsy | README 範例、docs/VALIDATION.md | 範例數字用錯價目算出：修正後快取重讀佔費用 66%→50%、寫入 29%→42%、>200k 69%→66%、輪詢 7.3%→8.0%、規則 1 13.5–27%→10.3–20.6%、規則 3 1.9–2.1%→1.4–1.6%；token 佔比不受影響 | 高 | 修 #1 後重跑更新；scan 時間寫「約 3–5 秒」 |
| 3 | dont-fool-yourself | symcheck.py:44-55 | 只有 START 沒 END 會把後面整份當已登記差異；實測多一行「secret hint: answer is 42」沒被抓到 | 中 | START／END 不配對回 exit 2，補測試 |
| 4 | dont-fool-yourself | README:9、FACTCHECK.md | 宣稱「每個數字都有來源」但來源都是私有知識庫，外部不可查證 | 中 | README 明講來源是內部紀錄，或附公開摘錄 |
| 5 | dont-fool-yourself | FACTCHECK.md:1,3,4,26,27,34 | 露出 session 代號 hmk-lead、Agy、主機路徑 ~/workspace/knowledge、~/.claude/skills、~/workspace/cairnwork | 中 | 換成中性名稱 |
| 6 | token-autopsy | scan.py:65 | 路徑遮罩是無鹽 sha256 前 8 碼，可字典反推；README 寫 masked | 低 | 每台機器隨機鹽（存本機設定），或改稱「假名化」 |
| 7 | token-autopsy | docs/VALIDATION.md:3 | 露出私有知識庫路徑 | 低 | 改寫成「先前一次人工驗屍」 |
| 8 | token-autopsy | pricing.py:47 | 1 小時快取寫入價應為輸入價 2 倍，程式一律 1.25 倍（佔寫入 token 7.7%） | 低 | 分開 ephemeral_1h／ephemeral_5m |
| 9 | dont-fool-yourself | ARTICLE zh/en:43 | 提到私有 Issue 編號 #2721 | 低 | 改成「某次盲測」 |
判定：兩者修後可公開。
