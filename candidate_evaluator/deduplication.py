"""Role/rubric history and process-safe evaluation ownership.

Successful run receipts are the durable registry's source of truth. Rebuilding
from them avoids stale claims after a crash and seeds history from old runs.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator
import hashlib
import json

from . import progress


def scope_key(role_key: str, rubric_text: str, custom_role_config: dict[str, Any] | None = None) -> str:
    payload = [role_key, rubric_text.replace("\r\n", "\n").strip(),
               custom_role_config if role_key == "custom" else None]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def original_id(candidate: dict[str, Any]) -> str:
    # Legacy runs retain the unsuffixed ID in their source row. Never strip a
    # suffix: a real source ID may itself contain '--duplicate-2'.
    value = candidate.get("original_profile_id")
    if value is None:
        value = (candidate.get("source_row") or {}).get("LinkedIn Profile ID")
    value = str(value or candidate["linkedin_profile_id"]).strip()
    # Generated row numbers are not identities across uploads.
    if value == f"candidate-{candidate.get('source_index', -1) + 1}":
        return ""
    return value


def run_scope(run_id: str) -> str:
    status = progress.load_status(run_id)
    if status.get("_load_error"):
        raise RuntimeError(f"Cannot read evaluation history for {run_id}")
    rubric = (progress.run_dir(run_id) / "rubric.md").read_text(encoding="utf-8")
    return scope_key(status.get("role", progress.DEFAULT_ROLE_KEY), rubric,
                     status.get("custom_role_config"))


def completed_history(scope: str, recover: bool = False) -> dict[str, str]:
    history = {}
    for run_id in reversed(progress.list_runs()):
        if run_scope(run_id) != scope:
            continue
        if recover:
            progress.recover_batch_results(run_id)
        completed = progress.result_rows_by_id(run_id)
        for candidate in progress.load_candidates(run_id):
            identity = original_id(candidate)
            if identity and candidate["linkedin_profile_id"] in completed:
                history.setdefault(identity, run_id)
    return history


def select_unique(
    candidates: list[dict[str, Any]], history: dict[str, str],
    input_issue: Callable[[dict[str, Any]], str],
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    eligible, duplicates, seen = [], {}, {}
    for candidate in candidates:
        identity = original_id(candidate)
        row_id = candidate["linkedin_profile_id"]
        if identity and identity in history:
            duplicates[row_id] = f"Duplicate: already evaluated for this role and rubric in run {history[identity]}."
        elif identity and identity in seen:
            duplicates[row_id] = f"Duplicate: repeated profile in this upload (first valid record: {seen[identity]})."
        else:
            eligible.append(candidate)
            if identity and not input_issue(candidate):
                seen[identity] = row_id
    return eligible, duplicates


@contextmanager
def evaluation_lock(scope: str) -> Iterator[dict[str, str]]:
    # Hold ownership through durable receipt commits. OS locks release on
    # exceptions/process exit, so no time-based lease can expire during an API call.
    if progress.fcntl is None:
        raise RuntimeError("Role-level evaluation locking requires a Unix host.")
    root = Path(progress.RUNS_DIR).parent / "evaluation_registry"
    root.mkdir(parents=True, exist_ok=True)
    with (root / f"{scope}.lock").open("a") as handle:
        try:
            progress.fcntl.flock(handle, progress.fcntl.LOCK_EX | progress.fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("An evaluation for this role and rubric is already running. Try again after it finishes.") from None
        try:
            history = completed_history(scope, recover=True)
            progress._write_json(root / f"{scope}.json", history)
            yield history
            progress._write_json(root / f"{scope}.json", completed_history(scope))
        finally:
            progress.fcntl.flock(handle, progress.fcntl.LOCK_UN)
