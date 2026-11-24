# Coordinator notes (Nov 17, 2026)

Brief = `GO.md` (pre-approved by Eli; no Codex audit). S1/S2 were merged into one coordinator run, so there are no subagent briefs.

1. **Existing raw reused.** `03_Data/Raw/BEA_IO_shock_tagging_2026-11-14/` already holds the 2017 detail use, make, import and TR tables and the bridge, plus the AllTablesIO zip with summary use and make for 1997–2023. Only the summary import matrix was new: https://apps.bea.gov/industry/xls/io-annual/ImportMatrices_Before_Redefinitions_SUM_1997-2023.xlsx.
2. **The published TR is not domestic.** I rebuilt (I − A)⁻¹ from use/make with and without imports. BEA's TR column sums match the incl.-imports inverse (median gap 0.035), not the domestic one (0.253). So the domestic L is built from the before-redefinitions tables, because BEA's import matrices exist only before redefinitions.
3. **Negative domestic use.** 85 detail cells had U − M_imp < 0 (325414 biologics; S00402 used goods). They are clipped to 0.
4. **Summary tables beyond 2023.** I probed apps.bea.gov URL patterns for 1997-2024 summary use, TR, import and bridge files. All returned HTML (not found). The AllTablesIO zip URL now also returns HTML.
5. **PPI uses NAICS 2022 codes.** For example, 455 general merchandise and 456 health retailers carry history back to 2003 under the new codes. Some series start only in 2022 (449, 457, 486), so the rule walks up past them. The crosswalk is in `XWALK`.
6. **BLS key bug.** .env lines start with `export `. The first fetch therefore went unregistered: BLS truncated to 25 series and 10 years, and every series failed the completeness check, which wrongly triggered walk-ups. I fixed the parser, deleted those files and refetched (8 batches, 287 series, no BLS messages). Note: `10_slide2_research/code/M_upstream_by_shock.py` uses the same parser pattern, so it has probably been fetching unregistered too. That's fine for its 21 series, but worth knowing.
7. **Cross-checks.** PCU33441 Oct 2026 12m is 30.64, the same as M. Group PCE shares match G exactly.
