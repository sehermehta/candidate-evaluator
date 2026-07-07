from __future__ import annotations

from pathlib import Path
from typing import Any
from html import escape
import csv
import io

import streamlit as st

from candidate_evaluator.constants import DEFAULT_MODEL, DEFAULT_PARALLEL_OPENAI_CALLS, MODEL_OPTIONS, OUTPUTS_DIR
from candidate_evaluator.extractor import load_profiles, load_profiles_from_text, normalize_candidates, preview_candidates
from candidate_evaluator.progress import (
    candidate_status_rows,
    completed_preview_rows,
    init_run,
    load_candidates,
    load_status,
    make_run_id,
    mark_completed,
    mark_failed,
    progress_counts,
    reset_running,
    result_rows,
    result_rows_by_id,
    role_for_run,
    run_dir,
    run_select_options,
    save_exports,
    set_current,
)
from candidate_evaluator.roles import DEFAULT_ROLE_KEY, role_options
from candidate_evaluator.validation import coerce_fixed_row, validate_output_row


DEFAULT_RUBRIC_PATH = "/Users/sehermehta/Documents/Documents - Seher’s MacBook Air/Codex/candidate-evaluator/rubric.md"
DEFAULT_SAMPLE_PATH = "/Users/sehermehta/Documents/Documents - Seher’s MacBook Air/Codex/candidate-evaluator/sample.json"


def main() -> None:
    st.set_page_config(page_title="Candidate Evaluator", layout="wide")
    st.title("Candidate Evaluator")

    with st.sidebar:
        st.header("Inputs")
        role_key = _role_selector()
        json_upload = st.file_uploader("LinkedIn JSON", type=["json"])
        sample_path = st.text_input("Or JSON file path", value=DEFAULT_SAMPLE_PATH if Path(DEFAULT_SAMPLE_PATH).exists() else "")
        rubric_upload = st.file_uploader("Rubric Markdown", type=["md", "txt"])
        rubric_path = st.text_input("Or rubric file path", value=DEFAULT_RUBRIC_PATH if Path(DEFAULT_RUBRIC_PATH).exists() else "")
        model = _model_selector()
        parallel_calls = st.number_input(
            "Parallel OpenAI calls",
            min_value=1,
            max_value=20,
            value=DEFAULT_PARALLEL_OPENAI_CALLS,
            step=1,
        )
        api_key = st.text_input("OpenAI API key", type="password")
        approved = st.checkbox("I approve paid OpenAI API calls for this run")

    candidates, rubric_text = _load_inputs(json_upload, sample_path, rubric_upload, rubric_path)

    _show_preview(candidates, rubric_text)
    _show_run_controls(candidates, rubric_text, role_key, model, int(parallel_calls), api_key, approved)


def _role_selector() -> str:
    options = role_options()
    selected_label = st.selectbox("Evaluation role", options=list(options), index=0)
    return options[selected_label]


def _model_selector() -> str:
    custom_options = _custom_model_options()
    model_options = {**MODEL_OPTIONS, **custom_options}
    labels = list(model_options)
    default_index = labels.index("GPT-5.5") if "GPT-5.5" in labels else 0
    selected_label = st.selectbox("OpenAI model", options=labels, index=default_index)
    selected_model = model_options[selected_label]
    if selected_label == "Custom":
        return st.text_input("Custom model name", value=DEFAULT_MODEL).strip()
    st.caption(f"API model: `{selected_model}`")
    return selected_model


def _custom_model_options() -> dict[str, str]:
    with st.expander("Add custom model options"):
        raw_models = st.text_area(
            "Extra model names",
            placeholder="Paste exact model IDs, one per line. Example:\ngpt-4o-mini\ngpt-4.1-mini",
            help="Use this when OpenAI gives you access to a model that is not listed above.",
        )
    options = {}
    for model in _parse_custom_models(raw_models):
        options[f"Custom: {model}"] = model
    return options


def _parse_custom_models(raw_models: str) -> list[str]:
    models = []
    seen = set()
    for line in raw_models.replace(",", "\n").splitlines():
        model = line.strip()
        if not model or model in seen:
            continue
        seen.add(model)
        models.append(model)
    return models


def _load_inputs(json_upload: Any, sample_path: str, rubric_upload: Any, rubric_path: str) -> tuple[list[dict[str, Any]], str]:
    candidates: list[dict[str, Any]] = []
    rubric_text = ""
    try:
        if json_upload is not None:
            candidates = _candidates_from_json_text(json_upload.getvalue().decode("utf-8"))
        elif sample_path:
            path = Path(sample_path)
            candidates = _candidates_from_json_path(str(path), path.stat().st_mtime_ns)
    except Exception as exc:
        st.error(f"Could not read LinkedIn JSON: {exc}")

    try:
        if rubric_upload is not None:
            rubric_text = rubric_upload.getvalue().decode("utf-8")
        elif rubric_path:
            rubric_text = Path(rubric_path).read_text(encoding="utf-8")
    except Exception as exc:
        st.error(f"Could not read rubric: {exc}")
    return candidates, rubric_text


@st.cache_data(show_spinner=False)
def _candidates_from_json_text(text: str) -> list[dict[str, Any]]:
    return normalize_candidates(load_profiles_from_text(text))


@st.cache_data(show_spinner=False)
def _candidates_from_json_path(path: str, _mtime_ns: int) -> list[dict[str, Any]]:
    return normalize_candidates(load_profiles(path))


def _show_preview(candidates: list[dict[str, Any]], rubric_text: str) -> None:
    st.subheader("Extraction Preview")
    st.write(f"Candidates loaded: {len(candidates)}")
    st.write(f"Rubric loaded: {'yes' if rubric_text else 'no'}")
    if st.button("Preview first five candidates", disabled=not candidates):
        st.session_state["preview"] = preview_candidates(candidates, limit=5)
    if st.session_state.get("preview"):
        _display_table(st.session_state["preview"])


def _show_run_controls(
    candidates: list[dict[str, Any]],
    rubric_text: str,
    role_key: str,
    model: str,
    parallel_calls: int,
    api_key: str,
    approved: bool,
) -> None:
    st.subheader("Evaluation")
    existing_run_options = run_select_options()
    selected_run_label = st.selectbox("Resume run", options=[""] + list(existing_run_options), index=0)
    selected_run = existing_run_options.get(selected_run_label, "")

    col1, col2, col3 = st.columns(3)
    with col1:
        start_clicked = st.button("Start / resume evaluation", disabled=not candidates or not rubric_text)
    with col2:
        retry_clicked = st.button("Retry failed candidates", disabled=not selected_run)
    with col3:
        export_clicked = st.button("Save exports", disabled=not selected_run)

    active_run = selected_run or st.session_state.get("active_run_id", "")
    ran_evaluation = False
    if start_clicked:
        _require_api_ready(api_key, approved)
        if not active_run:
            active_run = make_run_id()
            init_run(active_run, candidates, rubric_text, model, role_key)
            st.session_state["active_run_id"] = active_run
        _run_evaluation(active_run, api_key, model, parallel_calls, retry_failed=False)
        ran_evaluation = True

    if retry_clicked:
        _require_api_ready(api_key, approved)
        _run_evaluation(selected_run, api_key, model, parallel_calls, retry_failed=True)
        ran_evaluation = True

    if export_clicked:
        rows = result_rows(selected_run)
        csv_path, xlsx_path = save_exports(selected_run, rows)
        st.success(f"Saved exports: {csv_path} and {xlsx_path}")

    if active_run and not ran_evaluation:
        _show_evaluation_status(active_run, parallel_calls)
    if active_run:
        _show_downloads(active_run)


def _require_api_ready(api_key: str, approved: bool) -> None:
    if not approved:
        st.error("Approve OpenAI API calls before starting an evaluation.")
        st.stop()
    if not api_key:
        st.error("Paste an OpenAI API key before starting an evaluation.")
        st.stop()


def _run_evaluation(run_id: str, api_key: str, model: str, parallel_calls: int, retry_failed: bool) -> None:
    from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

    reset_running(run_id)
    candidates = load_candidates(run_id)
    status = load_status(run_id)
    role_key = status.get("role", DEFAULT_ROLE_KEY)
    status_by_id = status.get("candidates", {})
    completed_row_ids = set(result_rows_by_id(run_id))
    progress = st.progress(0)
    message = st.empty()
    dashboard = st.empty()
    preview = st.empty()
    summary = st.empty()

    worklist = []
    for candidate in candidates:
        candidate_id = candidate["linkedin_profile_id"]
        state = status_by_id.get(candidate_id, {}).get("state", "pending")
        if retry_failed and state == "failed":
            worklist.append(candidate)
        elif not retry_failed and state != "completed" and candidate_id not in completed_row_ids:
            worklist.append(candidate)

    rubric_text = (run_dir(run_id) / "rubric.md").read_text(encoding="utf-8")
    total = max(len(worklist), 1)
    max_workers = max(1, min(int(parallel_calls), len(worklist) or 1))
    completed_in_pass = 0
    pending = list(worklist)
    active: dict[Any, dict[str, Any]] = {}
    message.info(f"Running up to {max_workers} candidates at a time.")
    _render_live_status(run_id, dashboard, preview, summary, run_finished=False, parallel_calls=max_workers)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while pending and len(active) < max_workers:
            _submit_candidate(executor, active, pending, run_id, api_key, model, rubric_text, role_key)
        _render_live_status(run_id, dashboard, preview, summary, run_finished=False, parallel_calls=max_workers)

        while active:
            done, _ = wait(active.keys(), return_when=FIRST_COMPLETED)
            for future in done:
                candidate = active.pop(future)
                candidate_id = candidate["linkedin_profile_id"]
                result = future.result()
                if result["state"] == "completed":
                    mark_completed(run_id, candidate_id, result["row"], result["raw"], result["elapsed_seconds"])
                else:
                    mark_failed(run_id, candidate_id, result["error"], elapsed_seconds=result["elapsed_seconds"])
                completed_in_pass += 1
                progress.progress(completed_in_pass / total)

                if pending:
                    _submit_candidate(executor, active, pending, run_id, api_key, model, rubric_text, role_key)

            _render_live_status(run_id, dashboard, preview, summary, run_finished=False, parallel_calls=max_workers)

    message.success("Evaluation pass finished.")
    _render_live_status(run_id, dashboard, preview, summary, run_finished=True, parallel_calls=max_workers)


def _submit_candidate(
    executor: ThreadPoolExecutor,
    active: dict[Any, dict[str, Any]],
    pending: list[dict[str, Any]],
    run_id: str,
    api_key: str,
    model: str,
    rubric_text: str,
    role_key: str,
) -> None:
    candidate = pending.pop(0)
    candidate_id = candidate["linkedin_profile_id"]
    set_current(run_id, candidate_id)
    future = executor.submit(_evaluate_candidate_for_run, api_key, model, rubric_text, candidate, role_key)
    active[future] = candidate


def _evaluate_candidate_for_run(
    api_key: str,
    model: str,
    rubric_text: str,
    candidate: dict[str, Any],
    role_key: str,
) -> dict[str, Any]:
    import time

    started = time.monotonic()
    try:
        from candidate_evaluator.openai_scoring import evaluate_candidate

        grading, raw = evaluate_candidate(api_key=api_key, model=model, rubric_text=rubric_text, candidate=candidate, role_key=role_key)
        row = {**candidate["source_row"], **grading}
        row = coerce_fixed_row(row, role_key)
        errors = validate_output_row(row, role_key)
        if errors:
            raise ValueError("; ".join(errors))
        return {"state": "completed", "row": row, "raw": raw, "elapsed_seconds": time.monotonic() - started}
    except Exception as exc:
        return {"state": "failed", "error": str(exc), "elapsed_seconds": time.monotonic() - started}


def _show_evaluation_status(run_id: str, parallel_calls: int = DEFAULT_PARALLEL_OPENAI_CALLS) -> None:
    st.subheader("Evaluation Status")
    _render_live_status(
        run_id,
        st.empty(),
        st.empty(),
        st.empty(),
        run_finished=_run_is_finished(run_id),
        parallel_calls=parallel_calls,
    )


def _render_live_status(
    run_id: str,
    dashboard: Any,
    preview: Any,
    summary: Any,
    run_finished: bool,
    parallel_calls: int,
) -> None:
    counts = progress_counts(run_id)
    role = role_for_run(run_id)
    with dashboard.container():
        st.write(f"Evaluated: {counts['evaluated']} / {counts['total']}")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Completed", counts["completed"])
        col2.metric("Failed", counts["failed"])
        col3.metric("Remaining", counts["remaining"])
        col4.metric("Total candidates", counts["total"])
        col5.metric("Avg sec / candidate", _format_seconds(counts["avg_seconds_per_candidate"]))
        col6.metric("Est. time remaining", _format_eta(counts, parallel_calls))
        st.write(f"Current candidate: {counts['current_candidate'] or 'None'}")
        _display_table(candidate_status_rows(run_id, role.key))

    with preview.container():
        st.subheader("Completed Results Preview")
        rows = completed_preview_rows(run_id, role.key)
        if rows:
            _display_table(rows)
        else:
            st.caption("No completed candidates yet.")

    if run_finished:
        with summary.container():
            st.subheader("Run Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total candidates", counts["total"])
            col2.metric("Completed", counts["completed"])
            col3.metric("Failed", counts["failed"])
            col4.metric("Export ready", "yes" if counts["export_ready"] else "no")


def _run_is_finished(run_id: str) -> bool:
    counts = progress_counts(run_id)
    return counts["total"] > 0 and counts["evaluated"] == counts["total"]


def _format_seconds(value: float) -> str:
    if not value:
        return "n/a"
    return f"{value:.1f}s"


def _format_eta(counts: dict[str, Any], parallel_calls: int) -> str:
    avg_seconds = counts.get("avg_seconds_per_candidate", 0.0)
    remaining = counts.get("remaining", 0)
    if not avg_seconds or not remaining:
        return "n/a"
    effective_parallelism = max(1, min(int(parallel_calls), remaining + counts.get("running", 0)))
    return _format_duration(avg_seconds * remaining / effective_parallelism)


def _format_duration(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    minutes, secs = divmod(seconds, 60)
    hours, mins = divmod(minutes, 60)
    if hours:
        return f"{hours}h {mins}m"
    if mins:
        return f"{mins}m {secs}s"
    return f"{secs}s"


def _show_downloads(run_id: str) -> None:
    role = role_for_run(run_id)
    rows = result_rows(run_id)
    if not rows:
        return
    fixed_rows = [{column: row.get(column, "") for column in role.output_columns} for row in rows]
    csv_data = _rows_to_csv_bytes(fixed_rows, role.output_columns)
    st.subheader("Downloads")
    csv_col, excel_col = st.columns(2)
    with csv_col:
        st.download_button(
            "Download CSV",
            csv_data,
            file_name=f"candidate_evaluation_{run_id}.csv",
            mime="text/csv",
            key=f"download-csv-{run_id}",
        )
    xlsx_path = Path(OUTPUTS_DIR) / f"candidate_evaluation_{role.key}_{run_id}.xlsx"
    with excel_col:
        if xlsx_path.exists():
            st.download_button(
                "Download Excel",
                xlsx_path.read_bytes(),
                file_name=f"candidate_evaluation_{run_id}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download-excel-{run_id}",
            )
        else:
            st.caption("Click Save exports to create the Excel file.")
    st.subheader("Completed Output")
    _display_table(fixed_rows)


def _rows_to_csv_bytes(rows: list[dict[str, Any]], columns: list[str]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def _display_table(rows: list[dict[str, Any]]) -> None:
    if not rows:
        st.caption("No rows to show.")
        return
    columns = list(rows[0].keys())
    header = "".join(f"<th>{escape(str(column))}</th>" for column in columns)
    body = []
    for row in rows:
        cells = "".join(f"<td>{escape(str(row.get(column, '')))}</td>" for column in columns)
        body.append(f"<tr>{cells}</tr>")
    st.markdown(
        """
        <style>
        .candidate-table-wrap {
            max-height: 520px;
            overflow: auto;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
        }
        .candidate-table {
            border-collapse: collapse;
            width: max-content;
            min-width: 100%;
            font-size: 13px;
            line-height: 1.35;
        }
        .candidate-table th,
        .candidate-table td {
            border-bottom: 1px solid #e5e7eb;
            border-right: 1px solid #eef2f7;
            padding: 8px 10px;
            vertical-align: top;
            max-width: 360px;
            white-space: normal;
            word-break: break-word;
        }
        .candidate-table th {
            position: sticky;
            top: 0;
            background: #f8fafc;
            z-index: 1;
            text-align: left;
            font-weight: 600;
        }
        </style>
        """
        + f"<div class='candidate-table-wrap'><table class='candidate-table'><thead><tr>{header}</tr></thead><tbody>{''.join(body)}</tbody></table></div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
