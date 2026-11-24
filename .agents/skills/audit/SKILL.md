---
name: audit
description: Run one audit round of Claude's research output for this economics project. Copy the files, verify numbers, sources, quotes, citations and reasoning against external evidence, and write a findings file with a verdict. Use when asked to "run audit round <n> for task <task>".
---

# Audit round procedure

You are the independent auditor described in `AGENTS.md`; follow its file boundaries and findings format. These principles come from verification practice in economics (the AEA Data Editor's reproducibility checks, referee norms, statistical-agency vintage control, IFCN fact-checking) and from evidence on LLM failure modes. The research behind them is described in Eli's separate research project on AI audit practices.

**Core rule:** a second model adds value only by checking against **external evidence**: source text, raw data, recomputation. Reading the draft and judging how plausible it sounds adds little. LLM judges favor fluent, longer text and their own style, and self-correction without external feedback often makes things worse. Every finding must point to evidence.

## 0. Set up
1. Read `06_Audits/<task>/00_handoff.md`, `STATUS.md`, and from round 2 on, `R<n-1>_claude.md`.
2. Copy every file named in the handoff into `99_Codex/<task>/R<n>/`. Work only on those copies. Download any sources and write any recomputation scripts into the same folder.
3. Round 2 and later: limit the audit to the open IDs and Claude's fixes. Skip to step 3.

## 1. Build the claim map (round 1)
Before judging anything, list the load-bearing claims in the synthesis: every reported number, quote, attribution and takeaway. Start from the handoff's list and add any it missed. For each claim, record the note line and the source that supports it.

Flag:
- a claim that appears only in Claude's synthesis, with no note or source behind it;
- a note whose caveat disappeared in the synthesis.

(This catches errors added during synthesis and subagent errors carried through unchanged.)

## 2. Verify, in priority order
Spend effort roughly in this order. The commonest real errors are mundane: range slips, wrong series, unit confusion.

1. **Numbers.** Re-derive every reported number from the saved raw file (`03_Data/Raw/` or `03_Data/pipelines/<name>/raw/`) or from the primary source. Where the subtask has a script in `code/`, rerun it from your copy and compare. Check:
   - units: % vs percentage points, levels vs changes, millions vs billions;
   - period and frequency;
   - seasonal adjustment;
   - real vs nominal;
   - rounding;
   - arithmetic, by recomputing with a script rather than by eye.
2. **Vintage.** Note the series ID and the retrieval or release date. If a conclusion depends on the figure, compare it with the current vintage. Revisions are normal, and a mismatch may be a vintage difference rather than an error. Say which it is.
3. **Sources and attributions.** Open the cited source. Confirm the source says what is claimed, and attributes it to whom the report says. A secondary article describing a paper is not the paper.
4. **Quotes.** Search the source text for the exact string. Mark each quote verbatim, close paraphrase, or not found. Extract PDF text with Python and search with Python. "Not found" means unconfirmed, not fabricated. Try other phrasings or pages before calling it a finding.
5. **Citations.** Confirm each cited work exists: authors, year, venue, URL or DOI. Confirm the cited finding is in it, ideally by page or table. Fabricated or misattributed citations are a known LLM failure.
6. **Verified vs inferred.** Check that the stated confidence matches the evidence. Look for hedges lost in summary ("suggests" becoming "shows"), one study presented as consensus, and the coordinator's inference presented as a source's claim.
7. **Disconfirming evidence.** For each decisive claim, ask what a skeptic would cite. Check whether the sources independently confirm the claim or all trace back to one origin. Check whether the framing leans toward the researcher's prior without support; sycophancy is a documented LLM bias.
8. **Economic logic.**
   - correlation presented as causation;
   - level vs change;
   - composition effects;
   - mismatched populations, periods or units of analysis (firm vs worker, firm-weighted vs employment-weighted);
   - conclusions stronger than the evidence.
9. **Scope and fit.** Did the work answer what the brief asked? Is any part unanswered?
10. **Writing and framing.** Is it clear, and is it accurate to the evidence? Does it give data rather than unrequested interpretation? Style findings are Non-blocking or Note unless they distort meaning.
11. **Worth a look (optional).** While checking, note irregularities the evidence raises: an unusual reading and when it last occurred, a trend that looks off, series that disagree. Log them under "Worth a look". They never block. Finding none is fine.

## 3. Later rounds
For each open ID:
- confirm the fix was made in the original. Read it from your fresh copy;
- check the fix introduced no new error;
- if Claude rejected the finding with evidence, either close it or answer with *new* evidence. Never repeat a position.

## 4. Classify with proportionality
The test comes from the AEA Data Editor's scale: **does it change a conclusion?**
- **Blocking:** changes a takeaway, a reported number, a source attribution, or a recommendation.
- **Non-blocking:** a real issue that doesn't change how the work reads.
- **Note:** optional.

Keep the Blocking list short and ranked. Following referee norms, a handful of essential points, with everything else as suggestions. If you find many Blocking issues, say the problem is systemic rather than listing every instance. Don't chase immaterial imperfections; some are expected.

Judgment calls (framing, interpretation, scope) go under "Judgment calls for Eli" with both readings. They never block.

## 5. Write the findings
- Write `06_Audits/<task>/R<n>_codex.md` in the format from `AGENTS.md`.
- Include **Checked and confirmed** and **Not checked**, so silence is never read as clearance. Keep the audit reproducible: say how each check was done (recomputation script path, source page, search string).
- Verdict: `CONVERGED` only if no Blocking findings remain open.
- Final message: one line with the verdict and the number of findings by severity.
