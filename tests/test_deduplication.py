from pathlib import Path

import pytest

from candidate_evaluator import progress
from candidate_evaluator.deduplication import (
    completed_history, evaluation_lock, original_id, run_scope, scope_key, select_unique,
)
from candidate_evaluator.extractor import normalize_candidates


@pytest.fixture
def storage(tmp_path, monkeypatch):
    monkeypatch.setattr(progress, "RUNS_DIR", str(tmp_path / "runs"))
    return tmp_path


def candidates(ids):
    return normalize_candidates([{"publicIdentifier": identity, "firstName": "Test"} for identity in ids])


def test_repeated_upload_records_keep_source_identity():
    records = candidates([f"id-{i}" for i in range(93)] + [f"id-{i}" for i in range(7)])
    eligible, duplicates = select_unique(records, {}, lambda c: "")
    assert len(eligible) == 93
    assert len(duplicates) == 7
    assert records[-1]["original_profile_id"] == "id-6"
    assert records[-1]["linkedin_profile_id"] == "id-6--duplicate-2"


def test_first_valid_occurrence_wins():
    records = candidates(["a", "a", "a"])
    eligible, duplicates = select_unique(records, {}, lambda c: "invalid" if c["source_index"] == 0 else "")
    assert [c["source_index"] for c in eligible] == [0, 1]
    assert list(duplicates) == ["a--duplicate-3"]


def test_history_only_success_and_same_role_rubric(storage):
    records = candidates(["a", "b", "c"])
    progress.init_run("old", records, "rubric", "model", role_key="backend_engineer")
    progress.mark_completed("old", "a", {"Candidate Name": "A"}, {})
    progress.mark_failed("old", "b", "failure")
    progress.mark_skipped("old", "c", "unusable")
    history = completed_history(run_scope("old"))
    assert history == {"a": "old"}
    eligible, duplicates = select_unique(records, history, lambda c: "")
    assert len(eligible) == 2
    assert "old" in duplicates["a"]
    assert not completed_history(scope_key("backend_engineer", "new rubric"))
    assert not completed_history(scope_key("safegold", "rubric"))
    # Legacy source rows preserve the original identifier.
    legacy = dict(records[0], linkedin_profile_id="a--duplicate-2")
    legacy.pop("original_profile_id")
    assert original_id(legacy) == "a"


def test_custom_roles_and_rubric_line_endings():
    assert scope_key("custom", "r", {"name": "A"}) != scope_key("custom", "r", {"name": "B"})
    assert scope_key("role", "r\r\nx\n") == scope_key("role", "r\nx")


def test_lock_excludes_overlap_and_releases_after_failure(storage):
    with pytest.raises(ValueError):
        with evaluation_lock("scope"):
            with pytest.raises(RuntimeError, match="already running"):
                with evaluation_lock("scope"):
                    pass
            raise ValueError("interrupted")
    with evaluation_lock("scope") as history:
        assert history == {}


def test_recover_success_receipt_and_exclude_duplicates_from_exports(storage):
    records = candidates(["a", "a"])
    progress.init_run("old", records, "rubric", "model")
    # Simulate a response persisted before a process crash.
    progress._write_json(progress.run_dir("old") / "batch_receipts" / "receipt.json", {
        "receipt_id": "receipt", "candidates": [{"candidate_id": "a", "result": {
            "state": "completed", "row": {"Candidate Name": "A"}}}]})
    with evaluation_lock(run_scope("old")) as history:
        assert history == {"a": "old"}
    progress.init_run("new", records, "rubric", "model")
    _, duplicates = select_unique(records, history, lambda c: "")
    for identity, reason in duplicates.items():
        progress.mark_skipped("new", identity, reason)
    assert progress.result_rows("new") == []
    assert progress.progress_counts("new")["skipped"] == 2
    # Reopen the persistent store (a subsequent process uses the same files).
    with evaluation_lock(run_scope("new")) as reopened:
        assert reopened == history


def test_generated_row_ids_do_not_match_between_uploads():
    record = {"linkedin_profile_id": "candidate-1", "source_index": 0}
    assert original_id(record) == ""


def test_app_dispatches_only_unique_profiles(storage, monkeypatch):
    import app
    records = candidates(["a", "a", "b"])
    progress.init_run("new", records, "rubric", "model")
    monkeypatch.setattr(app, "rubric_input_issue", lambda *args: "")
    monkeypatch.setattr(app, "_candidate_input_issue_for_role", lambda *args: "")
    monkeypatch.setattr(app, "_render_live_status", lambda *args, **kwargs: None)
    sent = []
    def evaluate(*args):
        batch = args[3]
        sent.extend(c["original_profile_id"] for c in batch)
        return {"results": [{"state": "completed", "row": {"Candidate Name": "Test"}} for c in batch]}
    monkeypatch.setattr(app, "_evaluate_candidate_batch_for_run", evaluate)
    app._run_evaluation("new", "fake", 2, False)
    assert sent == ["a", "b"]
    assert progress.progress_counts("new")["skipped"] == 1
    assert len(progress.result_rows("new")) == 2
    progress.init_run("next", candidates(["a", "b", "c"]), "rubric", "model")
    app._run_evaluation("next", "fake", 2, False)
    assert sent == ["a", "b", "c"]
    assert len(progress.result_rows("next")) == 1
