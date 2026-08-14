# Book 2 — Code Review

The reference a maintainer consults when they need to know where a number came from, and the document a partner reads straight through to decide whether the tool can be relied on. It has to serve both, which is why the findings live at the end and the reference material in the middle.

## Structure

```
# Code Review
## <Tool name and version> — complete reference

   Working-paper statement       first page, before anything else substantive: this is an
                                 internal working paper supporting a preparer and a
                                 reviewer; not an attest report, and nothing in it is an
                                 audit, review or agreed-upon-procedures engagement under
                                 professional standards

1. Purpose and method            what was read, what was executed, what "verified" means here
2. The <domain> in one page      what the tool is for, in the reader's language, before any code
3. Architecture                  the module table; the two or three design decisions that shape everything
4. The execution spine           the ordered sequence of the main entry point

PART I   — <first layer, e.g. input and configuration>
PART II  — <second layer, e.g. transformation core>
PART III — <orchestration and controls>, including the full control inventory
PART IV  — <output, interface and tests>

PART V   — Cross-cutting findings and conclusion
   12  Findings          invariants; doc-vs-behaviour; controls that cannot fail; defects; what held up
   13  Unguarded reliance
   14  The test suite, summarised
   15  Conclusion and remediation order
```

## §1 — Purpose and method

Say what was read, what was executed, and what the evidence base is. Name the reference runs and their headline figures — every figure in the document traces to one of them, and stating that once at the front saves qualifying it a hundred times.

State the line-citation convention (`file.ext:NNN`, verified by reading the file at that line) and note that where the code contradicts its own comments the document says so and says which is right.

Then say what the document is *not*: not a security assessment, not a rewrite proposal, not an evaluation of the business judgements encoded in the configuration. Those belong elsewhere and the reader should not have to guess.

## §2 — The domain in one page

Written for someone who understands the business and not the code. What the source is, what the target expects, what the mapping does, what the tool constructs that the source never had, and what comes out.

Include a short list of what the tool deliberately does *not* do, each verified: no network calls, no state, no valuation arithmetic, N dependencies. These are load-bearing negatives — they are what makes the rest of the review tractable, and a reader who does not know them will assume worse.

## §3 — Architecture

A module table: layer, module, size, one-line role. Order it by dependency, not alphabetically, so the table doubles as a reading order.

Then the two or three design decisions that shape everything downstream. Every codebase has them and naming them early saves a great deal of explanation later. Typical shapes: "nothing is ever dropped from the working population — a row leaves the output by having a reason written, never by being deleted"; "the amount column is written once and never mutated". State the benefit and the consequence — the second decision above is what makes the arithmetic trustworthy *and* what makes the headline reconciliation incapable of failing.

## §4 — The execution spine

A numbered table: stage, call-site line, what it adds, and the state of the data at that point (population sizes on the reference run). Then three to five numbered observations under "what a reviewer must take from the ordering" — the ordering facts that matter, each stated as a claim with its two line numbers.

This is the most-consulted section of the finished document. Get the line numbers right; the verification pass should check every one.

## Per-function template

```markdown
### <exact signature>

**What it does.** The business purpose, one or two sentences a partner could read.

**How it does it.** The actual mechanism — the algorithm, the order, the masks,
the fallback ladder — with `file.ext:NNN` citations. Where the mechanism has a
worked consequence, work it: a numeric example beats a description.

**What it relies on.** The load-bearing assumptions, specifically. Column names,
file shapes, dtypes, upstream state, config keys, ordering relative to other calls.

**Failure modes.** What happens when the reliance is violated: raises, coerces
silently, drops rows, returns empty. Say which.
```

Keep the four labels in the same order everywhere. Where a function carries a finding, state it inline where a reader will meet it *and* in Part V — the reference reader and the straight-through reader are different people and both need it.

Module-level constants, hard-coded account numbers, default configurations and sentinel values deserve their own subsections. They are what someone changes, and they are where a change does damage.

## The control inventory

The heart of Part III, and usually the most useful table in the document. One row per control:

| Column | What goes in it |
|---|---|
| Identifier | Exactly as the user sees it |
| Title / question | What it asks |
| Line | Where it is computed |
| Population measured | The exact filter |
| Blocks? | And whether that matches what the documentation declares |
| **What it would fail to catch** | The point of the table |

Follow it with:

- **Controls measured on a population other than the deliverable** — a short table naming both populations and the consequence, distinguishing the ones where the difference is correct by design from the ones where it is not.
- **Controls whose arithmetic cannot return a failing value** — demonstrated from the code, not asserted. Separate those that are correctly declared informational from those declared as blocking controls, and quote the documentation's own words about the latter.
- **The register's evidence pointers**, if the tool has a register — every pointer followed and marked resolves / does not.
- **What the control set does not cover at all**, established by inspecting the artifacts rather than by reasoning about the code.

## Part V — the findings

Six subsections, in this order. The order is deliberate: invariants first because they explain how the defects are possible, and negative results before the conclusion so the conclusion has something to turn on.

**Invariants.** The properties several modules depend on and none checks. For each: what it is, who depends on it, and what breaks if it changes. Where the same rule is implemented twice in two places, say "they agree today; nothing makes them agree."

**Documentation versus behaviour.** A table: the claim | where | reality. Include the code's own docstrings and comments, not just the manuals.

**Controls and tests that cannot fail.** Consolidated from the inventory, with the demonstration.

**Defects.** Ordered by consequence, each headed by a one-line statement of the defect. Give the evidence that established it and reproduce it where reproducible — a finding that says "verified: deleting X produced a complete unblocked run attesting a hash for the absent file" is worth ten that say "this could fail". Distinguish defects that produce a wrong number from defects that produce a wrong file from defects that produce a wrong *statement about* a right file. They call for different urgency and readers conflate them.

Mark dormant defects clearly — a real defect in a path the current configuration never takes is still worth recording, and a reader needs to know they are not looking at a live misstatement.

**What held up under direct attack.** See `finding-patterns.md` §12. Without this the reader cannot distinguish "examined and sound" from "not examined".

**Unguarded reliance** as its own numbered section: a table of assumption | consequence if violated. This is the section a maintainer uses.

## §14 — The test suite, summarised

Distinct from the full inventory in Part IV. Say what the suite genuinely establishes — credit the real strengths specifically — then the structural gaps, numbered, each with an example from the actual test code. Close on the distinction between documentation coverage and detection coverage.

## §15 — Conclusion

Three paragraphs at most:

1. **What is sound**, specifically, and what was done to establish it. If no finding misstates a number on the current data, say exactly that — it is the most important sentence in the document and it should not be buried.
2. **What is serious**, as a numbered list of two to four items, each one sentence.
3. **The pattern**, if there is one. In most reviews of this kind it is that the tool's attestation is stronger than its detection, and the practical consequence is that a reader looking at a green board is not reading what they think they are.

Then a suggested remediation order, numbered, with the cheap-and-important items grouped. Where a fix needs a regression test that fails before it, say so — and if every existing test passes against the defect, say that too, because it is the argument for why the test is needed.

## Length and depth

Whatever the code needs. A function-level review of a 10,000-line tool runs 40,000–60,000 words and that is fine — it is a reference, not an essay. What is not fine is padding it with restatement. Every paragraph should carry a fact a reader could not get from the code faster themselves.

The failure mode to watch for is subtler than length: **writing well about a module instead of documenting its functions.** Three elegant paragraphs summarising what `parse.py` does will read better than twenty entries and will be useless to the maintainer who needs to know what `read_ledgerline_hierarchical` assumes. Check your own output against these before you consider a section finished:

- **A heading per function**, matching the actual name, so the document is searchable by symbol.
- **All four labels under each**, in the same order.
- **Roughly one line citation per 50 words.** Below that the document has stopped being anchored to the code; a section carrying two citations for a 400-line module has been written from memory.
- **Private helpers included where they carry real logic.** These are frequently where the finding is, because nobody reviews them.

If a section is short because the module genuinely is, say so and move on. If it is short because it summarises, go back.
