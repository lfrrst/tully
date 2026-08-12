# tully Release 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decompose a monolithic tool-review skill into the `tully` Claude Code plugin — six skills, two agents, one command, per-skill evals, a tested citation checker, and CI — publishable openly and holding no client-derived content.

**Architecture:** Six skills arranged along the engagement's phase spine, communicating through a file tree (`evidence/`) rather than conversation state, so any phase can be invoked alone or joined mid-engagement. Two behavioural constraints that must survive long tasks become agent system prompts rather than caller instructions. An orchestrator classifies the artifact and dispatches from a path registry with exactly one entry, declining anything else out loud.

**Tech Stack:** Markdown skills with YAML frontmatter; Python 3.10+ standard library only for scripts; pytest for tests; GitHub Actions for CI.

**Plan location note:** this plan lives at `docs/plans/`, not `docs/superpowers/plans/`, for the same reason as spec decision D10 — the repo is public and the default path would publish internal tooling naming into the docs tree.

## Global Constraints

Every task's requirements implicitly include this section.

- **Python floor: 3.10.** `citation_check.py` uses `Path | None` under `from __future__ import annotations`. Standard library only at runtime; `pytest` is a dev dependency.

- **Environment prerequisite: a real Python interpreter must be on `PATH` before Task 1.** This was an unstated assumption in the plan's first draft and it blocked Task 1 on the machine this was written on.

  On Windows, `python` and `python3` frequently resolve to zero-byte Microsoft Store *app execution aliases* rather than an interpreter. The trap that matters: **the stub prints "Python was not found" and exits 0.** A step that runs `python -m pytest` against the stub therefore looks like a pass — a check that cannot fail, in the build for the plugin that catalogues them. Verify the interpreter before relying on any test result:

  ```bash
  python --version   # must print a version; "Python was not found" means the stub
  which python       # must NOT be under .../Microsoft/WindowsApps/
  ```

  Where a real interpreter is installed but shadowed by the stubs, prepend it per shell invocation rather than editing persistent `PATH`:

  ```bash
  export PATH="<python-dir>:<python-dir>/Scripts:$PATH"
  ```

  Every local command in this plan that begins `python` assumes that has been done. **CI is unaffected** — it runs on `ubuntu-latest` where `actions/setup-python` puts a real interpreter on `PATH`, so the workflow keeps bare `python` and must not be changed to a local path.
- **No remote may be added and nothing may be pushed.** Spec D11. The repo stays local until the author clears the publication gate. No task performs `git remote add`, `git push`, or repository creation.
- **Client-derived content is never committed, not even once.** Spec D12. Anonymise in the working copy before the first `git add` of any affected file.
- **This plan never states an original client value.** It states only replacements. That is deliberate and it is a constraint on the plan itself, not only on the repo: this file is committed and will be published, so a substitution table listing the originals here would publish exactly what the anonymisation removes. The originals live in two places, neither of which is ever committed — `$SRC`, which the implementer reads directly, and `docs/anonymisation-review-aid.md`, which is git-ignored.

- **Replacement values** (spec §13; use these verbatim everywhere so substitutions are consistent across files):

  | Location | Replace with |
  |---|---|
  | `code-review-book.md` line 132, the example function name | `read_ledgerline_hierarchical` |
  | `citation_check.py` line 48, the example module path | `converter/fund.py:322` |
  | `citation_check.py` line 30, the example non-citation string | `"C01:Aurora.Segment"` |
  | `finding-patterns.md` line 81, the row count and gross amount | `roughly 40 rows carrying about $2M gross` |
  | `finding-patterns.md` line 81, the unclassifiable account code | `41205` |
  | `finding-patterns.md` line 81, the inherited account code | `41204` |
  | `finding-patterns.md` line 81, the failing source row number | `118` |
  | `finding-patterns.md` line 81, the preceding source row number | `117` |
  | every occurrence of the phrase introducing the source engagement | `In the engagement this catalogue was written from` |

  Fictional systems, chosen once: source system **Ledgerline Fund Accounting**, target system **Aurora ERP**. No client is named at all.

- **The pre-publication grep is local-only and never lives in CI.** A CI workflow that greps for the original values would contain them, and CI is published. The check therefore runs from the git-ignored aid, on the author's machine, before the gate clears. CI carries a weaker check that names no secret (Task 1 Step 6).
- **Statistics about the review itself stay verbatim** (spec §13): the count of a tool's own passing assertions, the 26 errors the verification pass caught across two documents, the five errors a self-verification caught without a subagent. These are the credibility of the method and identify nobody.
- **Skill frontmatter:** `name` must equal the containing directory name; `description` non-empty and ≤ 1024 characters.
- **Skill names, exactly:** `review-the-tool`, `establish-the-truth`, `map-the-code`, `hunt-the-findings`, `write-the-books`, `check-the-facts`.
- **The doctrine sentence is quoted verbatim wherever it appears:** "A figure you did not produce by executing something is not evidence."
- **Deliverable language:** every user-facing document states that output is an internal working paper, not an attest report.
- **Licence:** MIT.
- **Source material** (read-only; copy from, never edit in place):
  `C:\Users\LUCASF~1\AppData\Local\Temp\claude\C--Users-LucasForrest-Foxglove-Financial-Services-Client-Files---Documents-SumBridge--LLC-HealthPoint-Conversion-Tool\6135acee-cb83-4a06-8f87-0f578507f094\scratchpad\skill-unpack\tool-assurance-review\`
  Referred to below as `$SRC`. If it is gone, re-extract from `C:\Users\LucasForrest\Downloads\tool-assurance-review.skill` (a zip archive).
- **Commit trailer** on every commit:
  `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`

## A note on what "test" means here

Two of the ten tasks build Python and get ordinary TDD. The other eight produce Markdown, where the honest test cycle is:

1. Write `evals/evals.json` **first** — it is the specification of what the skill must do, written before the skill.
2. Run `tools/validate_skills.py`, which fails because the skill does not exist yet.
3. Write the skill.
4. Run the validator; it passes.
5. Read the skill against its own eval assertions and confirm each is satisfiable from the text. **CI cannot grade eval content** — it validates only that the JSON parses and matches its directory. Grading requires running the skill against the prompts, which is a human or LLM-judge activity outside CI. Do not claim otherwise anywhere in the repo.

---

### Task 1: Repo scaffold, manifests, and the skill validator

**Files:**
- Create: `tools/validate_skills.py`
- Create: `tools/tests/test_validate_skills.py`
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Create: `.github/workflows/validate.yml`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: nothing.
- Produces: `tools/validate_skills.py`, runnable as `python tools/validate_skills.py [--skills-dir DIR]`, exit 0 when every skill validates and 1 otherwise. Every later task runs it as its gate.

- [ ] **Step 1: Write the failing tests**

Create `tools/tests/test_validate_skills.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

VALIDATOR = Path(__file__).resolve().parents[2] / "tools" / "validate_skills.py"


def make_skill(root: Path, name: str, *, frontmatter_name=None, description="A valid description.",
               body="", references=(), evals_name=None, evals_body=None):
    """Build a skill directory on disk and return its path."""
    d = root / name
    (d / "evals").mkdir(parents=True)
    fm_name = name if frontmatter_name is None else frontmatter_name
    fm = "---\n"
    if fm_name is not None:
        fm += f"name: {fm_name}\n"
    if description is not None:
        fm += f"description: {description}\n"
    fm += "---\n"
    (d / "SKILL.md").write_text(fm + "\n# Heading\n\n" + body, encoding="utf-8")
    for ref in references:
        p = d / ref
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("reference body\n", encoding="utf-8")
    if evals_body is None:
        evals_body = {"skill_name": evals_name or name,
                      "evals": [{"id": 1, "prompt": "p", "expected_output": "e",
                                 "assertions": ["a"], "files": []}]}
    (d / "evals" / "evals.json").write_text(
        evals_body if isinstance(evals_body, str) else json.dumps(evals_body), encoding="utf-8")
    return d


def run(skills_dir: Path):
    return subprocess.run([sys.executable, str(VALIDATOR), "--skills-dir", str(skills_dir)],
                          capture_output=True, text=True)


def test_valid_skill_passes(tmp_path):
    make_skill(tmp_path, "good-skill")
    r = run(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_missing_skill_md_fails(tmp_path):
    d = make_skill(tmp_path, "no-body")
    (d / "SKILL.md").unlink()
    r = run(tmp_path)
    assert r.returncode == 1
    assert "SKILL.md" in r.stdout


def test_name_mismatch_fails(tmp_path):
    make_skill(tmp_path, "real-name", frontmatter_name="other-name")
    r = run(tmp_path)
    assert r.returncode == 1
    assert "name" in r.stdout


def test_missing_description_fails(tmp_path):
    make_skill(tmp_path, "no-desc", description=None)
    r = run(tmp_path)
    assert r.returncode == 1
    assert "description" in r.stdout


def test_overlong_description_fails(tmp_path):
    make_skill(tmp_path, "long-desc", description="x" * 1025)
    r = run(tmp_path)
    assert r.returncode == 1
    assert "1024" in r.stdout


def test_dangling_reference_fails(tmp_path):
    make_skill(tmp_path, "dangling", body="See `references/missing.md` for detail.")
    r = run(tmp_path)
    assert r.returncode == 1
    assert "references/missing.md" in r.stdout


def test_resolving_reference_passes(tmp_path):
    make_skill(tmp_path, "resolving", body="See `references/present.md` for detail.",
               references=("references/present.md",))
    r = run(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_malformed_evals_json_fails(tmp_path):
    make_skill(tmp_path, "bad-json", evals_body="{not json")
    r = run(tmp_path)
    assert r.returncode == 1
    assert "evals.json" in r.stdout


def test_evals_skill_name_mismatch_fails(tmp_path):
    make_skill(tmp_path, "mismatch", evals_name="something-else")
    r = run(tmp_path)
    assert r.returncode == 1
    assert "skill_name" in r.stdout


def test_empty_evals_list_fails(tmp_path):
    make_skill(tmp_path, "empty-evals",
               evals_body={"skill_name": "empty-evals", "evals": []})
    r = run(tmp_path)
    assert r.returncode == 1
    assert "evals" in r.stdout


def test_reports_every_failure_not_just_the_first(tmp_path):
    make_skill(tmp_path, "first-bad", description=None)
    make_skill(tmp_path, "second-bad", frontmatter_name="wrong")
    r = run(tmp_path)
    assert r.returncode == 1
    assert "first-bad" in r.stdout and "second-bad" in r.stdout
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tools/tests/test_validate_skills.py -v`
Expected: every test FAILS — the validator file does not exist, so `subprocess.run` returns a non-zero code with `can't open file` on stderr, and even the negative tests fail their `in r.stdout` assertions.

- [ ] **Step 3: Write the validator**

Create `tools/validate_skills.py`:

```python
#!/usr/bin/env python3
"""Validate the structure of every skill under skills/.

Checks what CI can check mechanically: frontmatter present and consistent with
the directory, a description within bounds, no dangling reference paths, and an
evals file that parses and belongs to this skill.

It does NOT grade eval content. That requires running the skill against its
prompts and is a human or LLM-judge activity.

    python tools/validate_skills.py
    python tools/validate_skills.py --skills-dir some/other/dir

Exit code is 1 if any skill fails, so it can gate a build.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MAX_DESCRIPTION = 1024

# `references/x.md`, `scripts/y.py`, `tests/z.py` mentioned anywhere in the body.
REF = re.compile(r"(?:references|scripts|tests)/[\w./-]+\.\w+")


def parse_frontmatter(text: str) -> dict | None:
    """Return the frontmatter as a flat dict, or None if absent or unterminated."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    data: dict[str, str] = {}
    key = None
    for line in block.split("\n"):
        if not line.strip():
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s?(.*)$", line)
        if m:
            key = m.group(1)
            data[key] = m.group(2).strip()
        elif key and (line.startswith(" ") or line.startswith("\t")):
            data[key] = (data[key] + " " + line.strip()).strip()
    return data


def check_skill(d: Path) -> list[str]:
    problems: list[str] = []
    skill_md = d / "SKILL.md"
    if not skill_md.is_file():
        return [f"{d.name}: SKILL.md is missing"]

    text = skill_md.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    if fm is None:
        problems.append(f"{d.name}: SKILL.md has no terminated YAML frontmatter")
        return problems

    if fm.get("name") != d.name:
        problems.append(
            f"{d.name}: frontmatter name is {fm.get('name')!r}, expected {d.name!r}")

    desc = fm.get("description", "")
    if not desc:
        problems.append(f"{d.name}: frontmatter description is missing or empty")
    elif len(desc) > MAX_DESCRIPTION:
        problems.append(
            f"{d.name}: description is {len(desc)} chars, limit is {MAX_DESCRIPTION}")

    body = text[text.find("\n---", 3) + 4:]
    for rel in sorted(set(REF.findall(body))):
        if not (d / rel).is_file():
            problems.append(f"{d.name}: body cites {rel} which does not exist")

    evals = d / "evals" / "evals.json"
    if not evals.is_file():
        problems.append(f"{d.name}: evals/evals.json is missing")
    else:
        try:
            data = json.loads(evals.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append(f"{d.name}: evals.json does not parse ({e.msg})")
        else:
            if data.get("skill_name") != d.name:
                problems.append(
                    f"{d.name}: evals.json skill_name is "
                    f"{data.get('skill_name')!r}, expected {d.name!r}")
            if not data.get("evals"):
                problems.append(f"{d.name}: evals.json has an empty evals list")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skills-dir", default="skills")
    args = ap.parse_args()

    root = Path(args.skills_dir)
    if not root.is_dir():
        print(f"no such skills directory: {root}", file=sys.stderr)
        return 2

    dirs = sorted(p for p in root.iterdir() if p.is_dir())
    all_problems: list[str] = []
    for d in dirs:
        problems = check_skill(d)
        all_problems.extend(problems)
        print(f"  {'FAIL' if problems else 'ok  '}  {d.name}")

    print(f"\n{len(dirs)} skills checked, {len(all_problems)} problems")
    for p in all_problems:
        print(f"  {p}")
    return 1 if all_problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tools/tests/test_validate_skills.py -v`
Expected: 11 passed. If `test_reports_every_failure_not_just_the_first` fails, the validator is returning early — it must accumulate across skills.

- [ ] **Step 5: Write the manifests**

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "tully",
  "description": "Review the tools your numbers come out of. Produces a human review checklist and a function-level code review for any script, model, or pipeline whose output a firm has to stand behind, with every figure verified by execution rather than documentation.",
  "version": "0.1.0",
  "license": "MIT",
  "skills": "./skills",
  "agents": "./agents",
  "commands": "./commands"
}
```

Create `.claude-plugin/marketplace.json`:

```json
{
  "name": "tully",
  "metadata": {
    "description": "Assurance over tools that produce financial deliverables, including ones an AI designed.",
    "version": "0.1.0"
  },
  "plugins": [
    {
      "name": "tully",
      "description": "Six skills for reviewing a tool whose output a firm has to stand behind: execute it and measure what it really produces, document every function, hunt the defect classes these tools actually have, write the checklist and the code review, and adversarially fact-check both before anything is handed on.",
      "source": "./"
    }
  ]
}
```

Leave `author`, `homepage` and `repository` out of `plugin.json` for now — they are populated when the publication gate clears and a remote exists. Adding them earlier would record a URL that does not resolve.

- [ ] **Step 6: Write CI**

Create `.github/workflows/validate.yml`:

```yaml
name: validate

on:
  push:
  pull_request:
  workflow_dispatch:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dev dependencies
        run: python -m pip install --upgrade pip pytest
      - name: Validate skill structure
        run: python tools/validate_skills.py
      - name: Run tests
        run: python -m pytest -q
      - name: Assert the anonymisation review aid was not committed
        run: |
          if git ls-files --error-unmatch docs/anonymisation-review-aid.md 2>/dev/null; then
            echo "::error::the anonymisation review aid is tracked; it must stay ignored"
            exit 1
          fi
          echo "review aid is not tracked"
```

**There is deliberately no CI step grepping for the original client values.** Such a step would have to contain them, and the workflow file is published — a grep for a secret publishes the secret. The mechanical check runs locally instead, from the git-ignored aid, before the publication gate clears.

What CI can safely assert is the invariant that protects the values: that the aid holding them is not tracked. Spec §13 is in any case explicit that the mechanical check only catches values someone thought to search for; the author's gate is the control.

- [ ] **Step 7: Extend .gitignore**

Confirm the current contents first with `cat .gitignore` and do not duplicate lines. `evidence/`, `__pycache__/`, `*.pyc`, `.pytest_cache/` and `docs/anonymisation-review-aid.md` are already present from the spec commits. Append only:

```
.venv/
*.egg-info/
```

- [ ] **Step 8: Start the anonymisation review aid**

Task 2 performs the first substitution, so the aid must exist before it. Confirm it is ignored *before* writing anything into it:

```bash
git check-ignore -v docs/anonymisation-review-aid.md
```

Expected: a line naming the matching `.gitignore` rule. **If this reports nothing, stop and fix `.gitignore` — the aid holds every original client value and must never be tracked.**

Then create `docs/anonymisation-review-aid.md` with a header explaining what it is, why it is ignored, and that it is deleted once the publication gate clears, followed by an empty **Substitutions made** table with columns: original value, replacement, file, line. Tasks 2, 5 and 6 each append their rows as they make the substitution.

Read the originals from `$SRC` at the lines given in the Global Constraints replacement table. Do not transcribe them into any file other than this one.

- [ ] **Step 9: Verify the validator runs clean against an empty skills tree**

Run: `mkdir -p skills && python tools/validate_skills.py`
Expected: `0 skills checked, 0 problems`, exit 0. This is the state Task 3 starts from.

- [ ] **Step 10: Commit**

```bash
git status --short docs/
# expected: docs/anonymisation-review-aid.md does NOT appear
git add tools .claude-plugin .github .gitignore
git commit -m "$(cat <<'EOF'
Add repo scaffold, plugin manifests, and the skill validator

The validator gates every later task: frontmatter consistency with the
directory, description bounds, no dangling reference paths, and an evals file
that parses and belongs to its skill. It deliberately does not grade eval
content, which needs the skill actually run.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: The citation checker and its tests

**Files:**
- Create: `skills/check-the-facts/scripts/citation_check.py` (copied from `$SRC/scripts/citation_check.py`, then anonymised)
- Create: `skills/check-the-facts/tests/test_citation_check.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `citation_check.py`, invoked as
  `python citation_check.py DOCUMENT --root SRCTREE [--sample N] [--only-findings] [--json OUT]`.
  Exit 0 when every citation resolves, 1 when any does not, 2 on a missing document or root. Task 7's skill body cites this path and quotes this contract.

The script is written before its skill because the skill's instructions quote the script's exact invocation and exit-code contract, and those must be established facts rather than intentions.

- [ ] **Step 1: Copy the script and anonymise it before any `git add`**

```bash
mkdir -p skills/check-the-facts/scripts skills/check-the-facts/tests
cp "$SRC/scripts/citation_check.py" skills/check-the-facts/scripts/citation_check.py
```

Then make exactly two edits, per the Global Constraints replacement table:

- **Line 30**, inside the `CITE` regex comment. It gives two examples of strings that must *not* be matched as citations. The second names the client's target system and a segment value; replace that example with `"C01:Aurora.Segment"`, leaving the first example and the sentence's structure untouched.
- **Line 48**, inside the `find_source` docstring. It gives two examples of how citations are written; the second carries a real module path from the client's tool. Replace it with `"converter/fund.py:322"`.

Read the originals at those two lines in `$SRC/scripts/citation_check.py` and append both rows to `docs/anonymisation-review-aid.md`.

Verify before staging, using the original values read from `$SRC` rather than any written here:

```bash
diff <(sed -n '30p;48p' "$SRC/scripts/citation_check.py") \
     <(sed -n '30p;48p' skills/check-the-facts/scripts/citation_check.py)
```

Expected: both lines differ. **If either line is unchanged, the substitution did not take — do not commit.**

Then confirm no other line changed:

```bash
diff "$SRC/scripts/citation_check.py" skills/check-the-facts/scripts/citation_check.py | grep -c "^[<>]"
```

Expected: `4` — two removed lines and two added.

- [ ] **Step 2: Write the failing tests**

Create `skills/check-the-facts/tests/test_citation_check.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "citation_check.py"


def run(doc: Path, root: Path, *extra):
    return subprocess.run([sys.executable, str(SCRIPT), str(doc), "--root", str(root), *extra],
                          capture_output=True, text=True)


def write(p: Path, text: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def test_resolving_citation_exits_zero(tmp_path):
    src = tmp_path / "src"
    write(src / "pipeline.py", "line one\nline two\nline three\n")
    doc = write(tmp_path / "book.md", "The stage runs at `pipeline.py:2`.\n")
    r = run(doc, src)
    assert r.returncode == 0, r.stdout
    assert "1 citations" in r.stdout
    assert "problems : 0" in r.stdout


def test_dead_file_exits_one(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    doc = write(tmp_path / "book.md", "See `ghost.py:12`.\n")
    r = run(doc, src)
    assert r.returncode == 1
    assert "FILE NOT FOUND" in r.stdout


def test_line_out_of_range_exits_one(tmp_path):
    src = tmp_path / "src"
    write(src / "short.py", "only one line\n")
    doc = write(tmp_path / "book.md", "See `short.py:99`.\n")
    r = run(doc, src)
    assert r.returncode == 1
    assert "LINE OUT OF RANGE" in r.stdout


def test_ambiguous_basename_exits_one(tmp_path):
    src = tmp_path / "src"
    write(src / "a" / "fund.py", "x\ny\n")
    write(src / "b" / "fund.py", "x\ny\n")
    doc = write(tmp_path / "book.md", "See `fund.py:1`.\n")
    r = run(doc, src)
    assert r.returncode == 1
    assert "AMBIGUOUS PATH" in r.stdout


def test_directory_prefixed_citation_resolves_by_tail(tmp_path):
    src = tmp_path / "src"
    write(src / "a" / "fund.py", "x\ny\n")
    write(src / "b" / "fund.py", "x\ny\n")
    doc = write(tmp_path / "book.md", "See `a/fund.py:1`.\n")
    r = run(doc, src)
    assert r.returncode == 0, r.stdout


def test_blank_target_is_reported(tmp_path):
    src = tmp_path / "src"
    write(src / "mod.py", "first\n\nthird\n")
    doc = write(tmp_path / "book.md", "See `mod.py:2`.\n")
    r = run(doc, src)
    assert r.returncode == 0, r.stdout
    assert "resolve to a blank line: 1" in r.stdout


def test_range_citation_starting_on_blank_line_is_not_flagged(tmp_path):
    src = tmp_path / "src"
    write(src / "mod.py", "first\n\nthird\n")
    doc = write(tmp_path / "book.md", "See `mod.py:2-3`.\n")
    r = run(doc, src)
    assert r.returncode == 0, r.stdout
    assert "resolve to a blank line" not in r.stdout


def test_non_citations_are_not_matched(tmp_path):
    src = tmp_path / "src"
    write(src / "pipeline.py", "a\nb\n")
    doc = write(tmp_path / "book.md",
                'Ignore note:12 and "C01:Aurora.Segment" but catch `pipeline.py:1`.\n')
    r = run(doc, src)
    assert r.returncode == 0, r.stdout
    assert "1 citations" in r.stdout


def test_only_findings_restricts_the_sample(tmp_path):
    src = tmp_path / "src"
    write(src / "mod.py", "aaa\nbbb\nccc\n")
    doc = write(tmp_path / "book.md",
                "Descriptive sentence citing `mod.py:1`.\n\n"
                "Verified: the guard at `mod.py:3` never fires.\n")
    r = run(doc, src, "--sample", "10", "--only-findings")
    assert r.returncode == 0, r.stdout
    assert "finding-adjacent" in r.stdout
    sample_section = r.stdout.split("SAMPLE")[1]
    assert "mod.py:3" in sample_section
    assert "mod.py:1" not in sample_section


def test_json_output_records_each_citation(tmp_path):
    src = tmp_path / "src"
    write(src / "mod.py", "aaa\nbbb\n")
    doc = write(tmp_path / "book.md", "See `mod.py:1` and `mod.py:2`.\n")
    out = tmp_path / "result.json"
    r = run(doc, src, "--json", str(out))
    assert r.returncode == 0, r.stdout
    data = json.loads(out.read_text(encoding="utf-8"))
    assert [rec["start"] for rec in data] == [1, 2]
    assert all(rec["status"] == "ok" for rec in data)


def test_missing_document_exits_two(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    r = run(tmp_path / "absent.md", src)
    assert r.returncode == 2


def test_missing_root_exits_two(tmp_path):
    doc = write(tmp_path / "book.md", "See `mod.py:1`.\n")
    r = run(doc, tmp_path / "absent-root")
    assert r.returncode == 2
```

- [ ] **Step 3: Run the tests**

Run: `python -m pytest skills/check-the-facts/tests/test_citation_check.py -v`

Expected: most pass, since the script already exists and is believed to work. **This is the point of the task — the tests are being written against untested code, so treat any failure as a genuine defect in the script and fix the script, not the test.** Two are worth watching specifically:

- `test_only_findings_restricts_the_sample` exercises `FINDING_WORDS` matching on the document line containing the citation. Confirm "Verified:" matches and the descriptive line does not.
- `test_blank_target_is_reported` depends on `blank_target` being set only when `start == end`.

If a test reveals a defect, fix the script, re-run, and describe the defect in the commit message. Do not silently relax an assertion to make it pass.

- [ ] **Step 4: Run the full suite to confirm nothing else broke**

Run: `python -m pytest -q`
Expected: all tests pass — 11 validator tests plus 12 citation tests.

- [ ] **Step 5: Commit**

```bash
git add skills/check-the-facts/scripts skills/check-the-facts/tests
git commit -m "$(cat <<'EOF'
Add the citation checker with a test suite

Establishes the invocation and exit-code contract the check-the-facts skill
quotes: 0 when every citation resolves, 1 when any does not, 2 on a missing
document or source root. Two docstring examples were anonymised before the
first commit per spec D12.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: `establish-the-truth`

**Files:**
- Create: `skills/establish-the-truth/SKILL.md`
- Create: `skills/establish-the-truth/references/evidence-base.md`
- Create: `skills/establish-the-truth/evals/evals.json`

**Interfaces:**
- Consumes: nothing.
- Produces: the `evidence/01-evidence-base.md` contract. Tasks 4–8 read these exact field names: `TOOL`, `VERSION`, `STAGED-AT`, `EXECUTED` (`yes`|`no`), `REASON-NOT-EXECUTED`, `OWN-TEST-SUITE`, and per-run `RUN <run-id>` sections each containing `SETTINGS`, `PATH` and a `FIGURES` table. Any later task quoting a figure names the `RUN` it sits under.

- [ ] **Step 1: Write the evals first**

Create `skills/establish-the-truth/evals/evals.json`:

```json
{
  "skill_name": "establish-the-truth",
  "evals": [
    {
      "id": 1,
      "prompt": "I need to review this conversion script before we hand its output to the client. Where do I start?",
      "expected_output": "Should stage the code and the real inputs into a scratch workspace rather than working in the original folder. Should run the tool's own test suite and record the exact pass count. Should execute the tool at least twice under settings that exercise genuinely different paths, and record a run identifier for each. Should measure the output by opening the files and counting rather than reading the tool's own summary. Should write evidence/01-evidence-base.md with EXECUTED, TOOL, VERSION, and a RUN section per run. Should not proceed to reading functions before output exists.",
      "assertions": [
        "Stages code and real inputs into a scratch workspace, leaving the original untouched",
        "Brings the real inputs rather than synthetic data, and says why",
        "Records the tool's own test suite pass count exactly",
        "Executes at least twice under genuinely different settings",
        "Records a run identifier per run",
        "Measures output by opening files and counting, not by reading the tool's summary",
        "Writes evidence/01-evidence-base.md with the required fields",
        "Records unreconciled observations rather than resolving them immediately"
      ],
      "files": []
    },
    {
      "id": 2,
      "prompt": "can you run this thing twice and tell me what it actually spits out",
      "expected_output": "Should trigger on casual phrasing. Should recognise this as establishing a baseline and execute under two different settings. Should report measured figures — row counts, totals, blank counts in columns that should never be blank — attributed to each run rather than quoting the tool's own reported numbers.",
      "assertions": [
        "Triggers on casual phrasing without the words baseline or evidence",
        "Executes under two different settings rather than twice identically",
        "Reports figures it measured itself",
        "Attributes every figure to a named run"
      ],
      "files": []
    },
    {
      "id": 3,
      "prompt": "The tool needs a licensed database driver we don't have, so it won't run here. Do the review anyway.",
      "expected_output": "Should still produce evidence/01-evidence-base.md, with EXECUTED: no and REASON-NOT-EXECUTED naming the missing driver. Should state plainly that a review that cannot run the tool is worth much less and that the reader must know that before relying on it. Should not fabricate figures, and should not silently continue as though a baseline existed. Should say which downstream work is now unverifiable.",
      "assertions": [
        "Writes the manifest with EXECUTED: no rather than skipping it",
        "Records the specific reason execution failed",
        "States plainly that the review is worth less and the reader must be told",
        "Fabricates no figures",
        "Names what downstream work becomes unverifiable"
      ],
      "files": []
    }
  ]
}
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python tools/validate_skills.py`
Expected: exit 1, reporting `establish-the-truth: SKILL.md is missing`.

- [ ] **Step 3: Write the evidence-base reference**

Create `skills/establish-the-truth/references/evidence-base.md`:

```markdown
# The evidence base

Every figure in every deliverable is quoted from this file, and every figure in
this file names the run it came from. That is the whole point of it: the most
common error a verification pass catches is a figure that was true of a
different run, and a manifest that makes the run identifier a structural
requirement rather than a convention removes the possibility.

Write it to `evidence/01-evidence-base.md`. Fields in this order.

## Header

    TOOL: <name as the user calls it>
    VERSION: <as stamped by the tool at runtime, not as documented>
    STAGED-AT: <the scratch path the code was copied to>
    EXECUTED: yes | no
    REASON-NOT-EXECUTED: <required when EXECUTED is no; omit otherwise>
    OWN-TEST-SUITE: PASS <n> / FAIL <n> | ABSENT

`VERSION` is the runtime stamp, not the changelog's. Archived runs are routinely
produced by older builds than the one deployed, and a review that assumes
otherwise is reviewing something nobody is using.

`OWN-TEST-SUITE` carries the exact count. The most quotable sentence in a review
of this kind is usually "all N of its own assertions pass against the defect
below", and it needs N.

## Inputs

One row per input actually used.

    | Input | Path | Real or synthetic | Notes |

A review run on synthetic data proves the code runs; it does not tell you what
the client's file will do. Where an input is synthetic, say so here, because
every figure derived from it inherits the qualification.

## Runs

One section per run, at least two.

    ### RUN <run-id>
    SETTINGS: <the settings that make this run different from the others>
    PATH: evidence/runs/<run-id>/

    FIGURES
    | Figure | Value | How measured |

"How measured" is a command or an operation, not an adjective — `wc -l on
output.csv minus the header`, `sum of column AMOUNT in the deliverable`,
`count of rows where ACCOUNT is blank`. If it cannot be written as an
operation, it was not measured.

Pick settings that exercise genuinely different paths — a different mode, a
different period, a different population. Two runs give you a comparison; one
gives you an anecdote.

## Unreconciled observations

    | # | What the run said or produced | Why it could not be reconciled |

Anything the run says that cannot be tied to something: a warning naming a
mechanism, a figure that disagrees with the documentation, a file the docs say
exists that does not. Each of these is a thread, and they are where the best
findings come from. Record them here without resolving them — resolution is the
finding hunt's job, and an observation resolved too early is an observation
nobody else can re-examine.

## When the tool cannot be executed

Write the file anyway, with `EXECUTED: no` and the reason. Then say plainly, at
the top of every deliverable that follows, that no figure in it was verified by
execution. A review that cannot run the thing is worth much less, and the reader
must know that before they rely on it.
```

- [ ] **Step 4: Write the skill**

Create `skills/establish-the-truth/SKILL.md`. Frontmatter first, description verbatim:

```markdown
---
name: establish-the-truth
description: "Execute a tool for real and measure its actual output, producing the evidence base that every later figure is quoted from. Use when starting a review of a tool and no measured baseline exists yet, or when asked to run something twice under different settings and record what it produced, establish a baseline before reviewing a script, or check whether a tool's own reported figures match its real output. Trigger on 'establish a baseline', 'run it and measure it', 'what does it actually produce', 'record the reference run', or 'the changelog says X, is that true'. Writes evidence/01-evidence-base.md."
---
```

Body, adapted from `$SRC/SKILL.md` Phase 1 (lines 25–39). It must contain:

1. **The doctrine, quoted verbatim**, and the reason this phase comes first: it takes about an hour and from then on any question can be settled by measurement instead of argument.
2. **The five numbered steps**, carried over intact: stage the code out of the client folder into a scratch workspace with the real inputs; run the tool's own test suite and record the exact pass count; execute at least twice under genuinely different settings and record the run identifiers; measure the output by opening the files and counting; note anything the run says that cannot be reconciled.
3. **The worked illustration** from the source, whose detail is already generic: a warning citing a heuristic led to the discovery that the heuristic had been deleted three versions earlier and the warning was still firing on a population it did not describe. Keep it — it is what tells a reader why step 5 is worth doing.
4. **A pointer to `references/evidence-base.md`** for the required fields.
5. **The un-runnable path**: write the manifest with `EXECUTED: no`, say so at the top of both books, and mark every figure unverified.
6. **The standalone contract**, as its own short section:
   - *Needs:* the tool and its real inputs.
   - *If that is missing:* if the tool cannot be executed, write the manifest with `EXECUTED: no` and the reason rather than producing nothing; if the real inputs are unavailable but the tool runs, record every input as synthetic and state that every derived figure inherits that qualification.
   - *Hands back:* the path to `evidence/01-evidence-base.md`.
7. **The prevention half of the run-attribution failure**, stated as a rule: a figure recorded without a run identifier is not recorded, because a figure that was true of a different run is the single most common error a verification pass catches.

Write proper prose, not bullet soup. The source is the model for register.

- [ ] **Step 5: Run the validator to verify it passes**

Run: `python tools/validate_skills.py`
Expected: `ok establish-the-truth`, exit 0.

- [ ] **Step 6: Read the skill against its own eval assertions**

Take the 17 assertions across the three evals in Step 1 and confirm each is satisfiable from the text written in Step 4. The ones most likely to be missing:

- "Records unreconciled observations rather than resolving them immediately" — the source says to note them; the skill must say *not* to resolve them yet.
- "Names what downstream work becomes unverifiable" — new material with no counterpart in the source. Add it if absent.
- "Attributes every figure to a named run" — must be a rule in the skill, not only in the reference.

- [ ] **Step 7: Commit**

```bash
git add skills/establish-the-truth
git commit -m "$(cat <<'EOF'
Add establish-the-truth, phase 1 of the review

Carries the doctrine and the five steps that produce a measured baseline, plus
the evidence-base contract every later skill reads. Makes the run identifier a
structural requirement of every recorded figure, which is the prevention half
of the most common verification error.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: `map-the-code` and the `code-mapper` agent

**Files:**
- Create: `skills/map-the-code/SKILL.md`
- Create: `skills/map-the-code/references/function-entry.md`
- Create: `skills/map-the-code/evals/evals.json`
- Create: `agents/code-mapper.md`

**Interfaces:**
- Consumes: `evidence/01-evidence-base.md` — reads `EXECUTED` and the per-`RUN` `FIGURES` tables for the population column of the execution spine.
- Produces: `evidence/02-execution-spine.md` (a numbered table: stage, call-site line, what it adds, population at that point) and one `evidence/02-map-<layer>.md` per layer. Task 5 reads both; Task 6 quotes both.

- [ ] **Step 1: Write the evals first**

Create `skills/map-the-code/evals/evals.json`:

```json
{
  "skill_name": "map-the-code",
  "evals": [
    {
      "id": 1,
      "prompt": "Document every function in this conversion tool. It's about 10,000 lines across four modules.",
      "expected_output": "Should split the modules into three to five groups along the layers the code actually has and dispatch one code-mapper agent per group in parallel. Should ask one agent for the execution spine. Should state the depth target explicitly: a heading per function, four labelled paragraphs under each, roughly one line citation per 50 words, private helpers included where they carry real logic. Should write to files and expect paths back rather than prose in the reply. Should say that a section describing a module in three good paragraphs has failed however well written it is.",
      "assertions": [
        "Splits into three to five groups along the code's actual layers",
        "Dispatches one code-mapper agent per group, in parallel",
        "Requests the execution spine as a distinct deliverable",
        "States the depth target with a heading per function and four labelled paragraphs",
        "Names the citation density target",
        "Includes private helpers that carry real logic",
        "Requires agents to write to files and return paths",
        "Names summarising-instead-of-documenting as the failure mode to avoid"
      ],
      "files": []
    },
    {
      "id": 2,
      "prompt": "what does this function actually do, and what does it assume",
      "expected_output": "Should trigger on a single-function question and answer in the per-function template: what it does, how it does it with line citations, what it relies on stated specifically, and what happens when that reliance is violated. Should distinguish raising from silently coercing from dropping rows. Should not answer with a generic description or say the function assumes valid input.",
      "assertions": [
        "Triggers on a single-function question",
        "Answers in the four-part template",
        "Cites specific lines as file.ext:NNN",
        "States assumptions specifically rather than as 'assumes valid input'",
        "Names the failure mode as raise, coerce, drop, or return empty"
      ],
      "files": []
    },
    {
      "id": 3,
      "prompt": "Map this code for me. There's no evidence base — nobody has run it yet.",
      "expected_output": "Should produce the map regardless, because the map does not depend on execution. Should keep the execution spine's population column but fill it with 'not measured' rather than omitting the column or inventing numbers. Should state at the top of its output that no baseline exists and which claims are therefore unverified. Should offer to establish the baseline first and explain what it would add.",
      "assertions": [
        "Produces the map rather than refusing",
        "Keeps the population column and fills it with 'not measured'",
        "Omits no column and invents no figures",
        "States the degradation at the top of its own output",
        "Offers to establish a baseline and says what it would add"
      ],
      "files": []
    }
  ]
}
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python tools/validate_skills.py`
Expected: exit 1, `map-the-code: SKILL.md is missing`.

- [ ] **Step 3: Write the per-function reference**

Create `skills/map-the-code/references/function-entry.md`. It holds the template and the depth target, so the skill and the agent cite one source and cannot drift apart. Content, from `$SRC/SKILL.md:47-52` and `$SRC/references/code-review-book.md:54-70,128-139`:

```markdown
# The per-function entry

Four labelled paragraphs, in this order, every time. Consistency across sections
is what makes the finished document usable as a reference rather than readable as
an essay.

### <exact signature, as written>

**What it does.** The business purpose, one or two sentences a partner could
read.

**How it does it.** The actual mechanism — the algorithm, the order of
operations, the masks, the fallback ladder — with `file.ext:NNN` citations, each
verified by reading the file at that line. Where the mechanism has a worked
consequence, work it: a numeric example beats a description.

**What it relies on.** The load-bearing assumptions, specifically. "Assumes the
column is named exactly X" is useful; "assumes valid input" is not. Column
names, file shapes, dtypes, upstream state, config keys, ordering relative to
other calls.

**Failure modes.** What happens when the reliance is violated. Does it raise,
silently coerce, drop rows, return empty? Say which.

## The depth target

The natural failure here is writing an essay about the code instead of a
reference to it. Three elegant paragraphs summarising what a module does will
read better than twenty entries and will be useless to the maintainer who needs
to know what one particular function assumes.

Check a section against these before considering it finished:

- **A heading per function**, matching the actual name, so the document is
  searchable by symbol.
- **All four labels under each**, in the same order.
- **Roughly one line citation per 50 words.** Below that the document has
  stopped being anchored to the code; a section carrying two citations for a
  400-line module was written from memory.
- **Private helpers included** where they carry real logic. These are frequently
  where the finding is, because nobody reviews them.

For a 10,000-line tool the finished code review runs 40,000–60,000 words. That
is fine — it is a reference, not an essay. What is not fine is padding it with
restatement: every paragraph should carry a fact a reader could not get from the
code faster themselves.

If a section is short because the module genuinely is, say so and move on. If it
is short because it summarises, go back.

## Module-level material

Module-level constants, hard-coded account numbers, default configurations and
sentinel values get their own subsections. They are what someone changes, and
they are where a change does damage.
```

- [ ] **Step 4: Write the agent**

Create `agents/code-mapper.md`:

```markdown
---
name: code-mapper
description: Documents one layer of a tool at function level — signature, purpose, mechanism with line citations, load-bearing assumptions, and failure modes — writing to a file and returning the path.
tools: Read, Grep, Glob, Bash, Write
---

You document one layer of a codebase at function level. Your output is a
reference a maintainer consults when they need to know where a number came from,
not an essay about the code.

For every module in your assigned layer, and every function within it including
private helpers that carry real logic, write an entry with four labelled
paragraphs in this order:

**What it does.** The business purpose, one or two sentences a partner could
read.

**How it does it.** The actual mechanism — the algorithm, the order of
operations, the masks, the fallback ladder — with `file.ext:NNN` citations, each
verified by reading the file at that line. Where the mechanism has a worked
consequence, work it: a numeric example beats a description.

**What it relies on.** The load-bearing assumptions, specifically. "Assumes the
column is named exactly X" is useful; "assumes valid input" is not.

**Failure modes.** What happens when the reliance is violated. Does it raise,
silently coerce, drop rows, return empty? Say which.

Three rules that separate this from a code summary:

1. **Reproduce behaviour where it is reproducible.** If a claim about an edge
   case can be tested by executing it, execute it. The strongest sentences you
   can write begin "Verified:".
2. **Where the code and its own comments disagree, say so and say which is
   right.** Stale docstrings are common and they mislead the next reader.
3. **Write to a file, not to your reply.** Your section will run past 10,000
   words. Return the path.

Depth is the thing you will get wrong if you are not deliberate about it. A
heading per function matching the actual name. All four labels under each, in
the same order. Roughly one line citation per 50 words — below that you are
writing from memory. A section that describes a module in three good paragraphs
and moves on has failed, however well written it is.

If you are asked for the execution spine rather than a layer, produce a numbered
table instead: stage, the line the stage is called at, what it adds, and the
state of the data at that point including population sizes. Then three to five
numbered observations on what a reviewer must take from the ordering, each
stated as a claim with its two line numbers. Ordering defects — a check that
runs before the thing it checks, a measurement taken after the construction that
conceals it — are only visible against this, so precision in the line numbers
matters more here than anywhere else.
```

- [ ] **Step 5: Write the skill**

Create `skills/map-the-code/SKILL.md`, frontmatter description verbatim:

```markdown
---
name: map-the-code
description: "Document every module and function in a tool — signature, business purpose, mechanism with line citations, load-bearing assumptions, and failure modes — plus the ordered execution spine of its entry point. Use when asked what a script or tool actually does at function level, to write a maintainer's reference for code, to document a pipeline stage by stage, or when a review needs a function-level map before findings can be hunted. Trigger on 'what does this function do', 'document every function', 'walk me through the code', 'what order does this run in', or 'write a reference for this tool'. Writes evidence/02-execution-spine.md and evidence/02-map-<layer>.md."
---
```

Body, from `$SRC/SKILL.md:41-64`. It must contain:

1. **The layer split**: three to five groups along the layers the code actually has, with the typical grouping named (input and configuration; transformation core; orchestration and controls; output, interface and tests) and an instruction to adapt to what is there.
2. **Parallel dispatch** of one `code-mapper` agent per group, and a pointer to `references/function-entry.md` as the shared template.
3. **The execution spine** as a distinct deliverable from one agent, with why it matters: nothing else in the tool makes sense without knowing what has and has not yet happened at a given moment, and ordering defects are only visible against it.
4. **The depth expectation stated explicitly**, with a pointer to the reference, and the sentence that a section describing a module in three good paragraphs has failed however well written it is.
5. **The sequential fallback** for no subagent tool, carried over in full: work the layers yourself in the same order, one at a time, writing each section to its own file before starting the next; do not hold four in context at once because quality collapses in the last one; check your own section against the depth target before moving on; after the last section re-read the execution spine against the finished sections hunting specifically for ordering defects; and say in §1 of the finished document that the review was performed sequentially, because it changes what a reader should expect of its uniformity.
6. **The standalone contract**:
   - *Needs:* `evidence/01-evidence-base.md`, for the population column of the spine.
   - *If that is missing:* produce the map anyway — it does not depend on execution. Keep the population column and fill it with `not measured`; do not omit the column, because its absence hides that the figure was never taken. State the degradation at the top of the output and offer to establish the baseline first.
   - *Hands back:* the list of written paths.

- [ ] **Step 6: Run the validator**

Run: `python tools/validate_skills.py`
Expected: `ok map-the-code`, exit 0.

- [ ] **Step 7: Read the skill and agent against the eval assertions**

Confirm all 18 assertions across the three evals are satisfiable. Check specifically that the depth target appears in **both** the skill and the agent — the skill states it so the dispatcher can enforce it, the agent carries it so it holds without being restated. This duplication is deliberate; do not remove it.

- [ ] **Step 8: Commit**

```bash
git add skills/map-the-code agents/code-mapper.md
git commit -m "$(cat <<'EOF'
Add map-the-code and the code-mapper agent

The per-function template and depth target move into a shared reference so the
skill and the agent cite one source and cannot drift. The agent carries the
three rules that separate a function-level map from a code summary in its own
system prompt, where they survive a 10,000-word task.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: `hunt-the-findings` and the anonymised catalogue

**Files:**
- Create: `skills/hunt-the-findings/SKILL.md`
- Create: `skills/hunt-the-findings/references/finding-patterns.md` (from `$SRC/references/finding-patterns.md`, anonymised before staging)
- Create: `skills/hunt-the-findings/evals/evals.json`
- Create: `docs/anonymisation-review-aid.md` (git-ignored; never committed)

**Interfaces:**
- Consumes: `evidence/01-evidence-base.md`, `evidence/02-execution-spine.md`, `evidence/02-map-<layer>.md`.
- Produces: `evidence/03-findings.md` — per candidate, the pattern class, the shape observed, how it was tested, the verdict, the evidence, and whether it is reproducible. Task 6 reads it; Task 7 reproduces each entry from scratch.

**This task handles client-derived content. Nothing gets staged before the substitutions are made and verified.**

- [ ] **Step 1: Write the evals first**

Create `skills/hunt-the-findings/evals/evals.json`:

```json
{
  "skill_name": "hunt-the-findings",
  "evals": [
    {
      "id": 1,
      "prompt": "The map is done. Now find what's wrong with this tool.",
      "expected_output": "Should work the catalogue in references/finding-patterns.md deliberately rather than hoping the module map surfaced the defects. Should explain that most of these classes are invisible from any single function and appear only when two things the code keeps apart are compared. Should test each candidate rather than reasoning about it, and record per candidate how it was tested and whether it is reproducible. Should record what held up under attack as well as what failed, so a reader can distinguish examined-and-sound from never-examined.",
      "assertions": [
        "Works the catalogue deliberately rather than opportunistically",
        "Explains that most classes need two things compared, not one function read",
        "Tests each candidate rather than reasoning about it",
        "Records how each candidate was tested",
        "Marks each finding reproducible or not",
        "Records negative results as part of the deliverable",
        "Writes evidence/03-findings.md"
      ],
      "files": []
    },
    {
      "id": 2,
      "prompt": "the dashboard is all green, 340-odd checks passing. are these checks actually worth anything?",
      "expected_output": "Should trigger on casual phrasing. Should separate what the tool attests from what the tool detects. Should test each check for the classes in the catalogue: whether both operands trace to the same data with nothing between that could move them apart, whether a verdict is a hard-coded literal, whether the step immediately before made the condition true, and whether the population measured is the population delivered. Should distinguish a check correctly declared informational from one documented as a control, and should credit checks whose expectation comes from outside the pipeline.",
      "assertions": [
        "Triggers on casual phrasing about a green dashboard",
        "Separates what the tool attests from what it detects",
        "Traces both operands of a check to where they are written",
        "Checks whether the preceding step made the condition true",
        "Compares the population measured against the population delivered",
        "Distinguishes correctly-declared informational checks from controls",
        "Credits checks whose expectation comes from outside the pipeline"
      ],
      "files": []
    },
    {
      "id": 3,
      "prompt": "There's no exceptions file in the output folder, so I take it there were no exceptions. Anything else to look at?",
      "expected_output": "Should reject the inference: many tools write an exceptions file only when there are exceptions, so its absence means the tool found none by its own definition — which is exactly the definition under review. Should say what to do instead, which is to establish from the artifacts what the control set does not cover at all rather than reasoning about the code.",
      "assertions": [
        "Rejects absence of an evidence file as evidence of nothing to report",
        "Names the circularity: found none by its own definition, which is the definition under review",
        "Says to establish coverage from the artifacts rather than from the code",
        "Does not simply agree with the user's inference"
      ],
      "files": []
    }
  ]
}
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python tools/validate_skills.py`
Expected: exit 1, `hunt-the-findings: SKILL.md is missing`.

- [ ] **Step 3: Copy the catalogue and anonymise it before staging**

```bash
mkdir -p skills/hunt-the-findings/references
cp "$SRC/references/finding-patterns.md" skills/hunt-the-findings/references/finding-patterns.md
```

Apply the replacement table from Global Constraints. The one substantial edit is the case-study sentence at line 81, in §5. Read the original at `$SRC/references/finding-patterns.md:81`; it names a row count, a gross amount, two adjacent account codes, and two adjacent source row numbers. Rewrite it so that it reads:

> In the engagement this catalogue was written from this was roughly 40 rows carrying about $2M gross: source row 118's own code was `41205`, unclassifiable, and the row shipped carrying `41204` from row 117.

Everything after that clause in the original sentence stays exactly as written. The mechanics are unchanged and that is the requirement — a record correctly flagged unresolvable whose emit step applies the open context to it anyway, so the field that failed to resolve holds the preceding record's value. The magnitude is preserved to order of magnitude, because a defect worth two million dollars and one worth two hundred are different findings, and the row numbers stay adjacent because adjacency *is* the mechanism.

Then replace every occurrence of the phrase that introduces the source engagement with `In the engagement this catalogue was written from`. Grep `$SRC/references/finding-patterns.md` for the original phrase to find them all; there is more than one.

Append every substitution to `docs/anonymisation-review-aid.md`.

- [ ] **Step 4: Add the judgement section to the review aid**

The aid was created in Task 1 Step 8 and has been accumulating substitution rows since Task 2. Confirm it is still ignored before appending:

```bash
git check-ignore -v docs/anonymisation-review-aid.md
```

**Stop and fix `.gitignore` if that reports nothing.**

Now append a second section, **Flagged for author judgement** — items that are not obviously client-derived but that a reader who knew the engagement might recognise. These are the point of the gate, because a grep cannot find them:

- `finding-patterns.md` §10 offers a specimen sentence about two numbering systems agreeing up to one line and diverging at the next, using concrete line numbers. Two small integers with no identifying power alone; listed so the author can decide whether to substitute them.
- `SKILL.md` Phase 1 illustrates step 5 with a warning citing a named heuristic that had been deleted three versions earlier. The mechanism name is generic-sounding but it is the client tool's own vocabulary.
- `SKILL.md` and the phase-5 material retain three statistics about the review itself — a count of a tool's own passing assertions, the errors a verification pass caught across two documents, and the errors a self-verification caught without a subagent. Retained deliberately under the §13 rule that statistics about the review stay; flagged so the author confirms that reading rather than inheriting it.
- Any defect description detailed enough to identify the engagement without naming it. §5's context-leak case is the one to look at hardest, since a chart-of-accounts conversion with an inherited-code defect is a recognisable combination even with every figure changed.

- [ ] **Step 5: Verify no client data will be staged**

Build the pattern list from the aid rather than from this plan, so no original value is ever written into a tracked file. The aid's first column is the original values; extract them and grep for them:

```bash
awk -F'|' '/^\|/ && NF>2 {gsub(/^ +| +$/,"",$2); if ($2 != "" && $2 !~ /original/) print $2}' \
  docs/anonymisation-review-aid.md > /tmp/tully-originals.txt
grep -rInFf /tmp/tully-originals.txt skills/ && echo "LEAK — do not stage" || echo "clean"
rm -f /tmp/tully-originals.txt
```

Expected: `clean`. **If it prints `LEAK`, do not stage anything.**

Then confirm the aid itself is not stageable:

```bash
git status --short docs/
```

Expected: `docs/anonymisation-review-aid.md` does not appear.

- [ ] **Step 6: Write the skill**

Create `skills/hunt-the-findings/SKILL.md`, frontmatter description verbatim:

```markdown
---
name: hunt-the-findings
description: "Work a catalogue of defect classes that tools producing financial deliverables actually have — checks that cannot fail, checks measured on the wrong population, ordering defects, attestation without detection, silent coercion, documentation contradicting behaviour, unguarded reliance. Use when a function-level map exists and the review needs its defects found, or when asked whether a tool's controls are worth anything, whether a green dashboard means what it appears to, or to look for what a test suite cannot see. Trigger on 'what could go wrong here', 'are these checks real', 'can this control fail', 'what does the test suite miss'. Writes evidence/03-findings.md."
---
```

Body, from `$SRC/SKILL.md:66-68` plus the warning it inherits from §"Things that reliably go wrong". Phase 3 is three sentences in the source, so most of this body is new material that the monolith left implicit:

1. **Why the catalogue is worked deliberately** rather than hoped for: most classes are invisible from any single function and appear only when two things the code keeps apart are compared — a check against the population it measures, a measurement against the construction that follows it, a document against the behaviour it describes.
2. **A pointer to `references/finding-patterns.md`** and an instruction to work its twelve sections in order, recording a verdict per class including the classes that came back clean.
3. **The output contract** for `evidence/03-findings.md`: per candidate, the pattern class, the shape observed, how it was tested (an operation, not an adjective), the verdict, the evidence, and whether it is reproducible. Reproduced findings are worth ten that say "this could fail".
4. **The absent-evidence-file warning**, in full: many tools write an exceptions file only when there are exceptions, so its absence means the tool found none by its own definition — which is exactly the definition under review. Establish what the control set does not cover by inspecting the artifacts, not by reasoning about the code.
5. **Negative results are part of the deliverable**, pointing at §12 of the catalogue: a review that lists only defects is not usable, because the reader cannot tell what was examined and found sound from what was never examined.
6. **The standalone contract**:
   - *Needs:* `evidence/01`, `02-execution-spine.md`, and the layer maps.
   - *If that is missing:* without the execution spine the ordering-defect classes (catalogue §3) cannot be worked at all, and without an evidence base the classes needing measurement cannot be tested. Name the classes not attempted rather than reporting a clean sweep — a catalogue silently worked at half coverage reads identically to one worked fully.
   - *Hands back:* the path to `evidence/03-findings.md`.

- [ ] **Step 7: Run the validator**

Run: `python tools/validate_skills.py`
Expected: `ok hunt-the-findings`, exit 0.

- [ ] **Step 8: Read the skill against the eval assertions**

Confirm all 18 assertions are satisfiable. Eval 3's "Does not simply agree with the user's inference" is the one at risk — the skill must be direct enough that a model reading it contradicts a user who has drawn the wrong conclusion.

- [ ] **Step 9: Commit**

```bash
git add skills/hunt-the-findings
git commit -m "$(cat <<'EOF'
Add hunt-the-findings and the anonymised defect catalogue

The catalogue was anonymised in the working copy before its first stage, per
spec D12, so no client-derived content enters history. Defect mechanics and
magnitudes are preserved because those are what a reader needs to recognise the
pattern in their own tool.

Phase 3 is three sentences in the monolith; the output contract, the coverage
rule, and the degraded mode are new material.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: `write-the-books`

**Files:**
- Create: `skills/write-the-books/SKILL.md`
- Create: `skills/write-the-books/references/checklist-book.md` (from `$SRC`, verbatim — verified clean)
- Create: `skills/write-the-books/references/code-review-book.md` (from `$SRC`, one substitution)
- Create: `skills/write-the-books/evals/evals.json`

**Interfaces:**
- Consumes: `evidence/01-evidence-base.md` (every figure and its `RUN`), `evidence/02-execution-spine.md`, `evidence/02-map-<layer>.md`, `evidence/03-findings.md`.
- Produces: two Markdown books named `<Client>-<Tool>-Human-Review-Checklist-v<X.Y>.md` and `<Client>-<Tool>-Code-Review-v<X.Y>.md`, plus the project record. Task 7 verifies them.

- [ ] **Step 1: Write the evals first**

Create `skills/write-the-books/evals/evals.json`:

```json
{
  "skill_name": "write-the-books",
  "evals": [
    {
      "id": 1,
      "prompt": "Research is done — evidence base, maps, spine, findings all written. Write it up.",
      "expected_output": "Should produce both books, because the checklist's compensating procedures exist only because the code review found the gaps they compensate for. Should organise the checklist by audit assertion, using both the transaction set and the balance set where the deliverable is both an event and a position, and should name the population each set tests so the two halves do not restate each other. Should rate every test T-INDEP, T-WEAK or NONE by where the control's expectation comes from. Should quote the reference figure in every procedure involving a count or total, attributed to its run. Should propose materiality against the deliverable's own units before the tests and flag it for partner agreement. Should state that the output is an internal working paper and not an attest report.",
      "assertions": [
        "Produces both books rather than one",
        "Organises the checklist by audit assertion",
        "Names the population each assertion set tests",
        "Rates every test T-INDEP, T-WEAK or NONE",
        "Bases the rating on where the control's expectation comes from",
        "Quotes reference figures attributed to a named run",
        "Proposes materiality before the tests and flags it for agreement",
        "Marks compensating procedures",
        "States the output is a working paper, not an attest report"
      ],
      "files": []
    },
    {
      "id": 2,
      "prompt": "I just need the checklist, not the code review. The code's fine.",
      "expected_output": "Should produce the checklist as asked. Should say once, without labouring it, that the research phase still runs in full because a checklist written without reading the code is a generic checklist. Should not produce a checklist consisting only of compensating procedures — the ordinary tests are needed too: does the total tie, is the period right, is the sign convention right.",
      "assertions": [
        "Produces the checklist as asked rather than insisting on both",
        "States once that the research phase still runs in full",
        "Includes ordinary tests, not only compensating procedures",
        "Does not labour the objection after making it"
      ],
      "files": []
    },
    {
      "id": 3,
      "prompt": "Write the code review. We couldn't run the tool — no test data.",
      "expected_output": "Should write the code review with a statement at the top of section 1 that the tool was not executed and that no figure in the document was verified by execution. Should mark every figure unverified rather than omitting figures or presenting documented figures as measured. Should omit the findings section and mark it explicitly not-performed rather than leaving it blank or filling it with speculation. Should state that this is documentation and not assurance.",
      "assertions": [
        "States at the top that the tool was not executed",
        "Marks every figure unverified rather than omitting them",
        "Presents no documented figure as measured",
        "Marks the findings section not-performed rather than leaving it blank",
        "States that the document is documentation, not assurance"
      ],
      "files": []
    }
  ]
}
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python tools/validate_skills.py`
Expected: exit 1, `write-the-books: SKILL.md is missing`.

- [ ] **Step 3: Copy the two book references, anonymising the one occurrence**

```bash
mkdir -p skills/write-the-books/references
cp "$SRC/references/checklist-book.md" skills/write-the-books/references/checklist-book.md
cp "$SRC/references/code-review-book.md" skills/write-the-books/references/code-review-book.md
```

`checklist-book.md` is clean and needs no edit.

In `code-review-book.md`, line 132 uses a function name as an incidental example of documentation depth, and that name embeds the client's source accounting system. Read the original at `$SRC/references/code-review-book.md:132` and replace just that identifier with `read_ledgerline_hierarchical`, leaving the rest of the sentence intact. Append the row to `docs/anonymisation-review-aid.md`.

Verify, without writing the original into any tracked file:

```bash
diff "$SRC/references/code-review-book.md" \
     skills/write-the-books/references/code-review-book.md | grep -c "^[<>]"
diff "$SRC/references/checklist-book.md" \
     skills/write-the-books/references/checklist-book.md | grep -c "^[<>]" || true
grep -c "read_ledgerline_hierarchical" skills/write-the-books/references/code-review-book.md
```

Expected: `2` for the first diff (one line changed), `0` for the second (checklist copied verbatim), and `1` for the replacement identifier.

- [ ] **Step 4: Write the skill**

Create `skills/write-the-books/SKILL.md`, frontmatter description verbatim:

```markdown
---
name: write-the-books
description: "Write the two deliverables of a tool review: a human review checklist organised by audit assertion, and a function-level code review, both Markdown, every figure attributed to a measured run. Use when the research phases of a review are complete and the deliverables need writing, or when asked to turn findings and a code map into a document a preparer works and a reviewer signs. Trigger on 'write it up', 'produce the checklist', 'write the code review', 'turn this into a workpaper', or 'I need something a partner can read'. Requires evidence/01 through 03; states what is missing rather than inventing figures."
---
```

Body, from `$SRC/SKILL.md:70-74` (phase 4), `:95-99` (phase 6), and four of the five items in `:101-111`:

1. **Both books by default**, and why they need each other: the checklist's compensating procedures exist only because the code review found the gaps they compensate for. If asked for one, produce that one, and say once that the research phase still runs in full.
2. **Pointers to both references** for structure and the per-test and per-function templates.
3. **Write to be read**: proper prose, tables where a table is clearer, no bullet soup. A partner has to be able to read the conclusion; a reviewer has to be able to work the checklist with the file open beside them.
4. **The four inherited warnings**, each as its own short paragraph:
   - A checklist that is only compensating procedures is not a checklist — the ordinary tests are needed too.
   - Where the tool's vocabulary and the register's differ, say so once and then be consistent, because the reader is holding two documents and a screen.
   - Every figure names which run it came from, or is stated for both. This is the most common error the verification pass catches.
   - Materiality is stated before the tests, against the deliverable's own units, proposed and flagged for partner agreement.
5. **Delivery**, from phase 6: name both files carrying the tool and version — `<Client>-<Tool>-Human-Review-Checklist-v<X.Y>.md` — and deliver them.
6. **The project record**, from phase 6: if a project or knowledge base is attached to the session, save a short record of what was produced, the reference runs and their key figures, the three findings that matter most, and anything that corrects an earlier document. The books are long; the record is what a future session reads first.
7. **The working-paper statement**, required in both books: the deliverable is an internal working paper supporting a preparer and a reviewer, not an attest report.
8. **The standalone contract**:
   - *Needs:* `evidence/01` through `03`.
   - *If that is missing:* with no `03`, the findings section is omitted and explicitly marked not-performed — never left blank, because a blank section reads as "nothing found". With `EXECUTED: no` in `01`, state at the top of section 1 that the tool was not executed, mark every figure unverified, and say the document is documentation rather than assurance. Never present a documented figure as a measured one.
   - *Hands back:* the book paths.

- [ ] **Step 5: Run the validator**

Run: `python tools/validate_skills.py`
Expected: `ok write-the-books`, exit 0.

- [ ] **Step 6: Read the skill against the eval assertions**

Confirm all 18 assertions are satisfiable. Eval 2's "Does not labour the objection after making it" is a tone requirement — the skill must say the thing once and move on, matching the source's own instruction that a document shouting at every finding flattens the ones that matter.

- [ ] **Step 7: Commit**

```bash
git add skills/write-the-books
git commit -m "$(cat <<'EOF'
Add write-the-books, phases 4 and 6

Carries both book structures and takes ownership of four of the five warnings
the monolith kept in a list at the end, each now sitting in the skill that can
act on it. One function name in the code-review reference was anonymised before
staging.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: `check-the-facts` and the `fact-checker` agent

**Files:**
- Create: `skills/check-the-facts/SKILL.md`
- Create: `skills/check-the-facts/evals/evals.json`
- Create: `agents/fact-checker.md`
- Already present from Task 2: `skills/check-the-facts/scripts/citation_check.py`, `skills/check-the-facts/tests/test_citation_check.py`

**Interfaces:**
- Consumes: a book path, the source tree, and `evidence/runs/`. Reads `evidence/03-findings.md` to reproduce each finding.
- Produces: `evidence/04-verification-<book>.md` — an error list, each entry naming the claim, where it is, what is actually true, and how that was established.

- [ ] **Step 1: Write the evals first**

Create `skills/check-the-facts/evals/evals.json`:

```json
{
  "skill_name": "check-the-facts",
  "evals": [
    {
      "id": 1,
      "prompt": "Both books are drafted. Check them before I send them to the partner.",
      "expected_output": "Should run scripts/citation_check.py first and hand its output to a fact-checker agent per book, so the agent's attention goes to whether a cited line supports the claim rather than to whether it exists. Should dispatch one agent per book with the instruction to find statements that are wrong and explicitly not to praise what checks out. Should check a large well-spread sample of citations including every citation supporting a finding, every table a reader would act on, every quantitative claim, and each finding reproduced from scratch. Should fix everything found and then report that the pass ran and what it caught.",
      "assertions": [
        "Runs citation_check.py before dispatching",
        "Hands the script output to the agent",
        "Dispatches one fact-checker per book",
        "Instructs the agent not to praise what checks out",
        "Checks every citation supporting a finding, not just a sample",
        "Re-derives every quantitative claim",
        "Reproduces each finding from scratch",
        "Reports that the pass ran and what it caught, as part of the deliverable's credibility"
      ],
      "files": []
    },
    {
      "id": 2,
      "prompt": "Someone's AI wrote this technical document with a load of file:line references in it. Are they real?",
      "expected_output": "Should recognise this as a standalone verification against a document it did not write, and run citation_check.py against the document and the source tree. Should distinguish what the script can establish — dead files, out-of-range lines, ambiguous paths, blank targets — from what it cannot, which is a citation resolving to a real line that says something else. Should sample the resolved citations and read whether each cited line supports the claim made at that point in the document.",
      "assertions": [
        "Triggers on a verification request for a document it did not write",
        "Runs the script against document and source tree",
        "States what the script can and cannot establish",
        "Reads sampled citations for whether the line supports the claim",
        "Does not treat a resolving citation as a correct one"
      ],
      "files": []
    },
    {
      "id": 3,
      "prompt": "No subagents available in this session. Verify the code review anyway.",
      "expected_output": "Should change the mode of work rather than re-reading: re-derive every quantitative claim mechanically from the run folders with a script, and re-resolve every finding-bearing citation, without looking at what was written until the script has produced its own answer, then compare. Should say explicitly that re-reading your own prose finds nothing while recomputing the number finds plenty. Should note that a self-verification done this way still caught five errors in testing, including an off-by-one in a total and a wrong divergence point.",
      "assertions": [
        "Changes the mode of work rather than re-reading the prose",
        "Re-derives quantitative claims mechanically with a script",
        "Produces its own answer before looking at what was written",
        "Explains why re-reading finds nothing",
        "Does not claim equivalence with a delegated pass"
      ],
      "files": []
    }
  ]
}
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python tools/validate_skills.py`
Expected: exit 1. Note that `check-the-facts` already exists as a directory from Task 2 with `scripts/` and `tests/` but no `SKILL.md` and no `evals/`, so before Step 1 the validator reports two problems for it and after Step 1 exactly one — `check-the-facts: SKILL.md is missing`.

- [ ] **Step 3: Write the agent**

Create `agents/fact-checker.md`:

```markdown
---
name: fact-checker
description: Adversarially verifies a review document by finding statements in it that are wrong — resolving citations, re-deriving quantitative claims from run folders, and reproducing findings from scratch.
tools: Read, Grep, Glob, Bash
---

Your job is to find statements in this document that are wrong.

**Do not praise what checks out.** Praise costs tokens and hides the errors. A
report that says "sections 1 through 8 are accurate" has spent its budget
telling the reader nothing they can act on. Report only what is wrong, what is
unsupported, or what is stated with more confidence than its evidence carries.

The person who wrote a sentence is the worst reader of it, which is why you are
here. Assume the document was written carefully and still contains errors,
because carefully written documents of this kind reliably do — in testing, a
pass of this sort found 26 errors across two documents that had already been
written carefully, and none was visible to their author.

Check, at minimum:

1. **Every citation that supports a finding**, rather than a description. You
   will be handed the output of a mechanical citation checker; it has already
   established which citations resolve. Your attention goes to whether the cited
   line *supports the claim made about it*. A citation that resolves to a real
   line saying something else is the error the machine cannot see.
2. **Every table a reader would act on.** A reviewer works from these with the
   file open beside them; a wrong key or a wrong row number sends them to the
   wrong number and they will not know.
3. **Every quantitative claim.** Re-derive it from the run folders yourself. Do
   not check that the document is internally consistent — check that the number
   is right.
4. **Every finding, reproduced from scratch.** Do not accept the document's
   account of how a finding was established. Establish it again. If you cannot,
   say so: a finding that cannot be reproduced is a different kind of claim from
   one that can.

You have the code, the run folders, and permission to execute things. Use them.
Measurement settles questions that argument does not.

Report each error as: the claim, where it is, what is actually true, and how you
established that. Order by consequence — an error that would send a reviewer to
the wrong number outranks a stale cross-reference.
```

- [ ] **Step 4: Write the skill**

Create `skills/check-the-facts/SKILL.md`, frontmatter description verbatim:

```markdown
---
name: check-the-facts
description: "Adversarially verify a review document by finding statements in it that are wrong — resolving every file.ext:NNN citation mechanically, re-deriving every quantitative claim from the run folders, and reproducing every finding from scratch. Use before any review document is handed on, and on any cited document whose accuracy is in question, including one written by a previous reviewer or by another AI. Trigger on 'check this document', 'fact-check the review', 'are these citations right', 'verify before I send this', or 'did we get the numbers right'. Writes evidence/04-verification-<book>.md."
---
```

Body, from `$SRC/SKILL.md:76-93`:

1. **Do not skip this**, stated first, and why: the person who wrote a sentence is the worst reader of it.
2. **Dispatch one `fact-checker` per book**, with the code, the run folders, and permission to execute.
3. **Run the script first** and hand the agent its output, with the exact invocations:

   ```bash
   python scripts/citation_check.py BOOK.md --root /path/to/source
   python scripts/citation_check.py BOOK.md --root /path/to/source --sample 40 --only-findings
   ```

   And the reason: it resolves every `file.ext:NNN` citation mechanically so the agent spends its attention on whether the cited line supports the claim rather than on whether it exists. State the exit-code contract established in Task 2 — 0 when every citation resolves, 1 when any does not, 2 on a missing document or root — and what the script cannot catch: a citation that resolves to a real line saying something else.
4. **The minimum check list**: a large well-spread sample of citations with every citation supporting a finding rather than a description; every table a reader would act on; every quantitative claim; each finding reproduced from scratch.
5. **The no-subagent fallback**, in full and as a change of mode rather than a re-read: re-derive every quantitative claim mechanically from the run folders with a script and re-resolve every finding-bearing citation, without looking at what was written until the script has produced its own answer, then compare. Re-reading your own prose finds nothing; recomputing the number finds plenty. Keep the reference statistic — a self-verification done this way still caught five errors, including an off-by-one in a total and a wrong divergence point that would have sent a reviewer to the wrong row.
6. **What the pass caught, in the report to the user**, because that is part of the deliverable's credibility. Keep the reference figure: 26 errors across two documents that had already been written carefully.
7. **The detection half of the run-attribution failure**: check every figure against the run it names, because a figure that was true of a different run is the most common error this pass catches.
8. **The standalone contract**:
   - *Needs:* a document, the source tree it cites, and the run folders.
   - *If that is missing:* with no run folders, quantitative claims cannot be re-derived — verify citations and internal consistency, and state the limitation at the top of the error list rather than presenting a partial pass as a complete one. With no source tree, the pass cannot run at all; say so instead of checking the document against itself.
   - *Hands back:* the path to `evidence/04-verification-<book>.md`.

- [ ] **Step 5: Run the validator**

Run: `python tools/validate_skills.py`
Expected: `ok check-the-facts`, exit 0. This also confirms the body's citations of `scripts/citation_check.py` and `tests/test_citation_check.py` resolve — the dangling-reference check earns its place here.

- [ ] **Step 6: Read the skill and agent against the eval assertions**

Confirm all 17 assertions are satisfiable. Eval 3's "Does not claim equivalence with a delegated pass" matters: the source is careful that the fallback is worse than delegation, and the skill must not flatten that into "either is fine".

- [ ] **Step 7: Run the full suite**

Run: `python -m pytest -q && python tools/validate_skills.py`
Expected: all tests pass; five skills `ok`.

- [ ] **Step 8: Commit**

```bash
git add skills/check-the-facts/SKILL.md skills/check-the-facts/evals agents/fact-checker.md
git commit -m "$(cat <<'EOF'
Add check-the-facts and the fact-checker agent

The instruction not to praise what checks out moves into the agent's system
prompt, where it survives a long task rather than competing with default
helpfulness each time a caller restates it.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 8: `review-the-tool`, the orchestrator

**Files:**
- Create: `skills/review-the-tool/SKILL.md`
- Create: `skills/review-the-tool/evals/evals.json`

**Interfaces:**
- Consumes: the five phase skills by exact name — `establish-the-truth`, `map-the-code`, `hunt-the-findings`, `write-the-books`, `check-the-facts` — and the two agents by name.
- Produces: the `evidence/` skeleton. Writes no deliverable itself; `write-the-books` owns the project record so that a `document`-mode run reached without the orchestrator still produces one.

Written last, deliberately: it names every other skill, and writing it after them means the names are settled facts rather than intentions.

- [ ] **Step 1: Write the evals first**

Create `skills/review-the-tool/evals/evals.json`:

```json
{
  "skill_name": "review-the-tool",
  "evals": [
    {
      "id": 1,
      "prompt": "We built a conversion tool with a lot of AI help and it's about to feed a client's opening balances. Can we rely on it?",
      "expected_output": "Should infer review mode and say so before starting, naming what it will and will not produce. Should classify the artifact as deterministic code and dispatch the registered path. Should run the phases in order: establish-the-truth, map-the-code, hunt-the-findings, write-the-books, check-the-facts. Should state the doctrine that a figure you did not produce by executing something is not evidence. Should separate what the tool attests from what it detects. Should create the evidence folder skeleton before phase 1.",
      "assertions": [
        "Infers review mode and states it before starting phase 1",
        "Names what the run will and will not produce",
        "Classifies the artifact by inspection rather than asking the user to",
        "Dispatches the five phase skills in order",
        "Quotes the doctrine verbatim",
        "Separates what the tool attests from what it detects",
        "Creates the evidence folder skeleton first",
        "Does not write the project record itself"
      ],
      "files": []
    },
    {
      "id": 2,
      "prompt": "Just document what this script does — I'm not signing off on anything, I need to hand it to a new hire.",
      "expected_output": "Should infer document mode and state it, along with what it will not produce: no checklist, no findings hunt, no assurance conclusion. Should still execute the tool where possible, because a documentation claim about an edge case is worth more when it can say verified. Should run establish-the-truth and map-the-code, then write-the-books limited to the code review. Should require the finished document to state on page one that it is documentation and not assurance.",
      "assertions": [
        "Infers document mode and states it",
        "Names what document mode will not produce",
        "Still executes the tool where possible and says why",
        "Runs only establish-the-truth, map-the-code, and write-the-books",
        "Requires the documentation-not-assurance statement on page one",
        "Produces no assurance language"
      ],
      "files": []
    },
    {
      "id": 3,
      "prompt": "Review this allocation model for me — it's an Excel workbook with about forty tabs of formulas.",
      "expected_output": "Should classify the artifact as a spreadsheet, find no registered path for it, say so plainly, and stop. Should explain why it will not force the code path: a spreadsheet forced through a code-shaped review produces a confident and badly wrong document, which is the failure this plugin exists to catch. Should say what a spreadsheet path would need — cell-level citation rather than line-level, formula dependency tracing, hardcode detection — and offer what it can legitimately do instead.",
      "assertions": [
        "Classifies the artifact as a spreadsheet",
        "Reports that no registered path exists and stops",
        "Refuses to force the deterministic-code path",
        "Explains why forcing it would be worse than declining",
        "Says what a spreadsheet path would require",
        "Offers a legitimate alternative rather than only refusing"
      ],
      "files": []
    }
  ]
}
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python tools/validate_skills.py`
Expected: exit 1, `review-the-tool: SKILL.md is missing`.

- [ ] **Step 3: Write the skill**

Create `skills/review-the-tool/SKILL.md`, frontmatter description verbatim — this is the only wide-net description in the plugin:

```markdown
---
name: review-the-tool
description: "Produce a human review checklist and a function-level code review for any tool whose output a firm has to stand behind, with every figure verified by executing the tool rather than reading its documentation. Use whenever the user asks to review, validate, document, sign off on, get comfortable with, or hand to a reviewer any script, model, macro, conversion utility, calculator, allocation engine, ETL job, migration tool, or reporting pipeline that produces client deliverables or feeds financial statements. Trigger on 'review this tool', 'can we rely on this', 'document what this code does', 'build a review checklist', 'what should a human check', 'the auditors will ask', 'workpaper for this script', or 'validate this conversion'. Also trigger proactively when someone is about to ship output from a tool nobody has independently reviewed."
---
```

Body, from `$SRC/SKILL.md:6-23` plus the new orchestration material:

1. **The two books**, and that they are written together because they need each other.
2. **The idea that makes this worth doing**, carried over close to verbatim — most tools that produce financial deliverables have some self-checking built in, and the single most useful thing this review does is separate what the tool attests from what the tool detects. Keep the three examples: passing 347 of its own assertions while shipping a file that fails on load; printing a zero-variance reconciliation from an arithmetic identity that cannot return any other number; declaring a control blocking in documentation while the code makes it a warning. Keep the sentence that none of this is dishonesty — it is what happens when checks are written by the same mind that wrote the thing being checked.
3. **The doctrine**, quoted verbatim, and its corollary that the changelog's figure, the README's, the code comment's and the previous reviewer's are all claims to be tested.
4. **Mode selection**, per spec §5.1: infer from the request — document, explain or write a reference means `document`; check, verify or fact-check an existing document means `verify`; relying on, signing off or handing on output means `review`. State the inferred mode and what it will and will not produce before starting phase 1. Ask only where the request genuinely reads both ways, and resolve ambiguity toward `review`, because inferring `document` when the caller wanted assurance is the costly direction.
5. **The mode table**, with the phases each runs.
6. **Artifact classification and the path registry**, per spec §8: inspect the artifact — extensions, entry points, whether execution is deterministic — and match against the registry. Do not ask the user to classify it; ask when inspection is genuinely ambiguous. Reproduce the four-row registry with three rows marked *not in this release*, and state the rule: if the artifact does not match a registered path, say so and stop, because a spreadsheet forced through a code-shaped review produces a confident and badly wrong document, which is the failure this plugin exists to catch. Say what the missing path would need, and offer what can legitimately be done instead.
7. **The phase sequence**, naming each skill and what it hands back, and the `evidence/` skeleton the orchestrator creates first.
8. **What this skill does not do**: it does not write the project record — `write-the-books` owns that, so a `document`-mode run reached without the orchestrator still produces one.

- [ ] **Step 4: Run the validator**

Run: `python tools/validate_skills.py`
Expected: all six skills `ok`, exit 0.

- [ ] **Step 5: Read the skill against the eval assertions**

Confirm all 20 assertions are satisfiable. Eval 3 is the most important in the plugin — it asserts the refusal behaviour, and a model that reads this skill and then forces a spreadsheet through `map-the-code` has defeated the design. If the refusal is not unmistakable in the text, make it more direct.

- [ ] **Step 6: Verify every skill and agent the orchestrator cites exists**

```bash
for n in establish-the-truth map-the-code hunt-the-findings write-the-books check-the-facts; do
  test -f "skills/$n/SKILL.md" && echo "ok   skill $n" || echo "MISSING skill $n"
done
for a in code-mapper fact-checker; do
  test -f "agents/$a.md" && echo "ok   agent $a" || echo "MISSING agent $a"
done
grep -c "not in this release" skills/review-the-tool/SKILL.md
```

Expected: seven `ok` lines and a count of at least 3 for the unregistered paths.

- [ ] **Step 7: Commit**

```bash
git add skills/review-the-tool
git commit -m "$(cat <<'EOF'
Add review-the-tool, the orchestrator

Written last so the five skill names it dispatches are settled facts. Carries
the doctrine, the attestation-versus-detection idea, mode inference, and the
path registry whose one entry means three of four artifact types are declined
out loud rather than forced through a review shaped for something else.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 9: The command and the open-source documentation

**Files:**
- Create: `commands/review.md`
- Create: `README.md`
- Create: `LICENSE`
- Create: `CONTRIBUTING.md`

**Interfaces:**
- Consumes: all six skills by name; `plugin.json` for the version.
- Produces: `/tully:review [path] [--mode document|review|verify]`.

- [ ] **Step 1: Write the command**

Create `commands/review.md`:

```markdown
---
description: Review a tool whose output a firm has to stand behind — execute it, document it, hunt its defects, write the checklist and the code review, then fact-check both.
argument-hint: "[path-to-tool] [--mode document|review|verify]"
---

Invoke the `review-the-tool` skill for the target below.

Target: $1
Mode: $2 (omit to let the skill infer it from the request)

If no target is given, ask for one before starting — do not review the current
working directory by assumption, because staging the wrong tree wastes an hour
of execution.
```

Named `review.md` rather than `review-the-tool.md` so `/tully:review` and the skill `tully:review-the-tool` cannot be mistaken for each other in a transcript.

- [ ] **Step 2: Write the licence**

Create `LICENSE`: the standard MIT licence text, copyright year 2026. Leave the copyright holder as the repository owner's name, to be filled at the publication gate — the repo is not published as any firm's work product.

- [ ] **Step 3: Write the README**

Create `README.md`. It must contain, in this order:

1. **What it is**, in two sentences: six skills for reviewing a tool whose output a firm has to stand behind, including one an AI designed. Every figure in the output is verified by executing the tool rather than by reading its documentation.
2. **The plain statement**, before anything else substantive: *the output is an internal working paper supporting a preparer and a reviewer. It is not an attest report, and nothing here constitutes an audit, review, or agreed-upon-procedures engagement under professional standards.*
3. **Why "tully"** — Louis Tully, the Ghostbusters' accountant, who itemises a party as a promotional expense and invites clients instead of friends. An accountant whose defining trait is substantiation, which is the doctrine of the plugin: a figure you did not produce by executing something is not evidence. Keep it to three sentences; the joke works once.
4. **Install**: `/plugin marketplace add <owner>/tully` then `/plugin install tully`. Mark the owner placeholder clearly as unresolved until the repo is published.
5. **The six skills**, as a table of name and one line each, in phase order.
6. **The three modes**, as a table of mode, phases run, and output.
7. **What it does not cover**: the path registry has one entry. Spreadsheets and models, workflows where an LLM runs at runtime, processes with human steps, and AI-written memos and technical positions each need their own path and do not have one yet. The plugin declines them rather than forcing the code path, and the reason is stated.
8. **A worked example** pointing at `examples/worked-engagement/`.
9. **Contributing**, pointing at `CONTRIBUTING.md`.

- [ ] **Step 4: Write CONTRIBUTING**

Create `CONTRIBUTING.md`, covering the two extension points that matter:

1. **Adding a finding pattern.** Each entry in `references/finding-patterns.md` gives the shape, how to test for it, and why it matters to a reader — in that order. A pattern without a test is an opinion. State the requirement that a submitted pattern names a way to establish its presence by execution or by comparison of two artifacts, not by reading one function.
2. **Adding an artifact path.** The extension seam: a new row in the orchestrator's registry, an evidence skill, a mapping skill, and a catalogue. State what a path must supply — what counts as evidence for that artifact type, what the citation format is, and what the degraded mode is when evidence cannot be obtained. Note honestly that the seam is designed but untested, so the first added path should expect to adjust its shape.
3. **Running the checks**: `python tools/validate_skills.py` and `python -m pytest -q`, both green before a pull request.
4. **The confidentiality rule**: no contribution may include client-derived content, and reviewers should assume a mechanical grep is insufficient.

- [ ] **Step 5: Verify the checks still pass**

Run: `python tools/validate_skills.py && python -m pytest -q`
Expected: six skills `ok`; all tests pass.

- [ ] **Step 6: Commit**

```bash
git add commands README.md LICENSE CONTRIBUTING.md
git commit -m "$(cat <<'EOF'
Add the /tully:review command and open-source documentation

README leads with the statement that output is an internal working paper and
not an attest report, before anything else substantive. CONTRIBUTING documents
the two extension points: a finding pattern must name a way to establish its
presence, and an artifact path must declare its evidence, citation format, and
degraded mode.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 10: The worked example and the publication gate handoff

**Files:**
- Create: `examples/worked-engagement/README.md`
- Create: `examples/worked-engagement/01-evidence-base.md`
- Create: `examples/worked-engagement/checklist-excerpt.md`
- Create: `examples/worked-engagement/code-review-excerpt.md`
- Modify: `docs/anonymisation-review-aid.md` (git-ignored)

**Interfaces:**
- Consumes: all six skills' output contracts.
- Produces: nothing other skills depend on. This is documentation.

The example is entirely synthetic — a fictional conversion from **Ledgerline Fund Accounting** to **Aurora ERP**, with invented figures. It is not a redacted real engagement, and it says so, because a reader who mistakes it for one will draw conclusions from its numbers.

- [ ] **Step 1: Write the example README**

Create `examples/worked-engagement/README.md` stating: this is a synthetic example showing the shape of each artifact, not a redacted real engagement; every figure is invented; the tool and both systems are fictional. Then a short table of the files and what each demonstrates.

- [ ] **Step 2: Write the filled evidence base**

Create `examples/worked-engagement/01-evidence-base.md`, following `skills/establish-the-truth/references/evidence-base.md` exactly: header block with `EXECUTED: yes`, an inputs table, two `RUN` sections with different `SETTINGS` and a `FIGURES` table each where every "How measured" cell is an operation, and two or three unreconciled observations.

The two runs must differ in a way that produces different figures, so the example demonstrates why one run is an anecdote.

- [ ] **Step 3: Write the checklist excerpt**

Create `examples/worked-engagement/checklist-excerpt.md`: the section-1 header, and three complete tests following the template in `skills/write-the-books/references/checklist-book.md` — one rated `[T-INDEP]`, one `[T-WEAK]`, one `[NONE]`. Each carries its reference figure attributed to a named run from Step 2.

The `[T-WEAK]` test must explain the mechanism that makes the control weak, not merely assert it, since the reference file is explicit that a reviewer who understands why a green light is empty can predict the next instance while one told only to distrust it cannot. Include one row of the PART F findings register and the working-paper statement.

- [ ] **Step 4: Write the code review excerpt**

Create `examples/worked-engagement/code-review-excerpt.md`: a §1 purpose-and-method naming the two runs as the evidence base, four rows of the execution spine with population figures traceable to Step 2, two complete per-function entries following `references/function-entry.md` with all four labels and citation density at roughly one per 50 words, and one control-inventory row whose "what it would fail to catch" cell is filled.

- [ ] **Step 5: Verify the example is internally consistent**

Every figure in Steps 3 and 4 must appear in Step 2's evidence base under the run it names. Check:

```bash
grep -ohE "RUN [A-Za-z0-9-]+" examples/worked-engagement/*.md | sort -u
```

Every run identifier appearing in the excerpts must appear in `01-evidence-base.md`. A worked example that quotes a figure from a run it does not define demonstrates the exact error the plugin's verification pass exists to catch.

- [ ] **Step 6: Complete the review aid**

Append to `docs/anonymisation-review-aid.md` a final section confirming which files in the repo are synthetic (everything under `examples/`) versus anonymised-from-real (the three files in the Global Constraints table), so the author's review knows which is which.

Confirm the aid is still ignored:

```bash
git check-ignore -v docs/anonymisation-review-aid.md
```

Expected: a line showing the matching `.gitignore` rule. **If this reports nothing, stop.**

- [ ] **Step 7: Run every check**

```bash
python tools/validate_skills.py
python -m pytest -q

# Pre-publication leak check, run locally only. The pattern list comes from the
# git-ignored aid so no original value is ever written into a tracked file.
awk -F'|' '/^\|/ && NF>2 {gsub(/^ +| +$/,"",$2); if ($2 != "" && $2 !~ /original/) print $2}' \
  docs/anonymisation-review-aid.md > /tmp/tully-originals.txt
wc -l < /tmp/tully-originals.txt   # expect 9 or more; 0 means the aid is empty and the check is vacuous
grep -rInFf /tmp/tully-originals.txt --exclude-dir=.git . && echo "LEAK" || echo "no client identifiers found"
rm -f /tmp/tully-originals.txt

git log --all --oneline | wc -l
git status --short
git remote -v
```

Expected: six skills `ok`; all tests pass; a non-zero pattern count followed by `no client identifiers found`; a clean working tree; **no remotes**.

The `wc -l` guard matters: a leak check whose pattern file is empty passes trivially and reports the same reassuring output as one that genuinely found nothing. That is the "check that cannot fail" pattern from the plugin's own catalogue, and it would be an embarrassing place to commit it.

- [ ] **Step 8: Commit**

```bash
git add examples
git commit -m "$(cat <<'EOF'
Add a synthetic worked engagement

Entirely invented figures from a fictional conversion, stated as such so no
reader mistakes it for a redacted real engagement. Every figure in the excerpts
traces to a run defined in the example evidence base, since an example that
quotes an undefined run demonstrates the error the verification pass exists to
catch.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 9: Hand off to the publication gate — do not push**

Report to the author, and stop:

1. The repo is complete and local, with no remote configured.
2. `docs/anonymisation-review-aid.md` is ready for review and lists every substitution plus the items flagged for their judgement.
3. The three files anonymised from real material, and the fact that everything under `examples/` is synthetic.
4. What the mechanical grep covered, and the spec's own caveat that it only catches values someone thought to search for.
5. That `plugin.json` still lacks `author`, `homepage` and `repository`, and `LICENSE` lacks a copyright holder, all pending the gate.

**Adding a remote, creating a repository, and pushing are the author's to perform or explicitly authorise.** Spec D11.

---

## Self-Review

**1. Spec coverage.** Walking the spec section by section:

| Spec | Task |
|---|---|
| §4 repo layout | 1 (manifests, CI), and every task creating its own files |
| §5.1 `review-the-tool`, mode selection, classification | 8 |
| §5.2 `establish-the-truth` | 3 |
| §5.3 `map-the-code` | 4 |
| §5.4 `hunt-the-findings` | 5 |
| §5.5 `write-the-books` | 6 |
| §5.6 `check-the-facts` | 7 |
| §6 modes | 8 (table and inference), 6 (document-mode degradation) |
| §7 `evidence/` folder | 3 defines the contract; 4–7 consume it |
| §8 path registry and the refusal rule | 8, with eval 3 asserting refusal |
| §9 agents | 4 (`code-mapper`), 7 (`fact-checker`) |
| §10 command | 9 |
| §11 migration map, warnings split by owner | 3 (run attribution, prevention), 5 (absent evidence file), 6 (three warnings), 7 (run attribution, detection) |
| §12 new content, all nine items | 1 (validator), 3 (evidence-base ref, degraded modes), 4 (function-entry ref, agent), 7 (agent), 9 (command, docs), 2 (script tests), all tasks (descriptions, evals) |
| §13 anonymisation, affected files, publication gate | 2 (script), 5 (catalogue, review aid), 6 (code-review ref), 10 (gate handoff) |
| §14 verification plan | 1 (validator, CI), 2 (script tests), 3–8 (three evals each: canonical, trigger, degraded) |
| §15 packaging | 1 (manifests), 9 (README, LICENSE, CONTRIBUTING), 10 (example) |
| §16 known gaps | 9 (README item 7 states the one-entry registry), CONTRIBUTING (untested seam) |

No gaps found. Spec §14's requirement of "one end-to-end eval on `review-the-tool` asserting the phase sequence and that a `document`-mode run produces no assurance language" is satisfied by Task 8 evals 1 and 2 rather than a separate file, which the spec allows since it specifies the assertion and not the location.

**2. Placeholder scan.** No "TBD", "TODO", "implement later", "add appropriate error handling", or "similar to Task N". Three deliberate deferrals are named as such with the reason and the gate that resolves them: `plugin.json`'s `author`/`homepage`/`repository`, the `LICENSE` copyright holder, and the README's install-command owner placeholder — all pending the publication gate, and all listed in Task 10 Step 9 so they are not forgotten.

**3. Type and name consistency.** Checked across tasks:

- Skill directory names match frontmatter `name` in every task, and match the names Task 8 dispatches.
- `evidence/01-evidence-base.md`, `02-execution-spine.md`, `02-map-<layer>.md`, `03-findings.md`, `04-verification-<book>.md` are spelled identically in Tasks 3–8 and in spec §7.
- Evidence-base field names — `TOOL`, `VERSION`, `STAGED-AT`, `EXECUTED`, `REASON-NOT-EXECUTED`, `OWN-TEST-SUITE`, `RUN`, `SETTINGS`, `PATH`, `FIGURES` — are defined once in Task 3 Step 3 and referenced with the same spelling in Tasks 4, 6, 7 and 10.
- `validate_skills.py` is invoked as `python tools/validate_skills.py` with the optional `--skills-dir`, consistently in Tasks 1–10 and in CI.
- `citation_check.py` lives at `skills/check-the-facts/scripts/citation_check.py` per Task 2 and is referenced from the skill body in Task 7 as `scripts/citation_check.py`, which is correct because the validator resolves reference paths relative to the skill directory.
- Agent names `code-mapper` and `fact-checker` match their filenames and the names Tasks 4, 7 and 8 use.
- The `[T-INDEP]` / `[T-WEAK]` / `[NONE]` rating vocabulary is used identically in Task 6 and Task 10.

Two issues found and fixed while reviewing:

- Task 7 Step 2's expected validator output originally said only `SKILL.md is missing`, but `check-the-facts` already exists as a directory from Task 2 without `evals/`, so the validator reports two problems before Step 1 and one after. Step 2 now says so.
- The validator's body-extraction line originally read `text[...] if fm else text`, which is dead code — the function has already returned when `fm` is None. Simplified to the unconditional slice.

**4. Confidentiality of the plan itself.** This check is not in the writing-plans template and was added because the first draft of this plan failed it.

The first draft carried a substitution table listing every original client value, and a CI step that grepped for those values. Both would have been committed and published — the plan into `docs/plans/`, the grep into `.github/workflows/`. A plan that publishes the values its own anonymisation removes defeats the anonymisation entirely, and **a grep for a secret publishes the secret.** Three consequences, now applied throughout:

- The plan states replacements only. Originals are read from `$SRC` at named line numbers, and catalogued in the git-ignored aid.
- The aid is created in Task 1 Step 8, before its first use in Task 2, and accumulates rows as substitutions are made.
- CI asserts the invariant that protects the values — that the aid is untracked — rather than grepping for them. The leak check runs locally, builds its pattern list from the aid, and guards against an empty pattern file, since a leak check with no patterns passes trivially and prints the same output as one that genuinely found nothing.

That last point is the plugin's own "checks that cannot fail" pattern, caught in the plan for the plugin that catalogues it.
