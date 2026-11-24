---
name: audit-loop
description: Claude's side of the Codex audit loop for this project. Package a finished Round 1 for Codex, run Codex headless, respond to its findings, and drive the loop to convergence (max 3 rounds), escalating judgment calls to Eli. Use after the coordinate skill declares Round 1 done, when a Codex audit file arrives, or when Eli invokes /audit-loop.
---

# Audit loop (Claude side)

Codex's role and finding format are defined in `AGENTS.md`; read it if unsure. Eli does not relay messages: I run Codex myself and bring Eli in only for judgment calls or the final synthesis.

## Files, per task: `06_Audits/<task>/`
- `STATUS.md`: task, round, whose turn, open finding IDs, and a "Judgment calls for Eli" list. Keep it current, because it's how work resumes after a new session or compaction.
- `00_handoff.md`: what to audit, written by me.
- `R<n>_checksums.txt`: fingerprints of the original files before round n.
- `R<n>_codex.md`: Codex's findings.
- `R<n>_codex_done.txt`: Codex's final message, which signals completion.
- `R<n>_claude.md`: my response to each finding.

Codex copies the audited files into `99_Codex/<task>/R<n>/` and works only on those copies.

## 1. Write the handoff (Round 1)
`00_handoff.md` lists:
- **Scope:** (A) facts, sources, data vintages and arithmetic; (B) economic reasoning; (C) writing and framing.
- **Files:** for each subtask, `report.md` (my synthesis plus coordinator review), `notes.md`, `sources.md`, `brief.md`, any scripts in `code/`, and the raw files behind reported numbers (`03_Data/Raw/` or `03_Data/pipelines/<name>/raw/`).
- **Load-bearing claims:** the numbers, quotes and attributions that the takeaways rest on.
- **Explicit asks:**
  - compare the subagents' raw notes with my report, looking for translation errors and anything I dropped or overstated;
  - check what I verified;
  - check anything I said I could not verify.
- **Materiality rule:** a finding blocks only if it would change a takeaway, a reported number, a source attribution, or a recommendation. Codex classifies these as Blocking. Everything else is Non-blocking or Note.

## 2. Run a round
1. **Freeze the originals.** Make no edits to the audited files while Codex runs.
2. **Record checksums:** `shasum -a 256 <files> > "06_Audits/<task>/R<n>_checksums.txt"`.
3. **Run Codex in the background** (Bash `run_in_background: true`), sending the log to my scratchpad. I never read the log.
   ```
   perl -e 'alarm shift; exec @ARGV' 2400 \
   codex exec --skip-git-repo-check -m gpt-6.2-sol -c model_reasoning_effort='"medium"' -s workspace-write \
     -C "<project root>" -c web_search='"live"' \
     -o "<project root>/06_Audits/<task>/R<n>_codex_done.txt" \
     "Run audit round <n> for task <task>. Follow AGENTS.md. Handoff: 06_Audits/<task>/00_handoff.md. Prior round files: 06_Audits/<task>/R<n-1>_claude.md (if any)." \
     < /dev/null > "<scratchpad>/codex_<task>_R<n>.log" 2>&1
   ```
   - Quote every path. Some paths contain spaces (e.g. `03_Data/pipelines/Price indexes/`).
   - `< /dev/null` is required: piped stdin is appended to the prompt.
   - macOS has no `timeout` command, so the perl alarm kills a hung run after 40 minutes.
   - The model is GPT-6.2 Sol at medium reasoning (Eli's choice, Nov 17, 2026; was GPT-6.1 Sol). Confirmed working on Codex CLI 0.166.0. If a run returns `model_not_found`, run `codex update` and retry.
4. **When notified:**
   - If the exit is nonzero, or `R<n>_codex.md` is missing, check the last 20 lines of the log once and retry once. If it fails again, tell Eli and fall back to them triggering Codex in the app (same files, same protocol).
   - Re-run `shasum -a 256 -c` on the checksums. If any original changed, flag it to Eli and don't trust that round.
5. **Read only `R<n>_codex.md`.**

## 3. Respond to findings: `R<n>_claude.md`
For each finding ID, give exactly one of:
- **Accept:** make the fix in the original file and note the file and location.
- **Reject:** give evidence, ideally the primary source checked again. Reject on the merits only.
- **Escalate:** a judgment call (framing, interpretation, scope) is Eli's decision. Add it to the "Judgment calls for Eli" list in `STATUS.md`.

How each finding type is handled:
- **Factual, Source mismatch and Arithmetic** disputes are settled by checking the primary source again. If we still disagree after that, it becomes an escalation with both positions side by side.
- **Reasoning:** accept or reject on the merits. If it is still contested and Blocking, escalate it.
- **Judgment:** always escalated, never argued over in the loop.
- **Style:** advisory. I apply what I agree with, and it never blocks.

Non-blocking and Note findings may be closed with "noted" or fixed. Don't chase perfection.

## 4. Bring judgment calls to Eli (batched, once per round)
Send a short catch-up:
- where the task stands;
- each disputed item, with Codex's position, mine, and the decision needed;
- questions last.

Apply Eli's decisions, record them in `R<n>_claude.md`, then continue.

## 5. Converge or stop
- **Next round:** if Codex's verdict is OPEN (open Blocking findings), run round n+1. Codex re-copies the files and audits only the open IDs plus my fixes, not the whole report again.
- **Converged:** Codex's verdict is CONVERGED (no open Blocking findings) and every escalated item is decided.
  - Set `STATUS.md` to `Converged R<n>` with a two-line summary of what changed.
  - Collect Codex's "Worth a look" items from every round; they go into the flags of Eli's final report.
  - Return to step 7 of the `coordinate` skill.
- **Cap of 3 rounds:** if Blocking findings are still open after R3, stop. Give Eli a catch-up with each remaining dispute side by side and let them decide.
- Nothing is reported to Eli before convergence, except escalations.
