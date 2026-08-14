---
name: check-the-facts
description: "Adversarially verify a review document by finding statements in it that are wrong — resolving every file.ext:NNN citation mechanically, re-deriving every quantitative claim from the run folders, and reproducing every finding from scratch. Use before any review document is handed on, and on any cited document whose accuracy is in question, including one written by a previous reviewer or by another AI. Trigger on 'check this document', 'fact-check the review', 'are these citations right', 'verify before I send this', or 'did we get the numbers right'. Writes evidence/04-verification-<book>.md."
---

# Check the facts

**Do not skip this.** The person who wrote a sentence is the worst reader of it: they
read the sentence they meant, and the one on the page is close enough that nothing
snags. That is not carelessness, and it does not yield to being more careful — in
testing, a pass of this sort found **26 errors across two documents that had already
been written carefully**. Every one would have been embarrassing in a workpaper and
none was visible to the person who wrote it. So the phase is not a final polish that a
tight deadline can drop. It is the difference between a document whose figures hold up
when a client's developer checks the first one and a document that loses the reader's
trust on page two and never gets it back, however good the other forty pages are.

This is **the verification pass** — the review's last phase, which fact-checks the
finished books adversarially by recomputing what they claim. What it opens is **both
books**: the human review checklist a person works through with the output open beside
them, and the function-level code review. It also runs on its own, against any cited
document whose accuracy is in question — one a previous reviewer wrote, one another AI
wrote, one that arrived with the engagement. That is not a degraded version of this
phase. It is the same work with the authorship changed, and everything below applies to
it except the parts that name a run folder.

## Delegate it — one `fact-checker` per book

Run the citation script first — the next section has the invocations — and then dispatch
one `fact-checker` agent per book. Give each of them the script's output, the source
tree, the run folders under `evidence/runs/`, and permission to execute things, because
measurement settles questions that argument does not and an agent that can only read
will reason its way to agreeing with the document.

Delegate whenever a subagent tool exists, for the reason in the first paragraph: the
value here is a reader who has never seen the sentence before, and that is the one thing
you cannot supply for your own prose at any level of effort. The dispatch carries a
single instruction — find statements that are wrong, and do not praise what checks out.
The agent's own system prompt carries it too, which is deliberate: praise is what a
long task drifts back into, and an instruction sitting in the system prompt holds for
the whole task rather than fading three thousand words after a caller said it once.
Praise costs tokens and hides the errors. "Sections 1 through 8 are accurate" has spent
the report's budget telling the reader nothing they can act on.

One agent per book rather than one for both. The two books make different kinds of
claim and are checked by different work — the checklist's procedures against their
reference figures, the code review's citations against the code — and a single agent
holding both spends most of its budget reading rather than checking, in a phase whose
entire value is checking.

## Run the script first and hand over its output

```bash
python scripts/citation_check.py BOOK.md --root /path/to/source
python scripts/citation_check.py BOOK.md --root /path/to/source --sample 40 --only-findings
```

`scripts/citation_check.py` is relative to this skill's own directory, not to the
repository root or to the tree being reviewed — so run it from the skill directory, or
give the script an absolute path. `--root` is the tree the citations point at, which is
a different directory from either.

It resolves every `file.ext:NNN` citation in the document against the source tree
mechanically, so the agent spends its attention on whether the cited line *supports the
claim* rather than on whether it exists. Run it yourself and hand the agent the output.
An agent told to run it will re-establish the resolvable half itself, at agent prices,
and then have less budget left for the half no script can do.

What it establishes is mechanical, and worth knowing precisely: a cited file that is not
in the tree, a line number past the end of the file it cites, a basename that matches
two files so the citation names neither, a file it cannot open at all, and a single-line
citation resolving to a blank line, which is usually an off-by-one against the block
below it. All five are checked on every run — the sample is for reading citations that
did resolve, not for finding the ones that did not — and all five fail the run. Each is
settled and should not be re-argued by a reader.

The exit codes are a contract, and it has four values to know:

- **0** — every citation resolved.
- **1** — at least one did not: a dead file, an out-of-range line, an ambiguous
  basename, an unreadable file, or a blank target.
- **2** — the check proved nothing: a missing document, a missing source root, or a
  document holding no citation the tool recognises at all.
- and the rule over all three: **a run that proved nothing must not be reported as a
  pass.** Treat 2 as a broken invocation or an inapplicable document rather than a
  clean one. It is the exit you get on a checklist book, which carries reference
  figures rather than `file.ext:NNN` citations, and on any document in `verify` mode
  that turns out to be uncited. Nothing was resolved, so nothing was established, and
  "0 problems" on a run that examined nothing is the same sentence as "every citation
  resolved" — which is false.

The 1 gates a build, which is why it is worth running before anything is handed on
rather than after. `tests/test_citation_check.py` holds the cases for all three exit
codes, so a change to the script that quietly breaks them fails the suite instead of
silently downgrading this phase.

Exit 0 is the weaker of the two things you need, and the trap in this phase is reading
it as verification. **What the script cannot catch is a citation that resolves to a
real line that says something else** — the line exists, the file exists, the number is
in range, and the sentence built on it is wrong. That error is invisible to any
mechanism and it is the reason an agent is here at all. `--sample 40 --only-findings`
narrows the sample to citations sitting next to finding language, which is where a
mis-supported citation does its damage: a wrong line under a description costs a
maintainer a minute, and a wrong line under a defect claim is the sentence a client's
developer picks up first.

## The minimum check list

**A large well-spread sample of the citations, and every citation that supports a
finding** rather than a description. Spread the sample through the document instead of
taking the first forty; citation rot is not uniform, and it clusters in the sections
edited last, which are the ones nobody re-read.

**Every table a reader would act on.** The checklist's procedures with their reference
figures, the code review's control inventory, and the stage table taken from **the
execution spine** — the ordered list of the stages the code runs, each with the state
of the data at that point. These are worked with the file open beside them, so a wrong
key or a wrong row number does not read as an error; it sends the reviewer to the wrong
number, which they will then believe.

**Every quantitative claim, re-derived from the run folders.** Do not check that the
document is internally consistent — check that the number is right. A figure that is
wrong in the summary and wrong in the same way in the procedure is perfectly
consistent, and consistency is the property a copied error has by construction.

**Each finding reproduced from scratch,** from `evidence/03-findings.md` — what **the
finding hunt** produced, the phase that works a catalogue of known defect classes
against the code. Do not accept that file's account of how a finding was established;
establish it again, from the operation it records. If it cannot be reproduced, say so
rather than dropping it: a finding that cannot be reproduced is a different kind of
claim from one that can, and it has to be reworded to what the evidence actually
supports or withdrawn. Left standing, it is the entry a developer disproves in ten
minutes, and one disproved finding is spent against every other finding in the book.

## Every figure against the run it names

Figures come from `evidence/01-evidence-base.md`, the manifest the first phase writes:
`EXECUTED`, one `RUN` block per execution, and a `FIGURES` table under each. Check each
figure in the books against the `RUN` it names, not merely against the manifest as a
whole. **A figure that was true of a different run is the most common error this pass
catches**, and it is the one nothing else can catch: the number is real, the arithmetic
around it is right, the document is internally consistent, and it belongs to the other
folder.

The earlier phase prevents what prevention can reach — a figure recorded without a run
identifier is not recorded — and that leaves this half to you, because the failure
arrives later than the manifest. A figure attributed correctly when it was measured
gets re-quoted from memory two documents downstream, and by then the run folder that
would contradict it is one of several and nobody remembers which one it came from. In
a checklist the damage is specific: a figure from the wrong run tells a reviewer their
correct count is wrong, and they will spend an hour proving the document wrong before
they conclude it was the document. Where a figure genuinely differs between runs, both
should be stated; a single figure standing in for both is a defect to report even when
it matches one of them.

## If you have no subagent tool, change the mode of work

Not the amount of effort — the mode. **Re-derive every quantitative claim mechanically
from the run folders with a script, and re-resolve every finding-bearing citation,
without looking at what was written until the script has produced its own answer. Then
compare.** The order is the entire technique. An answer you have already read is an
answer you will confirm, and no amount of resolve survives contact with a number you
recognise. Re-reading your own prose finds nothing; recomputing the number finds
plenty — in testing, a self-verification done this way still caught five errors,
including an off-by-one in a total and a wrong divergence point that would have sent a
reviewer to the wrong row.

Write the script even for a handful of figures. A recomputation done in your head is a
re-read with a calculator in it, and it will agree with the document.

This is the weaker pass, and it should be reported as one rather than presented as an
equivalent. What it recovers is the arithmetic, which is most of the volume. What it
cannot recover is the fresh reader, so the errors it reliably misses are the ones that
need one: a claim stated with more confidence than its evidence carries, a citation
resolving to a line that says something adjacent to the sentence built on it, a
conclusion that does not follow from the finding it rests on. Say in your answer and in
the verification file that the pass was self-performed, so a later reader knows which
kind of pass the books have been through.

## Say what the pass caught

Fix everything found, then state in your summary to the user that the pass ran and what
it caught. That is part of the deliverable's credibility, not an admission against it.
"The books have been verified" gives a partner nothing to weigh; "the pass ran, it
caught N errors of these kinds, all now fixed" tells them what standard the document was
held to and lets them calibrate how much of it to check themselves. The errors are the
evidence that the check was real. Suppressing them because they are embarrassing removes
the only proof that anything happened.

A pass that found nothing is worth stating plainly and worth being suspicious of. The
usual cause is a check that went where the author would have looked, and the fix is to
go somewhere else: the sections written last, the figures quoted twice, the findings
whose test was recorded as an adjective rather than an operation.

## The output contract

**The agent reports its error list back to you, and you write the file.** It has no
write tool, deliberately: the caller is the only party that sees every book's result,
and the caller is who has to fix the books afterwards, so routing the list through you
is what keeps the fix and the record from drifting apart. Where you ran the pass
yourself, the same obligation stands — the file is the output of the phase, not a
courtesy the delegated path happens to produce.

One file per book, `evidence/04-verification-<book>.md`, with `<book>` naming which
book it verifies. It is an error list, and every entry carries four things: the claim,
where it is, what is actually true, and how that was established — the operation, being
the command run, the file opened at a line, the column re-totalled. "Checked carefully"
records nothing, because it cannot be re-run and it cannot be wrong, which are the same
property.

Order by consequence. An error that would send a reviewer to the wrong number outranks
a stale cross-reference, and a reader triaging the list with an hour left needs the
order to have been decided by someone who saw all of it.

Keep the file after the books are fixed. A corrected book with no record of the
correction is indistinguishable from a book that was right the first time, and the
difference is exactly what tells a later reader — and the next engagement — what this
pass is worth.

## Standalone

- *Needs:* the document, the source tree it cites, and the run folders under
  `evidence/runs/`, plus `evidence/01-evidence-base.md` and `evidence/03-findings.md`
  where the document is a book from a full review.
- *If that is missing:* two holes have a required shape.

  **With no run folders,** quantitative claims cannot be re-derived at all. Verify the
  citations and the document's internal consistency, and state that limitation at the
  top of the error list rather than presenting a partial pass as a complete one.
  Internal consistency is precisely the check that a wrong figure passes, so a pass
  reduced to it is the pass that misses the most common error in this phase — and it
  will still produce a confident-looking file, which is what makes the disclosure
  load-bearing rather than polite.

  **With no source tree,** the pass cannot run at all. Say that instead of checking the
  document against itself. A document read only for coherence yields a report
  indistinguishable in form from a real one and establishing nothing, which is worse
  than producing no report at all: it occupies the place the real one would have gone,
  and nobody runs this pass twice.

  **Both are disclosures, and each goes in both channels:** at the top of your own
  answer, now, and in `evidence/04-verification-<book>.md`. Neither channel discharges
  the other, because the readers are different people deciding different things. The
  answer is the only thing the user sees, and what they decide on it is whether to send
  the books to the partner — a decision they make before they leave this conversation.
  The file is the only thing every later reader sees, and it is filed as the evidence
  that the books were checked; a verification file that does not say the figures were
  never re-derived asserts more than the pass supports, in the one document whose whole
  purpose is to be accurate about what was and was not established.

  Then offer to clear the blocker, in both places, and say what it buys: the run folders
  turn every quantitative claim from consistent into re-derived, and the source tree
  turns every citation from unresolvable into resolved or dead.
- *Hands back:* the path to `evidence/04-verification-<book>.md`, one per book, and the
  count and kinds of error found.
