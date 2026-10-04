"""Write `.claude-plugin/marketplace.json` for a release tag.

Release CI calls this after it publishes the GitHub release. Input: a tag
(`v0.2.0`) and the repo (`owner/name`). Output: the marketplace file whose
plugin entry points at the exact release asset of that tag
(`https://github.com/<repo>/releases/download/<tag>/sk-wwise-plugin.zip`) and
carries the matching version. The file shape comes from `build_plugin`; this
module only validates the inputs and calls it.

    python release/bump_marketplace.py --tag v0.2.0 --repo owner/name \\
        [--zip sk-wwise-plugin.zip] [--path .claude-plugin/marketplace.json]
    python release/bump_marketplace.py --tag v0.2.0 --print-version   # -> 0.2.0

`--zip` pins `source.sha256` to that file (Claude Code refuses a download that
does not match it). The same input always gives the same bytes, so re-running
a tag leaves the file unchanged. Only the standard library is needed.
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path

RELEASE_DIR = Path(__file__).resolve().parent
for _p in (str(RELEASE_DIR.parent), str(RELEASE_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from build_plugin import GITHUB_REPO, MARKETPLACE_PATH, write_marketplace  # noqa: E402

# v<major>.<minor>.<patch> with an optional -prerelease / +build suffix.
_TAG_RE = re.compile(r"^v(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z][0-9A-Za-z.+-]*)?)$")
_REPO_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9._-]+$")


def version_from_tag(tag):
    """`v0.2.0` -> `0.2.0`. Raises ValueError for anything that is not a version tag."""
    match = _TAG_RE.fullmatch(tag or "")
    if not match:
        raise ValueError(f"tag must look like v1.2.3 (optional -suffix): {tag!r}")
    return match.group(1)


def _check_repo(repo):
    if not _REPO_RE.fullmatch(repo or ""):
        raise ValueError(f"repo must be owner/name: {repo!r}")
    return repo


def bump_marketplace(tag, repo=GITHUB_REPO, path=MARKETPLACE_PATH, zip_path=None):
    """Write marketplace.json for `tag` in `repo`. Returns the Path written.

    Nothing is written when `tag` or `repo` is invalid.
    """
    version = version_from_tag(tag)
    _check_repo(repo)
    digest = None
    if zip_path is not None:
        digest = hashlib.sha256(Path(zip_path).read_bytes()).hexdigest()
    return write_marketplace(version, sha256=digest, path=path, repo=repo)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Write marketplace.json for a release tag")
    parser.add_argument("--tag", required=True, help="release tag, e.g. v0.2.0")
    parser.add_argument("--repo", default=GITHUB_REPO, help="GitHub repo, owner/name")
    parser.add_argument("--zip", default=None, help="plugin zip to pin as source.sha256")
    parser.add_argument("--path", default=str(MARKETPLACE_PATH), help="marketplace.json to write")
    parser.add_argument(
        "--print-version",
        action="store_true",
        help="print the version for --tag and exit without writing anything",
    )
    args = parser.parse_args(argv)
    try:
        if args.print_version:
            print(version_from_tag(args.tag))
            return 0
        out = bump_marketplace(args.tag, args.repo, args.path, args.zip)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Market:  {out} ({args.tag}, {args.repo})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
