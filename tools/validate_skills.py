#!/usr/bin/env python3
"""Validate the structure of every skill under skills/.

Checks what CI can check mechanically: frontmatter present and consistent with
the directory, a description within bounds, no dangling reference paths, and an
evals file that parses and belongs to this skill.

It does NOT grade eval content. That requires running the skill against its
prompts and is a human or LLM-judge activity.

    python tools/validate_skills.py
    python tools/validate_skills.py --skills-dir some/other/dir

Exit codes:
    0  every skill checked, none failed
    1  at least one failed, so it can gate a build
    2  the check proved nothing — the skills directory does not exist, or it exists
       and holds no skill. "0 problems" over nothing is not a pass.
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
    if not dirs:
        # An existing-but-empty skills directory reported "0 skills checked, 0
        # problems" and exited 0. CI runs this with the default directory, so that
        # is a green build over nothing checked.
        print("no skills found: the check proved nothing", file=sys.stderr)
        return 2

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
