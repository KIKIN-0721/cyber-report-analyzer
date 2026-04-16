from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple


LABELS: List[Tuple[str, str, str]] = [
    ("type:feature", "0e8a16", "Feature task"),
    ("type:bug", "d73a4a", "Bug report"),
    ("type:test", "1d76db", "Test task"),
    ("type:docs", "5319e7", "Docs task"),
    ("type:refactor", "fbca04", "Refactor task"),
    ("type:chore", "c5def5", "Chore task"),
    ("stage:S1", "bfdadc", "Stage 1"),
    ("stage:S2", "bfdadc", "Stage 2"),
    ("stage:S3", "bfdadc", "Stage 3"),
    ("stage:S4", "bfdadc", "Stage 4"),
    ("stage:S5", "bfdadc", "Stage 5"),
    ("module:parser", "0366d6", "Parser module"),
    ("module:ocr", "0366d6", "OCR module"),
    ("module:rules", "0366d6", "Rules module"),
    ("module:model", "0366d6", "Model module"),
    ("module:web", "0366d6", "Web module"),
    ("module:evidence", "0366d6", "Evidence module"),
    ("module:deploy", "0366d6", "Deploy module"),
    ("module:ci", "0366d6", "CI module"),
    ("module:docs", "0366d6", "Docs module"),
    ("priority:P0", "b60205", "Blocker"),
    ("priority:P1", "d93f0b", "High"),
    ("priority:P2", "fbca04", "Medium"),
    ("priority:P3", "0e8a16", "Low"),
    ("status:blocked", "d93f0b", "Blocked"),
    ("status:need-review", "1d76db", "Need review"),
    ("status:ready-for-test", "0e8a16", "Ready for test"),
    ("status:ready-for-release", "5319e7", "Ready for release"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap GitHub repository collaboration settings.")
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--default-branch", default="main")
    parser.add_argument("--develop-branch", default="develop")
    return parser.parse_args()


def run_command(args: List[str], *, cwd: Path | None = None, allow_failure: bool = False) -> int:
    completed = subprocess.run(args, cwd=cwd, check=False)
    if completed.returncode != 0 and not allow_failure:
        raise RuntimeError(f"command failed: {' '.join(args)}")
    return completed.returncode


def main() -> int:
    args = parse_args()

    print("Checking GitHub CLI...")
    run_command(["gh", "--version"])

    print(f"Setting default branch to {args.default_branch}")
    run_command(["gh", "repo", "edit", args.repo, "--default-branch", args.default_branch])

    print("Creating develop branch")
    run_command(["git", "checkout", args.default_branch])
    run_command(["git", "pull"])
    branch_exists = run_command(["git", "rev-parse", "--verify", args.develop_branch], allow_failure=True) == 0
    if branch_exists:
        run_command(["git", "checkout", args.develop_branch])
    else:
        run_command(["git", "checkout", "-b", args.develop_branch])
    run_command(["git", "push", "-u", "origin", args.develop_branch], allow_failure=True)

    print("Creating labels")
    for name, color, description in LABELS:
        create_rc = run_command(
            ["gh", "label", "create", name, "--repo", args.repo, "--color", color, "--description", description],
            allow_failure=True,
        )
        if create_rc != 0:
            run_command(["gh", "label", "edit", name, "--repo", args.repo, "--color", color, "--description", description])

    print("Applying branch protections")
    payload = {
        "required_status_checks": {
            "strict": True,
            "contexts": ["quality"],
        },
        "enforce_admins": False,
        "required_pull_request_reviews": {
            "required_approving_review_count": 1,
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
        },
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False,
    }

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".json") as handle:
        json.dump(payload, handle, ensure_ascii=False)
        temp_path = Path(handle.name)

    try:
        run_command(
            [
                "gh",
                "api",
                "-X",
                "PUT",
                f"repos/{args.repo}/branches/{args.default_branch}/protection",
                "--input",
                str(temp_path),
            ]
        )
    finally:
        temp_path.unlink(missing_ok=True)

    print("Done. Next: create S1 issues from docs/github/S1-issue-backlog.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
