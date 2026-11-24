# Slide 2 verbal-cue candidates (Agent D, Nov 15, 2026): all PENDING Eli

Short spoken lines, each with its figure and source. "est." = UMD October estimate. Files are in `10_slide2_research/outputs/` unless a path is given. Not audited.

| # | Candidate line | Figure(s) | Source (file → row / cell) |
|---|---|---|---|
| V1 | "Breadth was already high before the oil shock; what the shock changed is how hot the exposed items run." | Energy-tagged 12m breadth 71.3 (Feb) → 67.0 (Sep) → 73.3 (Oct est.); mean 12m rate 3.14 → 3.92 → 4.30 | `D_preshock.csv`: `group=energy, horizon=12m`, months 2026-02 / 09 / 10 |
| V2 | "Outside the hospitals, the untagged share above 3% has not moved since February." | 57.9 → 57.9 → 57.8 | `D_tag_variants.csv`: `variant=untagged ex hospitals 184-186, horizon=12m` |
| V3 | "At any line from 2 to 4 percent, breadth is 11 to 25 points above 2018–19." | 12m core: +15.7 (2%), +23.0 (2.5%), +25.4 (3%), +11.0 (3.5%), +11.2 (4%) | `D_threshold_sensitivity.csv`: `scope=core, horizon=12m`, column `sep_minus_2018_19_pp` |
| V4 | "The typical item is running 3.3 percent, a point above 2018–19." | Weighted median 12m core leaf rate 3.26 (Sep, Oct est.) vs 2.33 | `D_distribution.csv`: row `12m, weighted p50` |
| V5 | "A third of core spending sits between 3 and 3.5 percent, so one month's move in breadth tells you little." | 35.4% of core weight in (3.0, 3.5], Sep 12m | `D_band_summary.csv`: `2026-09, 12m, (3.0, 3.5]` |
| V6 | "All of October's drop, and more, is three hospital lines; take them out and breadth rose." | −8.72 of −6.59 pp; ex hospitals 56.86 → 59.24 | `A_q3_oct12m_drop_by_tag.csv`; `D_exclusions.csv`: `ex_hospitals_184_186, 12m` |
| V7 | "Last October's Medicare reset was the largest on record: 6 percent against a usual 1 to 4." | WPU5121010111 Oct 2025 +5.96%; 2016–24 Octobers +0.8 to +4.3 | `B_q7_hospital_octobers.csv` |
| V8 | "It would take a hospital revision more than twice the usual size to change the October breadth result." | Needs +0.26 pp to NSA; mean absolute revision 0.09; 1 of 22 that large | `D_hospital_flip.csv` |
| V9 | "The trimmed mean and breadth disagree because the trimmed mean cuts the big months of items that are running hot." | Above-3% leaves: 33% of leaf-months cut from top; 4.80% all months vs 2.65% kept; 12m-rate trim 2.98% vs Dallas 2.26% | `D_trimmed_above3_fate.csv`; `D_trimmed_reconcile.csv` |
| V10 | "We reproduce the Dallas trimmed mean to the hundredth." | 2.265 vs 2.26 (12m Sep); 2.848 vs 2.84 (1m) | `D_trimmed_reconcile.csv` rows 1–3 |
| V11 | "Energy is 4 percent of spending and food mostly runs below 3, so headline and core breadth are nearly the same." | Headline 12m 59.8 vs core 60.6 (Sep); energy +3.6 pp, food +2.2 pp | `D_headline_mechanics.csv`: `2026-09, 12m` |
| V12 | "We match Waller's 70 percent only on a spending-weighted basis; a simple count gives 63." | 70.8 weighted vs 63.1 count, core services 12m Sep | `B_q6_waller.csv` |
| V13 | "Stage 1 producer prices hit a record in October even as their energy part turned negative." | WPSID51 172.6, +0.55% m/m; energy contribution −0.25 pp | `C_q8_ppi_stages.csv`; `C_q8_energy_contributions_windows.csv` |
| V14 | "Trucking rose 3.9 percent in October while diesel fell 7.9." | PPI WPU3012 +3.9; WPS057303 −7.9 | `C_q11_confirming_items.md`, item 2 table |

**Do not use (failed stress test):**
- "Headline breadth rises mechanically in an energy shock." Our data show headline ≤ core at 12m (V11).
- "Bowman says it's concentrated." She says pressures "may be broadening" (saved speech, para 4).
- Any Sep → Oct "narrowing" or "widening" claim from the 3% number alone: the sign flips with the cutoff (`D_threshold_sensitivity.csv`, `change_pp`).
