# dont-fool-yourself (working name)

**English** | [中文](#中文)

How to run an A/B on an agent tool without fooling yourself. The main product is the article, built from our real mistakes with the numbers kept: [docs/ARTICLE_en.md](docs/ARTICLE_en.md) (中文：[docs/ARTICLE_zh.md](docs/ARTICLE_zh.md)). Every number is traced to a source file in [docs/FACTCHECK.md](docs/FACTCHECK.md).

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
Exit code 0: only registered differences. 1: unexpected differences (listed). 2: input error. Registered differences are lines between `ARM-SPECIFIC-START` / `ARM-SPECIFIC-END` marker lines, or lines matching an `--allow` regex. `*.json` files are flattened, so key order does not matter. Tests: `python3 -m unittest discover -s tests`. Python 3.10+, standard library only.

The evidence comes from the work behind [Cairnwork](https://github.com/cairnwork/cairnwork), a delivery-verification layer for AI coding agents whose value is "completion with evidence," not a higher success rate.

License: Apache-2.0. Author: James3014.

## 中文

agent 工具的 A/B 怎麼量才不會騙到自己。主產品是長文，用我們真實翻車的案例與原始數字寫成：[docs/ARTICLE_zh.md](docs/ARTICLE_zh.md)（英文：[docs/ARTICLE_en.md](docs/ARTICLE_en.md)）。每個數字的來源核對見 [docs/FACTCHECK.md](docs/FACTCHECK.md)。

另附三個小檔案（可選）：`PREREG.md`（預註冊範本：凍結欄位、補遺區、判定三段式、分母不足規則、同起點分叉規則）、`CHECKLIST.md`（一頁清單）、`symcheck.py`（單檔零依賴，零模型比對兩組提示／設定的差異；exit 0 表示只有已登記的差異，1 表示有未預期差異，2 表示輸入錯誤）。已登記的差異：夾在 `ARM-SPECIFIC-START`／`ARM-SPECIFIC-END` 標記行之間的行，或符合 `--allow` 正規式的行。測試：`python3 -m unittest discover -s tests`。

授權 Apache-2.0，作者 James3014。
