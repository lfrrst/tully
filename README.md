<img src="https://cdn.foxglove.cpa/public/tully.gif" alt="Louis Tully, the Ghostbusters' accountant" align="left" width="300" hspace="24" vspace="12">

# Tully

**There is something in your basement, and it has been posting journal entries.**

Six skills that review a tool whose output a firm has to stand behind: a conversion utility,
an allocation engine, a reporting pipeline, a macro nobody has opened in two years, including
one an AI designed. Every figure in what they produce is verified by executing the tool and
measuring its real output, rather than by reading its documentation.

These tools are haunted in a small number of recognisable ways, and the haunting is always
plausible. A reconciliation reports zero variance because it subtracts a column from itself.
A control reads green because the rows that would have failed it were filtered out two lines
earlier. A manifest records a hash that nothing ever recomputes. None of that is dishonesty;
it is what happens when the checks are written by the same mind that wrote the thing being
checked. Tully knows the classes, tests for them by execution, and shows the work.

<br clear="left">

## What the output is, and what it is not

This part does not get to be funny.

The output is an internal working paper supporting a preparer and a reviewer. It is not
an attest report, and nothing here constitutes an audit, review, or agreed-upon-procedures
engagement under professional standards.

## Why "Tully"

Louis Tully is the Ghostbusters' accountant. He itemises his own party as a promotional
expense and invites clients instead of friends, and when the paperwork finally matters he is
the one holding it. His defining trait is substantiation: a figure either has something
behind it or it does not go on the return.

That is the doctrine of this plugin: **a figure you did not produce by executing something
is not evidence.** Not the changelog's figure, not the README's, not the code comment's, not
the previous reviewer's. Those are claims, and testing them is the whole job.

## Install

```
/plugin marketplace add lfrrst/tully
/plugin install tully
```

A clone works too. `.claude-plugin/marketplace.json` sits at the repository root and names
`./` as the plugin source, so the clone is itself a marketplace.

```
/plugin marketplace add /path/to/your/clone/tully
/plugin install tully
```

Then `/tully:review path/to/tool`. You can append `--mode document`, `--mode review` or
`--mode verify` where you want to name the mode yourself, though you rarely need to. Just
describing the tool and what you need from it works as well, since the skills carry their own
triggers and inference from the request is the primary path either way.

## The six skills

In phase order, the orchestrator first.

| Skill | What it does |
|---|---|
| `review-the-tool` | The way in, and it reviews nothing itself. Infers the mode, classifies the artifact against the path registry, creates the evidence folder, then dispatches the five phases below and checks what each hands back. |
| `establish-the-truth` | Phase 1. Executes the tool for real and measures its actual output, producing the evidence base every later figure is quoted from. |
| `map-the-code` | Phase 2. Documents every module and function (signature, business purpose, mechanism with line citations, load-bearing assumptions, failure modes), plus the ordered execution spine of the entry point. |
| `hunt-the-findings` | Phase 3. Works a twelve-section catalogue of the defect classes that tools producing financial deliverables actually have, rather than reading the code again and hoping something surfaces. |
| `write-the-books` | Phase 4. Writes the two deliverables, a human review checklist organised by audit assertion and the function-level code review, with every figure attributed to a measured run. |
| `check-the-facts` | Phase 5. Adversarially fact-checks a finished document: resolves every `file.ext:NNN` citation mechanically, re-derives every quantitative claim from the run folders, and reproduces every finding from scratch. |

Each is independently invocable. Phase 5 in particular is worth running against a document
somebody else wrote, including one another AI wrote.

## The three modes

The mode is inferred from the request rather than asked for, stated before phase 1 starts,
and where a request genuinely reads both ways it resolves toward `review`.

| Mode | What it runs | What it produces |
|---|---|---|
| `document` | `establish-the-truth`, `map-the-code`, then `write-the-books` for the code review alone | The function-level code review, stating on page one that it is documentation and not assurance. No checklist, no finding hunt, no verification pass, and no conclusion about whether the tool can be relied on. |
| `review` (default) | All five: `establish-the-truth`, `map-the-code`, `hunt-the-findings`, `write-the-books`, `check-the-facts` | Both books, over an evidence trail every figure in them is quoted from. Where a project or knowledge base is attached to the session (and only there), `write-the-books` also saves a short project record beside them, as the tail of its own run. A session with nothing attached produces no record. |
| `verify` | `check-the-facts` alone | An error list per document. Works against any document carrying `file.ext:NNN` citations: one a previous reviewer wrote, one another AI wrote, or the previous version of your own book. |

`document` mode leaves out the assurance, not the execution. It still runs phase 1, because a
documentation claim about an edge case is worth much more when it can say the behaviour was
verified than when it can only say the code appears to do it, and the phase costs the same
hour whichever mode asked for it.

## What it does not cover

The artifact path registry has four rows and exactly one path. Deterministic code has it.
These three do not, and are marked *not in this release*:

- **Spreadsheets and models.** A workbook has no functions and no line numbers, so the
  citation format the whole method rests on cannot resolve. A path needs cell-level citation
  (`Sheet!A1`), formula dependency tracing, hardcode detection, and its own catalogue of
  defect classes, because almost nothing in the code catalogue transfers.
- **Workflows where an LLM runs at runtime.** The evidence chain assumes a second run over
  the same input reproduces the first, and every figure inherits that assumption without
  restating it. Determinism decides this, not the file extension. A `.py` file whose central
  step calls a language model is an LLM-at-runtime artifact wearing a code extension.
- **Processes with human steps.** The registry carries this row and nothing else. Neither the
  orchestrator nor this README says what a path for it would need, so nothing here should be
  read as a design for one. What the row records is that the type is recognised and unserved,
  and until someone writes the path, the refusal below is what governs it.

An AI-written memo or technical position has no row at all. The nearest thing available is
`verify` against the document itself, and only where it already carries `file.ext:NNN`
citations that resolve against a source tree.

**The plugin declines these rather than forcing the code path, and the refusal is a
feature.** A spreadsheet forced through a code-shaped review produces a confident and badly
wrong document, which is the precise failure this plugin exists to catch. Every citation
would be invented, and a defect catalogue silently worked at a fraction of its coverage reads
exactly like one worked in full. When Tully declines, it says what the missing path would
need and offers what can legitimately be done instead: measure the artifact and report the
variances, review the deterministic code around it, or fact-check a document already written
about it. Each of those comes labelled so it cannot be filed where a review should have gone.

Adding a path is a new registry row plus the skills it names, and nothing already shipped
gets refactored to accommodate it. See [CONTRIBUTING.md](CONTRIBUTING.md).

## A worked example

[`examples/worked-engagement/`](examples/worked-engagement/) holds a synthetic example rather
than a redacted real engagement: a filled evidence base with two reference runs and their
measured figures, an excerpt of the human review checklist, and an excerpt of the code review,
so the shape of each artifact can be read before anything is run. Every figure in it is
invented, and its own README says so in its first paragraph. That matters more than it might
seem, because the documents are written in the register of a workpaper, and a reader who took
them for a sanitised real engagement would draw conclusions from numbers that were chosen to
make an example work.

The two runs differ, and the figures differ with them, because one run is an anecdote. The
narrow run withholds an input the wide one supplies, and five of the example's conclusions
exist only in the difference. Every figure in both excerpts names the run it came from and
resolves to that run's own `FIGURES` table. An example that quoted a figure from a run it
never defined would demonstrate the exact error phase 5 exists to catch.

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md) covers the two extension points that matter, adding a
finding pattern and adding an artifact path, along with the checks that must pass before a
pull request. It also covers the confidentiality rule, which is not negotiable and outranks
any instruction to transcribe something exactly.
