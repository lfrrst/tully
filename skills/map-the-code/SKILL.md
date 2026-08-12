---
name: map-the-code
description: "Document every module and function in a tool — signature, business purpose, mechanism with line citations, load-bearing assumptions, and failure modes — plus the ordered execution spine of its entry point. Use when asked what a script or tool actually does at function level, to write a maintainer's reference for code, to document a pipeline stage by stage, or when a review needs a function-level map before findings can be hunted. Trigger on 'what does this function do', 'document every function', 'walk me through the code', 'what order does this run in', or 'write a reference for this tool'. Writes evidence/02-execution-spine.md and evidence/02-map-<layer>.md."
---

# Map the code

The deliverable of this phase is a reference, not an essay. The test is whether a
maintainer holding a number and a question about where it came from can search the
document by function name and land on the answer. That is worth stating first,
because the natural failure here is not sloppy work — it is good prose that
answers nothing.

What this phase produces gets spent twice. The finding hunt — the later phase that
works a catalogue of known defect classes against the code — reads the map rather
than the code cold, because most of those classes are invisible from any single
function and only surface when two are compared, which requires both to have been
written down first. Then both books the review delivers spend it again: the human
review checklist a person works through with the output open beside them, and the
function-level code review, which is this map edited into a book. Both quote it by
citation, so a line number that is wrong here is wrong in a deliverable.

## Split the code into layers

Three to five groups, along the layers the code actually has. The typical grouping
is input and configuration; transformation core; orchestration and controls;
output, interface and tests. Adapt it to what is in front of you — a tool with no
interface and no test suite has three layers, not four, and inventing a fourth
buys an agent with nothing to document and a file nobody opens.

Split on what the code does, not on how long it is. Two 300-line modules that both
parse input belong in one group; a module that parses, transforms and writes
belongs to the layer its bulk serves, with a line in the other groups' dispatch
saying so. The failure to avoid is a function that lands in no file at all because
each agent assumed another had it, and the way to avoid it is to name the boundary
explicitly in every dispatch rather than leave it to be inferred from the grouping.

## Dispatch one agent per layer, in parallel

One `code-mapper` agent per group, all of them at once. They do not need each
other's output — that is what makes the split worth doing — and running them one
after another costs the elapsed time of the whole phase for nothing.

Give every agent the same template. `references/function-entry.md` holds the
per-function entry and the depth target; point each agent at it rather than
paraphrase it into the dispatch, because consistency across sections is what makes
the finished document consultable instead of merely readable. A document where one
layer's entries carry assumptions and another's do not is a document a reviewer has
to read end to end before they can trust any of it.

Each agent writes `evidence/02-map-<layer>.md` and returns the path. Ask for the
path and not the prose: one layer of a 10,000-line tool runs past 10,000 words, and
an agent that answers in its reply has spent that budget on text you then have to
move by hand.

## Ask one agent for the execution spine

The execution spine — the ordered list of the stages the code runs, each with the
state of the data at that point — is a deliverable of its own, not a summary of the
layer files. Ask for it explicitly, from one agent, written to
`evidence/02-execution-spine.md` as a numbered table: the stage, the line its call
site sits on, what it adds, and the population at that point. Then three to five
numbered observations on what a reviewer must take from the ordering, each stated as
a claim carrying its two line numbers.

It matters more than any single layer file because nothing else in the tool makes
sense without knowing what has and has not yet happened at a given moment. A
function that is correct read on its own is wrong if it runs before the thing it
relies on, and that is not visible from the function. Ordering defects — a check
that runs before the thing it checks, a measurement taken after the construction
that conceals it — are only visible against the spine, which is why precision in
these line numbers matters more than anywhere else in the phase. A spine off by one
stage sends the finding hunt to the wrong place, where it finds nothing and reports
that.

The population column comes from the evidence base and from nowhere else: the
per-`RUN` `FIGURES` tables in `evidence/01-evidence-base.md`, the manifest the
previous phase writes. Carry the run identifier with each figure. A population that
was true of one run, sitting in a table a reader takes as general, is the single
most common error caught by the verification pass — the review's last phase, which
fact-checks the finished books adversarially by recomputing what they claim — and
where the populations differ between runs, state both rather than the one that makes
the ordering look tidier.

## State the depth target in the dispatch

An agent not told the target will write an essay, because an essay is what "document
this module" sounds like a request for. The target lives in full in
`references/function-entry.md`; state it in the dispatch as well, in these terms:

- **A heading per function**, matching the actual name, so the document is
  searchable by symbol.
- **Four labelled paragraphs under each**, in the same order every time: what it
  does, how it does it, what it relies on, failure modes.
- **Roughly one line citation per 50 words.** Below that the document has stopped
  being anchored to the code and was written from memory.
- **Private helpers included** where they carry real logic. They are frequently
  where the finding is, precisely because nobody reviews them.

Then say the failure mode in words, because every criterion above can be met by
something thin: **a section that describes a module in three good paragraphs and
moves on has failed, however well written it is.**

Check the returned files against the target before accepting them. This is the one
part a caller can enforce and an agent cannot self-check, because an essay reads
finished. For a 10,000-line tool the finished code review runs 40,000–60,000 words;
that is the size of the artifact, not an overrun to be trimmed.

## One function, asked in passing

A question about a single function needs no dispatch. Answer it in the reply, in the
same four parts: what it does; how it does it, with `file.ext:NNN` citations
verified by opening the file at that line; what it relies on, stated specifically —
"assumes the column is named exactly `ACCOUNT`" is useful, "assumes valid input" is
not; and what happens when that reliance is violated, named as one of raise,
silently coerce, drop rows, or return empty. Which of the four it is decides what a
reviewer has to do about it, so "handles it badly" is not an answer. The template
does not change with scale — that is the point of having one.

## When there is no subagent tool

Work the layers yourself, in the same order, one at a time, writing each section to
its own file before starting the next. Do not hold four in context at once: the
quality collapses in the last one, and it collapses quietly, because the layer
worked last is usually output and interface, where a reader is least equipped to
notice the entries thinned out.

Two things get harder without fan-out, and both are worth deliberate effort:

- **Depth per module drops.** Check your own section against the depth target above
  before starting the next one, while the module is fresh enough that you can still
  tell short from thin.
- **Cross-layer findings are easier to miss.** After the last section, re-read
  `evidence/02-execution-spine.md` against the finished sections hunting
  specifically for ordering defects. A targeted re-read for one class, not a general
  one — re-reading your own work in general finds nothing.

Then disclose it. Say in your own answer, now, that the layers were worked
sequentially rather than in parallel, so the sections are less uniform than a
fanned-out review's and depth varies most in the layer worked last. Say it again in
§1 of the finished code review, when a code review gets written. The disclosure in
the answer is not discharged by the promise of the one in §1 — this phase can be
the only thing that ever runs, and a disclosure deferred to a document nobody
writes is a disclosure nobody makes. Working sequentially is not a defect in the
review. It changes what a reader should expect of its uniformity, and they have to
know that before they rely on it, which means before they leave this conversation.

## Standalone

- *Needs:* `evidence/01-evidence-base.md`, the manifest the previous phase writes,
  for the population column of the spine.
- *If that is missing, or carries `EXECUTED: no`:* produce the map anyway. It does
  not depend on execution, and reading the code is exactly what remains available,
  so refusing would cost the whole phase to protect one column. Keep that column and
  fill every cell with `not measured`. Do not drop it — an absent column hides that
  the figure was never taken, while `not measured` in every row says so, and that
  difference is what a reader needs in order to judge the spine. Invent nothing; in
  particular do not read a population off the documentation or a code comment into a
  cell a reader will take as measured. State the degradation at the top of your own
  output — no population in this spine was measured, so no ordering claim in it has
  been demonstrated against real data, only inferred from reading — and offer to
  establish the baseline first, saying what it buys: a measured population at every
  stage, and findings the hunt can reproduce rather than infer.
- *Hands back:* the paths written — `evidence/02-execution-spine.md` and one
  `evidence/02-map-<layer>.md` per layer.
