"""Sensitivity: October 2026 PPI component weights and contributions on BLS's December 2025 relative importances
(2026 tables, posted 06/11/2026) instead of the pipeline's December 2024 base (2025 tables).

Run from the project root:
    python3 "03_Data/pipelines/Price indexes/code/ppi_ri2026_sensitivity.py"
Reads only saved files; writes PPI/processed/ppi_oct_2026_ri2026_sensitivity.csv and _reconciliation.csv.
Nothing in the workbook or in the audited October files changes.

Method = retrieve_bls_baskets.retrieve_ppi() weight logic, with only the RI table and its repricing base changed:
  raw weight at date p = RI(base) x (component NSA level p / level at base) / (aggregate NSA level p / level at base),
  normalized within each basket; base = 2024-12 (pipeline) or 2025-12 (this sensitivity).
Component rates (1m / 3m ann. / 12m) are the audited ones in PPI/processed/components_2026-10.csv.
"""
import glob, json, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, P = ROOT / "PPI" / "raw", ROOT / "PPI" / "processed"
T, PERIODS = "2026-10", {"1m": "2026-09", "3m": "2026-07", "12m": "2025-10"}


def terminal_nodes(table, root):  # copied from retrieve_bls_baskets.retrieve_ppi
    rows = []; seen = 0
    for i in range(len(table)):
        code = str(table.iloc[i, 1]).strip()
        if code == root:
            seen += 1
            if seen == 2:
                break
        if re.fullmatch(r"(?:FD|ID)\d+", code):
            rows.append((code, str(table.iloc[i, 3]).strip(), float(table.iloc[i, 5]), i))
    codes = list(dict.fromkeys(x[0] for x in rows))
    return [x for x in rows if not any(y.startswith(x[0]) and len(y) > len(x[0]) for y in codes)]


def baskets(fd_file, id_file):
    fd, idd = pd.read_excel(fd_file, header=None), pd.read_excel(id_file, header=None)
    out = [("PPI Final Demand", c, n, w, "FD4") for c, n, w, _ in terminal_nodes(fd, "FD4")]
    idn = terminal_nodes(idd, "ID61")
    for root in ("ID61", "ID62", "ID63"):
        out += [(f"PPI Intermediate Demand {root}", c, n, w, root) for c, n, w, _ in idn if c.startswith(root)]
    return out


levels = {}
for f in sorted(glob.glob(str(RAW / "bls_api_ppi_baskets_2017_2026_batch*_2026-11-13.json"))):
    for s in json.load(open(f))["Results"]["series"]:
        levels[s["seriesID"]] = {f"{d['year']}-{d['period'][1:]}": float(d["value"]) for d in s["data"]
                                 if d["period"].startswith("M") and d["period"] != "M13" and d["value"] not in ("-", "")}
agg_of = lambda root: "WPUFD4" if root == "FD4" else "WPUID" + root[-2:]


def weights(bk, base):
    w = {}
    for h, p in PERIODS.items():
        raw = {}
        for idx, code, name, ri, root in bk:
            c, a = levels.get("WPU" + code, {}), levels[agg_of(root)]
            if all(k in c for k in (p, base)) and all(k in a for k in (p, base)):
                raw[(idx, code)] = ri * (c[p] / c[base]) / (a[p] / a[base])
        for idx in {b[0] for b in bk}:
            tot = sum(v for (i, _), v in raw.items() if i == idx)
            for (i, code), v in raw.items():
                if i == idx:
                    w[(h, idx, code)] = 100 * v / tot
    return w


old_bk = baskets(RAW / "bls_ppi_fd_components_relative_importance_2025_2026-11-10.xlsx", RAW / "bls_ppi_id_components_relative_importance_2025_2026-11-10.xlsx")
new_bk = baskets(RAW / "bls_ppi_fd_components_relative_importance_2026_2026-11-14.xlsx", RAW / "bls_ppi_id_components_relative_importance_2026_2026-11-14.xlsx")
assert [(b[0], b[1]) for b in old_bk] == [(b[0], b[1]) for b in new_bk], "basket structure changed between the 2025 and 2026 tables"
w_old, w_new = weights(old_bk, "2024-12"), weights(new_bk, "2025-12")

comp = pd.read_csv(P / "components_2026-10.csv")
for c in ("pct_1m_calc", "pct_3m_ann_calc", "pct_12m_calc", "weight_base_1m", "weight_base_3m", "weight_base_12m"):
    comp[c] = pd.to_numeric(comp[c], errors="coerce")
rows = []
for r in comp.itertuples():
    code = re.sub(r"^WP[SU]", "", r.component_id)
    d = dict(index=r.index_name, code=code, component=r.component_name, ri_dec2024=next(b[3] for b in old_bk if b[0] == r.index_name and b[1] == code),
             ri_dec2025=next(b[3] for b in new_bk if b[0] == r.index_name and b[1] == code))
    for h, rate in (("1m", r.pct_1m_calc), ("3m", r.pct_3m_ann_calc), ("12m", r.pct_12m_calc)):
        wo, wn = w_old.get((h, r.index_name, code)), w_new.get((h, r.index_name, code))
        d.update({f"w_{h}_dec2024": wo, f"w_{h}_dec2025": wn, f"rate_{h}": rate,
                  f"contrib_{h}_dec2024": None if wo is None or pd.isna(rate) else wo * rate / 100,
                  f"contrib_{h}_dec2025": None if wn is None or pd.isna(rate) else wn * rate / 100})
    rows.append(d)
out = pd.DataFrame(rows)
# check: the Dec 2024 recomputation reproduces the audited weights
for h, col in (("1m", "weight_base_1m"), ("3m", "weight_base_3m"), ("12m", "weight_base_12m")):
    diff = (out[f"w_{h}_dec2024"].values - comp[col].values)
    assert abs(pd.Series(diff).abs().max()) < 1e-9, f"{h} weights do not reproduce the audited file"
out.to_csv(P / "ppi_oct_2026_ri2026_sensitivity.csv", index=False)

rec = pd.read_csv(P / "reconciliation_2026-10.csv")
rec["published_change"] = pd.to_numeric(rec.published_change, errors="coerce")
hz = {"1m SA": "1m", "3m annualized SA": "3m", "12m NSA": "12m"}
rr = []
for r in rec.itertuples():
    h = hz[r.horizon]; g = out[out["index"] == r.aggregate]
    s_old, s_new = g[f"contrib_{h}_dec2024"].sum(), g[f"contrib_{h}_dec2025"].sum()
    rr.append(dict(aggregate=r.aggregate, horizon=r.horizon, published=r.published_change, sum_contrib_dec2024=s_old, gap_dec2024=s_old - r.published_change,
                   sum_contrib_dec2025=s_new, gap_dec2025=s_new - r.published_change))
pd.DataFrame(rr).to_csv(P / "ppi_oct_2026_ri2026_sensitivity_reconciliation.csv", index=False)
print("written; Dec 2024 recomputation reproduces the audited weights exactly")
