---
name: aea-report-finalize
description: Use when finishing an AEA Data Editor replication review — the RA (or transparency-editor agent) has already filled out REPLICATION.md in an aearep-NNNN repo and it's time to run aeareq, write the SUMMARY, and double-check the replicator's findings before the editor approves. Triggers on requests like "finalize this report", "write the summary", "run the editor pass", "run aeareq", "prepare this for approval", or being asked to review/finish a REPLICATION.md in an aearep-NNNN directory.
allowed-tools: Bash(git rev-parse *) Bash(git log *) Bash(git tag *) Bash(git merge-base *) Bash(git show *) Bash(grep *) Bash(head *) Bash(cut *) Bash(ls *) Bash(source *) Bash(python3 *)
---

# AEA Replication Report — Editor's Finishing Pass

You are acting as the AEA Data Editor's finishing pass on a replication
review. An RA (or an automated agent) has already run the replication code
and filled out `REPLICATION.md` — everything except `## SUMMARY`. Your job
mirrors what the human editor actually does: consolidate the `[REQUIRED]`/
`[SUGGESTED]` tags, independently sanity-check the RA's findings, and draft a
short, non-chatty summary. **You do not approve or publish anything** —
sign-off is a human action (see Restrictions).

Do not hard-code paths, ticket numbers, or canned language in your own
reasoning — derive everything (repo root, deposit directory, phrase
library) from the repo you're actually working in, since these drift across
repos and template versions.

**Whenever this skill needs to ask the user something** — confirming
whether to touch an already-approved repo (Step 1), a judgment call from the
verification pass (Step 3), or whether to force `aeareq` past a missing
marker (Step 4) — pose it as concrete, clickable options (e.g. via
`AskUserQuestion`), not a vague prose question waiting on free-text
approval. This applies whether the session is in a terminal or the VS Code
panel.

**Normal path vs. revision path**: Steps 2–6 below, on their own, are the
complete first-round finishing pass and match the LDI Lab's approver
guidance for an original (non-revision) report — see
[13-1-approving-issues-original.md](https://github.com/labordynamicsinstitute/ldilab-manual/blob/main/13-1-approving-issues-original.md).
A first-round case never touches anything marked "revision rounds only"
below. Revision rounds (detected in Step 1/1b) add extra requirements at
Steps 1c, 3, and 5, per
[12-jira-revision-guidance.md](https://github.com/labordynamicsinstitute/ldilab-manual/blob/main/12-jira-revision-guidance.md)
(replicator-facing) and
[13-2-approving-issues-revision.md](https://github.com/labordynamicsinstitute/ldilab-manual/blob/main/13-2-approving-issues-revision.md)
(approver-facing).

## Step 0 — Locate the repo and its parts

```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"
ls -d [0-9]*/ 2>/dev/null   # the openICPSR numbered deposit directory
```

Confirm `REPLICATION.md` exists at `$REPO_ROOT`. If it doesn't, stop — this
isn't a replication-template repo, or you're in the wrong directory.

## Step 1 — Gate: is this already approved, and is a follow-up round underway?

```bash
git log --oneline | grep -E '#comment (Approved\. )?Ready to submit'
```

**No match** — never approved. This is a first-round case; proceed to Step 2.

**One or more matches** — take the most recent one as `LAST_APPROVAL_SHA`
(pre-approved for this skill — see frontmatter):

```bash
LAST_APPROVAL_SHA=$(git log --oneline | grep -E '#comment (Approved\. )?Ready to submit' | head -1 | cut -d' ' -f1)
```

and check for evidence of activity *after* it:

```bash
git log --oneline "${LAST_APPROVAL_SHA}..HEAD"
git tag -l 'update*'
```

Look for the pipeline's own automated markers in that post-approval range —
this is the real trail the tooling leaves behind when it re-runs for a
revision (concretely observed on `aearep-9147`): commits like
`AEAREP-NNNN #comment [skip ci] Adding code from <deposit-id>`,
`... Adding generated files and logs`, `[skip ci] Downloaded Jira
attachments for AEAREP-NNNN`, `[skip ci] Update of tools`, or an `updateN`
tag whose commit is a descendant of (not equal to) `LAST_APPROVAL_SHA`
(`git merge-base --is-ancestor $LAST_APPROVAL_SHA <tag>` confirms "after",
then check the tag's SHA isn't `LAST_APPROVAL_SHA` itself).

- **No such evidence** → genuinely finalized. **Stop.** Tell the user this
  repo already has an approval commit with nothing after it, and ask before
  touching it further.
- **Evidence found** → a revision round is in progress, not a finished case.
  Do **not** stop — but don't trust the repo's own ticket references for
  what to call "the current case." Continue to Step 1b before proceeding.

## Step 1b — Confirm the current ticket via Jira (only if Step 1 found a revision in progress)

AEA opens a **new Jira ticket for each revision round**, while the work
continues in the same physical repo — the repo's own history (`config.yml`'s
`jiraticket:` field, every commit message) keeps referencing the *original*
round's ticket forever and never mentions the new one. (Confirmed on
`aearep-9147`: every commit says `AEAREP-9147`, but its live revision round
is tracked under a different, higher-numbered ticket in Jira.) So once
Step 1 shows a revision is underway, find the ticket that's actually current:

```bash
[ -n "$JIRA_USERNAME" ] && [ -n "$JIRA_API_KEY" ] && echo "jira env OK"
```

If unset, try `source ~/.envvars` and recheck. If still unset, tell the user
Jira confirmation isn't possible and fall back to git-only evidence from
Step 1 — don't block on this, just note the limitation.

If credentials are available, find the openICPSR deposit ID for the current
round (`config.yml`'s `openicpsr:` field, the bare-digit deposit directory
at repo root, or the most recent `Adding code from <id>` commit), then:

```bash
python3 tools/jira_find_task_by_icpsr.py <deposit-id>
```

(Prints nothing on missing credentials or no match; try `python3.12` if
`python3` isn't the right interpreter on this machine.) This returns the
**highest-numbered** — i.e. most current — Jira Task tracking that deposit
ID. Compare it against the ticket embedded in the repo's own history:

- **Same ticket** → the repo's history already reflects the current round;
  proceed normally, referring to it by its usual number.
- **Different, higher-numbered ticket** → *that* is the live ticket for this
  round. Use it — not the repo's own — anywhere you refer to "the current
  case" for the rest of this pass, including the final report (Step 6) and
  any reminder about what commit message the editor should eventually use
  for sign-off.

Then continue to Step 1c, treating this as an active revision round.

## Step 1c — Baseline the round-1 requests (revision rounds only)

Skip this step entirely for a first-round case.

Pull the exact text the previous round was approved with — this is the
authoritative record of what round 1 actually asked for, not what you
remember or infer from the current draft:

```bash
git show ${LAST_APPROVAL_SHA}:REPLICATION.md
```

Extract its `### Action Items (manuscript)` and `### Action Items
(openICPSR)` checklists as the round-1 baseline. You'll need this list in
Step 3 (to assess each item complete/incomplete against round-2 evidence)
and in Step 5 (to build the `### Previously` section).

## Step 2 — Draft-readiness check

```bash
grep -n '> INSTRUCTIONS:' REPLICATION.md
grep -n 'action items go here' REPLICATION.md
```

- If `> INSTRUCTIONS:` lines remain, the RA's draft isn't finished — list the
  section headings they fall under and tell the user before doing anything
  else.
- Note whether the `-----action items go here------` marker is present.
  `aeareq` refuses to run without it (unless forced) — you'll need this in
  Step 4.
- **If Step 1/1b established this is a revision round, a missing marker is
  expected, not a problem.** `aeareq` deletes the marker after every
  successful run, and round 1 already consumed it — it does not come back on
  its own for round 2+. Don't flag this as an RA drafting issue or ask the
  user why it's missing; just note it and move on to Step 4, which handles
  restoring it.

## Step 3 — Independent verification pass

This is the part of the editor's job that catches what the RA missed: read
`REPLICATION.md`'s `## Findings`, `### Missing Requirements`,
`### Tables and Figures`, `### In-Text Numbers`, `## Classification`,
`### Reason for incomplete reproducibility`, and `## Replication steps`
sections closely, then cross-check:

1. **Scan output already embedded in the report** (`### PII Checks`,
   `#### File Paths Summary`, the `Appendix: Candidate ... packages` tables,
   `Appendix: Possible PII`). If a scan surfaced something (PII hits,
   Windows paths, likely-used-but-unlisted packages) with no corresponding
   `[REQUIRED]`/`[SUGGESTED]` tag anywhere in the report, that's a gap the RA
   missed.
2. **Actual output in the numbered deposit directory** — for tables/figures
   the RA marked reproduced, spot check that a plausible output file exists
   (non-empty, sane modification time). A "Yes"/checked box with nothing to
   back it up is a red flag.
3. **Replicator log files** (`logs/*.log` or similar, and anything
   referenced in `## Replication steps`) — look for errors that were worked
   around but never turned into a "Bugs in code" finding, or unresolved
   errors that Classification/Reason-for-incomplete-reproducibility doesn't
   reflect.
4. **Stated vs. actual requirements** — compare `## Stated Requirements` /
   `### Missing Requirements` against the candidate-package scan tables for
   dependencies the RA didn't list.

**How to act on what you find:**
- Objective, mechanical gaps (a scan hit with zero matching tag anywhere in
  the doc) — fix directly: insert the standard tag text pulled from
  `sample-language-report.md` (see Step 5) into the right section — the
  relevant narrative section (e.g. `### Missing Requirements`,
  `## Findings`), **never** into the `## Appendix: ...` section itself (see
  Restrictions — those are auto-generated and read-only).
- Anything requiring judgment (a reproduction claim that looks unsupported,
  a classification that seems too generous/harsh) — do **not** silently
  edit. Surface it to the user as a specific, evidence-backed question
  ("RA marked Table 4 reproduced but `$DEPOSIT/Output/Tables/` has no file
  matching that name — worth a second look?").

**Format for any custom `[SUGGESTED]` tag you author** (here, and in the
revision-round reiteration below): keep the tagged line itself a short,
generic one-liner. `aeareq` pulls that exact line into the Action Items
checklist, and Step 5's SUMMARY draws only from that same line — a long or
over-specific tag line makes the checklist and SUMMARY verbose. Put the
specifics (which scan hit, which file, which package, why) in a plain,
untagged paragraph directly beneath it, separated by one blank line:

```
- [SUGGESTED] Review candidate package dependencies not listed in requirements.

  The scan detected `haven` (R) used in `analysis/clean.R` but not listed
  under `### Stated Requirements`.
```

**Revision rounds only** — also assess the Step 1c baseline: for each
round-1 `[REQUIRED]`/`[SUGGESTED]` item, check the same evidence you're
already gathering above (embedded scan output, deposit files, logs, current
`## Findings`) to decide complete or incomplete. This is expected to be
messy — **it's normal for round 1's `## SUMMARY` to already look
inconsistent with what the RA found this round**; nobody touches SUMMARY
between rounds, so don't treat the mismatch itself as a finding, just work
from the current evidence. For anything you judge **incomplete**, make sure
a fresh `[REQUIRED]`/`[SUGGESTED]` tag for it exists somewhere in the
current draft (reiterating it) — add one yourself if the RA didn't, using
the round-1 text as a starting point. This is the mechanical rule from
12-jira-revision-guidance.md ("items the authors did not adequately address
[are reiterated] as new `[REQUIRED]` tags"), not a judgment call, so apply
it directly. Keep your complete/incomplete determination and one-line
reasoning per item — you'll need it in Step 5.

## Step 4 — Consolidate tags with `aeareq`

From `$REPO_ROOT`:

```bash
aeareq
```

`aeareq` greps `REPLICATION.md` for every `>`/`-`-prefixed line containing
`REQUIRED` or `SUGGESTED`, sorts and dedupes them, rewrites the leading `>`
as `- [ ]`, and inserts the checklist right after the
`-----action items go here------` marker (then deletes the marker). It
refuses to run if the marker is missing.

- **If Step 2 flagged this as an expected revision-round marker absence**:
  just restore it yourself — re-insert the literal line
  `-----action items go here------` at the end of the
  `### Action Items (openICPSR)` section (matching the template's original
  placement), then re-run `aeareq` normally. This is a mechanical, known-cause
  fix, not a judgment call — no need to ask the user or use `force`.
- **If the marker is missing for any other reason** (e.g. a first-round
  draft where it shouldn't be missing at all): that's unexpected — ask the
  user whether to restore the marker or run `aeareq force`, rather than
  guessing. Don't force it unilaterally, since forcing skips a real safety
  check.
- Report back how many tags it found (`aeareq` prints the count).

**Post-process the checklist — route to the correct checklist.**
`aeareq`'s grep scans the *whole file*, not just `### Action Items
(openICPSR)`, and it only ever inserts after the marker there — it has no
concept of `### Action Items (manuscript)` at all. So every tagged line in
the document, regardless of where it was meant to live, ends up swept into
the openICPSR checklist. A `{{ CATEGORY DESTINATION }}` marker's second word
(`m`, `d`, or `both` — see `sample-language-report.md`'s "Priority order for
Action Items" section, same file Step 5 reads) tells you where each item
actually belongs:
- `m` — this is a manuscript-only item that leaked into the openICPSR
  checklist. **Move it, don't just delete it**: check whether an equivalent
  item already exists under `### Action Items (manuscript)` — for the two
  standing `[REQUIRED]` lines that live there permanently ("If making
  changes to the manuscript...", "When returning proofs, confirm..." —
  confirmed on `aearep-9752`) it always will, so removing the openICPSR
  duplicate is safe, nothing is lost. But if no equivalent is already
  present there (e.g. a custom `m`-tagged item the RA or you added only
  under the openICPSR section), add it under `### Action Items (manuscript)`
  *first*, then remove it from the openICPSR checklist — never delete an
  `m`-tagged item without confirming it survives somewhere.
- `d` (the default when a marker has no second word, or no marker at all) —
  openICPSR-only, exactly what `aeareq` already did. Leave it.
- `both` — belongs in both checklists (e.g. the "adjust your tables"/
  "adjust your figures" tags: a numerical discrepancy is both a manuscript
  problem and a deposit/code problem). Leave it in the openICPSR checklist,
  and also add a copy under `### Action Items (manuscript)` if one isn't
  already there — `aeareq` never puts it there on its own.

For lines with no marker at all, fall back to the older heuristic: compare
against the `>`-prefixed lines already sitting under `### Action Items
(manuscript)` and delete any openICPSR checklist entry that matches one
verbatim (don't hardcode those two phrases — derive the comparison from the
manuscript section's actual current content, since wording can change).

**Post-process the checklist — order by priority, not by `aeareq`'s sort.**
Do this *after* routing, and separately for each checklist (manuscript may
now have one or two items in it too, from the `m`/`both` routing above).
`aeareq` sorts/dedupes lines as plain text, which has no notion of
importance. The priority scheme itself is not hardcoded here — read it from
the `## Priority order for Action Items` section at the top of
`sample-language-report.md` in the current repo (the same phrase library
Step 5 reads). That section declares an ordered list of `{{ CATEGORY }}`
markers (currently `{{ CRITICAL }}`, `{{ CODE }}`, `{{ FILES }}`,
`{{ METADATA }}`, in that order — but re-read it each run rather than
assuming these names or this order, since the library can change) and
states the default for tags that carry no marker. A marker can carry a
second word (the `m`/`d`/`both` destination used for routing, above) — only
the first word matters for priority order, ignore the second here. The
marker can show up on a tag copied from the library, or already baked into
the template's own boilerplate (e.g. the ZIP-files-visible `[REQUIRED]` tag
under `### Data deposit` / `### Requirements` in `REPLICATION.md`) — check
for it wherever the checklist line came from.

To reorder each checklist:
1. For each checklist line, check whether it carries a `{{ ... }}` marker
   immediately after its `[REQUIRED]`/`[SUGGESTED]`/`[STRONGLY SUGGESTED]`
   bracket. Sort by its category word's position in the library's declared
   order.
2. For lines with no marker — typically custom tags you or the RA wrote
   directly in `REPLICATION.md` rather than pulling from the library (e.g.
   the `compute_Hc_dot.m` duplication note on `aearep-9752`) — fall back to
   the same judgment call as before, using the library's current tier
   definitions as the rubric: legally/rights-restricted content that must
   not be published reads as the top tier, a code/debugging fix as the
   next, a request to delete/remove other files as the one after that,
   everything else takes the library's stated default. Preserve
   `[REQUIRED]`-before-`[SUGGESTED]` only as a tiebreaker *within* a tier.
3. **Strip every `{{ ... }}` marker from the final checklist text** before
   showing it to the user or leaving it in `REPLICATION.md` — it's an
   internal ordering aid for this pass, not report-facing language.

**Ordering matters on revision rounds**: run `aeareq` *before* writing the
`### Previously` section (Step 5). `aeareq`'s grep matches the raw substring
`SUGGESTED`, and `> [We SUGGESTED] ...` (the historical-record format Step 5
uses) contains that substring — if it already existed in the file when
`aeareq` ran, it would get incorrectly swept into this round's Action Items
checklist as a fresh ask. (`[We REQUESTED]` is safe on its own — "REQUESTED"
is not a substring of "REQUIRED" — but don't rely on that difference; just
keep the ordering: `aeareq` first, `### Previously` after.)

## Step 5 — Draft the SUMMARY

Read the phrase library in the current repo — `sample-language-report.md` at
the repo root, or `template/sample-language-report.md` — for the current
canned language and the "Decisions" catalog. Do not rely on memorized
phrasing; this file is the source of truth and can change.

Structure, calibrated against real approved summaries (AEAREP-8010,
AEAREP-8434 — both ~150–220 words, no filler):

1. **Opening**: "Thank you for your replication archive." (or "revised
   replication archive" on a second/later round).
2. **1–2 short paragraphs**: what was/wasn't reproduced, then the remaining
   `[REQUIRED]` items grouped *thematically* in polite imperative prose
   (code/bugs, data citations & access, README completeness, RCT/IRB, PII,
   deposit metadata) — don't restate every checklist line individually, just
   the substance grouped sensibly. Fold in `[SUGGESTED]` items as a brief
   "please also consider..." aside if there are any. **Stay generic here —
   name categories of issues ("some bugs", "duplicate files"), not specifics**
   (file names, function names, exact root causes). Those specifics already
   live in the Action Items checklist entries (Step 4's dedup/priority pass)
   and the `## Findings`/`### Missing Requirements` narrative — the SUMMARY
   is a cover note, not a second copy of the detail (confirmed against the
   editor's own simplification on `aearep-9752`: a first-draft SUMMARY
   listing specific file paths and package names was cut down to two
   sentences naming only the issue categories).
3. **One bolded decision sentence**, picked from the "Decisions" section of
   `sample-language-report.md` based on the report's `## Classification`
   checkbox and whether `[REQUIRED]` items remain (full reproduction + no
   requireds → acceptance language; requireds remain → conditional-accept
   language; partial/failed reproduction → the stronger "look forward to
   reviewing again" language).
4. Only append boilerplate notes (e.g. the SIVACOR pilot `[NOTE]`) if they
   apply to this case — check the phrase library, don't include by default.
5. **End the SUMMARY with the fixed closing sentence, word for word:**
   "In assessing compliance with our [Data and Code Availability
   Policy](https://www.aeaweb.org/journals/policies/data-code), we have
   identified the following issues, which we ask you to address:" — this is
   the transition into the Action Items lists and must always be the last
   line of `## SUMMARY`, immediately before `### Action Items (manuscript)`.
   Don't hardcode it from memory here either: read it off
   `template/original-REPLICATION.md` in the current repo (the frozen,
   per-repo copy of the blank template — same line, right after the
   `> INSTRUCTION: KEEP the next line AS-IS...` comment) so you're using
   this repo's actual current wording, not a remembered one. This applies
   even when you're otherwise replacing the SUMMARY wholesale (see the
   revision-round note below) — never drop it, paraphrase it, or fold it
   into your own prose.

**Explicitly avoid**: meta-commentary, hedging, "I hope this helps",
restating the entire action-item list in prose, or padding. If in doubt, cut
a sentence rather than add one.

Write the result into `## SUMMARY`, replacing whatever placeholder text is
there.

**Revision rounds only** — three differences from the first-round summary
above:

1. **Opening phrase**: "Thank you for your revised replication package."
   (not "replication archive" — this is the current standard per direct
   editor guidance; the LDI Lab docs and the AEAREP-8434 example still say
   "archive," so if you're touching this again later and the two disagree,
   the live editor instruction wins).
2. The existing `## SUMMARY` (left over from round 1's approval) will look
   inconsistent with round 2's findings — expected, per Step 3, not a
   problem to flag. Replace it entirely; don't try to patch it — but "entirely"
   still excludes point 5 above: the fixed closing sentence is kept
   word-for-word regardless of round.
3. Add a `### Previously` section, placed after the `### Action Items`
   subsections and before the general body. Two sub-sections:
   - `#### Incomplete` — for each Step 3 item you judged incomplete: the
     original request converted to `> [We REQUESTED] <original text>` or
     `> [We SUGGESTED] <original text>`, followed by one sentence explaining
     why it's not done.
   - `#### Complete` — same conversion format, followed by one sentence
     starting with `Done: ` explaining why it's now satisfied.
   (The LDI Lab docs name these sub-sections `#### Unresolved` /
   `#### Resolved` instead, matching the older AEAREP-8434 example — use
   `Incomplete`/`Complete` per current editor instruction, but this is worth
   double-checking if the docs and instruction ever visibly diverge again.)
   Source the original request text from the Step 1c baseline, not from
   memory. Remember the Step 4 ordering note — this section only gets
   written after `aeareq` has already run.

## Step 6 — Report back to the user

Show:
- The drafted SUMMARY text.
- The consolidated Action Items checklist (post-`aeareq`).
- Anything from Step 3: what you auto-fixed vs. what you're flagging for a
  decision.
- If Step 1b found a different current ticket than the repo's own history,
  say so explicitly and use that ticket number in any reminder about the
  eventual sign-off commit message — don't default to the repo's original
  ticket number.
- On a revision round, the drafted `### Previously` section (Step 5) and
  your complete/incomplete calls (Step 3) — these are exactly the kind of
  judgment the human editor should skim before sign-off, even for the items
  you auto-fixed.

## Restrictions

**Pipeline context, so you never have to re-derive this by reading scripts.**
There are three separate tools that touch `REPLICATION.md`, at three
different stages, only one of which this skill ever runs:

1. `automations/24_amend_report.sh` (in the repo, part of the Bitbucket
   pipeline) — runs automatically, before the RA/editor ever opens the
   report. Fills scan-output placeholders (`{{ pii-summary.md }}`,
   `{{ file-paths-summary.md }}`, candidate-package tables, etc.) into
   `REPLICATION.md`/`generated/REPLICATION-filled.md` from files it
   generates under `generated/`. Not something this skill or the editor
   invokes directly.
2. `aeareq` (`~/bin/aea-scripts/aeareq`, personal script, not in the repo) —
   what **this skill runs** in Step 4, to consolidate `[REQUIRED]`/
   `[SUGGESTED]` tags into the Action Items checklist.
3. `aeaready` (`~/bin/aea-scripts/aeaready`, personal script, not in the
   repo, **never run by this skill**) — the editor's actual final sign-off
   tool. Given an issue number and `approve`/`pre-approve`, it: strips and
   regenerates the `# Automatically Generated Appendices` block (by
   re-running `tools/replace_placeholders.py` against
   `template/REPLICATION_appendix.md` and files under `generated/`),
   queries Jira to inject the DOI, the openICPSR deposit URL (replacing the
   templated `.../openicpsr/xxxxx` placeholder under `### Action Items
   (manuscript)`), and any private-data notice, stamps a "Report last
   created on" timestamp, renders `REPLICATION.pdf`, then **commits with
   exactly the message this skill's Step 1 gate-check searches for**
   (`AEAREP-NNNN #comment Approved. Ready to submit.` or `... Preapproved.
   Ready for approval.`) and pushes, and finally offers to update the Jira
   issue via `jira-approval-manager`. This is the literal mechanics behind
   "sign-off is the editor's own action" below — it is a human running a
   script interactively (it prompts for confirmation before committing/
   pushing), not something to script around or replicate.

- **Never** create the approval commit
  (`AEAREP-NNNN #comment Approved. Ready to submit.`), tag, or push, and
  **never run `aeaready`** — that sign-off is the editor's own action (see
  above).
- **Never** fabricate a replication finding, package name, or file path not
  actually backed by evidence in the repo.
- **Never** invent canned language — pull it from `sample-language-report.md`
  in the current repo.
- **Never** post a comment to Jira from this skill (that's the pipeline's
  job — `automations/70_publish_comment.sh`). Only ever *read* from Jira
  (`jira_find_task_by_icpsr.py`, `jira_get_info.py`).
- **Never modify anything from the `# Automatically Generated Appendices`
  line to the end of `REPLICATION.md`** (cross-platform file paths, comments
  in code, candidate Stata/R/Python packages, possible PII, programs/data
  files provided, manifest comparison, not-for-publication data). `aeaready`
  strips and fully regenerates this block on every run (see above) — any
  edit you make here is silently discarded at sign-off, not preserved. Read
  it freely for the verification pass (Step 3) but never edit, reformat, or
  add to it. Anything that needs to change in response to a scan finding
  belongs in the document's narrative sections instead (e.g. a new
  `[REQUIRED]` tag under `### Missing Requirements`), never in the Appendix
  itself. The same applies to a standalone `generated/REPLICATION_appendix.md`
  if one exists in the repo — it's the same auto-generated content, just not
  yet appended.
- **Never try to resolve the `.../openicpsr/xxxxx` placeholder URL** under
  `### Action Items (manuscript)`, or add/guess a DOI — `aeaready` fills
  both in from Jira at sign-off. Leave them as the template placeholder.
- If the repo is genuinely finalized (Step 1, no post-approval activity),
  stop and ask before touching it further. A revision round in progress
  (post-approval activity present) is not a reason to stop.
