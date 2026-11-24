import csv
import json
from decimal import Decimal
from pathlib import Path

root = Path(__file__).resolve().parent
raw = root / 'Data/Raw/FRED_CPIAUCSL_2026-11-07.csv'
with raw.open() as f:
    rows = {r['observation_date']: r['CPIAUCSL'] for r in csv.DictReader(f)}
latest = Decimal(rows['2026-09-01'])
results = {'levels': {d: rows[d] for d in ['2025-09-01', '2025-10-01', '2026-08-01', '2026-09-01']}}
for label, date in [('12_month', '2025-09-01'), ('1_month', '2026-08-01')]:
    change = (latest / Decimal(rows[date]) - 1) * 100
    results[label] = {'percent': str(change), 'rounded_one_decimal': str(change.quantize(Decimal('0.1')))}
results['latest_observation'] = max(rows)
output = json.dumps(results, indent=2) + '\n'
(root / 'recomputed.json').write_text(output)
print(output)
