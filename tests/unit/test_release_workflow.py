"""Structure tests for .github/workflows/release.yml and the build.ps1 wiring.

These make the release contract checkable without running GitHub Actions:
triggers (loop safety), permissions, the marketplace bump condition, and the
three published assets. PyYAML is a test-only import (already installed as a
transitive dependency; not in pyproject.toml).
"""

import re
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release.yml"
BUILD_PS1 = REPO_ROOT / "build.ps1"

ASSETS = {"sk-wwise-plugin.zip", "sk-wwise-mcp.mcpb", "sk-wwise-mcp.zip"}

TAG_REF = "refs/tags/v1.2.3"
MAIN_REF = "refs/heads/main"


@pytest.fixture(scope="module")
def wf():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def steps(wf):
    return wf["jobs"]["build"]["steps"]


def _step(steps, needle):
    """The one step whose name contains `needle`."""
    found = [s for s in steps if needle.lower() in s.get("name", "").lower()]
    assert len(found) == 1, f"expected one step named like {needle!r}, got {len(found)}"
    return found[0]


def _index(steps, needle):
    return steps.index(_step(steps, needle))


def _runs(step, event, ref):
    """Evaluate a step's `if:` for (event, ref). Only the small expression
    subset used by this workflow is supported; anything else fails loudly."""
    expr = step.get("if")
    if expr is None:
        return True
    py = re.sub(r"\$\{\{|\}\}", "", str(expr)).strip()
    py = py.replace("github.event_name", repr(event))
    py = re.sub(r"github\.ref\b", repr(ref), py)
    py = re.sub(r"startsWith\(([^,]+),\s*('[^']*')\)", r"(\1).startswith(\2)", py)
    py = py.replace("&&", " and ").replace("||", " or ")
    assert re.fullmatch(r"[\w\s'().:/=!-]*", py), f"unsupported if expression: {expr!r}"
    return bool(eval(py, {"__builtins__": {}}))


def _files(step):
    raw = step["with"].get("files") or step["with"].get("path")
    return {line.strip() for line in str(raw).splitlines() if line.strip()}


# --- AC1: valid workflow with the expected shape ---


def test_workflow_parses_and_has_a_single_build_job(wf):
    assert wf["name"]
    assert list(wf["jobs"]) == ["build"]
    assert wf["jobs"]["build"]["runs-on"] == "windows-latest"


def test_every_step_has_a_uses_or_a_run(steps):
    for s in steps:
        assert ("uses" in s) != ("run" in s), s


def test_steps_run_in_release_order(steps):
    order = [
        _index(steps, "Build"),
        _index(steps, "Smoke test"),
        _index(steps, "Create release"),
        _index(steps, "marketplace"),
    ]
    assert order == sorted(order)
    assert len(set(order)) == 4


# --- AC2: bump only on tag builds, exact URL, no loop ---


def test_triggers_are_only_version_tags_and_manual_dispatch(wf):
    # YAML 1.1 reads the bare key `on` as boolean True.
    triggers = wf.get("on", wf.get(True))
    assert set(triggers) == {"push", "workflow_dispatch"}
    assert triggers["push"] == {"tags": ["v*"]}  # no `branches`: a push to main cannot trigger


RELEASE_ONLY = ("Create release", "marketplace")


@pytest.mark.parametrize("needle", RELEASE_ONLY)
def test_release_only_steps_run_on_a_tag_push(steps, needle):
    assert _runs(_step(steps, needle), "push", TAG_REF)


@pytest.mark.parametrize("needle", RELEASE_ONLY)
@pytest.mark.parametrize("ref", [TAG_REF, MAIN_REF])
def test_release_only_steps_never_run_on_manual_dispatch(steps, needle, ref):
    # "Use workflow from" lists tags, so a dispatch can carry a tag ref.
    # A manual run must not release or commit, whatever the ref.
    assert not _runs(_step(steps, needle), "workflow_dispatch", ref)


@pytest.mark.parametrize("ref", [TAG_REF, MAIN_REF])
def test_manual_dispatch_uploads_artifacts_on_any_ref(steps, ref):
    assert _runs(_step(steps, "Upload artifact"), "workflow_dispatch", ref)


def test_tag_push_does_not_upload_workflow_artifacts(steps):
    assert not _runs(_step(steps, "Upload artifact"), "push", TAG_REF)


def test_bump_step_uses_the_script_with_the_tag_and_repo(steps):
    step = _step(steps, "marketplace")
    run = step["run"]
    assert "release/bump_marketplace.py" in run
    assert "--tag" in run and "--repo" in run
    env = step["env"]
    assert env["TAG"] == "${{ github.ref_name }}"
    assert env["REPO"] == "${{ github.repository }}"
    # Untrusted ref names must reach the shell through env, not inline ${{ }}.
    assert "${{" not in run


def test_bump_commits_to_main_from_the_detached_tag_checkout(steps):
    run = _step(steps, "marketplace")["run"]
    assert re.search(r"git fetch .*origin .*main", run)
    assert re.search(r"git checkout .*main", run)
    assert "git push origin HEAD:main" in run
    assert "--tags" not in run and "--force" not in run


def test_bump_writes_the_file_before_switching_branches(steps):
    # The script that ran is the one from the tagged commit, not from main.
    run = _step(steps, "marketplace")["run"]
    assert run.index("bump_marketplace.py") < run.index("git checkout")


def test_bump_tolerates_nothing_to_commit(steps):
    run = _step(steps, "marketplace")["run"]
    assert "git diff --cached --quiet" in run


def test_bump_commit_message_skips_ci(steps):
    assert "[skip ci]" in _step(steps, "marketplace")["run"]


def test_bump_pins_the_sha256_of_the_zip_that_is_released(steps):
    assert "--zip sk-wwise-plugin.zip" in _step(steps, "marketplace")["run"]


# --- AC3: least privilege ---


def test_permissions_are_contents_write_only(wf):
    assert wf["permissions"] == {"contents": "write"}
    assert "permissions" not in wf["jobs"]["build"] or wf["jobs"]["build"]["permissions"] == {
        "contents": "write"
    }


def test_no_step_uses_a_personal_token(steps):
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "secrets." not in text.replace("secrets.GITHUB_TOKEN", "")


# --- the three artifacts ---


def test_release_publishes_all_three_assets(steps):
    step = _step(steps, "Create release")
    assert _files(step) == ASSETS
    assert step["with"]["fail_on_unmatched_files"] is True


def test_manual_runs_upload_all_three_assets_without_releasing(steps):
    step = _step(steps, "Upload artifact")
    assert step["if"] == "github.event_name == 'workflow_dispatch'"
    assert _files(step) == ASSETS
    assert step["with"]["if-no-files-found"] == "error"


def test_tag_version_is_passed_to_the_build(steps):
    resolve = _step(steps, "Resolve version")
    assert "bump_marketplace.py" in resolve["run"]
    assert "--print-version" in resolve["run"]
    build = _step(steps, "Build")
    assert "build.ps1" in build["run"] and "-Version" in build["run"]


def test_smoke_test_still_runs_the_exe(steps):
    assert "sk-wwise-mcp.exe" in _step(steps, "Smoke test")["run"]


def test_build_ps1_forwards_the_version_to_both_generators():
    text = BUILD_PS1.read_text(encoding="utf-8")
    assert re.search(r"param\(\s*\[string\]\$Version", text)
    for script in ("build_mcpb.py", "build_plugin.py"):
        line = next(ln for ln in text.splitlines() if script in ln and "python" in ln)
        assert "@VersionArgs" in line, line


# --- AC5: release/README.md documents the three artifacts ---


def test_readme_has_a_section_for_the_three_artifacts():
    text = (REPO_ROOT / "release" / "README.md").read_text(encoding="utf-8")
    match = re.search(r"^## Release artifacts[^\n]*\n(.*?)(?=^## )", text, re.S | re.M)
    assert match, "missing '## Release artifacts' section"
    section = match.group(1)
    for asset in sorted(ASSETS):
        assert f"`{asset}`" in section, asset
    assert "Claude Desktop" in section and "Code tab" in section  # who uses which
    assert "marketplace" in section.lower()
