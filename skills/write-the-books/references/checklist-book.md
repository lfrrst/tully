# Book 1 — Human Review Checklist

The document a preparer works and a reviewer signs. Its job is to say exactly what a person must look at, in what order, using which file, and why the tool's own controls do not settle it.

## Structure

```
# Human Review Checklist
## <Tool name and version> — <client / engagement>

   Working-paper statement      first page, before anything else substantive: this is an
                                internal working paper supporting a preparer and a
                                reviewer; not an attest report, and nothing in it is an
                                audit, review or agreed-upon-procedures engagement under
                                professional standards

1. What this document is        purpose, scope, who performs it, priority codes, and the
                                accounting assumptions table: all twelve standard items,
                                each with its verdict; the assertion set and its source,
                                plus the PCAOB crosswalk where the output feeds an issuer
2. Before you start             the conditions that make the review meaningful at all
3. The artifacts                every file the reviewer will open, what it is, its size on the reference run
4. Materiality and sample sizes
5. The top ten                  up to ten checks, ranked, each pointing at its test; ten is
                                a ceiling, not a quota

PART A — Preliminary procedures      establishing that you are reviewing what you think you are
PART B — Assertions for transactions and events
PART C — Assertions for account balances
PART D — The controls, and what each one is actually worth
PART E — Sign-off
PART F — Findings register: what the tool asserts that is not true
```

## Only what this project rests on

**Start from the accounting assumptions, not from the list of assertions.** Before writing a test, work the standard list in `accounting-assumptions.md`, beside this file, in order, and give every item a verdict: applies, with where the tool puts it into effect, or does not apply, with a fact that rules it out. The same list is worked on every engagement, so every book starts from the same thinking. The verdicts go in §1 as a table, so the reviewer can see what the book was built from. Every test traces to an item marked applies, to a finding in `evidence/03-findings.md`, or to a control in PART D, and says which.

**An assertion that no applicable item touches gets one sentence, not a test.** "Not applicable: the file moves balances between accounts of one entity and changes no ownership" is a complete Rights and obligations section. A test written to give a heading something under it is worse than that sentence. It costs the reviewer time, it teaches them that some tests in the book are padding, and from then on they guess which ones.

**Apply the swap test.** If a test would read the same in the checklist for a different tool or a different client, it is generic. Make it specific (the artifact, the column, the reference figure, the assumption it protects) or cut it.

**The count is an output.** No section has a minimum number of tests, and a short section is not a defect.

## The assertion spine

Use both assertion sets when the deliverable is both an event and a position — a conversion journal, for instance, is a transaction posted to a period *and* the opening balance of every account it establishes. Where only one applies, use only that one and say why.

**Name the population each set tests, and keep them apart.** This is what stops the two halves of the book restating each other. The transaction assertions test the *file as an event* — the journal as it will be posted, tested against the source. The balance assertions test the *position that results* — the account balances the file establishes in the target system, tested against the entity's own financial statements. They are different populations and often different procedures against the same numbers, and a reviewer who has not been told which one they are in will do the same test twice and miss the other.

**The twelve assertions are defined in `audit-assertions.md`, beside this file:** the definition of each, what it means for a tool review, its source (AU-C 315 as amended by SAS No. 145), and its PCAOB AS 1105.11 category. Read it before writing PARTs B and C. §1 names the assertion set and its source in one sentence, and carries the PCAOB crosswalk where the output feeds an issuer's financial statements.

A data element that bears on more than one assertion appears under each. Cross-reference rather than repeat the full procedure.

## Test template

Consistency matters more than elegance — a reviewer works down the page and needs the same fields in the same order every time.

```markdown
### <ID> · <One-line statement of what is being tested> [P1] [R] [T-WEAK]

**Data elements:** the exact columns, files and tabs. Name them as they appear.

**Risk:** what goes wrong if this is not tested. One or two sentences, concrete.

**Machine coverage:** which control in the tool covers part of this, whether it
blocks, and — the point of the section — precisely what it leaves. Where a control
reports green on something it cannot see, say so here and say why.

**Procedure:** numbered steps a person can follow with the file open. Name the
artifact, the tab, the column, the filter. Include the figure from the reference
run so the reviewer knows what right looks like.

**Expected result:** what a clean answer is.

**If it fails:** what to do. Omit where obvious.
```

Priority codes, defined once in §1:

- **[P1]** clear before the deliverable is handed on
- **[P2]** clear before sign-off
- **[P3]** documentation; may be cleared after, provided it is cleared
- **[R]** the reviewer independently re-performs this one

**Reliance rating**, also on the heading, one per test. This is the single most useful thing you can give a reviewer working under time pressure, because it tells them where their own effort is actually required rather than duplicating a control that already works:

- **[T-INDEP]** — the tool's control draws its expectation from *outside* the pipeline (the target system's own chart, the source report's own printed total, a third-party list). It is real evidence. Confirm it ran and passed, and move on.
- **[T-WEAK]** — the tool has a control here but it is self-referential, measured on the wrong population, or otherwise cannot fail. Perform the test yourself and do not credit the green.
- **[NONE]** — no control exists. Entirely manual.

The distinction that drives the rating is *where the expectation comes from*. A check that compares the tool's output to the tool's own earlier state is arithmetic; a check that compares it to something the tool did not produce is evidence. Applying that test to every control is most of the analytical work in this book, and stating the answer as a three-value tag is what makes it usable at speed.

## What makes a test worth including

**Name the artifact, not the concept.** "Agree the total to source" is not a test. "Open recon tab 1, work the waterfall as an actual reconciliation, agreeing each step to a named population in `dropped.csv`" is a test.

**Give the machine credit where it is due.** A checklist that treats every control as worthless wastes the reviewer's time and loses their trust. Where a control is genuine — measured before the construction that would conceal it, recomputed independently from the output rather than asserted — say so in terms and confine the human procedure to what it leaves. Some of the most useful sentences in the finished book are the ones that let a reviewer skip something.

**Where a control is not what it appears, explain the mechanism.** A reviewer who understands *why* a green light is empty can predict the next instance. A reviewer who is only told to distrust it cannot.

**Quote the reference figure.** Every procedure that involves a count or a total should carry the number from the reference run, attributed to that run. It turns a procedure into a comparison, which is much faster to perform.

**Rate every test, and let the ratings do work.** Once each test carries [T-INDEP] / [T-WEAK] / [NONE], a reviewer can triage: the [NONE] and [T-WEAK] tests are where their day goes. It also makes PART D almost write itself, and it surfaces something a prose paragraph hides — if most of a tool's controls come out [T-WEAK], that is the review's finding, not an accident of presentation.

**Mark the compensating procedures.** Where a test exists only because a control fails, label it. These are the tests that get dropped under time pressure and they are the ones that must not be.

## Sections that are not tests

**§2 — Before you start.** The two or three conditions under which the review means anything. Typically: the run under review was produced by the deployed build (check the version stamp — archived runs are routinely produced by older builds), and the reviewer knows which mode or basis they are looking at. These are not tests; if they fail, stop.

**§4 — Materiality.** Propose a figure against the deliverable's own units, name what carries zero tolerance, and flag it for partner agreement. Then say something honest about sampling: for a machine-readable, finite, complete population, 100% testing is usually available at trivial cost and is the better answer. Sample only where each item genuinely needs human judgement.

**§5 — The top ten.** The checks that matter most on this engagement, ranked, one short paragraph each: what to check, the specific reason it is on the list (the finding, the missing or [T-WEAK] control, or the assumption it protects) with its reference figure and `RUN`, and the ID of the test that performs it. This is the section a partner reads, and the one a reviewer works first when the day is short. It comes after §4 because the ranking is by what an error would do to the deliverable, in its own units, against that materiality. Put the risks no control addresses at all, the [NONE] tests, at the head of the list. A [T-INDEP] test belongs here only where the reviewer must still confirm the control ran.

Ten is a ceiling, not a quota. If six checks matter, list six and say so in one line, because a seventh added to reach ten dilutes the six. Every entry points at a test in PARTs A to C. An entry with no test behind it is a worry, not a check, and it belongs in PART F if it is demonstrably true and nowhere if it is not.

**PART D — The controls, and what each is worth.** One row per control: does it block, what did it say on the reference run, what does it genuinely cover, what does it not. This is the page a reviewer keeps open beside the tool's own dashboard, and it is the fastest way to communicate the attestation/detection gap.

**PART E — Sign-off.** One row per test: reference, name, priority, preparer, date, reviewer, date, result. Then a conclusion paragraph with blanks for the run identifier, the row count and the totals, and signature lines.

**PART F — Findings register.** A table: what the tool says | what is actually true | which test compensates. Every row must be reproducible from the run folder. This is the section that gets quoted in the review report, so keep it to things that are demonstrably true and stated without hedging.

## Tone

Write for a competent professional who is short of time. Direct, specific, no throat-clearing. Where something is serious, say it once, plainly, and move on — a document that shouts at every finding flattens the ones that matter.
