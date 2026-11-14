# 雙重 Fibonacci 0.382／1.618 回測程式

程式檔：`dual_fib_confluence_backtest.py`

## 已鎖定規則

- 第一組向下波段：最高轉折燭設為 `1`，其後低位設為 `0.786`。
- 第二組向上波段：之後更低的最低轉折燭設為 `1`，反彈高位設為 `0.786`。
- 兩組 `0.382` 價位距離不超過 2%。
- 第一組 `+1.618` 與第二組 `-1.618` 價位距離不超過 2%。
- 日線首次收市高過兩條 0.382 中較高者，下一交易日開市入場。
- 第二組最低燭影線低位作止蝕。
- 兩條 1.618 重疊價的平均數作目標。
- 先到目標為成功；先穿止蝕為失敗；90個交易日未到任何一邊為未完成。
- 同一日同時觸及目標和止蝕，因日線不能知道先後，保守列作失敗。
- 轉折點預設要等右邊3支日線完成才確認，避免回測偷看未來。
- 同一股票45日內只保留一個訊號，最多輸出最近500個獨立案例。

## CSV格式

每個CSV需要以下欄位（英文大小寫不限）：

```text
Date,Open,High,Low,Close,Volume
```

## 執行方法

單一股票：

```bash
python dual_fib_confluence_backtest.py \
  --input DEC.csv \
  --symbol DEC \
  --output result_DEC
```

一個資料夾內多隻股票：

```bash
python dual_fib_confluence_backtest.py \
  --input daily_csv \
  --output result_500
```

使用ticker清單下載十年日線（需要先安裝 `yfinance`）：

```bash
pip install pandas numpy yfinance
python dual_fib_confluence_backtest.py \
  --universe tickers.txt \
  --period 10y \
  --max-symbols 1000 \
  --output result_500
```

只保留回報風險比至少2.5R：

```bash
python dual_fib_confluence_backtest.py \
  --input daily_csv \
  --min-rr 2.5 \
  --output result_2_5R
```

## 輸出

- `dual_fib_trades.csv`：每宗交易、兩組錨點、入場、止蝕、目標及結果。
- `dual_fib_summary.json`：成功率、失敗率、平均R及未完成數量。
- `dual_fib_report.md`：廣東話摘要。

程式預設同時計算全部合格案例，以及計劃回報風險比至少2.5R的子組成功率。

## GitHub Actions

Repository內的 `dual-fib-confluence-backtest.yml` 可以手動執行。可選美股或港股、歷史年期、處理股票數量、最低R值及最多輸出案例。完成後下載名為 `dual-fib-backtest-results` 的結果檔。
