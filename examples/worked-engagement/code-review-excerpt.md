# Code Review — excerpt

## Ledgerline→Aurora Conversion Utility v3.4.1+g8f21c — complete reference

**Synthetic example.** The tool, both systems, every line number and every figure below
are invented. There is no `converter/` package; the citations are well-formed and they
resolve to nothing. See [README.md](README.md).

**This excerpt is §1, four rows of §4's execution spine with its ordering observations,
three per-function entries from PART II, two module-level subsections, and one row of
the control inventory from PART III.** The finished book also carries §2 (the domain in
one page), §3 (architecture and the design decisions that shape everything downstream),
the remaining 68 function entries across PARTs I to IV, the rest of the control
inventory, and PART V — invariants, documentation versus behaviour, controls that cannot
fail, defects, what held up under direct attack, unguarded reliance, the test suite, and
the conclusion.

---

## 1. Purpose and method

**The output is an internal working paper supporting a preparer and a reviewer. It is
not an attest report, and nothing here constitutes an audit, review, or
agreed-upon-procedures engagement under professional standards.**

**What was read.** Every line of the nine modules of `converter/` as staged at
`C:\Reviews\scratch\ledgerline-aurora-3.4.1\` — 6,340 lines, by `wc -l` over
`converter/*.py` at that path — together with its 74-test suite, its `CHANGELOG.md` and
the two operator notes in `docs/`. Nothing was read from
the deployed copy; the staged tree is the subject, and `VERSION` was taken from the
runtime stamp at `converter/convert.py:118` rather than from the changelog, which
disagrees with it.

**What was executed.** Two runs, both recorded in
[`01-evidence-base.md`](01-evidence-base.md), and every figure in this document is
quoted from one of them with its identifier attached:

- **RUN A-FULL-Q1** — `--mode full --as-of 2026-03-31 --funds all` with the restriction
  extract supplied. 4,380 parsed rows, 262 carrying a reason, 4,119 journal rows,
  84,216,933.42 gross on each side.
- **RUN B-FUND-100** — the same as-of date, one fund, restriction extract withheld. 104
  parsed rows, 8 carrying a reason, 96 journal rows, 6,480,217.09 gross on each side.

Two runs rather than one because four of this document's conclusions are only visible in
the difference between them, and one of them — what the balancing line does to control
C01 — is invisible in RUN B-FUND-100 entirely, since that run never writes one.

**What "verified" means here.** Every citation is `file.ext:NNN` and was resolved by
opening the staged file at that line; a citation in this document is a claim that the
named line says what the sentence says it says. Where the code contradicts its own
comment or docstring, this document says so and says which is right. Where a figure
differs between the two runs, both are given rather than the one that reads more tidily.

**Qualification carried from the evidence base.**
`inputs/restrictions-synthetic.csv` was fabricated: the client's restriction extract was
not available at the review date. Every figure touching `RESTRICTION` describes that
fabricated file. The mechanisms transfer; the counts do not, and they are marked where
they appear.

**What this document is not.** Not a security assessment — no attempt was made to
attack the tool or its host. Not a rewrite proposal; the remediation order in §15 names
the smallest change that closes each finding, not the design someone would choose
today. Not an evaluation of the business judgements encoded in
`aurora-segment-map-v11.xlsx`: whether Ledgerline account `4100` *should* map to Aurora
`4100` is the controller's call and this review takes the sheet as given. What it does
evaluate is whether the tool consumes the sheet the way the sheet is written, and that
is finding 12.2.

---

## 4. The execution spine

Rows 3, 5, 7 and 8 of the eleven-stage table. Every population is measured, and carries
the run it was measured on.

| # | Stage | Call site | What it adds | State of the data |
|---|---|---|---|---|
| 3 | `read_ledgerline_hierarchical(tb_path, as_of)` | `converter/convert.py:142` | The working population: one row per trial-balance detail line, with `FUND`, `LL_ACCOUNT`, `BALANCE` as `Decimal`, `SOURCE_LINE`, and `NO_GROUP_CONTEXT` written on any detail line that appeared before its account-group header | 4,380 rows, 8 already carrying a `REASON`, net 0.00 (RUN A-FULL-Q1). 104 rows, 0 carrying a `REASON`, net 0.00 (RUN B-FUND-100) |
| 5 | `apply_segments(rows, map_path)` | `converter/convert.py:161` | `AURORA_ACCOUNT` and the five-part `SEGMENT`; `NO_AURORA_MAPPING` on rows the sheet does not cover | 4,380 rows, 262 now carrying a `REASON` — 254 unmapped plus the 8 from stage 3 (RUN A-FULL-Q1). 104 rows, 8 (RUN B-FUND-100). The population is unchanged in both: nothing is deleted here or anywhere |
| 7 | `apply_restrictions(rows, register_path, extract_path)` | `converter/convert.py:174` | `RESTRICTION` on rows the extract covers; one `WARN` line per fund with no closing balance line | 4,380 rows, 812 carrying a restriction code (RUN A-FULL-Q1). 104 rows, 0 — the extract was not supplied and the fallback at `converter/fund.py:347` took the silent branch (RUN B-FUND-100) |
| 8 | `build_journal(rows, as_of)` | `converter/convert.py:188` | The deliverable: one line per row with no `REASON`, plus the balancing line `_plug_residue` appends | 4,119 journal rows = 4,118 retained + 1 balancing line for 1,284,406.17 credit (RUN A-FULL-Q1). 96 journal rows = 96 retained + none (RUN B-FUND-100) |

### What a reviewer must take from the ordering

1. **The controls run after the construction that settles them.** `_plug_residue` writes
   the balancing line during stage 8 (`converter/convert.py:188`, appended at
   `converter/journal.py:418`). C01 recomputes total debits against total credits during
   stage 9 (`converter/convert.py:203`, at `converter/controls.py:74`). C01's input is a
   file that was made to balance one stage earlier, so its arithmetic cannot return a
   failing value, and it returned `pass` on both runs — over 4,119 rows in
   RUN A-FULL-Q1 and 96 in RUN B-FUND-100.
2. **The population never shrinks, so every figure needs its file named.** Stage 5
   leaves 4,380 rows of which 262 carry a reason (`converter/convert.py:161`); stage 8
   emits 4,119 (`converter/convert.py:188`). `lineage.csv` is the stage-5 population and
   `journal.csv` the stage-8 one, so "rows" means 4,380, 4,118 or 4,119 depending on
   which file is meant (RUN A-FULL-Q1) — three defensible answers to one question, and
   the figure reads unambiguous in all three.
3. **Nothing between stage 3 and stage 8 compares `SEGMENT`'s first position to
   `FUND`.** Stage 3 reads `FUND` from the trial balance
   (`converter/convert.py:142`) and stage 5 writes `SEGMENT`'s first position from the
   mapping sheet (`converter/convert.py:161`); stage 8 copies both forward untouched
   (`converter/convert.py:188`). They agreed on every row of both runs — 0 differences
   over 4,119 rows in RUN A-FULL-Q1 — but nothing in the tool would report it if they
   stopped agreeing, and that comparison is the only mechanical detector of the defect
   at 12.2.
4. **The version stamp is written before anything is read, and the manifest after
   everything.** `run_header.txt` is stamped at `converter/convert.py:118`, before stage
   3; `manifest.json` is written at `converter/convert.py:229`, after stage 11. The
   stamp therefore describes the build and not the run, which is why the changelog
   disagreement is unresolvable from the artifacts alone (unreconciled observation 1).
   The manifest records 5 input digests in both runs, including one for a file
   RUN B-FUND-100 never opened (unreconciled observation 3), and 0 output digests: it
   attests what went in and nothing about what came out.

---

## PART II — The transformation core

### Module-level material: `converter/segments.py`

Five constants, and the fourth is the one that does damage.

`SEGMENT_WIDTHS = (3, 4, 2, 3, 1)` at `converter/segments.py:19` — the per-position
widths each segment part is left-padded to. Positions 1 and 4 share a width, which is
what makes a transposition between them undetectable by format. `SEGMENT_JOIN = "-"` at
`converter/segments.py:21` and `MAP_SHEET = "MAP"` at `converter/segments.py:22` are
what they look like. `MAP_FIRST_SEGMENT_COL = 1` at `converter/segments.py:23` is the
column index the five segment parts are read from, **by position** — the sheet's headers
are never consulted. `UNMAPPED_REASON = "NO_AURORA_MAPPING"` at
`converter/segments.py:25` is the string written into `REASON`, and it is compared as a
literal in three other modules rather than imported.

### Module-level material: `converter/journal.py`

`ROUNDING_ACCOUNT = "8910"` at `converter/journal.py:28`, `RESIDUE_FUND = "999"` at
`converter/journal.py:29` and `RESIDUE_SEGMENT = "999-8910-00-000-0"` at
`converter/journal.py:30` are the identity the balancing line is posted under. All three
are hard-coded; none is checked against the target chart, the fund register or each
other. `NORMAL_SIDE` at `converter/journal.py:33` maps an account's first digit to
`DEBIT` or `CREDIT` and has five keys, so it covers first digits 1 to 5 and raises on
anything else.

The balancing line is the only journal row whose `FUND` is absent from the fund register
— 1 of 4,119 rows in RUN A-FULL-Q1, and it is `999`.

### `apply_segments(rows: DataFrame, map_path: Path, sheet: str = MAP_SHEET) -> DataFrame`

**What it does.** Attaches the Aurora account and the five-part Aurora segment string to
every row of the working population, and writes `NO_AURORA_MAPPING` on the rows the
mapping sheet does not cover. It is the only place in the tool where a Ledgerline
account becomes an Aurora one.

**How it does it.** Reads tab `MAP` with `dtype=str` (`converter/segments.py:63`) so
leading zeros survive the read, keys a lookup on the sheet's first column
(`converter/segments.py:71`), then takes the five segment parts **by position** —
`frame.iloc[:, MAP_FIRST_SEGMENT_COL:MAP_FIRST_SEGMENT_COL + 5]` at
`converter/segments.py:74` — and never by header name. `AURORA_ACCOUNT` is written from
the second part (`converter/segments.py:81`); each part is left-padded to its
`SEGMENT_WIDTHS` entry with `str.rjust` (`converter/segments.py:88`), joined with
`SEGMENT_JOIN` (`converter/segments.py:92`) and written to `SEGMENT`
(`converter/segments.py:95`). Rows with no key match take the other branch: `SEGMENT`
stays blank and `REASON` receives `UNMAPPED_REASON` (`converter/segments.py:108`). 254
of 4,380 rows took that branch in RUN A-FULL-Q1 and 8 of 104 in RUN B-FUND-100.

Worked: fund `100`, account `4100`, department `07`, location `312`, basis `0` yields
`100-4100-07-312-0`. Because positions 1 and 4 are both three digits
(`converter/segments.py:19`), a sheet whose fund and location columns have been
transposed yields `312-4100-07-100-0` for the same row — a string that matches the
format regex, satisfies C05, passes C02 because the account position is untouched, and
posts fund 100's balances to fund 312. The one comparison that would catch it —
`SEGMENT`'s first position against the row's own `FUND` — is clean on both runs, 0 of
4,119 rows in RUN A-FULL-Q1, and the tool does not perform it. A reviewer must.

**What it relies on.** A tab named exactly `MAP` (`converter/segments.py:22`). The key
in the sheet's first column and the five segment parts in columns 1 to 5 **in Aurora's
own order** (`converter/segments.py:74`) — nothing verifies this and nothing reads
Aurora's segment definitions anywhere in the tool. `dtype=str` on the read
(`converter/segments.py:63`): without it the reader infers integers and a part like `07`
arrives as `7`, which `str.rjust` (`converter/segments.py:88`) then pads back to `07` —
so the tool appears to work without the argument. That repair is coincidental. It
restores the string only while each part's significant digits fit its declared width,
which is accidental correctness of the kind that survives every test and breaks the
first time a width in `SEGMENT_WIDTHS` changes. `rows` already carrying `LL_ACCOUNT`,
written by stage 3
(`converter/convert.py:142`). And that it runs before stage 8
(`converter/convert.py:161` before `:188`), because the balancing line's segment is a
constant and is not produced here.

**Failure modes.** A missing tab raises `ValueError` from the reader
(`converter/segments.py:63`) and the run stops with nothing written. A sheet with fewer
than six columns raises `IndexError` at `converter/segments.py:74`. An unmatched key
never raises — the row keeps a blank `SEGMENT`, receives its reason
(`converter/segments.py:108`) and leaves the deliverable by that route, which is
correct behaviour and is how 254 rows left in RUN A-FULL-Q1. A **reordered** sheet
raises nothing, drops nothing and reports nothing: it relabels every row silently, and
that is finding 12.2.

### `build_journal(rows: DataFrame, as_of: date) -> DataFrame`

**What it does.** Turns the retained working population into the conversion journal —
one line per row that carries no `REASON`, with the debit or credit side chosen from the
account's normal side — and appends a balancing line if the two sides do not agree.

**How it does it.** Filters on `rows["REASON"].fillna("") == ""`
(`converter/journal.py:358`), which retains 4,118 of 4,380 rows in RUN A-FULL-Q1 and 96
of 104 in RUN B-FUND-100. The `fillna` is load-bearing and correct: the parse stage
leaves `REASON` null rather than empty on untouched rows
(`converter/convert.py:142`), so an equality test alone would have dropped every clean
row from the journal without writing a reason for any of them. The side comes from
`NORMAL_SIDE` keyed on the account's first digit (`converter/journal.py:366`) and the
absolute balance is written into `DEBIT` or `CREDIT` (`converter/journal.py:371`);
`SOURCE_LINE` is copied forward (`converter/journal.py:377`) so every constructed row
traces to a trial-balance line; `EFFECTIVE_DATE` is stamped from `as_of`
(`converter/journal.py:384`). Then `_plug_residue` is called
(`converter/journal.py:404`).

The filter at `converter/journal.py:358` is where the 262 reasoned rows leave the
deliverable, and their net leaves with them. Because the parsed population is a trial
balance and nets 0.00, the retained population is out of balance by exactly the dropped
population's net, with the sign preserved: 1,284,406.17 credit in RUN A-FULL-Q1, on both
sides of that identity. Nothing in this function measures that, and no key in
`controls.json` reports it.

**What it relies on.** `REASON` present as a column (`converter/journal.py:358`) and
blank-or-null on rows to retain. `NORMAL_SIDE` covering every first digit that occurs
(`converter/journal.py:33`). Balances already parsed as `Decimal` by stage 3
(`converter/convert.py:142`) — this function performs no rounding and no float
arithmetic, which is why the measured float residue is 0.00 over the 4,118 sourced rows
in RUN A-FULL-Q1, and that is a real strength worth crediting. Ordering: after stage 5
(`converter/convert.py:161`) so `AURORA_ACCOUNT` exists, and before stage 9
(`converter/convert.py:203`), which is the load-bearing one — C01 measures the file this
function has already balanced.

**Failure modes.** `KeyError` at `converter/journal.py:366` on an account whose first
digit is absent from `NORMAL_SIDE`; the run stops, which is the right outcome. `KeyError`
at `converter/journal.py:358` if `REASON` is absent entirely. If every row carries a
reason it returns an empty frame and the run continues to stage 9
(`converter/convert.py:203`), where C01 reports `pass` over zero rows and C02 reports 0
exceptions over zero rows — an unblocked, fully green run producing an empty
deliverable. Not reproduced against the client data; reproduced against a fixture, and
recorded as a dormant defect at 12.4.

### `_plug_residue(journal: DataFrame) -> DataFrame`

Private, four lines of body, and the reason control C01 cannot fail. It is documented
here at the same depth as the public functions because nothing else in the tool decides
more.

**What it does.** Appends one balancing line for the difference between total debits and
total credits, so the journal handed to Aurora is always in balance.

**How it does it.** Computes `diff = journal["DEBIT"].sum() - journal["CREDIT"].sum()`
(`converter/journal.py:414`), returns the frame untouched when `diff == 0`
(`converter/journal.py:416`), and otherwise appends one row carrying `abs(diff)` on the
opposite side (`converter/journal.py:418`), with `AURORA_ACCOUNT` set to
`ROUNDING_ACCOUNT` (`converter/journal.py:419`), `FUND` and `SEGMENT` set to
`RESIDUE_FUND` and `RESIDUE_SEGMENT` (`converter/journal.py:420`), and `SOURCE_LINE`
left blank (`converter/journal.py:421`) — the only row in the deliverable without one,
and therefore the only way to find it.

In RUN A-FULL-Q1 `diff` was 1,284,406.17 on the debit side, the appended credit line
took the journal from 4,118 rows to 4,119, and the amount is 1.5% of the file's gross
debits. In RUN B-FUND-100 all 8 dropped rows carried `0.00`, `diff` was 0.00, the guard
at `converter/journal.py:416` returned early, and no such row exists — which is why a
review conducted on RUN B-FUND-100 alone could not have described this behaviour at all,
and why C01's `pass` means something different in each run.

**What it relies on.** Nothing outside the frame: no config key, no threshold, no
materiality figure, no maximum. The same four lines write six cents or the
1,284,406.17 they wrote in RUN A-FULL-Q1, with no difference in behaviour, in the
output, or in what the run reports. `ROUNDING_ACCOUNT` `8910`
(`converter/journal.py:28`) must exist in the Aurora chart or the deliverable fails at
import; it does exist in the 2 May 2026 extract of 1,946 accounts, so C02 reported 0
exceptions over 4,119 rows in RUN A-FULL-Q1. Nothing ties the constant to that chart,
so the coverage is coincidental and would lapse the first time `8910` is deactivated in
Aurora.

**Failure modes.** It never raises. It writes silently, at any magnitude, with no line
in `run_header.txt` and no key in `controls.json` — verified: neither run's
`controls.json` contains a key naming the balancing line, and the RUN A-FULL-Q1 line is
discoverable only by counting rows with a blank `SOURCE_LINE`, which is how it was found
here. **Finding, stated here where the reference reader meets it and again at 12.1:** a
material figure is written into the deliverable by a function with no threshold, and the
control that would have surfaced it measures the file afterwards.

---

## PART III — The control inventory

One row of six. Every column is filled for every control in the finished table; the last
one is the point of it.

| Identifier | Title / question | Line | Population measured | Blocks? | What it would fail to catch |
|---|---|---|---|---|---|
| C01 | *"Total debits equal total credits"* | `converter/controls.py:74` | Every row of `journal.csv` — 4,119 rows (RUN A-FULL-Q1), 96 (RUN B-FUND-100) — read after stage 8 has written it | Yes, and the operator note declares it *"the control that proves the conversion is complete"* | Any imbalance whatever, because `_plug_residue` (`converter/journal.py:418`) has already written the difference as a row before C01 measures it. Specifically: the 1,284,406.17 credit the 262 dropped rows left in RUN A-FULL-Q1, which C01 reported `pass` over; any misclassification, sign error or fund error that preserves the two totals, which is all of them, since the side comes from the account's first digit (`converter/journal.py:366`) and is not affected by which account within that digit was chosen; and completeness in every sense — it compares the file to itself, holds no expectation from outside the pipeline, and would report `pass` over an empty journal |

**Controls whose arithmetic cannot return a failing value.** Two of the six, and they
fail differently. C01 is declared as a blocking control and quoted above as proof of
completeness, so the documentation's claim and the code's capability are in direct
conflict — demonstrated, not asserted: the plug at `converter/journal.py:418` runs at
stage 8 (`converter/convert.py:188`) and the test at `converter/controls.py:74` runs at
stage 9 (`converter/convert.py:203`). C04's mechanism is different: its population
filter is the field it tests (`converter/controls.py:129`, verdict at `:137`), so the
rows that would make it fail are the rows it excludes, and it gets greener as the input
gets worse — 0 exceptions over 812 rows in RUN A-FULL-Q1 and 0 over 0 in
RUN B-FUND-100, where the extract was withheld entirely.

**The shape both share, and the thing to check about the next control added:** a control
that draws its expected value from the file it is measuring is arithmetic, not evidence.
C02 is the one control in this tool that does not — it compares `AURORA_ACCOUNT` against
an extract from the target system (`converter/controls.py:98`), a file the tool did not
produce — and it is the one control this review credits without qualification.
