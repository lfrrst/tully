#!/usr/bin/env python3
"""Search a tree for original client values listed in the anonymisation review aid.

Whitespace-insensitive by design. Markdown is hard-wrapped, so an original value
can straddle a newline in the anonymised prose; a line-based search would report
clean on a file that still contains it. Both the patterns and the file contents
are collapsed to single-spaced text before matching, and the reported line number
is the line the match starts on.

    python tools/leak_check.py --aid docs/anonymisation-review-aid.md skills docs

Exit 0 clean, 1 if anything matched, 2 on a usage or empty-pattern-list error.
The aid file is never scanned: it contains every original by definition.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".superpowers", ".venv"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".yml", ".yaml", ".txt", ".toml", ".cfg", ""}


def patterns_from_aid(aid: Path) -> list[str]:
    """First column of every data row of the aid's markdown table."""
    out: list[str] = []
    for line in aid.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        first = cells[0]
        if not first or set(first) <= set("-: ") or first.lower() == "original":
            continue
        out.append(first)
    return out


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def iter_files(targets: list[Path], aid: Path):
    for t in targets:
        if t.is_file():
            yield t
        elif t.is_dir():
            for p in sorted(t.rglob("*")):
                if p.is_file() and not (SKIP_DIRS & set(p.parts)) \
                        and p.suffix.lower() in TEXT_SUFFIXES:
                    yield p


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

    aid_resolved = aid.resolve()
    hits = []
    for f in iter_files([Path(t) for t in args.targets], aid):
        if f.resolve() == aid_resolved:
            continue
        raw = f.read_text(encoding="utf-8", errors="replace")
        flat = normalise(raw)
        for pat in pats:
            npat = normalise(pat)
            if npat and npat in flat:
                # locate the line the match starts on, tolerating the wrap
                idx = flat.index(npat)
                prefix_words = flat[:idx].count(" ")
                line_no, seen = 1, 0
                for i, line in enumerate(raw.splitlines(), 1):
                    seen += len(normalise(line).split(" ")) if line.strip() else 0
                    if seen > prefix_words:
                        line_no = i
                        break
                hits.append((f, line_no, pat))

    print(f"{len(pats)} patterns checked against the tree")
    if not hits:
        print("clean")
        return 0
    for f, line_no, pat in hits:
        print(f"  LEAK  {f}:{line_no}  matches {pat!r}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
