---
name: establish-the-truth
description: "Execute a tool for real and measure its actual output, producing the evidence base that every later figure is quoted from. Use when starting a review of a tool and no measured baseline exists yet, or when asked to run something twice under different settings and record what it produced, establish a baseline before reviewing a script, or check whether a tool's own reported figures match its real output. Trigger on 'establish a baseline', 'run it and measure it', 'what does it actually produce', 'record the reference run', or 'the changelog says X, is that true'. Writes evidence/01-evidence-base.md."
---

# Establish the truth

Before reading a single function, get the tool running and produce real output. It
takes about an hour, and from that point on any question about the tool can be
settled by measurement instead of argument. That is why it comes first — not
because execution is the interesting part of a review, but because every later
phase spends the figures this one produces.

The doctrine the phase exists to serve: **a figure you did not produce by
executing something is not evidence.** Not the changelog's figure, not the
README's, not the code comment's, not the previous reviewer's. Each of those is a
claim, and a claim is a thing you test the baseline against — never a substitute
for having one.

## The five steps

1. **Get the code somewhere you can execute it.** Copy it out of the client
   folder into a scratch workspace so nothing you do touches the original, and
   record where you put it. Bring the real inputs too — the actual source data,
   config, mapping tables, templates. A review run on synthetic data proves the
   code runs; it does not tell you what the client's file will do.

2. **Run the tool's own test suite, if it has one.** Record the exact number that
   passes and the exact number that fails. You need the count rather than the
   verdict, because the most quotable finding in a review of this kind is usually
   "all N of its own assertions pass against the defect below", and it does not
   land without N in it. If there is no suite, record that it is absent — absent
   and never-looked-for read identically in a finished document, and only one of
   them is a fact about the tool.

3. **Execute the tool for real, at least twice, under different settings.** Pick
   settings that exercise genuinely different paths — a different mode, a
   different period, a different population. Two runs give you a comparison; one
   gives you an anecdote. Give every run an identifier before you start it and
   write its output to its own folder under that identifier. These runs are the
   evidence base for every number in both books, and both books should say so on
   their first page.

4. **Measure the output yourself.** Do not read the tool's summary of its output
   — open the files and count. Row counts, totals, how many rows are blank in a
   column that should never be blank, how the line numbering in the lineage file
   relates to the line numbering in the deliverable. Write down how each figure
   was taken, as an operation: `wc -l` minus the header, the sum of a named
   column, the count of rows where a key is blank. A figure whose measurement
   cannot be restated as a command was not measured, it was read off a screen.
   This is where the best findings come from, and they come from arithmetic, not
   insight.

5. **Note anything the run says that you cannot reconcile, and leave it
   unresolved.** A warning naming a mechanism, a figure that does not match the
   documentation, a file the docs say exists that does not. Record each one —
   what the run said, and why it could not be tied to anything — and then stop.
   Do not chase it to an answer now. Resolution is the finding hunt's job; an
   observation resolved here in passing arrives downstream as an assertion nobody
   can re-examine, while an observation recorded open stays a thread anyone can
   pull. In the engagement this phase was written from, a warning citing a
   "next-row heuristic" led to the discovery that the heuristic had been deleted
   three versions earlier and the warning was still firing on a population it did
   not describe. Nobody reasoned their way to that. Someone wrote down a line
   they did not understand.

## Every figure names its run

**A figure recorded without a run identifier is not recorded.** Quoting a figure
that was true of a different run is the single most common error a verification
pass catches, and it is cheap to prevent and expensive to find later: by the time
the figure is sitting in a checklist procedure, the run folder that would
contradict it is one of several and nobody remembers which one it came from. So
attribute every figure to its run at the moment you write it down, not afterwards
from memory. Where a figure differs between runs, state both rather than picking
the one that reads better — a range across two runs is information about the
tool, and a single figure standing in for both is a guess wearing a number.

## Recording it

All of it goes to `evidence/01-evidence-base.md`. Read
`references/evidence-base.md` for the required fields, the order they go in, and
what each is for. Treat it as a contract rather than a template: the later phases
read those field names, so a manifest that renames them is a manifest they cannot
use.

## When the tool cannot be executed

No data, no environment, a licensed dependency the firm does not have, a hardware
requirement. Write the manifest anyway, with `EXECUTED: no` and a
`REASON-NOT-EXECUTED` that names the specific blocker rather than reporting that
the tool would not run. Then say so plainly at the top of both books and mark
every figure in them unverified. A review that cannot run the thing is worth much
less, and the reader must know that before they rely on it.

Fabricate nothing. In particular, do not promote a documented figure to a
measured one by putting it in a `FIGURES` table — the table is for figures you
took, so if nothing was executed it stays empty, and its emptiness is itself part
of what the review reports.

Then name what this makes unverifiable, so the reader learns it from the first
page rather than discovering it in the middle of relying on something:

- **The execution spine has no measured population.** The stages can still be
  listed in the order the code calls them, but what the data actually looked like
  at each point is unknown, and ordering defects are hardest to see without it.
- **No finding can be reproduced.** Every one becomes an inference from reading
  rather than a demonstrated defect. That is a materially weaker claim and has to
  be worded as one — no sentence in the output may begin "Verified:".
- **The checklist's procedures lose their reference figures.** A reviewer working
  the checklist has no measured value to compare their own result against, so
  each affected test silently becomes their job to baseline rather than to check.
- **The verification pass cannot re-derive anything.** Its strongest check is
  recomputing every quantitative claim from the run folders, and there are no run
  folders. The claims in the document will have been read, not recomputed.

If the blocker is something the user can clear — a driver, a data extract, a
machine with access to the source system — say so and offer to establish the
baseline first. An hour of setup buys back all four of those.

## Standalone

- *Needs:* the tool and its real inputs.
- *If that is missing:* if the tool cannot be executed, write the manifest with
  `EXECUTED: no` and the reason rather than producing nothing — an absent
  manifest tells the next phase nothing at all, while `EXECUTED: no` tells it
  precisely what to degrade. If the real inputs are unavailable but the tool
  runs, record every input as synthetic and state that every figure derived from
  it inherits that qualification.
- *Hands back:* the path to `evidence/01-evidence-base.md`.
