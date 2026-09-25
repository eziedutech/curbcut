"""Copy the reviewed OpenClass versions into the dashboard as static pages.

    python scripts/export_openclass.py

Each version is taken from the exact commit that was reviewed or fixed, so the
page a visitor opens is the code IBM Bob looked at.
"""

import json
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "codes" / "frontrouter" / "public" / "openclass"
SRC = "codes/fixture/src"


def head_sha(report_id: str) -> str:
    facts = json.loads((REPO / "reports" / "curbcut" / report_id / "facts.json").read_text(encoding="utf-8"))
    return facts["head"]["sha"]


VERSIONS = {
    "pr-1": head_sha("pr-1"),
    "pr-1-fixed": json.loads((REPO / "reports/curbcut/pr-1/verify.json").read_text(encoding="utf-8"))["head"]["sha"],
    "pr-2": head_sha("pr-2"),
}


def export(name: str, sha: str) -> None:
    target = OUT / name
    shutil.rmtree(target, ignore_errors=True)
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "src.tar"
        subprocess.run(["git", "-C", str(REPO), "archive", "--format=tar", "-o", str(archive), sha, SRC], check=True)
        with tarfile.open(archive) as tar:
            tar.extractall(tmp, filter="data")
        shutil.copytree(Path(tmp) / SRC, target)
    print(f"{name}: {sha[:7]} -> {target.relative_to(REPO).as_posix()} ({sum(1 for _ in target.rglob('*') if _.is_file())} files)")


if __name__ == "__main__":
    for name, sha in VERSIONS.items():
        export(name, sha)
