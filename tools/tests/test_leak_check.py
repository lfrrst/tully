import re
import subprocess
import sys
from pathlib import Path

CHECKER = Path(__file__).resolve().parents[2] / "tools" / "leak_check.py"


def run(aid: Path, *targets):
    return subprocess.run([sys.executable, str(CHECKER), "--aid", str(aid), *map(str, targets)],
                          capture_output=True, text=True)


def write_aid(tmp_path: Path, rows) -> Path:
    lines = ["# aid", "", "| original | replacement | file | line |", "|---|---|---|---|"]
    lines += [f"| {o} | {r} | f.md | 1 |" for o, r in rows]
    p = tmp_path / "aid.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def test_clean_tree_exits_zero(tmp_path):
    aid = write_aid(tmp_path, [("SECRETVALUE", "PUBLICVALUE")])
    (tmp_path / "doc.md").write_text("nothing sensitive here\n", encoding="utf-8")
    r = run(aid, tmp_path / "doc.md")
    assert r.returncode == 0, r.stdout
    assert "clean" in r.stdout


def test_same_line_leak_is_found(tmp_path):
    aid = write_aid(tmp_path, [("SECRETVALUE", "PUBLICVALUE")])
    (tmp_path / "doc.md").write_text("this holds SECRETVALUE inline\n", encoding="utf-8")
    r = run(aid, tmp_path / "doc.md")
    assert r.returncode == 1
    assert "SECRETVALUE" in r.stdout
    assert "doc.md:1" in r.stdout


def test_leak_wrapped_across_a_newline_is_found(tmp_path):
    # The whole point. A line-based grep misses this.
    #
    # The figures below are invented. They have to be: a fixture is a tracked file,
    # and this project's one unrecoverable rule is that no real client value enters
    # history. Any multi-token string straddling the newline exercises the behaviour
    # under test, so nothing is lost by making them up, and using a real one to
    # illustrate a leak check would be the leak.
    aid = write_aid(tmp_path, [("63 rows carrying $7M", "about 50 rows")])
    (tmp_path / "doc.md").write_text("the defect covered 63 rows\ncarrying $7M gross\n",
                                     encoding="utf-8")
    r = run(aid, tmp_path / "doc.md")
    assert r.returncode == 1
    assert "doc.md:1" in r.stdout


def test_empty_pattern_list_is_an_error_not_a_pass(tmp_path):
    aid = write_aid(tmp_path, [])
    (tmp_path / "doc.md").write_text("anything\n", encoding="utf-8")
    r = run(aid, tmp_path / "doc.md")
    assert r.returncode == 2
    assert "no patterns" in r.stderr


def test_missing_aid_is_an_error(tmp_path):
    r = run(tmp_path / "absent.md", tmp_path)
    assert r.returncode == 2
    # Assert the message, not just the code. Exit 2 is also what a deleted script
    # and any argparse usage error produce, so a bare returncode check passes with
    # the tool absent or its flag renamed — it cannot fail for the right reason.
    assert "no such aid file" in r.stderr


def test_leak_inside_hash_prefixed_comment_lines_is_found(tmp_path):
    # The case that matters most: this repo's convention is multi-line, #-prefixed
    # fixture comments, and that is exactly where this project's one real leak lived.
    aid = write_aid(tmp_path, [("63 rows carrying $7M", "about 50 rows")])
    (tmp_path / "mod.py").write_text("# the defect covered 63 rows\n# carrying $7M gross\n",
                                     encoding="utf-8")
    r = run(aid, tmp_path / "mod.py")
    assert r.returncode == 1
    assert "mod.py:1" in r.stdout


def test_leak_inside_a_blockquote_is_found(tmp_path):
    aid = write_aid(tmp_path, [("63 rows carrying $7M", "about 50 rows")])
    (tmp_path / "doc.md").write_text("> the defect covered 63 rows\n> carrying $7M gross\n",
                                     encoding="utf-8")
    r = run(aid, tmp_path / "doc.md")
    assert r.returncode == 1


def test_match_is_case_insensitive(tmp_path):
    aid = write_aid(tmp_path, [("Ledgerline Fund Accounting", "the source system")])
    (tmp_path / "doc.md").write_text("migrated from ledgerline fund accounting\n",
                                     encoding="utf-8")
    r = run(aid, tmp_path / "doc.md")
    assert r.returncode == 1


def test_a_target_that_does_not_exist_is_an_error(tmp_path):
    # A typo'd path must not read as a clean tree. This is the fail-open case.
    aid = write_aid(tmp_path, [("SECRETVALUE", "x")])
    r = run(aid, tmp_path / "no-such-directory")
    assert r.returncode == 2
    assert "no such target" in r.stderr


def test_scanning_zero_files_is_an_error(tmp_path):
    # An empty directory means the gate proved nothing; saying "clean" would be a lie.
    aid = write_aid(tmp_path, [("SECRETVALUE", "x")])
    empty = tmp_path / "empty"
    empty.mkdir()
    r = run(aid, empty)
    assert r.returncode == 2
    assert "no files" in r.stderr


def test_file_count_is_reported(tmp_path):
    aid = write_aid(tmp_path, [("SECRETVALUE", "x")])
    (tmp_path / "a.md").write_text("fine\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("also fine\n", encoding="utf-8")
    r = run(aid, tmp_path)
    assert r.returncode == 0, r.stdout
    # The pattern count alone cannot show the gate scanned anything.
    assert "2 files" in r.stdout


def test_only_the_value_table_contributes_patterns(tmp_path):
    # The aid is hand-edited and grows tables that are not value tables. Every
    # markdown row's first cell used to become a pattern, so a second table injected
    # its own first column: a row reading "the" matches every file in the tree, the
    # gate goes red having found nothing, and the pattern count — the number
    # designated as proof the gate is not vacuous — is inflated past the real one.
    aid = tmp_path / "aid.md"
    aid.write_text(
        "# aid\n"
        "\n"
        "| Original value | replacement | file | line |\n"
        "|---|---|---|---|\n"
        "| SECRETVALUE | PUBLICVALUE | f.md | 1 |\n"
        "\n"
        "## What was carried over rather than substituted\n"
        "\n"
        "| Word | Why it is here |\n"
        "|---|---|\n"
        "| the | a determiner, in every file in the tree |\n"
        "| a | so is this one |\n"
        "| mechanics | carried over deliberately |\n",
        encoding="utf-8")
    (tmp_path / "doc.md").write_text(
        "the quick brown fox, a sentence about mechanics\n", encoding="utf-8")
    r = run(aid, tmp_path / "doc.md")
    assert r.returncode == 0, r.stdout
    # One real value, not four. The count is the proof the gate is not vacuous.
    assert "1 patterns checked against 1 files" in r.stdout
    assert "clean" in r.stdout
    assert "LEAK" not in r.stdout


def test_aid_with_no_value_table_is_an_error(tmp_path):
    # No table headed "Original" means no values were listed, so nothing was checked.
    aid = tmp_path / "aid.md"
    aid.write_text("# aid\n\n| Word | Note |\n|---|---|\n| the | not a value |\n",
                   encoding="utf-8")
    (tmp_path / "doc.md").write_text("the\n", encoding="utf-8")
    r = run(aid, tmp_path / "doc.md")
    assert r.returncode == 2
    assert "no patterns" in r.stderr


def test_aid_header_row_is_not_treated_as_a_pattern(tmp_path):
    aid = tmp_path / "aid.md"
    aid.write_text("| Original value | replacement | file | line |\n|---|---|---|---|\n"
                   "| SECRETVALUE | x | f.md | 1 |\n", encoding="utf-8")
    (tmp_path / "doc.md").write_text("this mentions the Original value column\n",
                                     encoding="utf-8")
    r = run(aid, tmp_path / "doc.md")
    assert r.returncode == 0, r.stdout
    assert "1 patterns" in r.stdout


def test_directory_target_is_walked(tmp_path):
    aid = write_aid(tmp_path, [("SECRETVALUE", "x")])
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "deep.md").write_text("SECRETVALUE\n", encoding="utf-8")
    r = run(aid, sub)
    assert r.returncode == 1
    assert "deep.md:1" in r.stdout


def test_the_aid_itself_is_never_scanned(tmp_path):
    # The aid contains every original by definition; scanning it would always "leak".
    # A second, clean file is present deliberately: without it the run scans nothing
    # and trips the only-the-aid guard, so the test would pass for the wrong reason.
    aid = write_aid(tmp_path, [("SECRETVALUE", "x")])
    (tmp_path / "clean.md").write_text("nothing sensitive\n", encoding="utf-8")
    r = run(aid, tmp_path)
    assert r.returncode == 0, r.stdout
    assert "1 files" in r.stdout


def test_only_the_aid_in_scope_is_an_error(tmp_path):
    # If the aid is the only file in scope, nothing was checked and "clean" would lie.
    aid = write_aid(tmp_path, [("SECRETVALUE", "x")])
    r = run(aid, tmp_path)
    assert r.returncode == 2
    assert "only the aid" in r.stderr


def test_row_outside_any_value_table_is_an_error(tmp_path):
    # A `|`-row that never sits inside a recognised table -- the value table,
    # or some other table with its own header+separator -- must not be
    # silently discarded. That is exactly how the earlier fix (scoping
    # patterns to the "Original..." table) went fail-open: it stopped a
    # second table injecting junk patterns, but any row outside a recognised
    # table now vanishes with no trace instead.
    aid = tmp_path / "aid.md"
    aid.write_text(
        "# aid\n"
        "\n"
        "| Original value | replacement | file | line |\n"
        "|---|---|---|---|\n"
        "| SECRETVALUE | PUBLICVALUE | f.md | 1 |\n"
        "\n"
        "| ORPHANVALUE | x | f.md | 2 |\n",
        encoding="utf-8")
    (tmp_path / "doc.md").write_text("nothing sensitive\n", encoding="utf-8")
    r = run(aid, tmp_path / "doc.md")
    assert r.returncode == 2, r.stdout
    # Anchored, not a bare substring check: "1 rows" is also a substring of
    # "11 rows", which is exactly the discriminating-assertion defect this
    # build hit twice already.
    m = re.search(r"(\d+) rows? skipped outside the value table", r.stderr)
    assert m is not None, r.stderr
    assert int(m.group(1)) == 1
    assert re.search(r"\bline 7\b", r.stderr), r.stderr
    assert "value table" in r.stderr and "non-table text" in r.stderr


def test_value_table_split_by_blank_line_is_an_error(tmp_path):
    # This is the defect itself. A blank line resets the in-table flag, so
    # the row after it -- which is really a continuation of the same value
    # table, hand-added later -- used to vanish with no trace while the gate
    # printed "clean" over a smaller population instead of catching it.
    aid = tmp_path / "aid.md"
    aid.write_text(
        "| Original value | replacement | file | line |\n"
        "|---|---|---|---|\n"
        "| SECRETVALUE1 | x | f.md | 1 |\n"
        "\n"
        "| SECRETVALUE2 | y | f.md | 2 |\n",
        encoding="utf-8")
    (tmp_path / "doc.md").write_text("this file mentions SECRETVALUE2 plainly\n",
                                     encoding="utf-8")
    r = run(aid, tmp_path / "doc.md")
    assert r.returncode == 2, r.stdout
    assert "clean" not in r.stdout
    m = re.search(r"(\d+) rows? skipped outside the value table", r.stderr)
    assert m is not None, r.stderr
    assert int(m.group(1)) == 1
    assert re.search(r"\bline 5\b", r.stderr), r.stderr


def test_single_table_aid_reports_zero_rows_skipped(tmp_path):
    # The skipped count must be visible even when it is zero -- printing a
    # count only when it is nonzero is how a nobody-checks-it number happens.
    aid = write_aid(tmp_path, [("SECRETVALUE", "x")])
    (tmp_path / "doc.md").write_text("fine\n", encoding="utf-8")
    r = run(aid, tmp_path / "doc.md")
    assert r.returncode == 0, r.stdout
    m = re.search(r"(\d+) skipped outside the value table", r.stdout)
    assert m is not None, r.stdout
    assert int(m.group(1)) == 0
