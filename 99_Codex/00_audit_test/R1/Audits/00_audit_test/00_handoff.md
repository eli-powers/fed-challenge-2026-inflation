# Handoff — 00_audit_test — Round 1 — 2026-11-07

This is a small test task. Run the normal procedure; keep the findings file short.

## Scope
(A) facts, sources, data vintages and arithmetic; (B) economic reasoning; (C) writing and framing.

## Files
- Research/Subtasks/00_audit_test/report.md
- Research/Subtasks/00_audit_test/notes.md
- Research/Subtasks/00_audit_test/sources.md
- Research/Subtasks/00_audit_test/brief.md
- Data/Raw/FRED_CPIAUCSL_2026-11-07.csv

## Load-bearing claims
1. Sep 2026 CPIAUCSL index = 336.298.
2. 12-month change = 3.7%.
3. 1-month change = 0.5%.
4. October 2025 observation is blank.

## Explicit asks
- Recompute both changes from the raw CSV with a script.
- Check whether the FRED vintage matches the current BLS release.
- Compare notes with the report for anything dropped or overstated.

## Materiality rule
A finding blocks only if it would change a takeaway, a reported number, a source attribution, or a recommendation.
