# dont-fool-yourself

**English** | [中文](#中文)

In one of our internal cases, a NOOP fake model that does nothing still scored 12/12 on a problem set, which is why a scorer has to be calibrated before any number is trusted. This repo is about how to run an A/B on an agent tool without fooling yourself. The main product is the article, built from our real mistakes with the numbers kept: [docs/ARTICLE_en.md](docs/ARTICLE_en.md) (中文：[docs/ARTICLE_zh.md](docs/ARTICLE_zh.md)). The numbers come from our internal experiment records, which outsiders cannot check one by one; [docs/FACTCHECK.md](docs/FACTCHECK.md) lists, for every number, the title and date of the internal document it comes from.

Three small, optional files come with it:

| File | What it is |
|---|---|
| `PREREG.md` | Pre-registration template: frozen fields, addenda section, three-way verdict, denominator rule, same-start fork rule. |
| `CHECKLIST.md` | One-page checklist. |
| `symcheck.py` | Single-file, zero-dependency zero-model symmetry check. |

```
python3 symcheck.py armA/prompt.txt armB/prompt.txt --allow '^model:'
python3 symcheck.py armA/ armB/            # compare matching files in two directories
```
Exit codes: **0** no unexpected difference *within the checked scope* (this is not proof that the two arms are symmetric); **1** unexpected differences (listed); **2** input error (bad regex, unpaired marker, missing path); **3** INCOMPLETE: something could not be compared (non-UTF-8 file, invalid or duplicate-key JSON, zero file pairs, any symlink or special file such as a FIFO), listed, never to be read as success.

Checked scope: only the files you pass in (or the files with matching relative paths in two directories), compared as text lines. Directory mode skips only `.git/` and what you name with `--ignore GLOB`; other dotfiles and dirs such as `.claude/` are compared; a file present on one side only is a difference. Symlinks (even valid ones) and special files are never followed or opened; they are listed as INCOMPLETE. Not checked: anything outside those files (environment variables, tool permissions, model versions, network, files you did not pass), and whether the same text means the same thing to the model. Registered differences are lines between `ARM-SPECIFIC-START` / `ARM-SPECIFIC-END` marker lines (a replaced block must be marked in both files; an unpaired marker is exit 2), or lines matching an `--allow` regex. `*.json` files are flattened to JSON-pointer lines with a line for every object and array, so empty containers and object-versus-array differences count; they support `--allow` only, not markers. Tests: `python3 -m unittest discover -s tests`. Python 3.10+, standard library only.

The evidence comes from the work behind [Cairnwork](https://github.com/cairnwork/cairnwork), a delivery-verification layer for AI coding agents whose value is "completion with evidence," not a higher success rate.

License: Apache-2.0. Author: James3014.

## 中文

我們有一個內部案例：什麼都不做的 NOOP 假模型，在某組題目上仍得到 12/12，所以任何數字都要先校準評分器才能信。這個 repo 講 agent 工具的 A/B 怎麼量才不會騙到自己。主產品是長文，用我們真實翻車的案例與原始數字寫成：[docs/ARTICLE_zh.md](docs/ARTICLE_zh.md)（英文：[docs/ARTICLE_en.md](docs/ARTICLE_en.md)）。數字來自我們的內部實驗紀錄，外部無法逐一查證；[docs/FACTCHECK.md](docs/FACTCHECK.md) 列出每個數字對應的內部文件標題與日期。

另附三個小檔案（可選）：`PREREG.md`（預註冊範本：凍結欄位、補遺區、判定三段式、分母不足規則、同起點分叉規則）、`CHECKLIST.md`（一頁清單）、`symcheck.py`（單檔零依賴，零模型比對兩組提示／設定的差異；exit 0 表示「在檢查範圍內沒有未預期差異」，不等於證明兩組對稱；1 有未預期差異；2 輸入錯誤；3 INCOMPLETE，有東西無法比對（非 UTF-8 檔、無效或有重複鍵的 JSON、零個檔案配對、任何符號連結或 FIFO 等特殊檔），會列出，不可當成功）。檢查範圍：只比你給的檔案（或兩個資料夾中相同相對路徑的檔案）的文字行；目錄模式只跳過 `.git/` 與 `--ignore GLOB` 指定的，其他點開頭的檔案與目錄（例如 `.claude/`）都會比；只有一邊有的檔案算差異。符號連結（即使有效）與特殊檔一律不跟隨、不開啟，列為 INCOMPLETE。不檢查：這些檔案以外的東西（環境變數、工具權限、模型版本、網路、沒給的檔案），以及同樣文字對模型是否同樣意思。已登記的差異：夾在 `ARM-SPECIFIC-START`／`ARM-SPECIFIC-END` 標記行之間的行（被替換的區塊兩個檔案都要標記；標記不成對回 exit 2），或符合 `--allow` 正規式的行（非法正規式回 exit 2）。`.json` 攤平成 JSON pointer 行並保留每個物件與陣列（空物件、空陣列、物件對陣列的差異都算），只支援 `--allow`、不支援標記。測試：`python3 -m unittest discover -s tests`。

授權 Apache-2.0，作者 James3014。
