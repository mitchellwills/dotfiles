#!/usr/bin/env python3
"""Interactive git worktree cleanup tool with Antigravity conversation awareness.

Identifies linked git worktrees that are safe to remove (merged into main/master,
clean working tree, and no active non-archived Antigravity conversations), opens
the full list in $VISUAL/$EDITOR for review and editing, and removes the
selected worktrees.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlparse

BASE_BRANCH_CANDIDATES = ("main", "master", "origin/main", "origin/master")
ARCHIVED_RE = re.compile(r"\barchived:\s*true\b")


@dataclass
class ActiveConversation:
    """Represents a non-archived, non-killed Antigravity conversation."""

    conversation_id: str
    title: str
    status: str


@dataclass
class WorktreeInfo:
    """Parsed metadata and cleanup assessment for a git worktree."""

    path: str
    head: str | None = None
    branch: str | None = None
    bare: bool = False
    locked: bool = False
    prunable: bool = False
    merged: bool = False
    ahead_count: int = 0
    dirty: bool = False
    is_current: bool = False
    active_conversations: list[ActiveConversation] = field(default_factory=list)

    @property
    def keep_reasons(self) -> list[str]:
        reasons: list[str] = []
        if self.is_current:
            reasons.append("current worktree")
        if self.locked:
            reasons.append("locked")
        if self.prunable:
            reasons.append("prunable/missing")
        if self.dirty:
            reasons.append("uncommitted changes")
        if not self.merged:
            suffix = f" (+{self.ahead_count} ahead)" if self.ahead_count else ""
            reasons.append(f"unmerged{suffix}")
        if self.active_conversations:
            labels = list(
                dict.fromkeys(
                    f'"{c.title}"' if c.title else c.conversation_id[:8]
                    for c in self.active_conversations
                )
            )
            titles = ", ".join(labels[:3])
            extra = f" (+{len(labels) - 3} more)" if len(labels) > 3 else ""
            reasons.append(f"active conversation: {titles}{extra}")
        return reasons

    @property
    def recommend_delete(self) -> bool:
        return not self.keep_reasons


def run_git(
    args: list[str], cwd: Path | None = None, check: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run a git command and capture text output."""
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=check,
    )


def detect_base_branch(repo_dir: Path, explicit_base: str | None) -> str:
    """Resolve the base branch to check merge status against."""
    if explicit_base:
        res = run_git(
            ["rev-parse", "--verify", "--quiet", explicit_base],
            cwd=repo_dir,
            check=False,
        )
        if res.returncode != 0:
            raise RuntimeError(f"Base ref not found: {explicit_base}")
        return explicit_base

    for candidate in BASE_BRANCH_CANDIDATES:
        res = run_git(
            ["rev-parse", "--verify", "--quiet", candidate],
            cwd=repo_dir,
            check=False,
        )
        if res.returncode == 0:
            return candidate

    raise RuntimeError(
        "Could not find a base branch (tried: "
        + ", ".join(BASE_BRANCH_CANDIDATES)
        + "). Pass --base <ref>."
    )


def parse_worktree_list(porcelain_output: str) -> list[WorktreeInfo]:
    """Parse `git worktree list --porcelain` output into WorktreeInfo records."""
    worktrees: list[WorktreeInfo] = []
    blocks = [b for b in porcelain_output.strip().split("\n\n") if b.strip()]
    for block in blocks:
        info: WorktreeInfo | None = None
        for line in block.splitlines():
            if line.startswith("worktree "):
                info = WorktreeInfo(path=line.removeprefix("worktree "))
            elif info is None:
                continue
            elif line.startswith("HEAD "):
                info.head = line.removeprefix("HEAD ")
            elif line.startswith("branch "):
                info.branch = line.removeprefix("branch ").removeprefix("refs/heads/")
            elif line == "bare":
                info.bare = True
            elif line == "locked" or line.startswith("locked "):
                info.locked = True
            elif line == "prunable" or line.startswith("prunable "):
                info.prunable = True
        if info is not None:
            worktrees.append(info)
    return worktrees


def default_agy_dir() -> Path:
    """Return the default Antigravity app data directory."""
    env_dir = os.environ.get("ANTIGRAVITY_APP_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.home() / ".gemini" / "antigravity-cli"


def _is_annotation_archived(annotations_dir: Path, conversation_id: str) -> bool:
    ann_path = annotations_dir / f"{conversation_id}.pbtxt"
    if not ann_path.is_file():
        return False
    try:
        return bool(ARCHIVED_RE.search(ann_path.read_text(encoding="utf-8", errors="replace")))
    except OSError:
        return False


def load_active_conversations_by_path(
    agy_dir: Path,
) -> tuple[dict[str, list[ActiveConversation]], str | None]:
    """Map normalized workspace paths to active (non-archived) Antigravity conversations.

    Returns (mapping, warning_message).
    """
    db_path = agy_dir / "conversation_summaries.db"
    if not db_path.is_file():
        return {}, f"Antigravity database not found at {db_path}; skipping conversation check."

    annotations_dir = agy_dir / "annotations"
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5.0)
    except sqlite3.Error as exc:
        return {}, f"Failed to open Antigravity database {db_path}: {exc}"

    try:
        rows = conn.execute(
            "SELECT conversation_id, title, parent_conversation_id, workspace_uris, status, killed "
            "FROM conversation_summaries"
        ).fetchall()
    finally:
        conn.close()

    by_id: dict[str, tuple[str, str, str, str, int]] = {}
    for cid, title, parent_id, uris_json, status, killed in rows:
        by_id[cid] = (title or "", parent_id or "", uris_json or "[]", status or "", int(killed or 0))

    archived_cache: dict[str, bool] = {}

    def is_effectively_archived(cid: str) -> bool:
        if cid in archived_cache:
            return archived_cache[cid]
        visited: set[str] = set()
        curr: str | None = cid
        archived = False
        while curr and curr not in visited:
            visited.add(curr)
            if _is_annotation_archived(annotations_dir, curr):
                archived = True
                break
            entry = by_id.get(curr)
            curr = entry[1] if entry and entry[1] else None
        archived_cache[cid] = archived
        return archived

    def resolve_title(cid: str) -> str:
        visited: set[str] = set()
        curr: str | None = cid
        while curr and curr not in visited:
            visited.add(curr)
            entry = by_id.get(curr)
            if not entry:
                break
            if entry[0]:
                return entry[0]
            curr = entry[1] or None
        return ""

    by_path: dict[str, list[ActiveConversation]] = {}
    for cid, (title, _parent_id, uris_json, status, killed) in by_id.items():
        if killed:
            continue
        if is_effectively_archived(cid):
            continue

        try:
            uris = json.loads(uris_json)
        except json.JSONDecodeError:
            continue
        if not isinstance(uris, list):
            continue

        conv = ActiveConversation(
            conversation_id=cid,
            title=title or resolve_title(cid),
            status=status,
        )
        for uri in uris:
            if not isinstance(uri, str):
                continue
            parsed = urlparse(uri)
            if parsed.scheme and parsed.scheme != "file":
                continue
            fs_path = os.path.realpath(unquote(parsed.path if parsed.scheme == "file" else uri))
            by_path.setdefault(fs_path, []).append(conv)

    return by_path, None


def assess_worktrees(
    repo_dir: Path,
    base_branch: str,
    active_by_path: dict[str, list[ActiveConversation]],
    cwd: Path | None = None,
) -> list[WorktreeInfo]:
    """Collect and evaluate all linked worktrees (excluding the main working tree)."""
    porcelain = run_git(["worktree", "list", "--porcelain"], cwd=repo_dir).stdout
    all_worktrees = parse_worktree_list(porcelain)
    if len(all_worktrees) <= 1:
        return []

    resolved_cwd = (cwd or Path.cwd()).resolve()
    candidates = [wt for wt in all_worktrees[1:] if not wt.bare]

    def evaluate(wt: WorktreeInfo) -> WorktreeInfo:
        wt_path = Path(wt.path)
        wt_resolved = Path(os.path.realpath(wt.path))
        wt.is_current = resolved_cwd == wt_resolved or wt_resolved in resolved_cwd.parents
        wt.active_conversations = active_by_path.get(str(wt_resolved), [])

        if wt.head:
            is_anc = run_git(
                ["merge-base", "--is-ancestor", wt.head, base_branch],
                cwd=repo_dir,
                check=False,
            )
            wt.merged = is_anc.returncode == 0
            if not wt.merged:
                ahead = run_git(
                    ["rev-list", "--count", f"{base_branch}..{wt.head}"],
                    cwd=repo_dir,
                    check=False,
                )
                if ahead.returncode == 0 and ahead.stdout.strip().isdigit():
                    wt.ahead_count = int(ahead.stdout.strip())

        if wt_path.is_dir() and not wt.prunable:
            status_res = run_git(["status", "--porcelain"], cwd=wt_path, check=False)
            wt.dirty = status_res.returncode == 0 and bool(status_res.stdout.strip())

        return wt

    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(evaluate, candidates))


def format_cleanup_plan(worktrees: list[WorktreeInfo], base_branch: str) -> str:
    """Render the editable cleanup plan showing all linked worktrees."""
    to_delete = [wt for wt in worktrees if wt.recommend_delete]
    to_keep = [wt for wt in worktrees if not wt.recommend_delete]

    lines = [
        f"# Git worktree cleanup plan (base branch: {base_branch})",
        "#",
        "# Lines starting with 'delete ' will be removed.",
        "# Comment out (prefix with '#') or delete a line to KEEP that worktree.",
        "# Uncomment a '# delete ' line below to ALSO remove that worktree.",
        "# Remove or comment out all 'delete ' lines to abort without removing anything.",
        "#",
        f"# --- Recommended for deletion ({len(to_delete)}) ---",
    ]

    if not to_delete:
        lines.append("# (none)")
    for wt in to_delete:
        branch_label = wt.branch or "(detached)"
        lines.append(f"delete {shlex.quote(wt.path)}  # branch: {branch_label} | merged")

    lines.extend([
        "#",
        f"# --- Kept ({len(to_keep)}) ---",
    ])
    if not to_keep:
        lines.append("# (none)")
    for wt in to_keep:
        branch_label = wt.branch or "(detached)"
        reasons = ", ".join(wt.keep_reasons)
        lines.append(
            f"# delete {shlex.quote(wt.path)}  # KEEP: {reasons} | branch: {branch_label}"
        )

    lines.append("")
    return "\n".join(lines)


def parse_cleanup_plan(content: str) -> list[str]:
    """Parse the edited cleanup plan and return deduplicated worktree paths to delete."""
    selected: list[str] = []
    seen: set[str] = set()
    for lineno, raw_line in enumerate(content.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        tokens = shlex.split(stripped, comments=True)
        if not tokens:
            continue
        if len(tokens) != 2 or tokens[0] != "delete":
            raise ValueError(
                f"Invalid instruction on line {lineno}: {raw_line!r} "
                "(expected 'delete <worktree-path>')"
            )
        path = tokens[1]
        if path not in seen:
            seen.add(path)
            selected.append(path)
    return selected


def find_editor(repo_dir: Path) -> list[str]:
    """Determine the editor command to launch."""
    for env_var in ("VISUAL", "EDITOR"):
        val = os.environ.get(env_var, "").strip()
        if val:
            return shlex.split(val)

    res = run_git(["var", "GIT_EDITOR"], cwd=repo_dir, check=False)
    if res.returncode == 0:
        val = res.stdout.strip()
        if val and val != ":":
            return shlex.split(val)

    for fallback in ("nano", "vim", "vi"):
        if shutil.which(fallback):
            return [fallback]

    raise RuntimeError("No editor found. Set $VISUAL or $EDITOR.")


def open_in_editor(editor_cmd: list[str], initial_text: str) -> str | None:
    """Write initial_text to a temp file, open in editor, and return edited text (or None on error)."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix="worktree-cleanup-",
        suffix=".txt",
        delete=False,
    ) as tmp:
        tmp.write(initial_text)
        tmp_path = Path(tmp.name)

    try:
        res = subprocess.run([*editor_cmd, str(tmp_path)])
        if res.returncode != 0:
            return None
        return tmp_path.read_text(encoding="utf-8")
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            pass


def remove_worktrees(
    repo_dir: Path,
    selected_paths: list[str],
    worktrees_by_path: dict[str, WorktreeInfo],
    *,
    force: bool = False,
    delete_branches: bool = False,
) -> int:
    """Remove the selected worktrees (and optionally their merged branches). Returns error count."""
    errors = 0
    for path in selected_paths:
        wt = worktrees_by_path.get(path)
        if wt is None:
            print(f"Skipping unknown worktree path: {path}", file=sys.stderr)
            errors += 1
            continue

        if wt.prunable and not Path(path).exists():
            print(f"Worktree directory already missing ({path}); run `git worktree prune` to clean metadata.")
            continue

        cmd = ["worktree", "remove"]
        if force:
            cmd.append("--force")
        cmd.append(path)

        res = run_git(cmd, cwd=repo_dir, check=False)
        if res.returncode != 0:
            msg = res.stderr.strip() or res.stdout.strip() or f"exit code {res.returncode}"
            print(f"Failed to remove {path}: {msg}", file=sys.stderr)
            errors += 1
            continue

        print(f"Removed worktree: {path}")

        if delete_branches and wt.branch:
            b_res = run_git(["branch", "-d", wt.branch], cwd=repo_dir, check=False)
            if b_res.returncode == 0:
                print(f"Deleted branch: {wt.branch}")
            else:
                b_msg = b_res.stderr.strip() or b_res.stdout.strip()
                print(f"Kept branch {wt.branch}: {b_msg}", file=sys.stderr)

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Identify git worktrees merged into main/master without active "
            "Antigravity conversations, open an editor to review/edit the list, "
            "and remove selected worktrees."
        )
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Path inside the git repository (default: current directory).",
    )
    parser.add_argument(
        "--base",
        help="Base branch/ref to check merges against (default: auto-detect main/master).",
    )
    parser.add_argument(
        "--agy-dir",
        type=Path,
        default=default_agy_dir(),
        help="Antigravity data directory (default: $ANTIGRAVITY_APP_DATA_DIR or ~/.gemini/antigravity-cli).",
    )
    parser.add_argument(
        "-d",
        "--delete-branches",
        action="store_true",
        help="Also delete local branches (via `git branch -d`) after removing their worktree.",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Pass --force to `git worktree remove`.",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Print the proposed cleanup plan without opening an editor or deleting anything.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_dir = args.repo.resolve()

    top_res = run_git(["rev-parse", "--show-toplevel"], cwd=repo_dir, check=False)
    if top_res.returncode != 0:
        print(f"Not inside a git repository: {repo_dir}", file=sys.stderr)
        return 1

    try:
        base_branch = detect_base_branch(repo_dir, args.base)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    active_by_path, warning = load_active_conversations_by_path(args.agy_dir)
    if warning:
        print(f"Warning: {warning}", file=sys.stderr)

    worktrees = assess_worktrees(repo_dir, base_branch, active_by_path, cwd=Path.cwd())
    if not worktrees:
        print("No linked worktrees found.")
        return 0

    plan = format_cleanup_plan(worktrees, base_branch)
    if args.dry_run:
        print(plan, end="")
        return 0

    try:
        editor_cmd = find_editor(repo_dir)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    edited = open_in_editor(editor_cmd, plan)
    if edited is None:
        print("Editor exited with non-zero status; aborting without changes.")
        return 1

    try:
        selected = parse_cleanup_plan(edited)
    except ValueError as exc:
        print(f"Aborting: {exc}", file=sys.stderr)
        return 1

    if not selected:
        print("No worktrees selected for deletion.")
        return 0

    by_path = {wt.path: wt for wt in worktrees}
    errors = remove_worktrees(
        repo_dir,
        selected,
        by_path,
        force=args.force,
        delete_branches=args.delete_branches,
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
