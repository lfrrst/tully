# Evidence base

**Synthetic example.** The tool, both systems and every figure below are invented.
See [README.md](README.md).

    TOOL: Ledgerline→Aurora Conversion Utility, invoked as `python -m converter.convert`
    VERSION: 3.4.1+g8f21c
    STAGED-AT: C:\Reviews\scratch\ledgerline-aurora-3.4.1\
    EXECUTED: yes
    OWN-TEST-SUITE: PASS 74 / FAIL 0

`VERSION` is the string the tool stamps into `run_header.txt` at
`converter/convert.py:118`, not the one in `CHANGELOG.md`. They disagree; see
unreconciled observation 1.

`REASON-NOT-EXECUTED` is omitted because `EXECUTED` is `yes`. The field is required
only on the other branch.

## Inputs

| Input | Path | Real or synthetic | Notes |
|---|---|---|---|
| Ledgerline trial balance | `inputs/LL-TB-2026-03-31.txt` | Real | The `TB-Hierarchy` report writer's own output: fund header lines, account-group header lines, then indented detail lines. The only source of account codes and balances. It is a trial balance and it nets to zero, which is what makes the balancing-line arithmetic below checkable. |
| Ledgerline fund register | `inputs/LL-FUNDS-2026-03-31.csv` | Real | 312 rows, one per fund, carrying `FUND`, `NAME` and `RESTRICTED`. Read at `converter/fund.py:322`. The only independent statement of which funds are restricted. |
| Aurora segment map | `inputs/aurora-segment-map-v11.xlsx`, tab `MAP` | Real | Hand-maintained by the client's controller. Consumed positionally — see the `apply_segments` entry in [`code-review-excerpt.md`](code-review-excerpt.md). |
| Aurora chart of accounts | `inputs/aurora-coa-2026-05-02.csv` | Real | Exported from the target system on 2 May 2026. The only expectation in this tool that originates outside the pipeline, which is what makes control C02 worth crediting. |
| Restriction extract | `inputs/restrictions-synthetic.csv` | **Synthetic** | The client's restriction extract was not available at the review date. 40 rows were fabricated to exercise the path at all. **Every figure below touching column `RESTRICTION` inherits this qualification**: it describes the fabricated file, not the client's. The procedures that quote those figures still transfer; the counts do not. |

## Runs

### RUN A-FULL-Q1

    SETTINGS: --mode full --as-of 2026-03-31 --funds all --restrictions inputs/restrictions-synthetic.csv
    PATH: evidence/runs/A-FULL-Q1/

The deployed configuration, whole population, restriction extract supplied.

FIGURES

| Figure | Value | How measured |
|---|---|---|
| Parsed detail rows | 4,380 | `wc -l` on `lineage.csv` minus the header |
| Net of the parsed rows | 0.00 | sum of column `BALANCE` in `lineage.csv`, credits negative |
| Rows carrying a `REASON` | 262 | `wc -l` on `dropped.csv` minus the header |
| — of which `NO_AURORA_MAPPING` | 254 | count of rows in `dropped.csv` where `REASON` is `NO_AURORA_MAPPING` |
| — of which `NO_GROUP_CONTEXT` | 8 | count of rows in `dropped.csv` where `REASON` is `NO_GROUP_CONTEXT` |
| Dropped rows carrying a non-zero `BALANCE` | 249 of 262 | count of rows in `dropped.csv` where `BALANCE` is not `0.00` |
| Net of the dropped rows | 1,284,406.17 credit | sum of column `BALANCE` in `dropped.csv`, credits negative; result −1,284,406.17 |
| Journal rows | 4,119 | `wc -l` on `journal.csv` minus the header; equals 4,380 − 262 retained, plus the 1 balancing line below |
| Rows tracing to a trial-balance line | 4,118 | count of rows in `journal.csv` where `SOURCE_LINE` is non-blank |
| Balancing line | 1 row, 1,284,406.17 credit to account `8910` | count of rows in `journal.csv` where `SOURCE_LINE` is blank; sum of `CREDIT` on those rows. Equals the net of the dropped rows above, to the cent and on the same side |
| Gross debits | 84,216,933.42 | sum of column `DEBIT` in `journal.csv` |
| Gross credits | 84,216,933.42 | sum of column `CREDIT` in `journal.csv` |
| Net | 0.00 | sum of `DEBIT` minus sum of `CREDIT` in `journal.csv` |
| Balancing line as a share of gross debits | 1.5% | 1,284,406.17 ÷ 84,216,933.42 |
| Rows with blank `AURORA_ACCOUNT` | 0 | count of rows in `journal.csv` where `AURORA_ACCOUNT` is blank |
| Aurora COA extract accounts | 1,946 | `wc -l` on `inputs/aurora-coa-2026-05-02.csv` minus the header |
| Journal accounts absent from the COA extract | 0 | anti-join of `journal.csv.AURORA_ACCOUNT` onto column `ACCOUNT` of `aurora-coa-2026-05-02.csv`; count of non-matching rows |
| Journal rows whose `FUND` is absent from the fund register | 1 | anti-join of `journal.csv.FUND` onto column `FUND` of `LL-FUNDS-2026-03-31.csv`; count of non-matching rows. The one row is the balancing line, `FUND` `999` |
| Rows with a well-formed `SEGMENT` | 4,119 of 4,119 | count of rows in `journal.csv` where `SEGMENT` matches `^[0-9]{3}-[0-9]{4}-[0-9]{2}-[0-9]{3}-[0-9]$` |
| Rows where `SEGMENT`'s first position differs from `FUND` | 0 of 4,119 | count of rows in `journal.csv` where the substring of `SEGMENT` before the first `-` does not equal `FUND` |
| Distinct segment shapes, zeros preserved | 6 | `SEGMENT` with every non-zero digit replaced by `#` and every zero left as written, then `sort -u`, then `wc -l` |
| Rows carrying a restriction code | 812 | count of rows in `journal.csv` where `RESTRICTION` is non-blank |
| Rows in funds the register marks restricted | 1,204 | join of `journal.csv.FUND` onto `LL-FUNDS-2026-03-31.csv` on `FUND`, keeping `RESTRICTED` = `Y`; count of matching rows |
| — of those, rows blank in `RESTRICTION` | 392 | count of rows in that join where `RESTRICTION` is blank; equals 1,204 − 812 |
| Rows carrying a restriction code in funds the register marks unrestricted | 0 | count of rows in `journal.csv` where `RESTRICTION` is non-blank and the joined `RESTRICTED` is `N` |
| C01 verdict | pass, over 4,119 rows | value of key `C01.result` in `controls.json`, and the row count returned by the filter at `converter/controls.py:74` |
| C02 exceptions | 0, over 4,119 rows | value of key `C02.exceptions` in `controls.json`, and the row count at `converter/controls.py:98` |
| C04 exceptions | 0, over a population of 812 | value of key `C04.exceptions` in `controls.json`, and the row count returned by the filter at `converter/controls.py:129` |
| C05 populated-`SEGMENT` count | 4,119 of 4,119 | value of key `C05.count` in `controls.json`, and the row count at `converter/controls.py:151` |
| Input digests recorded in `manifest.json` | 5 | count of keys under `inputs` in `manifest.json` |
| Deliverable digests recorded | 0 | count of keys under `outputs` in `manifest.json` |
| Float residue | 0.00 | maximum absolute difference between `DEBIT` as written and the source amount re-parsed as `Decimal`, over the 4,118 rows carrying a `SOURCE_LINE` |

### RUN B-FUND-100

    SETTINGS: --mode full --as-of 2026-03-31 --funds 100   (--restrictions omitted)
    PATH: evidence/runs/B-FUND-100/

One fund rather than 312, and the restriction extract withheld so the absent-input
fallback at `converter/fund.py:347` is exercised. Fund 100 is marked `RESTRICTED: Y`
in the register, which is what makes the withheld file visible in the figures rather
than merely absent from them.

FIGURES

| Figure | Value | How measured |
|---|---|---|
| Parsed detail rows | 104 | `wc -l` on `lineage.csv` minus the header |
| Net of the parsed rows | 0.00 | sum of column `BALANCE` in `lineage.csv`, credits negative |
| Rows carrying a `REASON` | 8 | `wc -l` on `dropped.csv` minus the header |
| — of which `NO_AURORA_MAPPING` | 8 | count of rows in `dropped.csv` where `REASON` is `NO_AURORA_MAPPING` |
| — of which `NO_GROUP_CONTEXT` | 0 | count of rows in `dropped.csv` where `REASON` is `NO_GROUP_CONTEXT` |
| Dropped rows carrying a non-zero `BALANCE` | 0 of 8 | count of rows in `dropped.csv` where `BALANCE` is not `0.00` |
| Net of the dropped rows | 0.00 | sum of column `BALANCE` in `dropped.csv`, credits negative |
| Journal rows | 96 | `wc -l` on `journal.csv` minus the header; equals 104 − 8 retained, with no balancing line |
| Rows tracing to a trial-balance line | 96 | count of rows in `journal.csv` where `SOURCE_LINE` is non-blank |
| Balancing line | 0 rows | count of rows in `journal.csv` where `SOURCE_LINE` is blank |
| Gross debits | 6,480,217.09 | sum of column `DEBIT` in `journal.csv` |
| Gross credits | 6,480,217.09 | sum of column `CREDIT` in `journal.csv` |
| Net | 0.00 | sum of `DEBIT` minus sum of `CREDIT` in `journal.csv` |
| Rows with blank `AURORA_ACCOUNT` | 0 | count of rows in `journal.csv` where `AURORA_ACCOUNT` is blank |
| Aurora COA extract accounts | 1,946 | `wc -l` on `inputs/aurora-coa-2026-05-02.csv` minus the header |
| Journal accounts absent from the COA extract | 0 | anti-join of `journal.csv.AURORA_ACCOUNT` onto column `ACCOUNT` of `aurora-coa-2026-05-02.csv`; count of non-matching rows |
| Journal rows whose `FUND` is absent from the fund register | 0 | anti-join of `journal.csv.FUND` onto column `FUND` of `LL-FUNDS-2026-03-31.csv`; count of non-matching rows |
| Rows with a well-formed `SEGMENT` | 96 of 96 | count of rows in `journal.csv` where `SEGMENT` matches `^[0-9]{3}-[0-9]{4}-[0-9]{2}-[0-9]{3}-[0-9]$` |
| Rows where `SEGMENT`'s first position differs from `FUND` | 0 of 96 | count of rows in `journal.csv` where the substring of `SEGMENT` before the first `-` does not equal `FUND` |
| Distinct segment shapes, zeros preserved | 2 | `SEGMENT` with every non-zero digit replaced by `#` and every zero left as written, then `sort -u`, then `wc -l` |
| Rows carrying a restriction code | 0 | count of rows in `journal.csv` where `RESTRICTION` is non-blank |
| Rows in funds the register marks restricted | 96 | join of `journal.csv.FUND` onto `LL-FUNDS-2026-03-31.csv` on `FUND`, keeping `RESTRICTED` = `Y`; count of matching rows |
| — of those, rows blank in `RESTRICTION` | 96 | count of rows in that join where `RESTRICTION` is blank; equals 96 − 0 |
| Rows carrying a restriction code in funds the register marks unrestricted | 0 | count of rows in `journal.csv` where `RESTRICTION` is non-blank and the joined `RESTRICTED` is `N` |
| C01 verdict | pass, over 96 rows | value of key `C01.result` in `controls.json`, and the row count returned by the filter at `converter/controls.py:74` |
| C02 exceptions | 0, over 96 rows | value of key `C02.exceptions` in `controls.json`, and the row count at `converter/controls.py:98` |
| C04 exceptions | 0, over a population of 0 | value of key `C04.exceptions` in `controls.json`, and the row count returned by the filter at `converter/controls.py:129` |
| C05 populated-`SEGMENT` count | 96 of 96 | value of key `C05.count` in `controls.json`, and the row count at `converter/controls.py:151` |
| Input digests recorded in `manifest.json` | 5 | count of keys under `inputs` in `manifest.json` |
| Deliverable digests recorded | 0 | count of keys under `outputs` in `manifest.json` |

### What the second run bought

Five figures move in ways the first run alone could not have shown, and each one
changes a conclusion:

1. **C04's exception count is 0 in both runs and its population falls from 812 rows
   to 0.** The control reports the same green on a run where the restriction extract
   was withheld entirely. Read from RUN A-FULL-Q1 alone, C04 looks like a passing
   completeness control.
2. **Rows in a restricted fund and blank in `RESTRICTION` rise from 392 of the 1,204
   rows in restricted funds to 96 of 96.** The independent measure moves in the
   opposite direction to the control.
3. **The balancing line appears in RUN A-FULL-Q1 and not in RUN B-FUND-100.** It
   carries 1,284,406.17 — 1.5% of the file's gross debits — and it exists because the
   249 dropped rows that carried a balance netted to exactly that, on that side. In
   RUN B-FUND-100 all 8 dropped rows carried `0.00`, the difference was zero, and no
   line was written. Whether the tool plugs a remainder is therefore a property of the
   population, and a run that never triggers it cannot be used to say anything about
   what the plug does to control C01. Both runs report C01 `pass`.
4. **Distinct segment shapes fall from 6 to 2.** A reviewer who sampled
   RUN B-FUND-100 would have tested two of the six shapes the tool actually emits, and
   had no way to know four were missing. Shape is what the positional risk in
   `apply_segments` varies with: a row whose location position is `000` cannot reveal a
   transposed mapping sheet, and a row with a real location can.
5. **Journal rows exceed the retained population by one in RUN A-FULL-Q1 and by none
   in RUN B-FUND-100.** 4,380 − 262 = 4,118, and `journal.csv` holds 4,119. The gap is
   the balancing line. A figure quoted as "journal rows" without its run is ambiguous
   by exactly the row that matters most.

RUN B-FUND-100 is 96 of 4,119 journal rows and 6,480,217.09 of 84,216,933.42 gross —
2.3% of the rows and 7.7% of the value. Neither run is a subset of the other in the
sense that matters: the narrow run exercises the absent-extract path the wide one does
not, and the wide run exercises the plug the narrow one does not.

## Unreconciled observations

| # | What the run said or produced | Why it could not be reconciled |
|---|---|---|
| 1 | `run_header.txt` stamps `VERSION 3.4.1+g8f21c` in both runs. `CHANGELOG.md` describes the deployed build as `3.5.0` and credits it with a segment-order validation step. No such validation exists in the staged tree. | Two readings, and nothing in the run distinguishes them: either the archive was produced by an older build than the one deployed, or the changelog describes work that was never merged. The first makes this review a review of something nobody is running; the second makes it a review of a tool whose documentation claims a control it does not have. Not resolved here. |
| 2 | Both runs emit `WARN: fund 214 has no closing balance line; using the register's balance`, including RUN B-FUND-100, whose population is fund 100 only. | The warning names a fund outside the population the run wrote, so whatever it is measured on is not the delivered population. Whether the fallback it announces was actually applied to any shipped row is not established by the message. Left open. |
| 3 | `manifest.json` in RUN B-FUND-100 records five input digests, including one for `inputs/restrictions-synthetic.csv`, which was not passed to that run. | A digest recorded for a file the run did not read cannot have been computed by that run. Where the value came from — a cache, a previous manifest, a default — is not visible from the artifact. |
