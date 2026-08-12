# Finding patterns

The defect classes that tools producing financial deliverables actually have. Work through these deliberately. Most are invisible from any single function — they appear when you compare two things the code keeps apart: a check against the population it measures, a measurement against the construction that follows it, a document against the behaviour it describes.

Each pattern below gives the shape, how to test for it, and why it matters to a reader.

## Contents

1. [Checks that cannot fail](#1-checks-that-cannot-fail)
2. [Checks measured on the wrong population](#2-checks-measured-on-the-wrong-population)
3. [Ordering defects](#3-ordering-defects)
4. [Attestation without detection](#4-attestation-without-detection)
5. [Silent coercion and silent dropping](#5-silent-coercion-and-silent-dropping)
6. [Documentation that contradicts behaviour](#6-documentation-that-contradicts-behaviour)
7. [Unguarded reliance](#7-unguarded-reliance)
8. [Sign, rounding and arithmetic](#8-sign-rounding-and-arithmetic)
9. [The test suite's own blind spots](#9-the-test-suites-own-blind-spots)
10. [Deliverable hygiene](#10-deliverable-hygiene)
11. [Access, containment and provenance](#11-access-containment-and-provenance)
12. [What to record when something holds up](#12-what-to-record-when-something-holds-up)

---

## 1. Checks that cannot fail

The highest-value finding class, because these are exactly the indicators a reviewer trusts most.

**The tautology.** A check compares two values derived from the same source with nothing in between that could move them apart. The classic is a reconciliation that sums a column and subtracts the earlier sum of the same column of the same rows. It reports zero variance and always will.

*How to test:* for each check, trace both operands back to where they are written. If they are the same data and no stage between mutates it, the check is an identity. Confirm by searching the whole codebase for every assignment to the column in question — if there are only one or two and neither is in the path, you have it.

**The literal.** A check passes a hard-coded true, or reads a statistic that is a hard-coded constant. Sometimes this is honest — an informational measure correctly declared. It is a finding when the check is *documented* as a control.

*How to test:* read the value passed as the verdict. Grep for the statistic's key and see who writes it.

**The tautology under configuration.** A check that could fail in principle but cannot under the settings in force, usually because the step immediately before it has just made the condition true. A check that counts blanks, run right after a step that filled every blank on the identical mask, is measuring its own predecessor.

*How to test:* for each check, ask what ran immediately before it and on what population. If it is the same mask, note it.

**Why it matters:** state plainly for each one whether it is correctly declared informational or is presented as a control. A reader looking at a green board needs to know which greens carry weight.

## 2. Checks measured on the wrong population

A check computed on a population that differs from the one actually delivered. Usually harmless-looking and occasionally the whole ballgame.

*How to test:* for every check, write down the exact filter it applies. Write down the exact filter the deliverable writer applies. Compare. Where they differ, say which is wider and whether the difference is deliberate.

Some differences are correct and should be credited as such — a completeness check that is deliberately wider than the file, because its job is to account for rows that did not ship. Others are not: a check reporting on rows that are not in the file cannot see an error confined to rows that are.

Watch for the same population filter being re-derived independently in several modules. They agree today; nothing makes them agree.

## 3. Ordering defects

The richest seam, and only visible against the execution spine.

**A measurement taken after the construction that conceals it.** If the tool constructs balancing entries, plugs, or offsets, the check on whether the *source* balanced must be taken before the construction. Find where the figure is computed and where the construction is applied, and state the distance between them in lines and in stages. When this is done right it is the strongest control in the tool and should be credited loudly; when it is done wrong the run looks immaculate.

**A guard that only applies where a previous guard has not.** A common shape: a stand-down step writes its reason only where no reason is already present, so rows that an earlier stage already touched skip it silently. Then a later stage clears the earlier reason and returns those rows to the population — after the guard has passed by, with nothing re-testing them.

*How to test:* for every conditional guard, ask which rows are excluded by the condition, and then ask whether anything downstream returns those rows to scope.

**A field overwritten rather than appended.** Where several stages record problems into one field, an assignment loses whatever the earlier stage wrote. Look for the same field being assigned in more than one place, and check whether the later one appends.

**A reset that changes a headline count.** A flag set at one stage and cleared at another means the count a reader sees is the count after the reset, not the count that was found. Say where both are.

## 4. Attestation without detection

The tool records something as evidence which it never verifies.

- **Hashes recorded but never recomputed.** Almost universal. The manifest names an input and its digest; nothing ever compares the digest to the file. State it, and put "recompute the hashes yourself" in the checklist.
- **A cache that can serve when its source is absent.** Any caching layer keyed on a source file's hash needs testing on the path where the source file is *missing*, not just where it has changed. Delete the source, run the tool, and see what happens. If it completes and attests a digest for the absent file, that is a serious finding.
- **Outputs not hashed at all.** If the manifest hashes the inputs but nothing hashes the deliverable, the folder cannot self-certify that the file in it is the file the run produced.
- **Evidence pointers that do not resolve.** Where a register or a document tells a reviewer to look at a specific key, tab or file, follow every one. Keys get renamed; conditional files do not exist on a clean run. Test that the pointer resolves, not just that a pointer exists — a test asserting the evidence field is non-empty passes on a dead pointer.

## 5. Silent coercion and silent dropping

- **Numeric coercion to zero.** Find every place a value is coerced with errors suppressed and then filled with zero. Ask what formats reach it. Thousands separators and accounting parentheses are the usual killers, and they are invisible when the normal path reads a binary format and only the fallback path reads text.
- **Absent versus zero.** The tool should distinguish "no value" from "the value is zero". Where it does, credit it and test that the distinction survives to the deliverable. Where it does not, that is a finding — a column that was never populated silently becomes zero and the totals change without anybody seeing it.
- **State not cleared on the error path — the row that could not be classified ships with its neighbour's value.** When a tool carries context across records (a hierarchical report, a nested import, anything where a record inherits from the one above), check what happens to a record it *fails* to classify. The usual shape: the record is correctly flagged as unresolvable, and then the emit step applies the open context to it anyway — so the field it could not resolve is not blank, it holds the previous sibling's value. The row looks complete and is wrong, which is the worst combination. The tool's own documentation will describe these rows as "named rather than guessed", and that will be true of the flag and false of the data.

  *How to test:* take every record the tool flags as unresolvable and look at the field that failed to resolve. If it carries a value, find out where the value came from — it is almost always the preceding record. Then check whether the flag travels with the row all the way to the deliverable, or only to an internal column nobody exports. In the engagement this catalogue was written from this was roughly 40 rows carrying about $2M gross: source row 118's own code was `41205`, unclassifiable, and the row shipped carrying `41204` from row 117. Nothing caught it, including a context-leak check that recomputed inheritance independently and correctly returned zero — because the value was not leaked *across* a boundary, it simply was never cleared *at* one.

- **A missing column created as empty.** Convenient and dangerous: renaming a source column produces an all-blank field rather than an error.
- **Grouping that drops null keys.** Two functions grouping on the same keys with opposite null handling will disagree, and the one that drops is usually the one producing the deliverable that proves the other is right.
- **Broad exception handling around a fallback.** `except Exception` around a retry masks genuine failures and routes them into a slower path that may produce a plausible wrong answer.

## 6. Documentation that contradicts behaviour

Collect these into one table in the code review; they are individually small and collectively damning.

- Docstrings describing removed mechanisms.
- Warning strings naming mechanisms that no longer exist, or citing counts of a different population from the one described.
- Counts in documentation that no longer match (checks, assertions, tabs, columns).
- Quantitative claims produced against a different input file, where the document never names which file it is quoting.
- Version numbers not moved when behaviour changed.

*How to test:* take every quantitative sentence in the operating documentation and try to reproduce it against the current configuration. Report a verdict per claim: true / stale / false, with the actual figure.

## 7. Unguarded reliance

Consolidate into a single table, because it is the section a maintainer will actually use. An entry is a load-bearing assumption with no runtime check. Look for:

- **Ordering or positional configuration not derived from the target system.** A hand-maintained list of columns, segments or fields, matched positionally by the consuming system. This class is uniquely dangerous because a mis-ordered file is internally consistent — it balances, it ties, it passes every check — and is entirely wrong. If the tool has one of these, it belongs at the top of both books.
- Exact string matches on column names, sheet names, type codes.
- Template layout assumed by row and column index.
- "Exactly one file in this folder" assumptions, and what happens with two. Check whether the tie-break is by name or by date; alphabetical tie-breaks surprise people.
- Timestamp resolution used to name output folders, and what happens on a collision.
- Dependency version floors with no ceiling, when the tool's fidelity guarantees are actually the dependency's behaviours.
- Procedural controls that live only in a docstring — "never open this file in Excel and re-save it" — and appear nowhere the recipient will see.

## 8. Sign, rounding and arithmetic

Usually clean, and worth verifying precisely so you can say so.

- **Find the single place the sign convention is decided** and state it exactly. Then check whether anything consults the account type or class to flip a sign. If nothing does, the tool inherits the source's sign discipline rather than imposing one — say that, because it means a reversal in the source passes through without comment.
- **Count the negations in the whole codebase** and account for each.
- **Offsetting pairs.** Where the tool generates a matching entry, work through a numeric example by executing it. Getting both signs backwards is easy, survivable in the aggregate, and produces a wrong number the moment the two accounts differ. Note that a test asserting "the generated lines net to zero" passes with either sign.
- **Rounding relative to a zero test.** Whether rounding is applied before or after a `== 0` comparison decides whether a residue reaches an offset account or vanishes.
- **Float error.** Measure it rather than assuming. Check the source's own precision — if every input value has at most two decimals and nothing averages, prorates or allocates, float is fine and you should say so.

## 9. The test suite's own blind spots

Read the suite as a document about what the authors thought mattered. Then find the shapes:

- **Assertions on a net where either sign would pass.** `sum == 0` over a generated pair passes with the signs swapped.
- **Assertions on an absolute value where the sign is the point.**
- **Assertions that a field is non-empty rather than correct** — "names a source row" is not "names the right source row"; "the hash is recorded" is not "the hash is right".
- **`.any()` where `.all()` was meant**, asserted over a large population.
- **Assertions that are unconditionally true** — an expression compared to itself, a length compared to `>= 0`. Grep for these; they exist more often than anyone expects.
- **Name-based access to a positional format.** If every assertion reads the output by column name, none of them can see a column-order defect.
- **Magic numbers against one fixture.** Precise and powerful, but precise about one file — they cannot distinguish "the engine changed" from "the fixture changed".
- **Whole layers untested.** Web layer, UI, file-writing layer. Say how many lines have zero direct coverage.
- **No discovery.** If the runner calls a hand-maintained list of test functions, a new test not added to the list never runs and nothing detects it.
- **Narrow determinism tests.** Compare what the determinism test actually compares against what varies — a resolved header carrying today's date will differ between runs and pass a test that only compares the data.

Finish with the distinction that matters: a suite can verify **documentation coverage** (every control has an entry) without verifying **detection coverage** (a defect class exists for which no control was ever written). Name the defect classes in the second category.

## 10. Deliverable hygiene

- **Formula injection.** Check whether any client- or user-controlled string reaches a CSV or spreadsheet cell without a guard on a leading `=`, `+`, `-` or `@`. Test what the actual toolchain does — some spreadsheet libraries promote a leading `=` to a live formula, which makes the workbook path worse than the CSV path. Then name which deliverables carry free text and which carry only codes; often the machine-facing file is clean and the reviewer-facing ones are not, which inverts people's intuition.
- **Leading zeros.** Separate two questions that get conflated: do the zeros survive *in the bytes* of the file, and do they survive *through a reader*. The first is usually yes; the second depends entirely on the consumer, and spreadsheets strip them regardless of quoting.
- **Line numbering that does not mean what it looks like.** If a lineage file numbers a wider population than the deliverable, the numbers are not deliverable line numbers. Find where the two numbering systems diverge and state the exact line — "they agree through line 76 and diverge from 77" is far more useful than "they differ", because it explains why spot checks tie.
- **Encoding, line endings, quoting.** State them as verified facts.

## 11. Access, containment and provenance

Not a security assessment, but findings that emerge from reading the code belong in the review.

- **Path containment** on any user-supplied filename. Test traversal and absolute paths. For a firm handling multiple clients, the failure mode is not abstract — it is one client's data in another client's workpaper.
- **Local servers.** Check the bind interface, and check whether origin, referer, host and content type are validated. A loopback bind blocks cross-origin reads; it does not block cross-origin writes, and a tool that rewrites a client mapping table over an unauthenticated local POST is worth recording as a stated posture rather than discovering later.
- **Read-only or reviewer modes.** Enumerate every mutating entry point and check the guard on each. Modes usually guard persistence and not session state, which matters when the screen is the reviewer's evidence.
- **Any code-display or file-reading convenience feature.** These are frequently guarded by a string prefix on something later used as a path.

## 12. What to record when something holds up

Negative results are part of the deliverable, and a review that lists only defects is not usable — the reader cannot tell what was examined and found sound from what was never examined.

Give them their own section. For each, say what was probed and how. Good subjects: money handling and float error; the ordering of the key control; whether the population that ships is the population that was checked; sign correctness on the real data; whether anything is dropped between parse and output; duplicate-key handling; behaviour under the installed dependency versions; and the specific security axes you tested and found clean.

Then let the conclusion turn on the contrast. "Sound arithmetic, defective attestation" tells a partner more than either half alone.
