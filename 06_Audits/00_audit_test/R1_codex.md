# Audit R1 — 00_audit_test — 2026-11-07
VERDICT: OPEN (R1-F01)

## Blocking findings
### R1-F01 · Arithmetic · Research/Subtasks/00_audit_test/report.md:8
- Claim as written: "1-month change: 0.5% (vs Aug 2026, 334.131)."
- Evidence: Copied CSV gives September 336.298 and August 334.131. `100 × (336.298 / 334.131 − 1) = 0.648548…%`, rounding to **0.6%**. Reproduced by `Codex/00_audit_test/R1/recompute.py`, output `recomputed.json`. The [BLS September release](https://www.bls.gov/news.release/archives/cpi_10142026.htm), opening paragraph and Table A, independently reports 0.6% SA; [current FRED](https://fred.stlouisfed.org/series/CPIAUCSL) confirms both levels.
- Why it matters: Changes a reported headline inflation number; this is an arithmetic error, not a vintage difference.
- Suggested fix: Replace 0.5% with 0.6%.

## Non-blocking findings
None.

## Judgment calls for Eli
None.

## Worth a look
None beyond the report's existing missing-observation flag.

## Checked and confirmed
- All handoff inputs copied under `Codex/00_audit_test/R1/`; claim-to-note/source mapping saved in `claim_map.md` and external checks in `external_evidence.md`.
- September 336.298, August 334.131, and September 2025 324.245 agree with the saved CSV; latest two also match current FRED. October 2025 is blank in the saved file.
- Script recomputation gives 12-month **3.717250844…% → 3.7%**, using SA levels as the brief specifies. BLS's headline 12-month figure is NSA and also rounds to 3.7%; do not conflate those definitions.
- Latest observation remains September 2026: FRED updated October 14 and current BLS release dated October 14 agree on period and monthly change. Next release is November 10, before the November 18 cutoff; refresh then. No currently available newer release was omitted.
- Notes' levels and blank-observation caveat were preserved. Both calculations were added in synthesis; only the monthly result fails. No unrequested economic interpretation, causal claim, quotation, or policy recommendation appears.
- Originals compared byte-for-byte with round copies after the audit; no differences.

## Not checked
- Entire historical CSV beyond the observations needed for this task; historical revisions are outside scope.
- Exact SA index levels in BLS's underlying database: verified against current FRED; BLS release text independently confirms the rounded monthly rate, not those exact levels.
- Actual November 7 retrieval timestamp cannot be authenticated from CSV contents alone. The dated file and notes state it, and current FRED levels agree.
- Cause of the October 2025 blank; the report claims only that it is blank in the saved file.
