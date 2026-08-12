# Book 1 — Human Review Checklist

The document a preparer works and a reviewer signs. Its job is to say exactly what a person must look at, in what order, using which file, and why the tool's own controls do not settle it.

## Structure

```
# Human Review Checklist
## <Tool name and version> — <client / engagement>

1. What this document is        purpose, scope, who performs it, priority codes
2. Before you start             the conditions that make the review meaningful at all
3. The artifacts                every file the reviewer will open, what it is, its size on the reference run
4. The things only a human can check   the 3-5 risks no control in the tool addresses
5. Materiality and sample sizes

PART A — Preliminary procedures      establishing that you are reviewing what you think you are
PART B — Assertions for transactions and events
PART C — Assertions for account balances
PART D — The controls, and what each one is actually worth
PART E — Sign-off
PART F — Findings register: what the tool asserts that is not true
```

## The assertion spine

Use both assertion sets when the deliverable is both an event and a position — a conversion journal, for instance, is a transaction posted to a period *and* the opening balance of every account it establishes. Where only one applies, use only that one and say why.

**Name the population each set tests, and keep them apart.** This is what stops the two halves of the book restating each other. The transaction assertions test the *file as an event* — the journal as it will be posted, tested against the source. The balance assertions test the *position that results* — the account balances the file establishes in the target system, tested against the entity's own financial statements. They are different populations and often different procedures against the same numbers, and a reviewer who has not been told which one they are in will do the same test twice and miss the other.

**Transactions and events**

| Assertion | For a tool review, this means |
|---|---|
| Occurrence | Every line in the output traces to a real source record or to a construction that names its rule |
| Completeness | Every source record that should be there is, and everything withheld is named and justified |
| Accuracy | Amounts and attributes are right — signs, precision, constants, rejection counts |
| Cutoff | The period, the effective date and the basis all describe the same moment |
| Classification | Values landed in the right accounts and the right fields |
| Presentation | Right level of aggregation, clearly described, formatting survives to the consumer |

**Account balances**

| Assertion | For a tool review, this means |
|---|---|
| Existence | Every balance in the output exists in the source, and every value exists in the target system |
| Rights and obligations | Balances sit in the entity that owns them; restrictions survive |
| Completeness | Every account with a balance is present; the position foots and agrees |
| Accuracy, valuation and allocation | Amounts agree at account level; establish whether the tool performs any valuation at all |
| Classification | Current/non-current, contra accounts, equity — the places a plausible-but-wrong mapping hides |
| Presentation | The statement as the target system will render it, agreed to the last audited figures |

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

**§4 — The things only a human can check.** Three to five paragraphs naming the risks no control in the tool addresses at all. This is the section a partner reads. Each points at its test.

**§5 — Materiality.** Propose a figure against the deliverable's own units, name what carries zero tolerance, and flag it for partner agreement. Then say something honest about sampling: for a machine-readable, finite, complete population, 100% testing is usually available at trivial cost and is the better answer. Sample only where each item genuinely needs human judgement.

**PART D — The controls, and what each is worth.** One row per control: does it block, what did it say on the reference run, what does it genuinely cover, what does it not. This is the page a reviewer keeps open beside the tool's own dashboard, and it is the fastest way to communicate the attestation/detection gap.

**PART E — Sign-off.** One row per test: reference, name, priority, preparer, date, reviewer, date, result. Then a conclusion paragraph with blanks for the run identifier, the row count and the totals, and signature lines.

**PART F — Findings register.** A table: what the tool says | what is actually true | which test compensates. Every row must be reproducible from the run folder. This is the section that gets quoted in the review report, so keep it to things that are demonstrably true and stated without hedging.

## Tone

Write for a competent professional who is short of time. Direct, specific, no throat-clearing. Where something is serious, say it once, plainly, and move on — a document that shouts at every finding flattens the ones that matter.
