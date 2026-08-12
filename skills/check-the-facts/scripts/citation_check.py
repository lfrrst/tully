#!/usr/bin/env python3
"""Check `file.ext:NNN` line citations in a review document against the source tree.

A function-level code review carries hundreds of line citations, and they rot the
moment anyone edits the code. This resolves every one of them mechanically so the
verification pass can spend its attention on whether the cited line actually
supports the claim, rather than on whether the line exists.

    python citation_check.py BOOK.md --root /path/to/source
    python citation_check.py BOOK.md --root SRC --sample 40        # print context to eyeball
    python citation_check.py BOOK.md --root SRC --only-findings    # citations near a finding word
    python citation_check.py BOOK.md --root SRC --json out.json

Exit code is 1 if any citation fails to resolve, so it can gate a build.

What it catches: dead files, out-of-range lines, and (with --sample) citations that
resolve to a blank line or a line that is obviously not what the sentence describes.
What it cannot catch: a citation that resolves to a real line that says something
else. That still needs a reader — which is the point of --sample.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# file.ext:NNN or file.ext:NNN-MMM, optionally with a directory prefix.
# Requires a dot-extension so that "note:12" or "C01:Aurora.Segment" don't match.
CITE = re.compile(
    r"(?<![\w/.])"                       # not mid-identifier
    r"((?:[\w.-]+/)*[\w.-]+\.[A-Za-z][\w]*)"   # path with extension
    r":(\d+)"                             # first line
    r"(?:\s*[-–]\s*(\d+))?"               # optional end line
)

FINDING_WORDS = (
    "verified", "finding", "defect", "cannot fail", "wrong", "contradic", "stale",
    "false", "silently", "raises", "blind", "never", "does not", "unguarded",
)


def find_source(root: Path, cited: str, cache: dict) -> Path | None:
    """Resolve a cited path against the source tree.

    Citations are written the way a reader says them ("pipeline.py:168",
    "converter/fund.py:322"), not as full paths, so match on suffix and fall back
    to basename. An ambiguous basename is reported rather than guessed.
    """
    if cited in cache:
        return cache[cited]
    hit = None
    direct = root / cited
    if direct.is_file():
        hit = direct
    else:
        name = Path(cited).name
        matches = [p for p in root.rglob(name) if p.is_file()]
        # prefer a match whose tail equals the whole cited path
        tail = [p for p in matches if str(p).replace("\\", "/").endswith(cited)]
        pool = tail or matches
        if len(pool) == 1:
            hit = pool[0]
        elif len(pool) > 1:
            hit = "AMBIGUOUS"  # type: ignore[assignment]
    cache[cited] = hit
    return hit


def line_of(doc_lines: list[str], pos: int, offsets: list[int]) -> int:
    lo, hi = 0, len(offsets) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if offsets[mid] <= pos:
            lo = mid
        else:
            hi = mid - 1
    return lo + 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("document", help="the review .md file")
    ap.add_argument("--root", required=True, help="root of the source tree being cited")
    ap.add_argument("--sample", type=int, default=0,
                    help="print this many resolved citations with their source line, "
                         "spread evenly through the document, for a human to eyeball")
    ap.add_argument("--only-findings", action="store_true",
                    help="restrict the sample to citations sitting near finding language "
                         "— these are the ones worth a reader's time")
    ap.add_argument("--json", dest="json_out", help="write the full result as JSON")
    args = ap.parse_args()

    doc = Path(args.document)
    root = Path(args.root)
    if not doc.is_file():
        print(f"no such document: {doc}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"no such source root: {root}", file=sys.stderr)
        return 2

    text = doc.read_text(encoding="utf-8", errors="replace")
    doc_lines = text.split("\n")
    offsets, acc = [0], 0
    for l in doc_lines:
        acc += len(l) + 1
        offsets.append(acc)

    cache: dict = {}
    results = []
    for m in CITE.finditer(text):
        cited, start, end = m.group(1), int(m.group(2)), m.group(3)
        end = int(end) if end else start
        docline = line_of(doc_lines, m.start(), offsets)
        context = doc_lines[docline - 1]
        rec = {
            "citation": m.group(0),
            "cited_path": cited,
            "start": start,
            "end": end,
            "doc_line": docline,
            "near_finding": any(w in context.lower() for w in FINDING_WORDS),
        }
        src = find_source(root, cited, cache)
        if src is None:
            rec.update(status="FILE NOT FOUND", resolved=None)
        elif src == "AMBIGUOUS":
            rec.update(status="AMBIGUOUS PATH", resolved=None)
        else:
            rec["resolved"] = str(src)
            try:
                src_lines = src.read_text(encoding="utf-8", errors="replace").split("\n")
            except OSError as e:
                rec.update(status=f"UNREADABLE ({e.__class__.__name__})")
                results.append(rec)
                continue
            n = len(src_lines)
            if start < 1 or end > n:
                rec.update(status="LINE OUT OF RANGE", file_lines=n)
            else:
                body = src_lines[start - 1].strip()
                rec.update(status="ok", source_text=body,
                           # only meaningful for a single-line citation; a range
                           # legitimately starts on the blank line above a block
                           blank_target=(not body) and start == end)
        results.append(rec)

    bad = [r for r in results if r["status"] != "ok"]
    blank = [r for r in results if r.get("blank_target")]
    files = sorted({r["cited_path"] for r in results})

    print(f"{doc.name}: {len(results)} citations across {len(files)} cited files")
    print(f"  resolved : {len(results) - len(bad)}")
    print(f"  problems : {len(bad)}")
    if blank:
        print(f"  resolve to a blank line: {len(blank)}  (usually an off-by-one)")

    if bad:
        print("\nPROBLEMS")
        for r in bad:
            print(f"  doc line {r['doc_line']:>6}  {r['citation']:<34} {r['status']}"
                  + (f"  (file has {r['file_lines']} lines)" if "file_lines" in r else ""))

    if args.sample:
        pool = [r for r in results if r["status"] == "ok"]
        if args.only_findings:
            pool = [r for r in pool if r["near_finding"]]
        step = max(1, len(pool) // args.sample) if pool else 1
        chosen = pool[::step][:args.sample]
        label = "finding-adjacent " if args.only_findings else ""
        print(f"\nSAMPLE — {len(chosen)} {label}citations, with the line they resolve to.")
        print("Read the claim at the document line and ask whether this source line supports it.\n")
        for r in chosen:
            print(f"  doc {r['doc_line']:>6}  {r['citation']}")
            print(f"      -> {r['source_text'][:150]}")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(results, indent=1))
        print(f"\nwrote {args.json_out}")

    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
