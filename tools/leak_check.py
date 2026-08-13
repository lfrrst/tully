#!/usr/bin/env python3
"""Search a tree for original client values listed in the anonymisation review aid.

Insensitive to whitespace, line-leading markup, and case — each because a
line-based search fails open, and a gate on an unrecoverable rule must fail shut.
Prose and comments here are hard-wrapped, so a value can straddle a newline, and
the continuation line usually carries a prefix (`# `, `> `, `- `). Collapsing
whitespace alone is not enough: the prefix lands inside the joined text and the
value stops matching. This project's one real leak lived in a hash-prefixed
fixture comment, which is why that case has its own test.

    python tools/leak_check.py --aid docs/anonymisation-review-aid.md skills docs

Exit codes:
    0  every pattern checked against at least one file, nothing matched
    1  something matched
    2  the check proved nothing, and saying "clean" would be a lie — a missing aid,
       an aid with no value table or no patterns in it, a target that does not exist,
       no files under the targets, or only the aid in scope

The aid is never scanned: it holds every original by definition. The output states
how many files were scanned, because the pattern count alone cannot show that
anything was read.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".superpowers", ".venv", "node_modules"}

# An allow-list of text suffixes fails open: a value in a .csv or .html goes unseen
# and the gate still says clean. Skip only what cannot hold readable text.
BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".pdf", ".zip", ".gz", ".tar",
    ".7z", ".xls", ".xlsx", ".xlsm", ".doc", ".docx", ".ppt", ".pptx", ".so", ".dll",
    ".exe", ".pyc", ".whl", ".woff", ".woff2", ".ttf", ".otf", ".mp3", ".mp4", ".jar",
}


def patterns_from_aid(aid: Path) -> list[str]:
    """First column of every data row of the aid's value table, and of no other table.

    Scoped to the table whose header row's first cell begins "Original" — the real
    aid's reads "Original value" — because the aid is hand-edited and grows other
    tables: a summary, a substitution count, a table of what was carried over. Every
    markdown row's first cell used to become a pattern, so any second table injected
    its own first column into the gate. A row whose first cell reads `the` matches
    every file in the tree: the gate goes red having found nothing, and the pattern
    count — the one number designated as proof that the gate is not vacuous — is
    inflated past the number of real values, which is the signal destroyed.

    `startswith`, not `==`, on the header. A table ends at the first blank line after
    it, or at the first line that is not a table row; rows outside a value table are
    ignored. If the aid holds no such table, no patterns are returned and the caller
    exits 2 rather than reporting clean.
    """
    out: list[str] = []
    in_value_table = False
    for line in aid.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("|"):
            in_value_table = False        # a blank line or prose ends the table
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            in_value_table = False
            continue
        first = cells[0]
        if first.lower().startswith("original"):
            in_value_table = True         # the value table's header row
            continue
        if not in_value_table:
            continue                      # a row belonging to some other table
        if not first or set(first) <= set("-: "):
            continue                      # the separator row, or an empty first cell
        out.append(first)
    return out


def flatten(raw: str, strip_markup: bool) -> tuple[str, list[int]]:
    """Collapse the text to single-spaced form, tracking the source line per character.

    With strip_markup, a run of comment, quote or list markers at the start of a
    line is dropped first, so a value wrapped across `# ` or `> ` prefixed lines
    still reads as continuous text. Without it, such a prefix would sit inside the
    joined string and the value would not match.
    """
    out: list[str] = []
    line_of: list[int] = []
    for line_no, line in enumerate(raw.split("\n"), 1):
        body = re.sub(r"^[ \t]*[>#|*+\-]+[ \t]*", "", line) if strip_markup else line
        for ch in body:
            if ch in " \t":
                if out and out[-1] != " ":
                    out.append(" ")
                    line_of.append(line_no)
            else:
                out.append(ch)
                line_of.append(line_no)
        if out and out[-1] != " ":       # a line break behaves as a space
            out.append(" ")
            line_of.append(line_no)
    return "".join(out), line_of


def iter_files(targets: list[Path]):
    """Yield every candidate file, and report any target that does not exist."""
    missing: list[Path] = []
    found: list[Path] = []
    for t in targets:
        if t.is_file():
            found.append(t)
        elif t.is_dir():
            for p in sorted(t.rglob("*")):
                if p.is_file() and not (SKIP_DIRS & set(p.parts)) \
                        and p.suffix.lower() not in BINARY_SUFFIXES:
                    found.append(p)
        else:
            missing.append(t)
    return found, missing


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--aid", required=True)
    ap.add_argument("targets", nargs="+")
    args = ap.parse_args()

    aid = Path(args.aid)
    if not aid.is_file():
        print(f"no such aid file: {aid}", file=sys.stderr)
        return 2
    pats = patterns_from_aid(aid)
    if not pats:
        print("no patterns in the aid: the check would pass trivially", file=sys.stderr)
        return 2

    considered, missing = iter_files([Path(t) for t in args.targets])
    if missing:
        for m in missing:
            print(f"no such target: {m}", file=sys.stderr)
        return 2
    if not considered:
        print("no files under the given targets: the check proved nothing",
              file=sys.stderr)
        return 2

    aid_resolved = aid.resolve()
    scanned = 0
    hits = []
    for f in considered:
        if f.resolve() == aid_resolved:
            continue                      # holds every original by definition
        scanned += 1
        raw = f.read_text(encoding="utf-8", errors="replace")
        views = (flatten(raw, False), flatten(raw, True))
        for pat in pats:
            npat = " ".join(pat.split()).casefold()
            if not npat:
                continue
            for hay, line_of in views:
                idx = hay.casefold().find(npat)
                if idx != -1:
                    hits.append((f, line_of[idx], pat))
                    break                 # one report per pattern per file

    if not scanned:
        print("only the aid was in scope: the check proved nothing", file=sys.stderr)
        return 2

    print(f"{len(pats)} patterns checked against {scanned} files "
          f"(the aid itself is never scanned)")
    if not hits:
        print("clean")
        return 0
    print("first occurrence per pattern per file only — treat as a gate, "
          "not a cleanup inventory")
    for f, line_no, pat in hits:
        print(f"  LEAK  {f}:{line_no}  matches {pat!r}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
