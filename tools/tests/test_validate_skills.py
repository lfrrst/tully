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
    # The fixture directory name must not contain any word the assertion checks
    # for. The validator prints one result line per directory, so a fixture named
    # "real-name" would satisfy `assert "name" in stdout` from its own name alone
    # and the test would pass whether or not the mismatch was detected.
    make_skill(tmp_path, "alpha", frontmatter_name="beta")
    r = run(tmp_path)
    assert r.returncode == 1
    assert "frontmatter name is 'beta', expected 'alpha'" in r.stdout


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
    # Named "barren" rather than "empty-evals" for the same reason as
    # test_name_mismatch_fails: the assertion must not be satisfiable by the
    # fixture's own directory name appearing in the result line.
    make_skill(tmp_path, "barren", evals_body={"skill_name": "barren", "evals": []})
    r = run(tmp_path)
    assert r.returncode == 1
    assert "has an empty evals list" in r.stdout


def test_missing_evals_json_fails(tmp_path):
    d = make_skill(tmp_path, "no-evals-file")
    (d / "evals" / "evals.json").unlink()
    r = run(tmp_path)
    assert r.returncode == 1
    assert "evals/evals.json is missing" in r.stdout


def test_unterminated_frontmatter_fails(tmp_path):
    d = make_skill(tmp_path, "unterminated")
    (d / "SKILL.md").write_text("---\nname: unterminated\ndescription: x\n",
                                encoding="utf-8")
    r = run(tmp_path)
    assert r.returncode == 1
    assert "no terminated YAML frontmatter" in r.stdout


def test_nonexistent_skills_dir_exits_two(tmp_path):
    r = run(tmp_path / "absent")
    assert r.returncode == 2
    assert "no such skills directory" in r.stderr


def test_existing_but_empty_skills_dir_exits_two(tmp_path):
    # This one exists and holds nothing. It printed "0 skills checked, 0 problems"
    # and exited 0 — and CI invokes the validator with the default directory, so a
    # skills/ holding only a .gitkeep produced a green build over nothing checked.
    empty = tmp_path / "skills"
    empty.mkdir()
    r = run(empty)
    assert r.returncode == 2
    assert "no skills found: the check proved nothing" in r.stderr


def test_reports_every_failure_not_just_the_first(tmp_path):
    make_skill(tmp_path, "first-bad", description=None)
    make_skill(tmp_path, "second-bad", frontmatter_name="wrong")
    r = run(tmp_path)
    assert r.returncode == 1
    assert "first-bad" in r.stdout and "second-bad" in r.stdout
