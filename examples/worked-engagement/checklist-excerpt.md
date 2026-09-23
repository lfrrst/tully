# Human Review Checklist — excerpt

## Ledgerline→Aurora Conversion Utility v3.4.1+g8f21c — `<client>`, 2026 Q1 opening-balance conversion

**Synthetic example.** The tool, both systems and every figure below are invented.
The client slot in the heading is left as a placeholder because no client, real or
invented, is named anywhere in this repository. See [README.md](README.md).

**This excerpt is §1, one test from PART B, two from PART C, and two rows of PART F.**
The finished book also carries §2 (before you start), §3 (the artifacts), §4
(materiality and sample sizes), §5 (the top ten), PART A
(preliminary procedures), the rest of PARTs B and C, PART D (the control inventory
and what each control is worth) and PART E (sign-off). The tests below quote
materiality only where a threshold is part of the procedure.

---

## 1. What this document is

**The output is an internal working paper supporting a preparer and a reviewer. It is
not an attest report, and nothing here constitutes an audit, review, or
agreed-upon-procedures engagement under professional standards.** It is a checklist
for a person, worked with the conversion journal open beside them.

**Scope.** The 2026 Q1 opening-balance conversion produced by
`python -m converter.convert` at version 3.4.1+g8f21c, and the five deliverable
artifacts that run writes: `journal.csv`, `dropped.csv`, `lineage.csv`, `controls.json`
and `manifest.json`. The run also writes `run_header.txt`, which is a log rather than a
deliverable; §2 uses it to confirm the build before anything else is done. Both
reference runs are defined in
[`01-evidence-base.md`](01-evidence-base.md): RUN A-FULL-Q1 (all 312 funds, restriction
extract supplied) and RUN B-FUND-100 (one fund, restriction extract withheld).
Every figure quoted in a procedure below names the run it came from. Where the two
runs disagree, both are given, because the disagreement is usually the point.

**The accounting assumptions this conversion rests on.** Every test below traces to an
item marked *applies*. An assertion that no such item touches carries one sentence
saying why, and no test. The finished book's table has all twelve standard items,
including the ones that do not apply. This excerpt shows only the three that the tests
below trace to.

| # | Assumption | Verdict | How this conversion relies on it | Tests |
|---|---|---|---|---|
| 3 | Period, cutoff and effective date | Applies | The balances are stated as of 2026-03-31, the `--as-of` both reference runs used | not in this excerpt |
| 6 | Chart of accounts mapping | Applies | Every Aurora account the journal names has to exist in Aurora's own chart of accounts | C-1 |
| 7 | Dimensions and attributes | Applies | The segment string has to be in the order Aurora's import layout reads it, which the tool takes on trust from the column order of the client's segment map. Restriction status comes from the Ledgerline fund register and has to survive onto every line of a restricted fund | B-5, C-3 |

**Who performs it.** A preparer works every test and initials it. The reviewer
re-performs independently every test marked `[R]`. Nothing here is delegated to the
tool's own dashboard; where a control does part of the work, the test says so and
says what it leaves.

**Priority codes.**

- **[P1]** clear before the deliverable is handed on
- **[P2]** clear before sign-off
- **[P3]** documentation; may be cleared afterwards, provided it is cleared
- **[R]** the reviewer independently re-performs this one

**Reliance ratings.** One per test, on the heading. The rating turns on where the
control's expectation comes from, not on how the control is described.

- **[T-INDEP]** the tool's control draws its expectation from outside the pipeline.
  It is evidence. Confirm it ran and passed, and move on.
- **[T-WEAK]** a control exists here but it is self-referential, measured on the
  wrong population, or otherwise cannot fail. Perform the test yourself and do not
  credit the green.
- **[NONE]** no control exists. Entirely manual.

Of this tool's six controls, one rates [T-INDEP] (C02), two [T-WEAK] (C01, C04),
two are correctly declared informational, and one covers nothing the deliverable
depends on. **Tests marked *compensating* exist only because a control fails.** They
are the first tests dropped when the day runs out and they are the ones that must
not be.

---

## PART B — Assertions for transactions and events

*Population: the conversion journal as an event — `journal.csv` as it will be posted,
tested against the Ledgerline trial balance it was built from.*

### B-5 · The Aurora segment string on every journal line is in the order Aurora reads it [P1] [R] [NONE]

**Data elements:** `journal.csv` columns `SEGMENT`, `FUND`, `AURORA_ACCOUNT`;
`inputs/aurora-segment-map-v11.xlsx` tab `MAP`, all five segment columns, in sheet
order; Aurora's own import layout for the `GL-JE-IMPORT` template; the segment
definitions in Aurora under Setup → Chart Structure.

**Risk:** the tool builds `SEGMENT` by joining the mapping sheet's five columns in
the order they appear on the sheet, and Aurora consumes the joined string
positionally. A mapping sheet whose columns have been reordered — by anybody, for any
reason, including a well-meant tidy-up — produces a journal that balances, ties to
the trial balance, and posts every amount to the wrong segment. This is the failure
mode with no arithmetic signature: the file is internally consistent and entirely
wrong.

**Machine coverage:** none for this assertion. C05 counts rows where `SEGMENT` is
populated and reports 4,119 of 4,119 (RUN A-FULL-Q1), which is a statement about
blankness and not about order; it is correctly declared informational and it is not
being criticised here. Nothing in the tool reads Aurora's segment definitions, so
nothing in the tool holds an expectation that could disagree with the sheet. Nor does
anything compare `SEGMENT`'s own first position against the `FUND` the same row
carries, though the two come from different files and must agree — which is what makes
step 6 below the cheapest test on this page. The changelog claims a segment-order
validation was added in 3.5.0; the staged build stamps 3.4.1+g8f21c and contains no
such step (unreconciled observation 1).

**Procedure:**

1. Print the five segment column headers from tab `MAP` in sheet order. Print
   Aurora's segment order from Setup → Chart Structure. Compare position by position.
   They must agree by name, not by count.
2. In `journal.csv`, confirm every `SEGMENT` value matches
   `^[0-9]{3}-[0-9]{4}-[0-9]{2}-[0-9]{3}-[0-9]$`. Expect 4,119 of 4,119
   (RUN A-FULL-Q1). One of those rows is the balancing line, whose `SEGMENT` is the
   hard-coded constant `999-8910-00-000-0` and did not come from the mapping sheet at
   all; it is the row with a blank `SOURCE_LINE` and it is excluded from steps 3 and 4.
3. Reduce `SEGMENT` to its shape by replacing every non-zero digit with `#` and
   leaving every zero as written, then take the distinct values. Expect 6 shapes
   (RUN A-FULL-Q1). **Test one line of each shape**, not one line of each fund — the
   shapes are what the positional risk varies with, because a row whose location
   position is `000` cannot reveal a transposition and a row with a real location can.
4. For those 6 lines, re-derive the segment string by hand from tab `MAP` and agree
   each of the five parts to the Aurora definition it claims to be. Positions 1 and 4
   are both three digits, so a transposition between them produces a well-formed
   string: `100-4100-07-312-0` and `312-4100-07-100-0` are both valid segment strings
   and only one of them is the right answer.
5. Confirm the sheet's own change history: the file is `v11`. Ask who last edited it
   and whether any column was added, removed or moved after v10.
6. Compare the first three characters of `SEGMENT` against `FUND`, row by row. Expect
   0 differences over 4,119 rows (RUN A-FULL-Q1) and 0 over 96 (RUN B-FUND-100). This
   is one line of work and it is the only mechanical detector available for a
   transposed fund column, because `FUND` is read from the trial balance and
   `SEGMENT`'s first position from the mapping sheet. Nothing in the tool performs it.

**Expected result:** the five positions agree by name with Aurora's structure, all
4,119 rows carry a well-formed string (RUN A-FULL-Q1), each of the 6 shapes re-derives
by hand, and step 6 returns 0.

**If it fails:** stop. Do not post, and do not correct the journal — correct the
mapping sheet and re-run, because a hand-edited segment column breaks the tie between
`journal.csv` and `lineage.csv` and no later test will detect that.

**Note on sampling this from one run.** RUN B-FUND-100 emits 2 distinct shapes, not 6.
A reviewer who worked step 3 against that run would have tested a third of the
positional surface and had nothing in front of them to say so — the count of shapes is
not printed anywhere, and 2 of 2 reads exactly like 6 of 6.

---

## PART C — Assertions for account balances

*Population: the position the journal establishes — the opening balances in Aurora
after posting, tested against the entity's own statements and against Aurora's own
chart.*

### C-1 · Every Aurora account in the journal exists in Aurora's chart of accounts [P2] [T-INDEP]

**Data elements:** `journal.csv` column `AURORA_ACCOUNT`;
`inputs/aurora-coa-2026-05-02.csv` column `ACCOUNT`; `controls.json` key `C02`.

**Risk:** an account code that does not exist in the target system fails at import,
or worse, is created on the fly by an import setting nobody checked, producing a
chart the client did not design.

**Machine coverage:** C02 anti-joins `AURORA_ACCOUNT` against the chart extract and
blocks on any non-match. **This is a real control and should be credited as one.** Its
expectation comes from a file the tool did not produce — an extract from the target
system — so something is present that can disagree with it. It reported 0 exceptions
over 4,119 rows (RUN A-FULL-Q1) and 0 over 96 rows (RUN B-FUND-100), against a chart
extract of 1,946 accounts (RUN A-FULL-Q1). Confirm it ran and move on; the human work
here is confined to the one thing C02 cannot see, which is whether the extract is
current.

C02 also happens to be the only thing standing between the balancing line's hard-coded
account `8910` and a failed import, and it covers it for the same reason it covers
everything else: `8910` is in the 2 May 2026 extract. Nothing ties the constant to that
chart, so this is coverage by coincidence rather than by design — see the
`_plug_residue` entry in [`code-review-excerpt.md`](code-review-excerpt.md).

**Procedure:**

1. In `controls.json`, confirm `C02` is present, blocking, and reports 0 exceptions.
   Expect 0 over 4,119 rows (RUN A-FULL-Q1).
2. Check the extract's date in its filename and its own header row:
   `aurora-coa-2026-05-02.csv`, exported 2 May 2026. Confirm no accounts have been
   added, deactivated or renumbered in Aurora since. This is the whole of the human
   procedure and it is the only part C02 is blind to — the control tests the journal
   against the extract, not the extract against Aurora.
3. Confirm the extract's row count against Aurora's own account listing: expect
   1,946 (RUN A-FULL-Q1).

**Expected result:** 0 exceptions, and an extract that is still current as at the
posting date.

**If it fails:** re-export the chart and re-run. Do not clear the exception by editing
`journal.csv`.

### C-3 · Restriction codes are present on every line belonging to a restricted fund [P1] [R] [T-WEAK] *(compensating)*

**Data elements:** `journal.csv` columns `RESTRICTION` and `FUND`;
`inputs/LL-FUNDS-2026-03-31.csv` column `RESTRICTED`;
`inputs/restrictions-synthetic.csv`; `controls.json` key `C04`.

**Risk:** a restricted balance that arrives in Aurora with no restriction code is
unrestricted in the target system from the moment it posts. Nothing downstream
recovers it, and the error is in the direction that overstates what the entity may
spend.

**Machine coverage:** C04 is titled *"All restricted funds carry a restriction code"*
and it is declared as a blocking control. **It cannot fail, and the mechanism is worth
understanding rather than merely distrusting: C04's population is the set of rows
where `RESTRICTION` is non-blank** (the filter at `converter/controls.py:129`), and
within that population it tests whether `RESTRICTION` is non-blank (the verdict at
`converter/controls.py:137`). The rows it would need to see in order to fail are the
rows its own filter removes.

The consequence is not that C04 is merely uninformative — it is that **C04 gets
greener as the input gets worse.** In RUN A-FULL-Q1 it reported 0 exceptions over a
population of 812 rows. In RUN B-FUND-100, where the restriction extract was withheld
altogether, it reported 0 exceptions over a population of 0 rows: the same green, on a
run where no row carried a code at all. An empty population passes.

**That is the transferable shape, and it is what makes this rating predictable rather
than a verdict to be taken on trust: any control whose population filter is the field
it tests cannot fail, and every additional missing value makes it pass more
comfortably.** When the next control is added, this is the first thing to check about
it — and the check is mechanical, because the filter and the verdict are two lines in
the same function.

C04 is one of two controls in this tool that cannot fail. The other is C01, and it
cannot fail for a different reason — it measures a file the tool balanced one stage
earlier — so the two are not one finding stated twice. PART F carries both.

**Procedure:**

1. Join `journal.csv` to `inputs/LL-FUNDS-2026-03-31.csv` on `FUND` and count the
   rows where `RESTRICTED` is `Y`. Expect 1,204 (RUN A-FULL-Q1). Do not use
   `restrictions-synthetic.csv` for this step — the register is the independent
   statement of which funds are restricted, and it is the whole reason this test is
   worth performing.
2. Of those rows, count the ones where `RESTRICTION` is blank. Expect 392
   (RUN A-FULL-Q1) and 96 of 96 (RUN B-FUND-100).
3. Read `C04` out of `controls.json` and record both its exception count and its
   population: 0 over 812 (RUN A-FULL-Q1), 0 over 0 (RUN B-FUND-100). Record the
   population, not just the verdict. A green C04 with a population smaller than
   step 1's count is the signature of this defect and it is legible at a glance once
   you are looking for it.
4. For every row from step 2, obtain the restriction from the fund documentation and
   post the codes by hand before the journal is handed on. There is no run of this
   tool that produces them.

**Expected result:** step 2 returns 0. It does not, on either reference run.

**If it fails:** it does. Treat step 4 as required work, not as an exception routine,
and record the count you posted by hand in PART E so the reviewer can agree it to
step 2.

**Qualification on these figures.** `restrictions-synthetic.csv` is a fabricated
input (see the inputs table in [`01-evidence-base.md`](01-evidence-base.md)), so 812
and 392 are properties of that file and not of the client's restriction extract. The
comparison in step 3 is what transfers; the counts must be re-baselined on the first
run that uses the real extract, and until then the reviewer is establishing this
figure rather than checking it.

---

## PART F — Findings register: what the tool asserts that is not true

Two of the register's rows. Every row in the finished register is reproducible from a
run folder; these two are reproducible from both.

| What the tool says | What is actually true | Which test compensates |
|---|---|---|
| `controls.json` reports control C01, *"Total debits equal total credits"*, as a blocking control, `pass`, in both reference runs. | The journal was made to balance one stage before C01 measured it. `_plug_residue` (`converter/journal.py:410`, appended at `converter/journal.py:418`) writes the difference between the two sides as a row, so C01's arithmetic at `converter/controls.py:74` cannot return a failing value. In RUN A-FULL-Q1 that row carries 1,284,406.17 credit — 1.5% of the file's gross debits, and equal to the net of the 262 rows the tool dropped. In RUN B-FUND-100 the difference was 0.00 and no row was written, so C01 reported the same `pass` for an entirely different reason. | B-2 (agree the journal to the trial balance through `dropped.csv` as a reconciliation, and identify the row with a blank `SOURCE_LINE` by name) — not reproduced in this excerpt |
| `controls.json` reports control C04, *"All restricted funds carry a restriction code"*, as a blocking control with 0 exceptions, in both reference runs. | C04's population is the rows that already carry a restriction code — 812 rows in RUN A-FULL-Q1, 0 rows in RUN B-FUND-100 — so the rows that would make it fail are excluded by its own filter (`converter/controls.py:129`, verdict at `converter/controls.py:137`). In RUN A-FULL-Q1, 392 journal rows belong to funds the register marks `RESTRICTED: Y` and carry no restriction code, and C04 was green. In RUN B-FUND-100 the figure is 96 of 96 rows, and C04 was green over a population of 0. | C-3 |
