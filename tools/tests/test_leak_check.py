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


def test_directory_target_is_walked(tmp_path):
    aid = write_aid(tmp_path, [("SECRETVALUE", "x")])
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "deep.md").write_text("SECRETVALUE\n", encoding="utf-8")
    r = run(aid, sub)
    assert r.returncode == 1
    assert "deep.md:1" in r.stdout


def test_the_aid_itself_is_never_scanned(tmp_path):
    # The aid contains every original by definition; scanning it always "leaks".
    aid = write_aid(tmp_path, [("SECRETVALUE", "x")])
    r = run(aid, aid.parent)
    assert r.returncode == 0, r.stdout
