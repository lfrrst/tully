# A worked engagement

**Everything in this folder is invented.** It is a synthetic example, written to show
the shape of each artifact a review produces, and it is not a redacted real engagement.
There is no client here, redacted or otherwise. Nothing in it was measured, because
there is nothing to measure: the tool does not exist.

Specifically:

- **The tool is fictional.** There is no Ledgerline→Aurora Conversion Utility, no
  `converter/` package and no version 3.4.1+g8f21c. Every `file.ext:NNN` citation is
  well-formed and resolves to nothing.
- **Both systems are fictional.** Ledgerline Fund Accounting and Aurora ERP are invented
  names. They are not stand-ins for particular products.
- **Every figure is invented.** The row counts, the amounts, the control results, the
  populations, the file names and the dates were made up to be internally consistent
  with each other, and with nothing else. Do not benchmark against them, do not cite
  them, and do not read the 1.5% or the 392 as anything a real conversion tends to
  produce.

That last point is why the warning is at the top rather than in a footnote. These
documents are written in the register of a workpaper, which is a register that invites
belief — and a reader who took this for a sanitised real engagement would draw
conclusions from figures that were chosen to make an example work.

The example is deliberately not a template with placeholders. A template shows you the
headings; it does not show you whether you would want to receive the document. These
read as workpapers so that the question can be asked.

## The files

| File | What it demonstrates |
|---|---|
| [`01-evidence-base.md`](01-evidence-base.md) | The output of phase 1, `establish-the-truth`, and the contract in `skills/establish-the-truth/references/evidence-base.md`: the header block, the inputs table with a synthetic input qualified as one, two `RUN` sections whose settings differ, a `FIGURES` table under each in which every "How measured" cell is an operation someone could re-run, and three unreconciled observations left unresolved on purpose. |
| [`checklist-excerpt.md`](checklist-excerpt.md) | An excerpt of Book 1, the human review checklist — §1, three complete tests rated `[T-INDEP]`, `[T-WEAK]` and `[NONE]`, and two rows of the PART F findings register. Shows the per-test template, the priority codes, the reliance ratings, and the working-paper statement. |
| [`code-review-excerpt.md`](code-review-excerpt.md) | An excerpt of Book 2, the function-level code review — §1's purpose-and-method, four rows of the execution spine with its ordering observations, three per-function entries with all four labels, two module-level subsections, and one row of the control inventory with the "what it would fail to catch" cell filled. |

Both excerpts say at the top which sections of the finished book they reproduce and
which they leave out. A real review produces both books whole; an excerpt is what fits
in a repository.

## What to read it for

**Every figure in both excerpts traces to a run defined in the evidence base**, quoted
with the run's identifier attached. That is the property the plugin's verification pass
exists to enforce, and an example that quoted a figure from a run it never defined would
demonstrate the exact error it is meant to catch. Two runs, `A-FULL-Q1` and
`B-FUND-100`, and each figure names one of them.

**The two runs differ, and the figures differ with them.** One run is an anecdote. The
narrow run withholds an input the wide run supplies and covers one fund of 312, so the
control populations, the segment coverage and the balancing line all move — and the
section *What the second run bought* in the evidence base names five conclusions that
only exist in the difference. Two of them reverse what a single run would have
suggested.

**The `[T-WEAK]` test explains a mechanism rather than issuing a verdict.** Test C-3
does not tell the reviewer to distrust control C04; it shows that C04's population
filter is the field C04 tests, so the rows that would fail it are the rows it excludes,
and that it therefore reports a better result as the input gets worse. A reviewer who
has read that can recognise the next control of that shape without being told.
