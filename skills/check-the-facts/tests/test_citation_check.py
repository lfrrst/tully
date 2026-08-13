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


def test_blank_target_fails_the_run(tmp_path):
    # A single-line citation to a blank line resolves to nothing a reader can use,
    # so it is counted as a problem and gates the build. Reported as well as counted:
    # the summary line is what tells a human it is probably an off-by-one.
    src = tmp_path / "src"
    write(src / "mod.py", "first\n\nthird\n")
    doc = write(tmp_path / "book.md", "See `mod.py:2`.\n")
    r = run(doc, src)
    assert r.returncode == 1, r.stdout
    assert "resolve to a blank line: 1" in r.stdout
    assert "BLANK TARGET" in r.stdout
    assert "problems : 1" in r.stdout


def test_citation_one_past_the_last_content_line_fails(tmp_path):
    # The off-by-one this tool exists to catch: a trailing newline yields a phantom
    # empty line, so `mod.py:3` against a two-content-line file is in range and
    # resolves. Before blank targets entered the problem count this exited 0 — a
    # document whose every citation was off by one passed the gate.
    src = tmp_path / "src"
    write(src / "mod.py", "first\nsecond\n")
    doc = write(tmp_path / "book.md", "The stage runs at `mod.py:3`.\n")
    r = run(doc, src)
    assert r.returncode == 1, r.stdout
    assert "BLANK TARGET" in r.stdout


def test_range_citation_starting_on_blank_line_is_not_flagged(tmp_path):
    src = tmp_path / "src"
    write(src / "mod.py", "first\n\nthird\n")
    doc = write(tmp_path / "book.md", "See `mod.py:2-3`.\n")
    r = run(doc, src)
    assert r.returncode == 0, r.stdout
    assert "resolve to a blank line" not in r.stdout


def test_non_citations_are_not_matched(tmp_path):
    # The document carries one real citation as well as the two colon-forms that must
    # not match, so the run is non-vacuous: a tool that matched nothing at all would
    # now exit 2 rather than satisfy this test by finding nothing to complain about.
    # The count is asserted as a whole line — "1 citations" alone is a substring of
    # "11 citations" and could not tell one match from eleven.
    src = tmp_path / "src"
    write(src / "pipeline.py", "a\nb\n")
    doc = write(tmp_path / "book.md",
                'Ignore note:12 and "C01:Aurora.Segment" but catch `pipeline.py:1`.\n')
    out = tmp_path / "result.json"
    r = run(doc, src, "--json", str(out))
    assert r.returncode == 0, r.stdout
    assert "book.md: 1 citations across 1 cited files" in r.stdout
    # Name what did match, so the assertion fails if the wrong thing matched once.
    data = json.loads(out.read_text(encoding="utf-8"))
    assert [rec["citation"] for rec in data] == ["pipeline.py:1"]


def test_document_with_no_citations_exits_two(tmp_path):
    # A checklist book carries reference figures rather than code citations, and
    # `verify` mode runs against whatever document it is handed. Zero recognised
    # citations means the check proved nothing; reporting that as a pass would say
    # every citation resolved on a run that resolved none.
    src = tmp_path / "src"
    write(src / "pipeline.py", "a\nb\n")
    doc = write(tmp_path / "book.md",
                "Procedure 4: expect 1,204 rows against the reference run.\n"
                "Ignore note:12 and the segment key C01:Aurora.Segment.\n")
    r = run(doc, src)
    assert r.returncode == 2, r.stdout
    assert "no citations found: the check proved nothing" in r.stderr


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
    # The message is asserted, not only the code: a deleted script and any argparse
    # usage error also exit 2, so a bare code assertion passes with no tool present.
    src = tmp_path / "src"
    src.mkdir()
    r = run(tmp_path / "absent.md", src)
    assert r.returncode == 2
    assert "no such document" in r.stderr


def test_missing_root_exits_two(tmp_path):
    doc = write(tmp_path / "book.md", "See `mod.py:1`.\n")
    r = run(doc, tmp_path / "absent-root")
    assert r.returncode == 2
    assert "no such source root" in r.stderr
