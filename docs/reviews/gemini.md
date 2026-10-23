1｜`dont-fool-yourself/docs/ARTICLE_zh.md`｜第四節邏輯自相矛盾：前句才寫第二輪交付精確率僅 42.9%（12/28 正確、16/28 為錯且延後驗收 28/28 全放行），後句卻將平手歸因於「小 bug 上模型本來就很少錯（Haiku 89 題只錯 6 題）」，拿低錯誤率解釋高錯誤率（57% 錯卻 0 攔截）的放行失敗｜高｜拆開兩場不同題庫／機制的因果敘述，直接承認第二輪是「16 筆真錯全漏攔」而非「模型很少錯」。

2｜`token-autopsy/src/token_autopsy/scan.py`、`report.py`｜費用歸因嚴重灌水：`poll_cost`、`browse_cost`、`waste_cost` 直接把含該工具的「整次 API 呼叫總費用 `costs[i]`」全額算進浪費（同一回應若並行呼叫 `Grep` 與 `Edit` 也全算瀏覽費）；且 `waste_runs` 依 `tools` 列表計數，單次 API 呼叫若並行發 3 個 `Glob`/`Grep` 就會被算成「連續 3 次瀏覽呼叫」｜高｜改按同次 API 呼叫內的 `tool_use` 數量分攤費用，且 `waste_runs` 必須跨不同呼叫（`ci`）才計數。

3｜`token-autopsy/src/token_autopsy/scan.py`、`rules.py`｜`d3`（精簡基底脈絡）拿作者私庫離線實測的常數（14%–16%）硬套所有使用者；且 `base_cost = ctxs[0] * (n - 1) * cache_read_rate` 假設首呼脈絡在後續每呼都完整重讀，若首呼剛好帶大檔或中途曾 `/compact`，`base_cost` 甚至會超過該會話實際 `cost_cr`｜高｜`base_cost` 改取 `min(ctxs[0], 各呼實際 cr)` 計算（或以 `cost_cr` 為上限），並將 `d3` 標明為假設性常數而非實測省率。

4｜`token-autopsy/src/token_autopsy/report.py`｜`build_rules_blocks` 計算總省率與額度餘裕時，只對上限 `phi` 取 `min(95.0, ...)`，下限 `plo` 未設上限；當重疊規則下限加總 ≥95% 時會出現「下限 > 上限」，≥100% 時 `1 / (1 - plo / 100)` 會觸發 `ZeroDivisionError` 或算出負數｜高｜對 `plo` 同樣加上 `min(90.0, ...)` 並確保 `plo <= phi`。

5｜`dont-fool-yourself/symcheck.py`｜文档宣稱 `ARM-SPECIFIC` 標記「寫在任一檔案即可（in either file）」，但 `compare()` 分別檢查 `i not in ma` 與 `j not in mb`；若只在 A 檔加標記，B 檔對應修改行仍會被判 `changed-B` 報錯。此外，若漏寫 `ARM-SPECIFIC-END`，`_marked()` 會把檔案後續所有行全部放行（假陰性）｜高｜未閉合標記直接拋 `ValueError`（exit 2）；修正文件與 docstring 說明「替換區塊須於兩檔皆標記」。

6｜`token-autopsy/src/token_autopsy/cli.py`｜1. `--from SCAN.json` 直接回傳已存檔的 `sessions`，完全忽略同時傳入的 `--since`、`--until`、`--project`、`--prices`、`--show-paths`，卻不報錯（README 宣稱篩選參數適用於所有子命令）。2. `main(argv)` 寫成 `argv or sys.argv[1:]`，若測試傳入空陣列 `main([])` 會誤吃系統 `sys.argv`｜中｜`--from` 載入後仍套用時間與專案過濾（或與衝突旗標並用時報錯）；`argv` 改用 `sys.argv[1:] if argv is None else argv`。

7｜`token-autopsy/src/token_autopsy/scan.py`｜1. `parse_claude` 以 `mid = m.get("id") or o.get("uuid")` 去重，若舊版或異常日誌兩者皆無（`None`），整檔所有無 ID 呼叫會被合併成第 0 筆。2. 60 秒重複指令偵測未排除空指令（`cmd == ""`）與同一次 API 呼叫內的並行工具（`ts - prev == 0`）｜中｜`mid` 為 `None` 時不合併；重複指令偵測要求 `cmd != ""` 且 `ci != prev_ci`。

8｜`dont-fool-yourself/symcheck.py`｜1. 對 `.json` 檔啟用 `_flatten` 會將鍵名排序，使 `ARM-SPECIFIC` 標記順序錯亂且標準 JSON 本就不支援註解標記。2. 目錄比對 `rglob("*")` 未排除 `.git`、`.DS_Store` 或二進位檔，遇單一非 UTF-8 檔即整批崩潰（exit 2）。3. `--allow` 傳入非法正規式時拋出 `re.error`，不在 `except` 捕捉範圍內而直接印出 Traceback｜中｜`except` 加入 `re.error`；忽略隱藏與二進位檔；說明 JSON 檔僅支援 `--allow`。

9｜`token-autopsy/src/token_autopsy/i18n.py`、`scan.py`｜隱私文案與實作不符：`i18n.py` 寫「只讀寫聚合數字、session id、專案目錄名…」，但程式實際會讀取完整 prompt 與指令進記憶體分類，且預設是寫出雜湊遮罩 `proj-<hash>` 而非原目錄名；另若子代理路徑為 `<proj>/subagents/x.jsonl`，`root = parts[1]` 會把所有子代理全歸入名為 `"subagents"` 的同一個假 session｜中｜修正 `i18n.py` 措辭為「僅將聚合數字寫入輸出」；子代理 `root` 檢查 `parts[1] != "subagents"`。

10｜兩專案 `README.md`、`VALIDATION.md`、`ARTICLE_zh.md`｜大量引用外部讀者無法查證的內部私有路徑（如 `knowledge/nexus/...`、`measurement-calibration-audit/README.md`、`#2721`）；且 `token-autopsy` 的 `README.md` 範例輸出（輪詢 5,373 次）與 `VALIDATION.md` 同批掃描數字（5,374 次）不一致｜低｜移除私有內部路徑或全部集中至公開的 `FACTCHECK.md` 摘要；統一 5,373／5,374 數字。

修後可公開：兩專案核心方向誠實有價值，但計算口徑灌水、`symcheck.py` 假陰性與文章第四節的邏輯矛盾若直接發出，會在開源社群立刻被抓包打臉。
