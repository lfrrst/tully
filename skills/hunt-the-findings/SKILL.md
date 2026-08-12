---
name: hunt-the-findings
description: "Work a catalogue of defect classes that tools producing financial deliverables actually have — checks that cannot fail, checks measured on the wrong population, ordering defects, attestation without detection, silent coercion, documentation contradicting behaviour, unguarded reliance. Use when a function-level map exists and the review needs its defects found, or when asked whether a tool's controls are worth anything, whether a green dashboard means what it appears to, or to look for what a test suite cannot see. Trigger on 'what could go wrong here', 'are these checks real', 'can this control fail', 'what does the test suite miss'. Writes evidence/03-findings.md."
---

# Hunt the findings

This is the finding hunt — the phase that works a catalogue of known defect classes
against the code, rather than reading the code again and hoping something surfaces.
The difference is the whole method. A map tells you what each function does. It does
not tell you that the reconciliation two layers away compares that function's output
against itself.

Most classes in the catalogue are invisible from any single function. They appear only
when two things the code keeps apart are compared: a check against the population it
measures, a measurement against the construction that follows it, a document against
the behaviour it describes. Nobody reads their way to those. Each is a comparison
somebody has to decide to make, which is why the catalogue is worked deliberately and
in order instead of consulted when something looks odd. The defects that would have
caught your eye unaided are the shallow ones.

## Work the catalogue in order

`references/finding-patterns.md` is the catalogue: twelve sections, each giving the
shape of a class, how to test for it, and why it matters to a reader. Work them in
order and record a verdict for every one.

In order, because the sections are arranged roughly by yield — checks that cannot fail
first, deliverable hygiene and containment last. Working them in sequence front-loads
the findings that change a reader's mind, so a hunt that runs out of time has covered
the ground that mattered most rather than a random half of it.

A verdict for every one, including the classes that come back clean, because a class
with no verdict is indistinguishable in the finished document from a class with no
defect. The reader cannot tell which they are looking at, and will assume the
flattering one.

## What a check is worth

The single most useful thing this phase does is separate **what the tool attests** from
**what the tool detects**. A tool can pass every one of its own assertions and still
ship a file that fails on load. It can print "reconciles to source: $0.00 variance"
from an arithmetic identity that cannot return another number. It can declare a control
blocking in its documentation while the code turns it into a warning. None of that is
dishonesty. It is what happens when the checks are written by the mind that wrote the
thing being checked.

So treat the green board as the object of study, never as evidence. For every check on
it:

- **Trace both operands back to where they are written.** If they are the same data and
  no stage between them mutates it, the check is an identity and will report zero
  variance forever. Confirm it by searching the codebase for every assignment to the
  column in question, not by reading the check again — if there are only one or two and
  neither is in the path, you have it.
- **Read the value passed as the verdict.** Some are a hard-coded true. Some read a
  statistic that is itself a constant. Grep for the statistic's key and see who writes
  it.
- **Ask what ran immediately before it, and on what population.** A check counting
  blanks, run directly after a step that filled every blank on the identical mask, is
  measuring its own predecessor. It could fail in principle and cannot under the
  settings in force, which is the version of this defect that survives review.
- **Compare the filter the check applies against the filter the deliverable writer
  applies.** Write both down exactly rather than summarising them, then say which is
  wider and whether the difference is deliberate. A check reporting on rows that are
  not in the file cannot see an error confined to rows that are.

Then say, per check, whether it is **correctly declared informational** or is
**presented as a control**. That distinction is the finding — not the tautology by
itself. An informational measure honestly labelled is fine and should be left alone;
the same code described in the operating documentation as a control is a finding, and
the finding is the gap between the two documents rather than anything in the code.

And credit the checks that can actually fail. A check whose expected value comes from
outside the pipeline — a control total from the source system, a figure the client
supplied, a count from a system the tool does not write to — is doing real work,
because there is something present that can disagree with it. Where a completeness
check is deliberately wider than the deliverable so it can account for rows that did
not ship, say so and credit it. A reader looking at a green board needs to know which
greens carry weight, and a review that only subtracts leaves them with no board at all.

## Test it, don't reason about it

Every candidate gets tested, and how it was tested gets recorded as an operation rather
than an adjective: the command run, the file deleted, the value edited, the number that
came back. "Carefully reviewed" records nothing — it cannot be re-run, and it cannot be
wrong, which are the same property.

The strongest tests are provocations. Delete the source file a cache is keyed on and
run the tool; if it completes and attests a digest for a file that is not there, that
is a serious finding and you now have it rather than suspect it. Put a thousands
separator or accounting parentheses into a column that reaches a coercion with errors
suppressed. Put two files in the folder that assumes exactly one, and see whether the
tie-break is by name or by date. Work an offsetting pair through with real numbers by
executing it, because getting both signs backwards is easy, survives the aggregate, and
a test asserting the generated lines net to zero passes either way.

One reproduced finding is worth ten that say "this could fail". A reproduced finding
survives the verification pass — the review's last phase, which fact-checks the
finished books adversarially by recomputing what they claim — while an inferred one
gets re-argued there by someone with less context than you have now, and often loses.
**Both books** are what the full review delivers: the human review checklist a person
works through with the output open beside them, and the function-level code review.

## What the spine and the maps are for

Ordering defects (catalogue §3) are the richest seam and are only visible against the
**execution spine** — the ordered list of the stages the code runs, each with the state
of the data at that point, written by the mapping phase to
`evidence/02-execution-spine.md`. Use it to find where a figure is computed and where
the construction that could conceal it is applied, then state the distance between them
in lines and in stages. When the control is ordered correctly this is the strongest
thing in the tool and should be credited loudly; when it is not, the run looks
immaculate.

If that file opens with a paragraph above its numbered table saying no population was
measured, that is correct output and not a malformed file. The mapping phase ran
without a measured baseline and is telling you so. Read it as a constraint on this
phase specifically: it is the ordering work that degrades, because a stage table with
`not measured` in every population cell still fixes the order but no longer shows the
data moving, so a claim about what a stage saw is inference rather than measurement and
has to be worded as one.

The layer maps are `evidence/02-map-<layer>.md`, one per layer — the function-level
record of what each function does, how it does it, what it relies on, and how it fails
when that reliance is violated. A complete one also carries **module-level subsections**
outside the per-function entries: constants, hard-coded account numbers, default
configurations, sentinel values. Several classes live exactly there — the positional
configuration in §7 that makes a mis-ordered file internally consistent and entirely
wrong, the sentinel behind §5's absent-versus-zero distinction, the hard-coded accounts
behind §8's sign convention. If those subsections are missing, the map is incomplete;
it does not mean the tool has no module-level state. Say which maps lack them and read
those modules' top level yourself before working those classes.

Figures come from `evidence/01-evidence-base.md`, the manifest the first phase writes:
`EXECUTED`, one `RUN` per execution, and a `FIGURES` table under each. Quote every
figure with its `RUN` identifier attached. A figure that was true of one run, sitting in
a finding a reader takes as general, is the single most common error the verification
pass catches, and here it is worse than elsewhere — it is the number the finding rests
on.

## An absent evidence file is not evidence

Many tools write an exceptions file only when there are exceptions. Its absence means
the tool found none *by its own definition* — which is exactly the definition under
review.

When someone offers the empty folder as reassurance, say plainly that it is not
reassurance, and say why: the artifact that would record the exceptions is generated by
the same logic whose completeness is the question, so its silence is the claim being
tested rather than support for it. Contradict the inference rather than softening it.
Agreeing costs the review the one class of finding the user has already ruled out for
you, and they will not raise it again. The same shape arrives as an empty exceptions
tab, a log with no warnings, a variance cell reading zero, and a suite that is all
green.

What to do instead is establish what the control set does not cover **by inspecting the
artifacts** — enumerate the checks that actually exist from the register and the output
files, then set that list against the catalogue and name the classes for which no check
was ever written — rather than by reasoning about the code, which is how you end up
describing the controls the author intended. This is §9's closing distinction and it is
worth stating in the finished document in those terms: a suite can verify
**documentation coverage**, every control having an entry, without verifying
**detection coverage**, a defect class existing for which no control was ever written.
Name the classes in the second category. That list is frequently the most valuable
paragraph in the review.

## Record what held up

Negative results are part of the deliverable. A review that lists only defects is not
usable, because the reader cannot tell what was examined and found sound from what was
never examined — and silence reads as absence of defect when it is absence of
information. Catalogue §12 has the standing subjects.

Give them their own section, and for each say what was probed and how, in the same
operational terms as a finding. Good subjects: money handling and float error; the
ordering of the key control; whether the population that ships is the population that
was checked; sign correctness on the real data; whether anything is dropped between
parse and output; duplicate-key handling; behaviour under the installed dependency
versions; and the specific security axes tested and found clean.

Then let the conclusion turn on the contrast. "Sound arithmetic, defective attestation"
tells a partner more than either half alone, and it is only available to a review that
wrote down both.

## The output contract

Everything goes to `evidence/03-findings.md`. Per candidate:

- **Pattern class** — the catalogue section it came from, by number, so coverage can be
  audited against the twelve rather than taken on trust.
- **The shape observed** — what is actually in the code, with `file.ext:NNN` citations
  verified by opening the file at that line.
- **How it was tested** — the operation. A command, an edit, a deletion, a run.
- **The verdict** — defect, sound, or not determinable, and for a defect what it does to
  the deliverable stated in the deliverable's own units.
- **The evidence** — the figures the verdict rests on, each naming its `RUN`.
- **Reproducible** — yes, with the steps; or no, with the reason.

Two readers spend this file and both need it in this shape. Both books draw on it, and
the checklist's compensating procedures exist only because of what this file records, so
a finding with no stated deliverable impact produces a procedure nobody can size. Then the verification pass
reproduces every entry from scratch. Write each one to be reproduced: a candidate whose
test is not restated as an operation cannot be re-run, and what comes back is not a
confirmed finding but an unverifiable claim, which is worse than nothing in a workpaper
because it has to be either chased or withdrawn.

## Standalone

- *Needs:* `evidence/01-evidence-base.md` for figures, `evidence/02-execution-spine.md`
  for the ordering classes, and the `evidence/02-map-<layer>.md` layer maps for
  everything reached function by function.
- *If that is missing:* work the classes that need only the code, and be explicit about
  which ones you did not work. Without the execution spine the ordering-defect classes
  (§3) cannot be worked at all — every one of them is a comparison between two stages,
  and with no ordered stages there is nothing to compare, so this is not a matter of
  reduced confidence but of the class being unavailable. Without an evidence base the
  classes that need measurement cannot be tested: population mismatch (§2), the
  coercion and dropping shapes (§5) that need real input formats, float error (§8),
  and deliverable hygiene (§10), which needs the actual bytes of an actual output file.
  What remains genuinely workable from the code alone is most of §1, §6's
  documentation contradictions, §7's unguarded reliance, and §9's test-suite shapes —
  which is real value, so produce it rather than refusing.

  Then name the classes not attempted, rather than reporting a clean sweep. A catalogue
  silently worked at half coverage reads identically to one worked fully, and the
  reader's mistake is not that they overestimate the findings — it is that they
  conclude the unnamed classes were checked. Say it in both channels: at the top of
  your own answer, now, and as the first thing in `evidence/03-findings.md`, above the
  findings. Neither channel discharges the other, because they have different readers.
  The answer is the only one the user sees, and they decide what to rely on before they
  leave this conversation. The file is the only one the downstream phases see — the
  book-writing phase, and the verification pass, which opens it without this
  conversation attached and reproduces each entry from scratch. An unmarked gap is read
  there as ground that was covered and found clean, and a verification pass cannot
  reproduce an absence it was never told about. Offer to establish what is missing, in
  both places, and say what it buys: the ordering classes become workable at all, and
  the measured classes become reproducible instead of inferred.
- *Hands back:* the path to `evidence/03-findings.md`, and the list of catalogue
  sections worked, with the verdict for each.
