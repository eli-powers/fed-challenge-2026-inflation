"""Core PCE (PCEPILFE) index m/m as of the Aug-26 vs Sep-30 2026 vintages (ALFRED file in 03_Data/Raw) -> shows which months the annual update revised.
Run from project root: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/B_vintage_revision_check.py"""
import json
def vint(series,asof):
    d=json.load(open(f"03_Data/Raw/ALFRED_{series}_all_vintages_2026-11-11.json"))["observations"]
    return {o["date"][:7]:float(o["value"]) for o in d if o["realtime_start"]<=asof<=o["realtime_end"] and o["value"]!="."}
for s in ["PCEPILFE","PCEPI"]:
    a,b=vint(s,"2026-09-29"),vint(s,"2026-09-30")
    print(s,"month  m/m(%) old_vintage(2026-09-29)  new_vintage(2026-09-30)  level_old level_new")
    ms=sorted(a)
    for i,m in enumerate(ms):
        if m>="2025-11" and i>0 and m in b and ms[i-1] in b:
            p=ms[i-1]
            print(f"  {m}  {100*(a[m]/a[p]-1):6.3f}  {100*(b[m]/b[p]-1):6.3f}   {a[m]:.3f} {b[m]:.3f}")
