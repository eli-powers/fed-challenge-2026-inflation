# 13_persistence_angle (Nov 15, 2026)

Status: verified by Claude, NOT AUDITED (quick read-across for Eli; no Codex round).

Question: is US inflation becoming persistent, which sources drive it, and what do base effects imply mechanically for the next prints? Data only; no rate recommendation.

Run from the project root (in order; P3 reads P2's output):
- `python3 -I "02_Research/Subtasks/13_persistence_angle/code/P1_base_effects.py"`: 12m paths Oct 2026 est. to Mar 2027 under constant-m/m scenarios (2% pace, 2018–19 average, last 6m, last 3m), plus the break-even pace (average m/m of the months leaving the window). Outputs: `P1_base_effect_paths.csv`, `P1_base_effect_summary.csv`, `P1_breakeven_pace.csv`.
- `python3 -I "02_Research/Subtasks/13_persistence_angle/code/P2_core_decomposition.py"`: core PCE 12m contributions from core goods (L375), housing (L153) and services ex energy & housing (Fisher removal of L153 from L376; reproduces BEA's published supercore, 3.595 vs 3.596 in Sep 2026). Weights are nominal shares at t−12 (an approximation; the residual is ≤ 0.01 pp). Outputs: `P2_core_decomposition*.csv`.
- `python3 -I "02_Research/Subtasks/13_persistence_angle/code/P3_transport_split.py"`: splits supercore into transportation services (L190) and the Logan measure, Sep 2025 → Feb 2026 → Sep 2026. Output: `P3_transport_split.csv`.

Inputs (no new downloads):
- BEA U20404/U20405 (vintage LastRevised 2026-10-29), from `03_Data/pipelines/Price indexes/PCE/raw/*_2026-11-10.json`.
- `11_slide3a_research/outputs/C_q6_underlying.csv` and `C_q6_logan_measure.csv`.
- `04_oct_pce_build/outputs/D_build_2026-10_summary.csv`: the Oct core m/m UMD est., 0.295.

Caveats:
- The scenarios are mechanical arithmetic, not forecasts.
- Oct 2026 values are estimates.
- The shutdown explanation for the soft Oct–Nov 2025 base months is unverified.
