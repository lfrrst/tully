# Contributing to tully

Two extension points carry most of the value here: the catalogue of defect classes the
finding hunt works, and the registry of artifact types that have a review path at all.
Both have a shape, and a contribution that does not fit the shape is harder to accept than
one that is simply wrong, because the shape is what makes the output checkable.

## Adding a finding pattern

The catalogue lives in `skills/hunt-the-findings/references/finding-patterns.md`. Every
entry gives three things, in this order:

1. **The shape.** What the defect looks like in code, stated concretely enough to
   recognise in a file you have never seen.
2. **How to test for it.** Stated as an operation someone performs, not as a quality to
   notice.
3. **Why it matters to a reader.** Who is misled, and about what, when it is present and
   nobody says so.

**A pattern without a test is an opinion.** So the requirement on a submitted pattern is
specific: it must name a way to establish the defect's presence either by executing
something, or by comparing two artifacts — two stages of the execution spine, a check
against the population it measures, a document against the behaviour it describes, a
control's documented severity against what the code does with it. Reading one function and
concluding it looks wrong does not qualify, however sound the judgement, because the
finding then rests on the reviewer's authority rather than on something the reader can
repeat.

That constraint is also why the richest entries in the catalogue compare things the code
deliberately keeps apart. If your pattern can be tested by reading a single function, it is
usually a style preference, and if it cannot be tested at all it belongs in a code review's
prose rather than in a catalogue whose sections get reported as worked.

Include, with the pattern: the operation that establishes it, and at least one worked
statement of the verdict it produces — what the finding says when the defect is present,
and what it says when the class was worked and came back clean. A class with no verdict is
indistinguishable in the finished book from a class with no defect, and the reader will
assume the flattering one.

## Adding an artifact path

This is the extension seam. `skills/review-the-tool/SKILL.md` holds a registry of artifact
types; one row — deterministic code — carries a path, and three are marked *not in this
release*. Adding a path means four things:

- **A new row in the orchestrator's registry**, naming the three skills below.
- **An evidence skill**, the phase-1 equivalent for that artifact type: it executes or
  otherwise exercises the artifact and writes the measured evidence base every later figure
  is quoted from.
- **A mapping skill**, the phase-2 equivalent: the structural record a later phase compares
  against itself.
- **A catalogue** of defect classes for that artifact type, worked by the finding hunt in
  the same way the code catalogue is.

A path must declare three things explicitly, and a submission that leaves any of them
implicit will be sent back:

1. **What counts as evidence** for that artifact type. For code it is a run: the tool
   executed on real input, with the output opened and counted. For something that cannot be
   executed in that sense, say what takes its place and why a reader should accept it.
2. **What the citation format is.** Code uses `file.ext:NNN`, and the mechanical citation
   check resolves it against a source tree. A spreadsheet path would need something like
   `Sheet!A1`. The test is whether a claim resolves to something a reader can open and
   check, because that is the one property this method exists to guarantee.
3. **What the degraded mode is** when evidence cannot be obtained. Every skill here has
   one, and each requires the degradation to be disclosed in the output rather than
   absorbed silently. A path whose degraded mode is "proceed and hope" is not a path.

**The seam is designed but untested.** No second path has been built, so its shape is an
inference from one worked example, and the first contributor to add a path should expect to
adjust it — likely in the evidence contract, which is the part most specific to
deterministic code. Propose the shape before writing four skills against it.

## Running the checks

Three, and the first two must be green before a pull request:

```
python tools/validate_skills.py
python -m pytest -q
python tools/leak_check.py --aid docs/anonymisation-review-aid.md skills docs tools agents
```

The validator checks what CI can check mechanically: frontmatter present and matching the
directory, a description within the length limit, no dangling reference paths, and an evals
file that parses and belongs to its skill. It does not grade eval content — that needs the
skill actually run against its prompts, which is a human or LLM-judge activity, so a green
validator is not evidence that a skill behaves.

One trap worth knowing before it costs you an hour: the validator's reference check matches
any `references/…`, `scripts/…` or `tests/…` path appearing **anywhere** in a skill body and
resolves it against *that* skill's own directory. So naming a sibling skill's reference file
by its full path inside a skill body fails the build even though the path is correct. That
is why the catalogue is cited bare, as `finding-patterns.md`, in the orchestrator. Prose
outside `skills/` — this file, the README — is not scanned and can spell paths in full.

**The third check needs a file you will not have.** `docs/anonymisation-review-aid.md` holds
the original values from the engagement this material was written from, so it is
git-ignored, it is asserted untracked by CI, and it is never distributed. Without it
`leak_check.py` exits 2 — "the check proved nothing" — rather than falsely reporting clean.
An outside contributor should therefore run the first two checks, and state in the pull
request where every example in the contribution came from: synthetic, a public repository,
or a tool you own. A maintainer runs the leak gate against the aid before merge. Do not
work around the exit 2 by inventing an aid file; the exit code is the point.

## The confidentiality rule

**No contribution may include client-derived content.** Not a figure, not a column name, not
a row count, not a file name, not an account code, not a sentence of a real engagement's
prose. Where an example is needed, invent one, and make it obviously invented.

Two things follow from how this repository actually went, and both are rules rather than
suggestions.

**A mechanical grep is insufficient.** `leak_check.py` exists and it works — this project's
one real leak was caught by it on its first real run, in a test fixture, in the same commit
that added the tool built to prevent leaks. But it can only match values somebody already
wrote down in the aid, and it is normalised the way it is because a line-based search over
hard-wrapped prose fails open: the value straddles a newline, the continuation line carries
a `# ` or `> ` prefix, and the pattern silently stops matching. A reviewer who treats a
green gate as clearance has confirmed only that no listed value appears in a form the tool
checks. Read the diff.

**Where "transcribe this exactly" collides with "never commit a client value", the
confidentiality rule wins.** That is not hypothetical. An implementer in this build was
handed a fixture to transcribe verbatim, recognised that it carried a real value, declined,
substituted invented figures, and disclosed the deviation in their report. The refusal was
correct, and it was correct independently of the leak checker finding the same thing. A
contributor who declines an instruction on those grounds — from a plan, from a brief, from a
maintainer, from a reviewer — is doing the right thing, and should say plainly in the pull
request what they declined and what they substituted. An undisclosed substitution is a
different problem, not a solution to this one.
