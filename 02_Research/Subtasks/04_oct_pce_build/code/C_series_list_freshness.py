"""C_series_list_freshness.py: compare BLS series lists downloaded 2026-11-11 vs pipeline copies of 2026-09-27.
Run: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/C_series_list_freshness.py   (writes outputs/C_series_list_freshness.csv)"""
import csv, hashlib
P = "03_Data/pipelines/Price indexes/"
pairs = [("cu.item", P+"CPI/raw/bls_cu_item_2026-09-27.txt", "03_Data/Raw/bls_cu_item_2026-11-11.txt", "item_code"),
         ("cu.series", P+"CPI/raw/bls_cu_series_2026-09-27.txt", "03_Data/Raw/bls_cu_series_2026-11-11.txt", "series_id"),
         ("pc.series", P+"PPI/raw/bls_pc_series_2026-09-27.txt", "03_Data/Raw/bls_pc_series_2026-11-11.txt", "series_id"),
         ("wp.series", P+"PPI/raw/bls_wp_series_2026-09-27.txt", "03_Data/Raw/bls_wp_series_2026-11-11.txt", "series_id")]
def load(path, key):
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    hdr = [h.strip() for h in lines[0].split("\t")]; rows = {}
    for l in lines[1:]:
        if not l.strip(): continue
        f = [x.strip() for x in l.split("\t")]; rec = dict(zip(hdr, f)); rows[rec[key]] = rec
    return hdr, rows
out = []
for name, old, new, key in pairs:
    ho, ro = load(old, key); hn, rn = load(new, key)
    same_bytes = hashlib.sha256(open(old, "rb").read()).hexdigest() == hashlib.sha256(open(new, "rb").read()).hexdigest()
    added = sorted(set(rn) - set(ro)); dropped = sorted(set(ro) - set(rn))
    changed = [k for k in set(ro) & set(rn) if ro[k] != rn[k]]
    # field-level change summary
    from collections import Counter
    fc = Counter()
    for k in changed:
        for h in ho:
            if ro[k].get(h) != rn[k].get(h): fc[h] += 1
    print(name, "old", len(ro), "new", len(rn), "identical bytes", same_bytes, "added", len(added), "dropped", len(dropped), "changed", len(changed), dict(fc), "header same", ho == hn)
    print("  added sample", added[:8], "dropped sample", dropped[:8])
    out.append([name, len(ro), len(rn), same_bytes, len(added), len(dropped), len(changed), dict(fc), ";".join(added[:50]), ";".join(dropped[:50])])
with open("02_Research/Subtasks/04_oct_pce_build/outputs/C_series_list_freshness.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["file", "n_old_2026-09-27", "n_new_2026-11-11", "bytes_identical", "added", "dropped", "changed_fields_rows", "changed_by_field", "added_first50", "dropped_first50"]); w.writerows(out)
