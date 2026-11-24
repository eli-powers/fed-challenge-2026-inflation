# forecast_3b: slide 3B core PCE scenario pipeline

**What it does.** Takes an outside forecast (the Philadelphia Fed SPF median path for core PCE), adjusts it
for oil, and labels every step. Two axes: **oil path (3) x pass-through regime (2) = 3x2 grid**, through
2027Q4. **These are scenarios, not probabilities.** Nothing is weighted unless Eli sets the hook below.

Built 2026-11-15 (slide 3B research, Agent C). Inputs verified by the coordinator in
`02_Research/Subtasks/12_slide3b_research/report_A.md` and `report_B.md`.

## Rerun on the Q4 2026 SPF (exact commands, from the project root)

```bash
python3 -I 03_Data/pipelines/forecast_3b/code/fetch_inputs.py              # new raw/<today>/ folder
python3 -I 03_Data/pipelines/forecast_3b/code/forecast.py --spf 2026Q4      # Q4 grid
python3 -I 03_Data/pipelines/forecast_3b/code/forecast.py --spf 2026Q3 --compare   # Q3 grid + vintage_compare.csv
python3 -I 03_Data/pipelines/forecast_3b/tests/test_zero_gap.py --spf 2026Q4
```

No code or config edits are needed for this. The SPF files are cumulative, so the new raw folder still holds the
Q3 row. `fetch_inputs.py` reads the Q4 deadline from `spf-release-dates.txt` and downloads the matching STEO
vintage (the latest one released on or before that deadline) plus the one before it.

For the Q4 survey:
- COREPCE2..6 cover 2026Q4..2027Q4, so 2027Q4 is published and not derived.
- The gap starts in 2026Q4.
- If the deadline is on or after Nov 10, the Nov STEO is the matched proxy. P1 (the latest STEO) then has a near-zero gap by construction.
- The futures-proxy sensitivity is skipped: no `config/assumption_futures_2026Q4.csv` exists.
- `Dispersion_1.xlsx` may lag by a release. If it has no Q4 row, the fan omits the SPF IQR and the script says so.

**Tested only on a synthetic Q4 row** (scratch copy, made-up numbers), not on a real Q4 file, because none
existed on Nov 15.

On Nov 18 (the data cutoff), rerun all four commands. EIA's next Brent daily release is Nov 18 (per Agent B), so
the 2026Q4 splice will pick up the new days.

## Files

| Path | What |
|---|---|
| `code/fetch_inputs.py` | Downloads into `raw/<YYYY-MM-DD>/`, adding `_2`, `_3` if that folder exists; it never overwrites. Files are staged in a hidden folder and validated first. **On any failure it deletes the staging folder, exits with status 1 and names the previous raw folder, which stays the input.** Writes `manifest.json` (url, bytes, sha256, time). |
| `code/forecast.py` | CLI: `--spf`, `--raw`, `--compare`. Writes `processed/`. Holds the `REGIME_WEIGHT_POST` hook. |
| `code/parsers.py` | SPF/STEO/FRED/EIA parsers, copied from the subtask's `A_common.py` (Agent A) with small generalizations (listed in its docstring). |
| `config/` | Fixed inputs with provenance and checksums (`config/PROVENANCE.md`): the oil note's response table, the oil path rules, and two secondary futures files for sensitivity rows. |
| `tests/test_zero_gap.py` | Plain-assert tests: zero gap returns the baseline exactly; a constant +10% gap reproduces the response function; linearity. |
| `raw/`, `processed/`, `archive/` | Pipeline convention (`03_Data/README.md`). Move superseded `processed/` files to `archive/<date>/` before a rerun if you want to keep them; the script overwrites the same-name outputs. |

### Inputs (`raw/<date>/`) and provenance

| File | Source | Used for |
|---|---|---|
| `medianLevel.xlsx` (sheet COREPCE), `Dispersion_1.xlsx`, `spf-release-dates.txt` | Philadelphia Fed SPF | Baseline median path, published P25/P75 (quarterly horizons only), survey deadline |
| `page_steo_outlook.html` | EIA STEO page (archive list with release dates) | Choosing the STEO vintage that matches the SPF deadline |
| `<vintage>_base.xlsx` | EIA STEO archive, sheet `2tab`, series `BREPUUS` (Brent spot, $/bbl) | The latest vintage drives P1. The matched vintage is the oil assumption proxy, and the one before it is a sensitivity. `feb26` (the last pre-war vintage) drives P3 |
| `EIA_RBRTEd.xls` | EIA daily Brent spot FOB | Actual quarters, and the splice for the current quarter |
| `PCEPILFE_observations.json` | FRED (BEA core PCE price index, SA) | Actual quarters; Q4/Q4 |

`processed/metadata_<spf>.json` lists every input path with its sha256, the vintages, the run time and the parameters.

## The math

```
gap      g_s = 100 * ln(Brent_scenario_s / Brent_assumed_s),   s = survey quarter .. 2027Q4   (log points)
level    L_t = sum_{s<=t} R_{t-s} * (g_s - g_{s-1}) / 10        (g before the survey quarter = 0;
         R_k = cumulative % core price-level response k quarters after a permanent 10% oil rise; R held at R_12 beyond k=12)
q/q ann. (1 + s_t/100) = (1 + b_t/100) * exp(4 * (L_t - L_{t-1}) / 100)    for forecast quarters only
Q4/Q4    Q4/Q4_Y = prod_{q in Y} (1 + x_q/100)^(1/4) - 1, using the quarterly path (actual quarters + scenario quarters)
```

Here b is the baseline: the SPF median, with actual core PCE in place of the SPF for quarters that are already
published. **Actual quarters are not adjusted.** For the Q3 survey that means 2026Q3 (actual 2.47 vs SPF 2.70).
Its share of L is treated as already in the data, so the first applied adjustment is 2026Q4, equal to
4·(L_26Q4 − L_26Q3). This is why the 2026 Q4/Q4 adjustment here (0.01–0.06 pp) is smaller than B's
L_26Q4 − L_25Q4 (0.03–0.08 pp).

Each output shows both Q4/Q4 numbers:
- `scenario_qq_ann` on the `q4q4` rows is built from the quarterly path;
- `spf_published_q4q4` is the SPF's own published annual median.

They differ for two reasons: the quarterly and annual SPF medians come from different respondents, and the
actual quarters were revised after the survey.

Under the Q3 survey, 2027Q4 is not published. It is derived from the 2027 Q4/Q4 median, so the
baseline-path 2027 Q4/Q4 equals the published 2.4004 by construction.

**Regimes (from the oil note's Figure 2 data table):**
- central: `pre` = pre-pandemic; `post` = post-pandemic (stronger persistence and pass-through);
- backup only: `persistence_only`.

**Oil paths** (`config/oil_path_rules.json`):

| Path | Central | Alternates (sensitivity) |
|---|---|---|
| P1 | latest EIA STEO | Nov-13 futures curve [secondary] |
| P2 | $110 flat. Bowman (Nov 10): Brent moved "up to and above $110 per barrel" in late October | Oct-2026 average, flat |
| P3 | pre-war trend (Feb-2026 STEO) + $25. Waller (Nov 10): "$20 to $30 a barrel" | +$20, +$30, +$0; Jan–Feb 2026 spot mean + $25 |

All paths use actual Brent through the last EIA observation, and rules start the next day.

## Outputs (`processed/`)

| File | Content |
|---|---|
| `scenario_grid_<spf>.csv` | Long format. `is_central` = the 6 grid cells; every other row is sensitivity. Columns: spf_vintage, oil_path, oil_variant, is_central, regime, assumption_proxy, horizon (`qq_ann` or `q4q4`), quarter, status (actual/forecast), brent_usd, assumed_brent_usd, baseline_qq_ann, spf_median_qq_ann (the SPF as published, incl. its 2026Q3), oil_gap_pct (**100·ln**, the value used), oil_gap_simple_pct, level_adj_pct (L; on Q4/Q4 rows the model's L_Q4 − L_Q4(prev), part of which can fall in an actual quarter), adj_qq_ann_pp (applied), scenario_qq_ann, spf_published_q4q4 |
| `fan_<spf>.csv` | Per quarter and Q4/Q4: baseline, min/max across the 6 central cells, the cells at the extremes, and the SPF P25/P75 where published. **A scenario range, not a probability fan.** |
| `sensitivity_proxy_<spf>.csv` | The central oil paths under alternative assumption proxies: the previous STEO vintage, and futures at the deadline (2027 only, from secondary data; 2026 quarters use the matched STEO). |
| `oil_paths_<spf>.csv`, `oil_assumption_<spf>.csv` | Quarterly Brent per variant (with its kind: actual, splice or rule) and the assumed paths. |
| `metadata_<spf>.json` | Inputs with checksums, vintages, timestamp, parameters, caveats. |
| `vintage_compare.csv` | Only with `--compare` when both 2026Q3 and 2026Q4 surveys are present: baseline, adjustment and scenario per central cell for each vintage, plus later minus earlier. |

## Regime-weight hook

In `code/forecast.py`:

```python
REGIME_WEIGHT_POST = None  # Eli's input after slide 3A; None = no weighting
```

Leave it at `None` and no weighted path is produced. If Eli sets a number w in [0, 1], the script adds rows with
regime `weighted_post_<w>`, computed as L = w·L_post + (1 − w)·L_pre for each oil path. This is Eli's
judgment, made after slide 3A; the pipeline does not pick a regime.

## Caveats (state them on the slide or in Q&A)

1. **The oil note is a five-economy panel average** (De Michelis et al., FEDS Note, Nov 9 2026), not a U.S.
   estimate. The authors treat the post-pandemic projection as an **upper bound**.
2. **The baseline's own oil assumption is unpublished.** The SPF asks for none, so the matched STEO vintage
   is a proxy. The Aug STEO sits about $8/bbl below the Aug-11 futures curve in 2027, and a lower assumed path
   makes every gap larger. See `sensitivity_proxy_<spf>.csv`.
3. **Scenarios, not probabilities.** The range in `fan_<spf>.csv` is a min/max across scenario cells, not a
   confidence band.
4. **Never present the note as evidence of changed price-setting behaviour.** It reports how the estimated
   oil-to-core coefficients differ from 2021Q1 on (a dummy interaction), nothing more.
5. The responses are read from the note's Fig. 2 table. The pre and persistence-only lines cannot be
   reconstructed from Table 2's pass-through sum (Agent B, Worth a look #1), and the response is lumpy (a dip at
   k=1, a jump at k=4). So quarterly annualized adjustments are uneven. Lead with Q4/Q4.
6. "10%" in the note is read as 10 log points. If it means 10% simple, scale every adjustment by about ×1.049
   (unverified).
7. The 2026Q4 Brent splice assumes EIA has no observations on Thanksgiving and Dec 25.
