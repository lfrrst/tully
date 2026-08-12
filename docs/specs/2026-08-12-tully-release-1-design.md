# tully — Release 1 design

**Date:** 2026-08-12
**Status:** design approved; implementation plan not yet written
**Scope:** the core review engine and the deterministic-code path, plus the minimum packaging needed to publish

---

## 1. What tully is

A Claude Code plugin for reviewing accounting workflows that were designed in part or wholly by AI, and more generally any tool whose output a firm has to stand behind.

Named for Louis Tully, the Ghostbusters' accountant, whose running gag is substantiation — he itemises a party as a promotional expense and invites clients instead of friends. Keeping the receipts is the doctrine of the plugin:

> **A figure you did not produce by executing something is not evidence.** Not the changelog's figure, not the README's, not the code comment's, not the previous reviewer's. Those are claims to be tested.

Release 1 decomposes an existing monolithic skill — a 111-line `SKILL.md`, three reference documents, and one Python script, written out of a real chart-of-accounts conversion engagement — into six composable skills, two agent definitions, and one command, published openly so any firm can install it.

The plugin is not an attest tool. Its output is an internal working paper supporting a preparer and a reviewer. The README states this plainly, because the vocabulary of the domain ("assurance", "review") carries defined professional meaning that the deliverable does not claim.

## 2. Where release 1 sits

The full subject — governance over AI-designed accounting workflows — is larger than one spec. It decomposes as follows, on the structural insight that **the engagement spine is artifact-agnostic; only the evidence base and the finding catalogue change per artifact type.**

| # | Sub-project | What is new in it | Depends on |
|---|---|---|---|
| **1** | **Core engine + deterministic-code path** | Decomposing the existing skill into spine skills | — |
| 2 | Non-deterministic AI path | The artifact *is* an LLM at runtime, so no single ground-truth run exists; evidence becomes distribution, variance and reproducibility. New defect classes: non-determinism inside a control, model-version drift, no reasoning trail | 1 |
| 3 | Process / non-code workflow path | AI-designed processes with human steps; evidence is walkthrough and re-performance rather than execution | 1 |
| 4 | Spreadsheet and model path | Cell-level citation rather than line-level; formula dependency tracing, hardcode detection; needs its own citation checker | 1 |
| 5 | Judgment and authority-citation path | AI-written memos and technical positions; verifying that cited authority exists and says what is claimed | 1 |
| 6 | Governance layer | What AI touched versus what a human verified; re-review triggers on version or model change; client-data posture | thin, cross-cutting |
| 7 | Repo, packaging, docs, worked example | Manifests, README, sanitized worked engagement, CI | parallel with 1 |

**Release 1 = sub-project 1 plus a thin slice of 7.** Sub-projects 2–6 each get their own spec, plan and build cycle. Sub-projects 2–5 are independent leaves; 2 is the highest-value new work.

## 3. Decision log

| # | Decision | Rationale |
|---|---|---|
| D1 | Subject is AI-in-accounting governance, released open-source for any firm | Broader reuse than a firm-internal tool; forces everything generic and puts docs and worked examples on the critical path |
| D2 | Release 1 is the core engine plus minimum packaging | Ships something installable and proves the skill boundaries before four more paths depend on them |
| D3 | Decompose along the phase spine, with artifact-agnostic parts factored out | The engagement genuinely is a sequence, so the workflow stays visible; the reusable parts are already separated, so paths 2–5 plug in without a refactor |
| D4 | Six skills, not seven | `deliver` is five lines of real content and folds into the writing skill; citation checking folds into fact-checking until a second citation format (cell refs, authority refs) justifies extracting it |
| D5 | The interface between skills is a file tree, not conversation state | Skills must be independently invocable and able to join mid-engagement; a 40,000-word code review cannot live in context; and it makes "every figure names its run" mechanically enforceable |
| D6 | Agent instructions become defined agents, not prose handed down by a caller | "Do not praise what checks out" is a behavioural constraint; in a system prompt it holds across a long task, whereas from a caller it competes with default helpfulness |
| D7 | Reference-engagement evidence is anonymised in place, keeping defect shapes and magnitudes | Generic pattern descriptions teach nothing; the specificity is the value. Known gap recorded in §16 |
| D8 | Plugin named `tully`; skills named as imperative instructions to it | Fun confined to the package name, skill names and docs; skill *content* reads dead straight |
| D9 | Working folder is `evidence/` | The word the doctrine already uses, and safe if a firm archives the folder into a client file |
| D10 | Spec lives at `docs/specs/`, not `docs/superpowers/specs/` | Public repo; the default path would publish internal tooling naming into the docs tree |
| D11 | Publication is gated on author review of the anonymised material; the repo stays local until then | A mechanical grep only catches values someone thought to search for. Confidentiality failures are not recoverable once pushed, so the gate is a hard stop rather than a checklist item (§13) |
| D12 | Client-derived content is anonymised before its first commit and never enters git history | Git history survives a later push, so an "anonymise it afterwards" commit leaks the original blobs permanently. Supersedes the earlier intent of reviewing the anonymisation as a diff (§13) |

## 4. Repository layout

```
tully/
├── .claude-plugin/
│   ├── plugin.json                     name, version, license, "skills": "./skills"
│   └── marketplace.json                makes the repo itself installable
├── skills/
│   ├── review-the-tool/
│   │   ├── SKILL.md
│   │   └── evals/evals.json
│   ├── establish-the-truth/
│   │   ├── SKILL.md
│   │   ├── references/evidence-base.md
│   │   └── evals/evals.json
│   ├── map-the-code/
│   │   ├── SKILL.md
│   │   ├── references/function-entry.md
│   │   └── evals/evals.json
│   ├── hunt-the-findings/
│   │   ├── SKILL.md
│   │   ├── references/finding-patterns.md
│   │   └── evals/evals.json
│   ├── write-the-books/
│   │   ├── SKILL.md
│   │   ├── references/checklist-book.md
│   │   ├── references/code-review-book.md
│   │   └── evals/evals.json
│   └── check-the-facts/
│       ├── SKILL.md
│       ├── scripts/citation_check.py
│       ├── tests/test_citation_check.py
│       └── evals/evals.json
├── agents/
│   ├── code-mapper.md
│   └── fact-checker.md
├── commands/
│   └── review.md
├── examples/worked-engagement/
├── docs/specs/
├── README.md
├── LICENSE                             MIT
├── CONTRIBUTING.md
└── .github/workflows/validate.yml
```

The command is `review.md` rather than `review-the-tool.md` so that `/tully:review` and the skill `tully:review-the-tool` cannot be mistaken for each other in a transcript.

## 5. The six skills

Each `SKILL.md` declares four things beyond its instructions: what it needs, what it does when that is missing, what it writes, and what it hands back. The degraded-mode declaration is what makes independent invocation safe.

### 5.1 `review-the-tool` — orchestrator

Holds the doctrine, the attestation-versus-detection idea, mode selection, artifact classification and the path registry, and the phase sequence. Writes the `evidence/` skeleton, then dispatches. It does *not* write the project record — that belongs to `write-the-books` as the tail of phase 6, so that a `document`-mode run reached without the orchestrator still produces one.

Two mechanics that must be explicit in the skill rather than left to inference:

**Mode selection.** Infer the mode from the request — a request to document, explain or write a reference for a tool is `document`; a request to check, verify or fact-check an existing document is `verify`; anything about relying on, signing off or handing on output is `review`. State the inferred mode and what it will and will not produce *before* starting phase 1, and ask only where the request genuinely reads both ways. Inferring `document` when the caller wanted assurance is the costly direction, so resolve ambiguity toward `review`.

**Artifact classification.** Inspect the artifact — file extensions, entry points, whether execution is deterministic — and match it against the §8 registry. Do not ask the user to classify it; do ask when inspection is genuinely ambiguous, and stop rather than guess when nothing matches.

**Draft description trigger set** (the wide net; inherited from the monolith): review, validate, document, sign off on, get comfortable with, or hand to a reviewer any script, model, macro, conversion utility, calculator, allocation engine, ETL job, migration tool or reporting pipeline that produces client deliverables or feeds financial statements. Phrases: "review this tool", "can we rely on this", "document what this code does", "build a review checklist", "what should a human check", "the auditors will ask", "workpaper for this script", "validate this conversion". Also fires proactively when someone is about to ship output from a tool nobody has independently reviewed.

### 5.2 `establish-the-truth` — phase 1

Stage the code and the real inputs in a scratch workspace so nothing touches the original. Run the tool's own test suite and record the exact pass count. Execute the tool at least twice under settings that exercise genuinely different paths, and record the run identifiers. Measure the output by opening the files and counting, not by reading the tool's own summary. Record anything the run says that cannot be reconciled.

Writes `evidence/01-evidence-base.md`, whose required fields are given in `references/evidence-base.md` and include `EXECUTED: yes|no`.

**Needs:** the tool and its real inputs. **Degraded:** if the tool cannot be executed at all, still write the manifest with `EXECUTED: no` and the reason; downstream skills must read that flag and mark every figure unverified. **Hands back:** the path to `01-evidence-base.md`.

Also owns the *prevention* half of the "figure quoted from a different run" failure: the run identifier is a required field of every recorded figure.

### 5.3 `map-the-code` — phase 2

Split the modules into three to five groups along the layers the code actually has and dispatch one `code-mapper` agent per group in parallel. Ask one agent for the execution spine: the ordered sequence of the main entry point, every stage, the line it is called at, what it adds, and the state of the data at that point.

Carries the depth expectation (a heading per function, four labelled paragraphs under each, roughly one line citation per 50 words) and the sequential fallback for when no subagent tool is available — work the layers one at a time, write each to its own file before starting the next, then re-read the execution spine against the finished sections hunting specifically for ordering defects, and state in the finished document that the review was performed sequentially.

Writes `evidence/02-execution-spine.md` and `evidence/02-map-<layer>.md`.

**Needs:** `01-evidence-base.md` for the population sizes in the spine table. **Degraded:** produces the map regardless; the spine's population column reads `not measured` and the skill says so at the top of its output rather than omitting the column. **Hands back:** the list of written paths.

### 5.4 `hunt-the-findings` — phase 3

Work `references/finding-patterns.md` deliberately rather than hoping the module map surfaces the defects, because most of them are invisible from any single function and only appear when two things the code keeps apart are compared.

Writes `evidence/03-findings.md`: per candidate, the shape, how it was tested, the verdict, the evidence, and whether it is reproducible.

**Needs:** `01`, `02`. **Degraded:** without the execution spine, the ordering-defect classes cannot be worked; say which pattern classes were not attempted rather than reporting a clean sweep. **Hands back:** the path to `03-findings.md`.

Owns the "absent evidence file is not evidence of nothing to report" warning, since that is a finding-hunt judgment.

### 5.5 `write-the-books` — phases 4 and 6

Produce the two Markdown books to the structures in `references/checklist-book.md` and `references/code-review-book.md`, name them carrying the tool and version, deliver them, and save the short project record.

**Needs:** `01`–`03`. **Degraded:** in `document` mode there is no `03`; the findings section is *omitted and explicitly marked not-performed*, never left blank. **Hands back:** the book paths.

Owns three of the five "things that reliably go wrong": writing the checklist from the findings only, letting the tool's vocabulary become the book's vocabulary, and leaving materiality implicit.

### 5.6 `check-the-facts` — phase 5

Find statements that are wrong. Run `scripts/citation_check.py` first and hand its output to a `fact-checker` agent per book, so the agent spends its attention on whether a cited line *supports* the claim rather than on whether it exists. Check at minimum a large well-spread sample of citations including every citation supporting a finding, every table a reader would act on, every quantitative claim, and each finding reproduced from scratch.

Carries the no-subagent fallback, which is a change in the *mode* of work rather than a re-read: re-derive every quantitative claim mechanically from the run folders with a script, and re-resolve every finding-bearing citation, without looking at what was written until the script has produced its own answer, then compare.

Writes `evidence/04-verification-<book>.md`.

**Needs:** a document, the source tree, the run folders. **Degraded:** with no run folders, quantitative claims cannot be re-derived; verify citations and internal consistency and state the limitation at the top of the error list. **Hands back:** the error-list path.

Owns the *detection* half of the "figure from a different run" failure.

## 6. Modes

| Mode | Runs | Produces | Rule that governs it |
|---|---|---|---|
| `document` | establish → map → write | Code review book only | Still executes where it can, because a documentation claim about an edge case is worth more when it says "verified:". Tolerates `EXECUTED: no` far more gracefully than `review`. Must state on page one that it is documentation and not assurance |
| `review` (default) | all six phases | Both books | The full engagement |
| `verify` | `check-the-facts` alone | An error list | Works against any document carrying `file.ext:NNN` citations, including one a previous reviewer or another AI wrote, and including the previous version of your own book |

The books are produced together by default because they need each other: the checklist's compensating procedures exist only because the code review found the gaps they compensate for. If the user asks for only one, produce that one — but still do the research phase in full, because a checklist written without reading the code is a generic checklist.

**Erratum, found at Task 8.** This table originally described `document` mode as "establish → map", which cannot be right: the mode produces a code review book, and the phase that writes books is `write-the-books`. The mode runs three skills, with `write-the-books` limited to the code review and its findings section marked not-performed. The shorthand named the research phases and silently dropped the one that produces the deliverable — the kind of gap that survives because the "Produces" column looks correct beside it.

## 7. The engagement folder

```
evidence/
├── 01-evidence-base.md        run IDs, settings, measured figures, test-suite pass count,
│                              unreconciled observations, EXECUTED: yes|no
├── 02-execution-spine.md      stage, call-site line, what it adds, population at that point
├── 02-map-<layer>.md          one per layer, written by code-mapper agents in parallel
├── 03-findings.md             per candidate: shape, how tested, verdict, reproducible?
├── 04-verification-<book>.md  the error list
└── runs/<run-id>/             actual tool outputs, never edited
```

Three reasons this is a file tree and not conversation state: skills must be independently invocable and able to join an engagement mid-flight; a 40,000-word code review cannot be held in context; and it makes the most-caught verification error mechanically preventable — a figure that is not in `01-evidence-base.md` against a run identifier has no business appearing in a book.

## 8. Path registry and extensibility

`review-the-tool` classifies the artifact before dispatching, and dispatches from a table in its own `SKILL.md`:

| Artifact type | Evidence | Mapping | Catalogue |
|---|---|---|---|
| Deterministic code | `establish-the-truth` | `map-the-code` | `finding-patterns.md` |
| Spreadsheet / model | not in this release | | |
| LLM at runtime | not in this release | | |
| Process with human steps | not in this release | | |

Adding a path in a later release is a new row plus new skills; nothing already shipped is refactored.

**The rule that makes the registry honest: if the artifact does not match a registered path, say so and stop.** A spreadsheet model forced through a code-shaped review produces a confident, badly wrong document, which is precisely the failure mode the plugin exists to catch. Release 1 declining three of four artifact types out loud is correct behaviour, not a shortfall.

## 9. Agents

**`code-mapper`** — tools: Read, Grep, Glob, Bash, Write. System prompt carries the per-function template (signature; what it does; how it does it, with `file.ext:NNN` citations; what it relies on; failure modes), the three instructions that separate this from a code summary (reproduce behaviour where reproducible; where the code and its own comments disagree say so and say which is right; write to a file and return a path, because sections run past 10,000 words), and the depth target.

**`fact-checker`** — tools: Read, Grep, Glob, Bash. System prompt carries the single instruction to find statements that are wrong, the explicit instruction not to praise what checks out because praise costs tokens and hides the errors, and the minimum check list.

Both exist as agents rather than as prose because their governing instructions are behavioural constraints that must survive a long task.

## 10. Command

`commands/review.md`, invoked as `/tully:review` — accepts an optional path and an optional mode, and invokes the orchestrator. Its only job is to be a short way in.

## 11. Migration map

Every part of the monolith has a destination. Nothing is dropped.

| Source | Destination |
|---|---|
| Two-books intro; "the idea that makes this worth doing"; the doctrine | `review-the-tool` (the doctrine sentence is *quoted*, not restated, in skills that depend on it) |
| Phase 1 | `establish-the-truth` |
| Phase 2 — grouping, execution spine, depth expectation, sequential fallback | `map-the-code` |
| Phase 2 — the per-agent template and its three instructions | `agents/code-mapper.md` |
| Phase 3 | `hunt-the-findings` |
| `references/finding-patterns.md` | `hunt-the-findings/references/` (anonymised) |
| Phase 4 | `write-the-books` |
| `references/checklist-book.md`, `references/code-review-book.md` | `write-the-books/references/` |
| Phase 5 | `check-the-facts` |
| Phase 5 — the fact-checker's instructions | `agents/fact-checker.md` |
| `scripts/citation_check.py` | `check-the-facts/scripts/` |
| Phase 6 | `write-the-books` (tail section) |
| "Things that reliably go wrong" | **split by owner** — see below |

"Things that reliably go wrong" is deliberately not moved as a block. Today it is five warnings in a list at the end, easy to skim past. Distributed, each lands in the skill that can act on it:

| Warning | Owner |
|---|---|
| Writing the checklist from the code review's findings only | `write-the-books` |
| Letting the tool's vocabulary become the book's vocabulary | `write-the-books` |
| Materiality left implicit | `write-the-books` |
| Treating an absent evidence file as evidence of nothing to report | `hunt-the-findings` |
| Quoting a figure that was true of a different run | split: prevention in `establish-the-truth`, detection in `check-the-facts` |

## 12. New content, not migrated

Most of the work in release 1 is writing these, not moving files.

1. **Six skill descriptions.** The monolith has one enormous trigger paragraph. Only `review-the-tool` keeps the wide net; the other five need narrow descriptions that fire when a caller genuinely wants that phase alone and stay quiet otherwise. Getting these wrong is the main way a decomposition fails, which is why every skill gets a trigger eval.
2. **`establish-the-truth/references/evidence-base.md`** — the manifest template. Implicit in the monolith's prose; now a contract, so required fields are enumerated, including `EXECUTED: yes|no` and a run identifier on every recorded figure.
3. **`map-the-code/references/function-entry.md`** — the per-function template extracted so the skill and the agent cite one source rather than drifting apart.
4. **`agents/code-mapper.md`**, **`agents/fact-checker.md`**.
5. **`commands/review.md`**.
6. **Six `evals/evals.json`.**
7. **`check-the-facts/tests/test_citation_check.py`** — the script has no tests today and it exits 1 to gate a build.
8. **README, LICENSE, CONTRIBUTING**, and `examples/worked-engagement/`.
9. **The degraded-mode paragraph in each of the five phase skills** — new material with no counterpart in the monolith, and load-bearing for independent invocation.

## 13. Anonymisation policy

The reference material draws its force from concrete detail; generic pattern descriptions teach nothing. The rule that resolves this:

> **The review's own statistics stay verbatim; client-derived data changes.**

Facts about the *review* — the count of the tool's own assertions that passed, the number of errors the verification pass caught across two carefully written documents, the number a self-verification still caught without a subagent — are the credibility of the method and are not client-identifying. They stay.

Client-derived data changes: client and system names become a consistent fictional pair; monetary amounts are rounded and altered; account and type codes are substituted. Defect *mechanics* are preserved exactly — a record correctly flagged unresolvable, whose emit step applies the open context to it anyway, so the field that failed to resolve holds the preceding sibling's value — because the mechanics are what a reader needs in order to recognise the pattern in their own tool. Magnitudes are preserved to order of magnitude, because a defect worth two million dollars and one worth two hundred are different findings.

The phrase that introduces the source engagement becomes "in the engagement this catalogue was written from" — provenance signalled, identity removed. The original phrase is not quoted here, so that the aid-derived leak check returns genuinely clean rather than carrying a permanent known false positive. A check a reader learns to wave through has stopped being a check, which is a pattern this plugin catalogues.

### Affected files

A scan of the source material found client-derived content in three files, not the one this section originally assumed. The catalogue is wider than the obvious case study, and the widening is the point: two of the three are incidental mentions inside otherwise generic material, which is exactly the kind of leak a grep for known values does not find.

| File | Line | What is client-derived |
|---|---|---|
| `references/finding-patterns.md` | 81 | The worked case study: row count, gross amount, both account codes, and the two source row numbers |
| `references/code-review-book.md` | 132 | A function name naming the client's source accounting system, used as an incidental example of documentation depth |
| `scripts/citation_check.py` | 30, 48 | A docstring example naming the target system and a segment value, and a second example carrying a real module path from the client's tool |

`SKILL.md` and `references/checklist-book.md` are clean and may be split verbatim. Substitutions must be *consistent across all three files* — a fictional source system and target system chosen once and used everywhere — because inconsistent replacements read as carelessness and invite a reader to work out which one was real.

Verification of this pass is a required implementation step, not a best effort: a grep for client names, the substituted codes, and the original amounts across the whole repo must return nothing before publication.

**That grep runs locally and never lives in CI, and no committed file may contain the values it searches for** — including this spec and the implementation plan. A workflow or a document that greps for a client value contains that value, and both are published, so such a check would leak precisely what the anonymisation removed. The pattern list is therefore built at run time from the git-ignored review aid below, and CI asserts only the invariant that protects it: that the aid is untracked.

The check must also guard against an empty pattern list. A leak check with no patterns passes trivially and prints the same output as one that genuinely found nothing — which is the "checks that cannot fail" class from this plugin's own catalogue, and an unusually poor place to commit it.

### Publication gate

**The repository stays local until the anonymised reference material has been read and approved by the author.** Adding a remote and the first push are both behind this gate; no implementation step may perform either.

Two requirements follow from that, and they belong in the plan:

1. **Client-derived content is never committed, not even once.** Each affected file is anonymised in the scratch copy and only the anonymised version is ever added to git. An earlier draft of this section called for anonymisation as its own commit so the gate could review a clean diff; that is wrong, because git history survives and a later push would carry the un-anonymised blobs regardless of the state of the tip. There is no acceptable commit containing client data, so the author's review is served by the substitution aid below rather than by a diff.
2. Alongside it, a review aid listing every substitution — original value, replacement, and the file and line of each occurrence — written to `docs/` and **git-ignored**, since it would otherwise reconstruct exactly what the anonymisation removed. The aid is for the author's review and is deleted once the gate clears.

The mechanical grep is necessary and not sufficient: it catches values someone remembered to search for, and the gate exists to catch the ones nobody thought of — a defect described in enough detail to identify the client without naming it, a magnitude paired with an industry, a file path in an example.

## 14. Verification plan

The genuine risk: a monolith that works decomposes into six skills that do not — a description that never fires, an agent template separated from the depth target it enforces, a caveat that falls between two skills.

**Per-skill `evals/evals.json`**, in prompt / expected-output / assertions form. Each skill gets three cases:

1. **Canonical** — the plain invocation, asserting the skill's core obligations.
2. **Trigger** — casual phrasing that must reach *this* skill and not a sibling. "Can we rely on this script" must reach `review-the-tool`; "what does this function actually do" must reach `map-the-code`; "check whether this document is accurate" must reach `check-the-facts`.
3. **Degraded** — invoked standalone with its input missing, asserting that it names the degradation rather than fabricating figures or silently omitting a column.

**One end-to-end eval** on `review-the-tool` asserting the phase sequence, and asserting that a `document`-mode run produces no assurance language and carries the documentation-not-assurance statement.

**`test_citation_check.py`** covering: a resolving citation, a dead file, an out-of-range line, an ambiguous basename, the blank-target off-by-one, the `--only-findings` filter, and the exit code contract.

**CI** (`.github/workflows/validate.yml`): frontmatter validation across all six skills, the pytest run, and a link check on cross-skill and cross-reference paths so that renaming a reference file breaks the build rather than the engagement.

## 15. Packaging

- `plugin.json` and `marketplace.json` so `/plugin marketplace add <owner>/tully` installs it.
- MIT licence.
- README: what the plugin does, the Louis Tully explanation, install instructions, the six skills and three modes, a worked example, and a plain statement that output is an internal working paper and not an attest report.
- CONTRIBUTING: how to add a finding pattern, and how to add an artifact path — the second being the extension point sub-projects 2–5 will use.
- `examples/worked-engagement/`: anonymised excerpts of both books plus a filled evidence base, so a reader can see the shape of the deliverable before running anything.

## 16. Known gaps

**No example in the repo is reproducible by a user.** Anonymised case studies are assertions about an engagement the reader cannot inspect. The named candidate to close this is a small deliberately-defective demo tool — roughly 400 lines, with seeded instances of the main defect classes — published in the repo as a new reference engagement. It would make every example reproducible and would double as the fixture that proves the skills still find what the monolith found. Deferred out of release 1 to avoid the build swallowing the release; recorded here so the decision is visible rather than forgotten.

**Trigger quality is unproven until the plugin is installed and used.** Evals assert intent, not real-world routing among the user's other installed skills. Expect to tune the six descriptions after first use.

**The path registry has one entry.** Its extension seam is designed but untested until sub-project 2 or 4 exercises it, so the first added path should expect to adjust the registry's shape.

## 17. Out of scope for release 1

Sub-projects 2–6: the non-deterministic AI path, the process path, the spreadsheet path, the authority-citation path, and the governance layer. The synthetic demo tool. Any firm-specific templates, file-naming conventions or branding.
