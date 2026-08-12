---
name: review-the-tool
description: "Produce a human review checklist and a function-level code review for any tool whose output a firm has to stand behind, with every figure verified by executing the tool rather than reading its documentation. Use whenever the user asks to review, validate, document, sign off on, get comfortable with, or hand to a reviewer any script, model, macro, conversion utility, calculator, allocation engine, ETL job, migration tool, or reporting pipeline that produces client deliverables or feeds financial statements. Trigger on 'review this tool', 'can we rely on this', 'document what this code does', 'build a review checklist', 'what should a human check', 'the auditors will ask', 'workpaper for this script', or 'validate this conversion'. Also trigger proactively when someone is about to ship output from a tool nobody has independently reviewed."
---

# Review the tool

This is the way in, and it performs none of the review itself. Four decisions get made
here and nowhere else — what mode the request is in, what kind of artifact is in front of
you, whether a registered path exists for it, and where the evidence will live — and then
five other skills run in order and you check what each hands back. All four are cheap now
and expensive later. A mode inferred wrongly spends the whole run producing something
nobody asked for; an artifact forced through a path built for something else produces a
document that is worse than useless, because it is confident.

## Both books

A full review delivers **both books** — the human review checklist a person works through
with the output open beside them, and the function-level code review. The checklist covers
every element of the tool's output a person must check, organised by audit assertion, each
test naming the exact artifact, tab and column, what the tool's own controls already cover
and what they leave. The code review covers every module and every function: what it does,
how, what it relies on, and what happens when that reliance is violated.

They are written together because they need each other. The checklist's compensating
procedures exist only because the code review found the gaps they compensate for — a
procedure telling a reviewer to re-perform a reconciliation by hand is busywork until the
code review has established that the tool's own reconciliation compares a column against
itself. Produce both by default. If the user asks for one, produce that one and still run
the research phases in full, because a checklist written without reading the code is a
generic checklist and the specific one is what is being paid for.

## The idea that makes this worth doing

Most tools that produce financial deliverables have some self-checking built in: tests,
validation gates, reconciliations, a green dashboard. The single most useful thing this
review does is separate **what the tool attests** from **what the tool detects**.

A tool can pass 347 of its own assertions and still ship a file that fails on load. It can
print "reconciles to source: $0.00 variance" from an arithmetic identity that cannot return
any other number. It can declare a control blocking in its documentation while the code
turns it into a warning. None of that is dishonesty — it is what happens when checks are
written by the same mind that wrote the thing being checked.

So the work is not to read the code and describe it. It is to run the tool, measure its real
output yourself, and find the places where the green light means less than a reader would
assume. Every phase below serves that, and it is worth saying in your own first answer: a
caller who believes they commissioned a description will not understand why phase 1 spends
an hour executing things instead of reading.

## The doctrine

**A figure you did not produce by executing something is not evidence.** Not the changelog's
figure, not the README's, not the code comment's, not the previous reviewer's. Each of those
is a claim to be tested, and repeating one is not testing it.

It governs every phase, and it is why the sequence starts with execution rather than with
reading. A review that reads first spends the rest of its life quoting figures it inherited,
and an inherited figure is indistinguishable from a measured one by the time it reaches a
document with a signature under it.

## Decide the mode before anything runs

Infer the mode from the request rather than asking for it. A request to document, explain or
write a reference for a tool is `document`. A request to check, verify or fact-check an
existing document is `verify`. Anything about relying on the output, signing it off or
handing it on is `review`.

Then state the mode you inferred, the phases it will run, and what it will and will not
produce — before phase 1 starts, not in the delivery. The caller is the only party who can
catch a wrong inference, and they can only do it while the work is still ahead of them. In
`review` mode the part of "will not produce" most worth stating is the standing of the
output: both books are internal working papers supporting a preparer and a reviewer, and
nothing the run produces is an attest report or constitutes an audit, review or
agreed-upon-procedures engagement under professional standards.

Ask only where the request genuinely reads both ways, and where it does, **resolve the
ambiguity toward `review`**. Inferring `document` when the caller wanted assurance is the
costly direction, and the cost is invisible: nothing in a document-mode run is wrong, it
simply never asks whether the tool can be relied on, so the caller receives a competent
description of a tool whose defects nobody went looking for and it reads as finished work.
The opposite error costs time and delivers more than was asked for, which a caller can see
and decline.

## What each mode runs

| Mode | Phases | Produces | The rule that governs it |
|---|---|---|---|
| `document` | `establish-the-truth`, `map-the-code`, then `write-the-books` for the code review alone | the function-level code review | Still executes the tool wherever it can, because a documentation claim about an edge case is worth more when it can say verified. Tolerates `EXECUTED: no` far more gracefully than `review` does. The finished document states on page one that it is documentation and not assurance |
| `review` (default) | all five: `establish-the-truth`, `map-the-code`, `hunt-the-findings`, `write-the-books`, `check-the-facts` | both books, over an evidence trail every figure in them is quoted from, and — only where a project or knowledge base is attached to the session — the short project record `write-the-books` saves beside them as the tail of its own run, giving what was produced, the reference runs and their key figures, the findings that matter most, and anything it corrects | The full engagement |
| `verify` | `check-the-facts` alone | an error list per document | Works against any document carrying `file.ext:NNN` citations — one a previous reviewer wrote, one another AI wrote, or the previous version of your own book |

Say what `document` mode leaves out, in these terms: no checklist, no finding hunt, no
verification pass, and no conclusion about whether the tool can be relied on. A caller who
asked for documentation and receives a document containing a control inventory will
otherwise assume the controls were tested. `write-the-books` marks the findings section
explicitly not-performed rather than leaving it blank, for the same reason — a blank section
under a findings heading reads as "nothing found", which is the most flattering misreading
available and the one a reader defaults to.

What `document` mode does not leave out is execution. It still runs phase 1, because a
documentation claim about an edge case is worth much more when it can say the behaviour was
verified than when it can only say the code appears to do it — and the phase costs the same
hour whichever mode asked for it.

## Classify the artifact yourself

Inspect it: the extensions and what they imply, whether there is an entry point and where,
and whether running it twice over the same input produces the same output. Match what you
find against the registry below. **Do not ask the user to classify it.** They will answer
with what they call it, and what decides the path is what it is — which is available only by
opening it. Ask where inspection is genuinely ambiguous rather than guessing: a folder
holding both a workbook and the script that writes it, where either could be the artifact
under review, is a question and not an inference.

Determinism decides, not the extension. A `.py` file whose central step calls a language
model at runtime is an LLM-at-runtime artifact wearing a code extension, and it has no
registered path — because the whole evidence chain assumes a second run over the same input
reproduces the first, and every figure in the evidence base inherits that assumption without
restating it.

| Artifact type | Evidence | Mapping | Catalogue |
|---|---|---|---|
| Deterministic code | `establish-the-truth` | `map-the-code` | the twelve defect classes in `finding-patterns.md`, worked by `hunt-the-findings` |
| Spreadsheet or model | *not in this release* | | |
| LLM at runtime | *not in this release* | | |
| Process with human steps | *not in this release* | | |

One row of four carries a path. That is the release rather than an oversight: adding a path
later is a new row plus the skills it names, and nothing already shipped gets refactored to
accommodate it.

## If it does not match a registered path, say so and stop

**Stop. Do not run the deterministic-code path over something that is not deterministic
code.** This is the most important instruction in this skill. It is not a caveat to be
recorded in §1 of a document that then proceeds anyway, and no amount of hedging in the prose
converts a review of the wrong shape into a limited one.

The reason is specific rather than procedural: a spreadsheet forced through a code-shaped
review produces a confident and badly wrong document, which is the exact failure this plugin
exists to catch. Name the mechanism, so the refusal is not mistaken for caution.
`map-the-code` splits the artifact into layers and dispatches `code-mapper` agents that
anchor roughly one `file.ext:NNN` citation per 50 words; a workbook has no functions and no
line numbers, so every citation would be invented and no reader could check a single claim,
which is the one property this method exists to guarantee. `hunt-the-findings` then works a
catalogue whose classes are stated in statements, call order and assignments to a column.
Worked against a workbook most of them come back clean because they cannot be worked at all
— and a catalogue silently worked at a fraction of its coverage reads exactly like one worked
in full.

Then say what the missing path would need, because that is the difference between declining
and stonewalling. A spreadsheet path needs cell-level citation — `Sheet!A1` rather than
`file.ext:NNN` — so a claim resolves to something a reader can open; formula dependency
tracing, so the blast radius of a change is stated rather than guessed; hardcode detection,
to find the constants typed into formulas that no input governs; and a catalogue of
spreadsheet defect classes, because almost nothing in the code catalogue transfers.

Then offer what can legitimately be done, and label it so it cannot be filed as a review.

- **Measure it.** Execute the artifact on the real inputs and independently recompute the
  figures the deliverable rests on, then report the variances. That is a baseline and a
  variance report rather than a review, and it is worth having, because the doctrine above
  holds whatever the artifact is made of. Deliver it as measurement, not as phase 1 of a
  review whose later phases have no path to run.
- **Review the code around it.** A macro, an export utility, or the script that builds the
  workbook or consumes its output is deterministic code and does match the registry. Scope
  the review to that, and say in the delivery that the formula layer was not reviewed, in
  those words.
- **Run `verify` against a document about it.** `check-the-facts` re-derives quantitative
  claims from whatever produced them, so a document already written about the workbook can be
  fact-checked against the workbook itself. Its citation script resolves `file.ext:NNN`
  against a source tree and will have nothing to resolve here, so report that half of the
  pass did not run.

Whatever is offered, give it a name that cannot be mistaken for a review, because the risk in
declining well is that the substitute gets filed where the review would have gone and a year
later nobody remembers it was a substitute. Declining three of four artifact types out loud
is this release working as designed. A plugin whose purpose is to find the places where a
confident output is not backed by evidence cannot be the thing that produces one.

## Create the evidence folder before phase 1

Make `evidence/` and `evidence/runs/` first. Everything the phases produce travels through
files rather than through the conversation, for three reasons that all bite: every phase is
independently invocable and has to be able to join an engagement mid-flight; a code review of
a substantial tool runs to tens of thousands of words and cannot be held in context; and it
makes the most-caught verification error mechanically preventable, since a figure that is not
in the manifest against a run identifier has no business appearing in a book.

Six paths live there, and each is a contract the phases read by name:

- **`evidence/01-evidence-base.md`** — the manifest phase 1 writes: `EXECUTED: yes|no`, one
  `RUN` block per execution with the settings it used, a `FIGURES` table under each, the
  tool's own pass and fail counts, and the observations that could not be reconciled.
- **`evidence/02-execution-spine.md`** — **the execution spine**, the ordered list of the
  stages the code runs, each with the state of the data at that point.
- **`evidence/02-map-<layer>.md`** — one per layer: the function-level record of what each
  function does, how it does it, what it relies on, and how it fails when that reliance is
  violated, plus the module-level constants and defaults that sit outside every function.
- **`evidence/03-findings.md`** — per candidate: the catalogue class, the shape observed with
  its citations, how it was tested stated as an operation, the verdict, the figures the
  verdict rests on, and whether it is reproducible.
- **`evidence/04-verification-<book>.md`** — one per book: an error list whose entries each
  carry the claim, where it is, what is actually true, and how that was established.
- **`evidence/runs/<run-id>/`** — the tool's actual outputs, one folder per run, never edited.
  This one has to exist before the first execution, or the outputs land wherever the working
  directory happens to be and the second run overwrites the first.

Create the directories and not the files. A phase writes its own file, and an empty file
sitting at a path a later phase checks for is worse than an absent one: a phase opening
`evidence/03-findings.md` can tell a missing file from a hunt that ran, and cannot tell an
empty one from a hunt that found nothing.

## The phase sequence

Dispatch these by name rather than performing them inline. Each carries its own degraded
mode, its own output contract and, in two cases, its own agents, and none of that survives
being paraphrased into a plan.

**Phase 1 — `establish-the-truth`.** Stages the code and the real inputs somewhere they can
be executed, runs the tool at least twice under settings that exercise genuinely different
paths, and measures the output by opening the files and counting. Hands back the path to
`evidence/01-evidence-base.md`. Read `EXECUTED` before dispatching anything else:
`EXECUTED: no` is not a failure to retry but the flag every later phase reads to mark its
figures unverified, and if the blocker is something the caller can clear — a driver, a data
extract, access to the source system — say so now rather than four phases later, when the
cost of the gap is already sunk into the books.

**Phase 2 — `map-the-code`.** Splits the modules into three to five layers along the layers
the code actually has, dispatches one `code-mapper` agent per layer in parallel, and asks one
agent for the spine. Hands back the paths written: `evidence/02-execution-spine.md` and one
`evidence/02-map-<layer>.md` per layer. Check them against the depth target that skill states
before accepting them, because an essay reads finished — this is the one part of the phase a
caller can enforce and an agent cannot self-check.

**Phase 3 — `hunt-the-findings`.** This is **the finding hunt** — the phase that works a
catalogue of known defect classes against the code, rather than reading the code again and
hoping something surfaces. Hands back the path to `evidence/03-findings.md` and the list of
catalogue sections worked, with the verdict for each. Read that list and not only the
findings: a class with no verdict is indistinguishable in the finished book from a class with
no defect, and the reader will assume the flattering one.

**Phase 4 — `write-the-books`.** Turns the evidence files into the two deliverables, each
named for the client, the tool and the tool's version. Hands back both book paths, or the
path to the one book where only one was asked for. Where a project or knowledge base is
attached to the session, that skill also saves **the project record** as the tail of its
own run: a short note beside the books giving what was produced, the reference runs and
their key figures, the findings that matter most, and anything that corrects an earlier
document in the project. The condition is real and belongs in what you tell the caller — a
run with nothing attached produces no record, and promising one anyway promises a file that
will not exist.

**Phase 5 — `check-the-facts`.** This is **the verification pass** — the review's last phase,
which fact-checks the finished books adversarially by recomputing what they claim. It
dispatches one `fact-checker` agent per book. That agent has no write tool, by design: it
reports its error list back, and `check-the-facts` writes `evidence/04-verification-<book>.md`
itself, one per book, so the party who has to fix the books is the party holding the record of
what was wrong. Hands back those paths and the count and kinds of error found. Do not drop
this phase to a deadline — it is what stands between a document whose first figure holds up
when a client's developer checks it and one that loses the reader on page two and never gets
them back.

Run them in order, and do not reorder to buy time. Each phase spends what the one before
produced, and the dependencies are hard rather than soft. The ordering-defect classes in
phase 3 are comparisons between two stages of the spine, so a hunt run before phase 2 cannot
work them at all — not with less confidence, but not at all. Phase 5 recomputes figures from
the run folders, so a run that skipped execution leaves it nothing to recompute and it
degrades to checking that the books agree with themselves, which is precisely the check a
wrong figure passes.

## What this skill does not do

It does not write the project record. `write-the-books` owns it, deliberately: that skill
can be invoked directly in `document` mode without this one ever running, and a record
produced by the orchestrator would be missing from exactly the runs that never had one. Nor
is it a guaranteed output of a review, so do not describe it as one — it is written only
where a project or knowledge base is attached to the session.

It writes no deliverable and it measures nothing. Its entire output is four decisions, two
directories and five dispatches — and, where nothing in the registry matches, one refusal
that matters more than all of them.

## Standalone

- *Needs:* the artifact, and enough access to inspect it and to execute it.
- *If that is missing:* with no access to the artifact, classification cannot be done by
  inspection, which is the one step that must not be taken on description. Ask for the
  artifact, or for the specific facts that would settle its type — the extensions present,
  the entry point, whether a second run reproduces the first — rather than classifying from
  what the caller calls it and proceeding. With no subagent tool, dispatch phases 2 and 5
  anyway: each carries its own sequential fallback, and each requires a disclosure of it.
  Carry both disclosures into your own answer, because the orchestrator is the only party
  that sees every phase's, and the user is holding one conversation rather than five.
- *Hands back:* the inferred mode and the classification, both stated before phase 1; the
  evidence paths each phase wrote; and the deliverable paths.
