"""Git helpers. Each ref is checked out into its own detached worktree, so the
working copy the developer (or IBM Bob) is using is never touched."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def git(repo: Path, *args: str) -> str:
    res = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {res.stderr.strip()}")
    return res.stdout


def repo_root(start: Path) -> Path:
    return Path(git(start, "rev-parse", "--show-toplevel").strip())


def rev_parse(repo: Path, ref: str) -> str:
    return git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").strip()


def changed_files(repo: Path, base: str, head: str, path: str) -> list[tuple[str, str]]:
    """(status, path) for files under `path` changed between the merge base and head."""
    out = git(repo, "diff", "--name-status", "--no-renames", f"{base}...{head}", "--", path)
    rows = []
    for line in out.splitlines():
        if not line.strip():
            continue
        status, name = line.split("\t", 1)
        rows.append((status[0], name))
    return rows


@contextmanager
def worktree(repo: Path, sha: str) -> Iterator[Path]:
    tmp = Path(tempfile.mkdtemp(prefix="curbcut-wt-"))
    target = tmp / "wt"
    git(repo, "worktree", "add", "--detach", "--quiet", str(target), sha)
    try:
        yield target
    finally:
        try:
            git(repo, "worktree", "remove", "--force", str(target))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
            git(repo, "worktree", "prune")
