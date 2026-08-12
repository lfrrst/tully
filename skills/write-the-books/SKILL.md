---
name: write-the-books
description: "Write the two deliverables of a tool review: a human review checklist organised by audit assertion, and a function-level code review, both Markdown, every figure attributed to a measured run. Use when the research phases of a review are complete and the deliverables need writing, or when asked to turn findings and a code map into a document a preparer works and a reviewer signs. Trigger on 'write it up', 'produce the checklist', 'write the code review', 'turn this into a workpaper', or 'I need something a partner can read'. Requires evidence/01 through 03; states what is missing rather than inventing figures."
---

# Write the books

This is the phase that writes **both books** — the human review checklist a person
works through with the output open beside them, and the function-level code review.
Everything the earlier phases produced was working material. These two files are the
deliverable, and they are the only part of the review that leaves the room it was done
in.

That raises the standard rather than merely changing the tone. An unattributed figure in
an evidence file is untidy; the same figure in a checklist procedure sends a reviewer to
compare their own count against a number that was never true of the run in front of
them, and they will spend an hour proving the document wrong. Write every sentence for
someone who does not have this conversation and cannot ask what you meant, because that
is exactly who reads it.

## Both books, because each is the other's justification

Produce both by default. They are not two views of the same material. The checklist's
compensating procedures exist only because the code review found the gaps they
compensate for — a procedure telling a reviewer to re-perform the reconciliation by hand
is arbitrary busywork until the code review has established that the tool's own
reconciliation compares a column against itself. Write the checklist with no code review
behind it and you get a plausible list of tests with no way to defend which of them
matter, which is the same thing as having no checklist.

**Label the compensating procedures** where they appear. These are the tests that exist
only because a control fails, they are the first things dropped when the reviewer runs
out of day, and they are the ones that must not be — every other test on the page has a
machine doing part of the work, and these have nothing.

If you are asked for one book, produce that one. Say once that the research phases still
run in full, because a checklist written without reading the code is a generic checklist
and the specific one is what the client is paying for. Then let it go. Do not restate the
objection in the delivery, in a preamble, or as a standing caveat in the document itself:
a document that presses every point flattens the ones that matter, and an argument made
three times reads as an argument the author lost.

## The structures are in the references, and they are contracts

`references/checklist-book.md` holds the checklist's section order, the assertion spine,
the per-test template, the priority codes and the reliance ratings.
`references/code-review-book.md` holds the code review's section order, the per-function
template, the control inventory's columns and the shape of Part V. Read the one you are
writing before you write it.

Follow the field order given rather than improving on it. Both documents are worked, not
read: a reviewer goes down the page expecting the same fields in the same order every
time, and a template varied for variety costs them the ability to skim — which is the
only reason a checklist is faster than reasoning from scratch. Same for the code review's
four labels under every function. A maintainer searching by symbol needs the assumptions
in the same place in every entry, and one section that puts them elsewhere means reading
all of them.

Two things in those files carry most of the analytical work, so they are worth stating
here rather than leaving to be discovered.

**Organise the checklist by audit assertion, and name the population each set tests.**
Use the transactions-and-events set and the account-balances set both, where the
deliverable is both an event and a position — a conversion journal is a transaction
posted to a period *and* the opening balance of every account it establishes. Where only
one applies, use that one and say why. Then name the population each set tests, because
that is the only thing that keeps the two halves from restating each other: the
transaction assertions test the file as an event, against the source; the balance
assertions test the position it establishes, against the entity's own financial
statements. Often they are different procedures over the same numbers, and a reviewer who
has not been told which one they are in will do one test twice and never do the other.

**Rate every test [T-INDEP], [T-WEAK] or [NONE], on where the control's expectation comes
from.** Not on how the control looks, and not on how the tool's documentation describes
it. A check whose expected value comes from outside the pipeline — the target system's own
chart, the source report's printed total, a third-party list — is evidence, because
something is present that can disagree with it. A check comparing the tool's output
against the tool's own earlier state is arithmetic. Applying that one distinction to every
control is most of the thinking in this book, and compressing the answer to a three-value
tag on the heading is what makes it usable by someone triaging a day. The ratings also
carry a finding by themselves: if most of a tool's controls come out [T-WEAK], that is the
review's conclusion, not an accident of presentation. Give the machine its credit where a
control is genuine and confine the human procedure to what it leaves — some of the most
valuable sentences in the finished book are the ones that let a reviewer skip something,
and a book that treats every control as worthless loses their trust and then their
attention.

## What you are writing from

Four inputs, each with a shape to expect:

- **`evidence/01-evidence-base.md`** — the manifest the first phase writes, carrying
  `EXECUTED`, one `RUN` block per execution, and a `FIGURES` table under each. Every
  number in either book is quoted from here with its `RUN` identifier attached.
- **`evidence/02-execution-spine.md`** — **the execution spine**: the ordered list of the
  stages the code runs, each with the state of the data at that point. It becomes §4 of
  the code review almost directly, and it is what tells you which controls are ordered so
  they could catch anything at all.
- **`evidence/02-map-<layer>.md`** — one per layer, the function-level record of what each
  function does, how it does it, what it relies on, and how it fails when that reliance is
  violated. Edited into a book, it is Parts I to IV.
- **`evidence/03-findings.md`** — what **the finding hunt** produced, the phase that works
  a catalogue of known defect classes against the code. It feeds Part V of the code review
  and, through the compensating procedures, the checklist's findings register.

Two shapes in those files are correct output that reads as damage, and trimming either
costs you something a reader needs.

**A spine that opens with a disclosure above its numbered table.** A paragraph saying no
population was measured is not a malformed file and not editorial throat-clearing to be
cut on the way into §4. It is the sentence that makes the table honest: with it, the stage
order is fixed and the data movement is unknown, so every ordering claim in the book is an
inference from reading. Carry its substance into the code review in your own words, next to
the table it qualifies. Keep the table and drop the banner and you have converted inference
into apparent measurement, in the one section a reviewer consults most.

**Module-level subsections in the layer maps** — constants, hard-coded account numbers,
default configurations, sentinel values. They sit outside every per-function entry, which
is exactly why an editor working function by function loses them without noticing: no
entry reads incomplete when they are gone. Carry them into the code review as their own
subsections. They are what someone changes and where a change does damage, and several
findings live nowhere else — the positional configuration that makes a mis-ordered file
internally consistent and entirely wrong, the sentinel behind an absent-versus-zero
distinction, the hard-coded accounts behind a sign convention.

## Write to be read

Proper prose. Tables where a table is genuinely clearer — the module table, the control
inventory, documentation-versus-behaviour, the sign-off grid — and sentences everywhere
else. The failure to avoid is bullet soup: a page of fragments that looks organised,
carries no argument, and cannot be read aloud.

Each book has two readers who want opposite things, and that is the real difficulty. A
partner reads the conclusion straight through and needs it readable; a reviewer works the
checklist with the file open beside them and needs it consultable. Serve both by putting
the argument in prose and the working material in tables, and by stating a finding twice
where a function carries one — inline, where the reference reader meets it, and again in
Part V, where the straight-through reader does. That duplication is deliberate and should
survive editing.

Where a control is not what it appears, explain the mechanism rather than issuing a
verdict. A reviewer who understands why a green light is empty can predict the next
instance and will catch the one this review did not find; a reviewer merely told to
distrust it has learned nothing transferable and will re-ask the question next quarter.

## The working-paper statement, in both books

Both books state, on the first page and before anything else substantive: the output is an
internal working paper supporting a preparer and a reviewer. It is not an attest report,
and nothing here constitutes an audit, review, or agreed-upon-procedures engagement under
professional standards.

This is not boilerplate, and being obvious does not discharge it. These are the two
documents that leave the firm — they get filed, forwarded, and read a year later by
someone who was not in the engagement — and a document that works through audit
assertions, rates controls, registers findings and closes with a signed grid looks exactly
like an attest deliverable to a reader who has only met that form in attest work. The
resemblance is the risk, and it is strongest precisely when the checklist is well built.
Say it in both books rather than once across the pair, because they travel separately and
each will be read alone.

## Four things that reliably go wrong

**A checklist that is only compensating procedures is not a checklist.** The findings are
the interesting part and they are not the job. The reviewer also needs the ordinary
tests — does the total tie, is the period right, is the sign convention right — and those
are the ones written last or not at all, because nothing in the research phases pushed
them at you. Write them anyway. The reviewer's real exposure is a mundane error in an area
where nobody found a defect, and a checklist that omits the ordinary test has told them by
omission that it was covered.

**Where the tool's vocabulary and the register's differ, say so once and then be
consistent.** If the tool calls something a gate and the register calls the same thing a
check, state the equivalence in §1 and use one term thereafter. The reader is holding two
documents and a screen, and the cost of two names for one thing is not confusion but a
reviewer who concludes there are two things and goes looking for the second.

**Every figure names the run it came from, or is stated for both.** Quote it from the
`FIGURES` table with its `RUN` identifier attached, at the moment you write it, not
afterwards from memory. Every procedure involving a count or a total should carry its
reference figure, which is also what turns a procedure into a comparison and makes it
quick to perform. This is the single most common error **the verification pass** catches —
the review's last phase, which fact-checks the finished books adversarially by recomputing
what they claim — and in a checklist the damage is specific: a figure from the wrong run
tells a reviewer their correct count is wrong. Where a figure differs between runs, state
both. A range across two runs is information about the tool; one figure standing in for
both is a guess wearing a number.

**Materiality goes before the tests, in the deliverable's own units, proposed rather than
set.** Name a figure and name what carries zero tolerance. Before the tests, because
materiality stated afterwards cannot have shaped them and a reader can see that. In the
deliverable's own units, because a figure drawn against a consolidated balance sheet is
not something a reviewer can apply to a journal line. Proposed and flagged for partner
agreement, because the number is a partner's to set, and a checklist that sets it quietly
has taken a judgement it has no standing to take.

## Name them and deliver them

Two `.md` files, each name carrying the client, the tool and the version:
`<Client>-<Tool>-Human-Review-Checklist-v<X.Y>.md` and
`<Client>-<Tool>-Code-Review-v<X.Y>.md`. Deliver them — the paths, in your answer, rather
than a description of what you wrote.

The version in the name is the tool's, not the document's, and it earns its place. These
files get filed and quoted, and a checklist worked against the wrong build is worse than
no checklist, because the reviewer's ticks then attest to something that was never tested.
A name that pins the build puts that error on the file listing instead of three sections
into the document, where nobody looks for it.

## The project record

If a project or knowledge base is attached to the session, save a short record beside the
books: what was produced, the reference runs and their key figures, the three findings that
matter most, and anything that corrects an earlier document in the project. Short enough to
read in a minute.

The books are long — a function-level review of a substantial tool runs to tens of
thousands of words — and nobody re-reads them to get their bearings. The record is what a
future session opens first. The correction line is the part that earns the most: a project
accumulating documents that quietly disagree is worse than one holding a single stale
document, because a reader has no way to tell which is current and will trust whichever
they open. Name the earlier statement that is now wrong, rather than only stating the new
one and leaving both in the file.

## Standalone

- *Needs:* `evidence/01-evidence-base.md` through `evidence/03-findings.md` — the manifest
  for every figure, the spine and the layer maps for the code review's structure and body,
  and the findings for Part V and for the checklist's compensating procedures.
- *If that is missing:* write the books from what exists and disclose the hole precisely.
  Two holes have a required shape.

  **With no `evidence/03-findings.md`,** omit the findings section and mark it explicitly
  not-performed, naming what a hunt would have covered. Never leave it blank and never drop
  the heading silently: a blank section under a findings heading reads as "nothing found",
  which is the most flattering available misreading and the one a reader defaults to. Do
  not fill it by inferring findings from the maps while editing, either — an inference
  produced in passing is not a worked catalogue, and presenting it as one spends the
  review's credibility on the weakest thing in it. The checklist then carries ordinary
  tests only and says so, because compensating procedures with no findings behind them
  would be invented ones.

  **With `EXECUTED: no` in `evidence/01-evidence-base.md`,** state at the top of §1 that
  the tool was not executed and that no figure in the document was verified by execution.
  Mark every figure unverified and name its source — the documentation, the changelog, a
  code comment. Do not omit the figures: an absent figure hides that it was never measured,
  while a figure marked unverified says so, and that difference is what a reader needs to
  judge what they are holding. Never let a documented figure sit unlabelled where a measured
  one belongs — by the time anyone reads it, it is indistinguishable from evidence, and that
  substitution is the one thing the whole method exists to prevent. Say the document is
  documentation rather than assurance, in those terms, and let no sentence in it begin
  "Verified:". The checklist's procedures lose their reference figures too, so each affected
  test becomes the reviewer's job to baseline rather than to check — a much larger job than
  the one they agreed to, and one they have to be told they have taken on. Findings under
  this condition are inferences from reading rather than reproduced defects; where none were
  worked at all, the not-performed marking above applies as well.

  **Both are disclosures, and each goes in both channels:** at the top of your own answer,
  now, and in the books themselves. Neither channel discharges the other, because they have
  different readers. The answer is the only thing the user sees, and they decide what to
  rely on before they leave this conversation. The books are the only thing every later
  reader sees — the partner reading the conclusion, the reviewer signing the grid, and the
  verification pass, which opens them without this conversation attached and recomputes what
  they claim.

  The asymmetry is sharper here than in the earlier phases, and worth being deliberate
  about: these documents get filed. A caveat that exists only in a chat reply is absent from
  the artifact a partner reads six months later and a reviewer has already signed, and
  nothing in the file will ever hint that it was said. That is not the milder of the two
  failures. It is the one that ends in a signed workpaper resting on figures nobody
  measured.

  Then offer to clear the blocker, in both places, and say what it buys: a baseline makes
  every figure in both books measured rather than quoted, and a worked catalogue gives the
  checklist its compensating procedures — the tests only this review could have told the
  reviewer to perform.
- *Hands back:* the paths to both books, or to the one that was asked for.
