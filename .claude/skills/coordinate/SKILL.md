---
name: coordinate
description: Run a research subtask for this project as coordinator. Propose an agent split, write and save briefs, launch subagents, verify their work against primary sources, save reports, and declare Round 1 done for the Codex audit. Use whenever Eli hands over a research subtask (literature, data, computation, fact-finding), or invokes /coordinate.
---

# Coordinating a research subtask

I am the coordinator (Opus 5.5). Eli directs; I run the subtask and verify it before anything reaches them. Follow the CLAUDE.md output and disagreement rules throughout.

## 1. Check the premise
If I disagree with the task's premise (an error, or a rival explanation that changes the task), say so and stop before planning any agents.

## 2. Propose the split (skip if Eli defined it)
Write a few conversational lines, then wait for confirmation:
- the agents, one line each: what it answers and which model;
- the folder names `02_Research/Subtasks/NN_name/` (continue the numbering);
- anything I'd push back on.

Model defaults:
- Sonnet 5.5 for routine work: landscapes, data pulls, factual lookups, brief consensus checks.
- Opus 5.5 for hard work: conceptual stress tests, reconciling papers, judgment-heavy synthesis.
- Eli's explicit choice overrides both.

If Eli specified the split, launch directly unless I have pushback.

## 3. Write and save briefs
Save each brief as `02_Research/Subtasks/NN_name/brief.md` before launching it. Use this structure:

```
You are a research [assistant|collaborator] for an undergraduate economics student preparing
UMD's College Fed Challenge national-finals presentation (an FOMC policy simulation; live Q&A with
Fed judges; data cutoff Nov 18, 2026). Explain technical concepts plainly. Today is <date>.
Prefer primary sources: official data releases, methodology pages, Fed publications, papers.

## Project context
<3–6 sentences: only what this agent needs. Not the whole STATE.md.>

## Your task
<numbered questions with the exact deliverable for each>

## Rules
- Verify every claim against a source you opened. Tag each one: [O] opened, [S] search snippet only, [2] secondary.
  Mark anything unconfirmed "unverified". Never invent numbers or citations.
- Use primary data, not summaries: pull FRED/BLS/BEA as CSV, and extract PDF text locally with Python (pypdf).
  Search extracted text with Python, not grep. A "not found" means unconfirmed, not absent.
- Save every series behind a reported number to 03_Data/Raw/<source>_<series>_<YYYY-MM-DD>.csv. Never edit files in 03_Data/Raw.
  If the number comes from an existing pipeline in 03_Data/pipelines/, cite that pipeline's raw file instead.
- Compute every number with a saved script in 02_Research/Subtasks/NN_name/code/, rerunnable from the
  project root. No hand calculations.
- Give every number its series ID, reference period, release date and vintage. State the horizon
  (m/m, 3m/6m annualized, y/y) and seasonal adjustment.
- Report data, trends and anything notable. Don't interpret what it means for policy unless asked.
- If a source is paywalled or blocked, say so. Don't reason from guesses about its contents.
- Keep an eye out for irregularities: a trend that looks off, an unusual reading (is it strange, and
  when did it last happen?), a series that disagrees with related ones. Log them under "Worth a look".
  This is not required; finding nothing is fine.
- Use the Write tool with the exact absolute paths below. Some paths contain spaces (e.g. `03_Data/pipelines/Price indexes/`).

## Output
Save to "<absolute path>/02_Research/Subtasks/NN_name/":
- notes.md: raw notes with URLs, as you go
- sources.md: every source, with URL, [O]/[S]/[2], and a one-line note on what it supports
Do NOT write report.md. Return the report as your final message, in this structure:
Findings · Worth a look (only if something stood out) · Spot-check examples (3–5, exact URL and location) · What to verify.
Write as a professional economist: concise, not an essay.
```

## 4. Launch
- Run independent agents in parallel, in the background.
- While they run, tell Eli in one line what's running. Don't predict results.
- If Eli asks for progress, check only file listings. Never read an agent's transcript file.

## 5. Verify each returned report
Report on each agent as it finishes. Never report unverified content.
1. Save the report to `report.md`. The first line must be `Status: Round 1 — NOT AUDITED`. Then the agent's report, then a `## Coordinator review` section.
2. Check the load-bearing claims against the primary source: every number in the findings, every direct quote, and every attribution that a takeaway depends on (usually 3–6 per report).
   - Data: pull the raw CSV myself.
   - PDFs: download to my scratchpad and extract with pypdf.
   - Paywalled sources: ask Eli to approve Chrome access or paste the text.
3. Fix small errors myself (a misquote, a date) and log each one in the coordinator review.
4. Send back material problems: a wrong number behind a takeaway, an unsupported core claim, or a task part left unanswered.
   - Message the same agent with the specific issue.
   - If that agent is gone (new session, compaction), launch a fresh one with the old `notes.md` plus the issue.
   - Re-verify whatever comes back.
5. The coordinator review lists: what I verified and how, what I corrected, what I could not check, any irregularities I noticed myself (Worth a look), and my interpretive notes. The interpretive notes stay in the file; I share them with Eli only when asked.

## 6. Declare Round 1
When every report is verified:
- Create `06_Audits/<task>/STATUS.md` with: task, the report paths, `Round: 1`, `Turn: Codex`, and the date.
- Hand off with the `audit-loop` skill. It writes the handoff file and runs Codex.
- Tell Eli only: **"Round 1 done: \<task\>."** No findings and no synthesis.

Skip the audit (with Eli's agreement) only for quick sanity checks that won't shape their thinking. In that case, label the report `Status: verified, not audited` and give the final report (step 7 format) directly.

## 7. After convergence
- Update each report's status line, e.g. `Status: Audited — converged R2`.
- Give Eli the final report in chat, per CLAUDE.md. Not an essay. It contains:
  - the specific answers to Eli's questions;
  - the data itself (headline, trends, anything notable), without interpretation unless asked;
  - flags: subagent issues, what couldn't be verified, and Worth a look items from subagents, my review and Codex.
  Questions go last.
- Update `STATE.md`: add the subtask to completed work (one line, pointing to its report) and update open threads.
- Append Worth a look items to `04_Ideas/questions_log.md`.
- If the subtask produced data that will need rerunning on future releases, propose promoting it into `03_Data/pipelines/` (Eli decides).
