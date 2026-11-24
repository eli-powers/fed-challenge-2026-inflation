# Notes, Agent C (forecast pipeline and scenario results), 2026-11-15

## Run order (project root, `python3 -I`)
1. `03_Data/pipelines/forecast_3b/code/fetch_inputs.py` writes `raw/2026-11-15/`. All checksums match A's and B's raw copies in `03_Data/Raw/*_2026-11-15/` (medianLevel, Dispersion_1, RBRTEd, aug26, feb26, nov26), and the PCEPILFE values are identical.
2. `.../code/forecast.py --spf 2026Q3` writes `processed/*_2026Q3.*`.
3. `.../tests/test_zero_gap.py` writes `outputs/C_test_output.txt` (all pass, exit 0).
4. `02_Research/Subtasks/12_slide3b_research/code/C_q6_results.py 2026Q3` writes `outputs/C_q6_results.csv`, `C_q6_axis_compare.csv`, `C_q6_sensitivity.csv`, `C_q6_jumpoff.md` and `C_q6_jumpoff_decomposition.csv`.
5. `.../code/C_q6_handcheck.py` writes `outputs/C_q6_handcheck_output.txt` (MATCH; max |diff| 4e-7 pp, from the 6-decimal CSV).

## Design decisions (all follow the coordinator's binding notes)
- **Baseline path:**
  - 2026Q1 to Q3 are actual: PCEPILFE realtime 2026-10-29, quarterly average of the SA index, q/q annualized.
  - 2026Q4 to 2027Q3 are the SPF 2026Q3 medians. 2027Q4 = 2.2679 is derived from COREPCEB (A's formula).
  - The SPF's published 2026Q3 (2.70) is kept as a reference column, `spf_median_qq_ann`.
- **Gap start:** the survey quarter (2026Q3). The 2026Q3 gap enters L, but **2026Q3 is not adjusted** because it is actual. The first applied change is 2026Q4, equal to 4·(L_26Q4 − L_26Q3). So the 2026 Q4/Q4 adjustment (+0.008 to +0.058 pp) is smaller than B's L_26Q4 (0.03–0.08).
- **Gap units:** 100·ln, as B's mapping recommends. The simple % gap is also stored.
- **Compounding:** (1+s/100) = (1+b/100)·exp(4ΔL/100), coded as b + adj, so a zero gap returns b bit-for-bit. Against B's additive a_qa this scales the adjustment by (1+b/100), about ×1.024, which is why P1 post 2027 Q4/Q4 is +0.527 here vs B's +0.513.
- **Oil assumption proxy:** the latest STEO released **on or before** the SPF deadline, using release dates parsed from EIA's outlook page. For Q3 that is Aug STEO, released 08/11 on the deadline day itself. Sensitivity rows: the previous vintage (Jul STEO) and a futures hybrid (Aug-11 BZ closes for 2027, secondary [2], with the Aug STEO for 2026Q3–Q4 since those contracts expired).
- **Oil paths:** rebuilt from raw with B's rules. They match `B_q3_oil_paths.csv` within 0.0005 $/bbl and 0.0008 log points, which is B's 3-decimal rounding.
- **Regimes:** pre and post are central. persistence_only is kept as backup rows only. Responses are copied from B's table (`config/regime_response.csv`, sha256 in `config/PROVENANCE.md`).
- **Q4 SPF readiness:** a dry run on a synthetic Q4 row (made-up numbers, scratch only) runs end to end. It publishes 2027Q4 (no derivation), the gap starts 2026Q4, the matched proxy is nov26, and `write_compare` works. The real fetch will also pull oct26 (the previous vintage). Not tested on a real Q4 file.
- **Fetch failure path:** tested by injecting a bad Brent URL. The script exits with status 1, prints "FETCH FAILED at step 'Brent daily' ... previous input: raw/2026-11-15", and removes the staging folder.
- **Not done:** the optional headline mapping (B skipped it too), and the SPF microdata annual IQR (not "published"; A has it).

## Q6 key numbers: SPF 2026Q3 baseline, Aug-STEO proxy, Brent to Nov 11 (core PCE, SA, %)

| Cell | 2026Q4 q/q ann. | 2027Q4 q/q ann. | 2026 Q4/Q4 | 2027 Q4/Q4 |
|---|---|---|---|---|
| Baseline (actual + SPF) | 2.616 | 2.268 | 3.082 | 2.400 |
| P1 STEO × pre | 2.812 | 2.346 | 3.131 | 2.399 |
| P1 STEO × post | 2.732 | 3.137 | 3.111 | 2.927 |
| P2 $110 × pre | 2.848 | 2.422 | 3.140 | 2.482 |
| P2 $110 × post | 2.765 | 3.598 | 3.119 | 3.163 |
| P3 Hormuz+$25 × pre | 2.721 | 2.417 | 3.108 | 2.418 |
| P3 Hormuz+$25 × post | 2.647 | 2.785 | 3.090 | 2.721 |
| Spread (max − min) | 0.202 | 1.252 | 0.051 | 0.764 |

SPF published Q4/Q4 medians: 2026 3.2876; 2027 2.4004.

**Axis comparison** (range in pp):

| Measure | Across oil paths, pre held | Across oil paths, post held | Across regimes: P1 | P2 | P3 |
|---|---|---|---|---|---|
| 2027Q4 q/q ann. | 0.076 | 0.814 | 0.791 | 1.176 | 0.368 |
| 2027 Q4/Q4 | 0.083 | 0.442 | 0.528 | 0.681 | 0.303 |

## Worth a look
1. **Jump-off gap dwarfs the 2026Q4 oil adjustment.** Given our Oct estimate (m/m 0.295), the SPF's 2026Q4 of 2.6158 requires Nov and Dec core m/m of 0.053% each. The six cells require 0.061–0.110%. Holding Oct's pace through Nov–Dec gives 2026Q4 at 3.61 and 2026 Q4/Q4 at 3.33, while the cells sit at 3.09–3.14 Q4/Q4. The 2026Q4 oil adjustments (+0.03 to +0.23 pp) are small next to that ~1 pp gap. Source: `C_q6_jumpoff.md`.
2. **The 2027 adjustment comes mostly from oil moves that have already happened.** In the post regime, the 2026Q3–Q4 gap steps alone account for 92–134% of the 2027 Q4/Q4 adjustment, and the fully realized 2026Q3 step alone for 35–84%. The 2027 regime spread is therefore mostly about how persistent the past spike is, not the 2027 oil path.
3. **2026Q4 is higher under pre than post in every path** (e.g., P1 2.81 vs 2.73). This comes from the note's post line dipping at k=1 (0.0184 → 0.0105). It looks odd on a slide.
4. **2027Q4 q/q post spikes** (P2 3.60, P1 3.14) because of the k=4 jump in the post response (0.0896 → 0.185) hitting the large 2026Q4 gap step. Quarterly paths are lumpy, so lead with Q4/Q4.
5. **The assumption proxy moves the post cells about as much as the oil-path axis does.** For P1 post 2027 Q4/Q4: Aug STEO 2.927, Jul STEO 3.156, futures hybrid 2.826, a span of 0.33 pp (`C_q6_sensitivity.csv`).
6. **P3 + $0 is the only cell below the baseline:** post 2027 Q4/Q4 2.250 and 2027Q4 q/q 1.961.
7. **P1 × pre 2027 Q4/Q4 is −0.002 vs baseline.** The 2027 fall in the gap (32.8 → 16.9 log points) offsets the lagged rise.
8. **On the Q4 SPF, P1's gap becomes about 0 by construction** if the deadline is on or after Nov 10 (P1 = latest STEO = matched proxy). The grid will then shift between vintages partly because the proxy changes, not only the forecast. Seen in the synthetic dry run only.
9. **The SPF 2026Q3 median (2.70) missed the actual (2.47) while Brent ran $11 above the assumption.** In the post regime the model's own 2026Q3 impact is only +0.09 pp annualized, so the miss is not oil-related in this framework.
