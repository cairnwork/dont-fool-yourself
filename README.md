# dont-fool-yourself

**English** | [中文](#中文)

How to run an A/B on an agent tool without fooling yourself. The main product is the article, built from our real mistakes with the numbers kept: [docs/ARTICLE_en.md](docs/ARTICLE_en.md) (中文：[docs/ARTICLE_zh.md](docs/ARTICLE_zh.md)). The numbers come from our internal experiment records, which outsiders cannot check one by one; [docs/FACTCHECK.md](docs/FACTCHECK.md) lists, for every number, the title and date of the internal document it comes from.

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
Exit code 0: only registered differences. 1: unexpected differences (listed). 2: input error. Registered differences are lines between `ARM-SPECIFIC-START` / `ARM-SPECIFIC-END` marker lines (a replaced block must be marked in both files; an unpaired marker is exit 2), or lines matching an `--allow` regex (invalid regex is exit 2). `*.json` files are flattened, so key order does not matter; they support `--allow` only, not markers. In directory mode hidden files (`.git`, `.DS_Store`) are ignored and non-UTF-8 files are skipped and listed. Tests: `python3 -m unittest discover -s tests`. Python 3.10+, standard library only.

The evidence comes from the work behind [Cairnwork](https://github.com/cairnwork/cairnwork), a delivery-verification layer for AI coding agents whose value is "completion with evidence," not a higher success rate.

License: Apache-2.0. Author: James3014.

## 中文

agent 工具的 A/B 怎麼量才不會騙到自己。主產品是長文，用我們真實翻車的案例與原始數字寫成：[docs/ARTICLE_zh.md](docs/ARTICLE_zh.md)（英文：[docs/ARTICLE_en.md](docs/ARTICLE_en.md)）。數字來自我們的內部實驗紀錄，外部無法逐一查證；[docs/FACTCHECK.md](docs/FACTCHECK.md) 列出每個數字對應的內部文件標題與日期。

另附三個小檔案（可選）：`PREREG.md`（預註冊範本：凍結欄位、補遺區、判定三段式、分母不足規則、同起點分叉規則）、`CHECKLIST.md`（一頁清單）、`symcheck.py`（單檔零依賴，零模型比對兩組提示／設定的差異；exit 0 表示只有已登記的差異，1 表示有未預期差異，2 表示輸入錯誤）。已登記的差異：夾在 `ARM-SPECIFIC-START`／`ARM-SPECIFIC-END` 標記行之間的行（被替換的區塊兩個檔案都要標記；標記不成對回 exit 2），或符合 `--allow` 正規式的行（非法正規式回 exit 2）。`.json` 只支援 `--allow`、不支援標記；目錄模式忽略隱藏檔（`.git`、`.DS_Store`），非 UTF-8 檔跳過並列出。測試：`python3 -m unittest discover -s tests`。

授權 Apache-2.0，作者 James3014。
