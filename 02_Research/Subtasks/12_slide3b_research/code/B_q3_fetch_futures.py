"""Q3 market check: NYMEX Brent Last-Day futures (BZ) contract closes, latest dates, via the Yahoo Finance chart API
(secondary source [2]; CME/ICE primary pages are blocked, see B_paywalled.csv). Saves raw JSON (never edited) to
03_Data/Raw/Yahoo_BZ_futures_current_2026-11-15/ and writes outputs/B_q3_futures_curve.csv.
Run: python3 -I 02_Research/Subtasks/12_slide3b_research/code/B_q3_fetch_futures.py"""
import sys, json, datetime
sys.path.insert(0, "./02_Research/Subtasks/12_slide3b_research/code")
from B_common import *
import pandas as pd

F = RAW / "Yahoo_BZ_futures_current_2026-11-15"
F.mkdir(parents=True, exist_ok=True)
codes = "FGHJKMNQUVXZ"
tickers = ["BZ=F", "BZZ26.NYM"] + [f"BZ{c}27.NYM" for c in codes] + [f"BZ{c}28.NYM" for c in "FGH"]
rows = []
for tk in tickers:
    fn = F / (tk.replace("=", "_") + ".json")
    if not fn.exists():
        try:
            fn.write_bytes(http_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{tk}", {"range": "1mo", "interval": "1d"}))
        except Exception as e:
            print("FAIL", tk, e); continue
    j = json.loads(fn.read_text())
    res = (j.get("chart") or {}).get("result")
    if not res:
        print("no data", tk); continue
    r = res[0]
    for ts, c in zip(r.get("timestamp", []), r["indicators"]["quote"][0]["close"]):
        if c is not None:
            rows.append({"ticker": tk, "date": datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d"), "close": round(c, 3)})
df = pd.DataFrame(rows)
last = df.groupby("ticker").date.max()
print(last.to_string())
d = df.date.max()
curve = df[df.date == d].copy()
mo = {c: i + 1 for i, c in enumerate(codes)}
curve["contract_month"] = curve.ticker.map(lambda t: None if t == "BZ=F" else f"20{t[3:5]}-{mo[t[2]]:02d}")
curve["source"] = "Yahoo Finance chart API daily close of NYMEX BZ (Brent Last Day Financial) contracts; secondary [2]"
curve.sort_values("contract_month", na_position="first").to_csv(OUT / "B_q3_futures_curve.csv", index=False)
print("curve date", d); print(curve.sort_values("contract_month", na_position="first").to_string())
# quarterly mean of contract months (contract month ~ delivery month; approximate mapping, stated)
c = curve.dropna(subset=["contract_month"]).copy()
c["q"] = c.contract_month.map(lambda m: quarter_of(m + "-01"))
print(c.groupby("q").close.agg(["mean", "count"]).round(2))
