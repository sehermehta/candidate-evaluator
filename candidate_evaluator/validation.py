from __future__ import annotations

import re
from typing import Any, Optional

from .roles import RoleProfile, get_role_profile


def expected_outcome(total_score: int, role: RoleProfile) -> str:
    for low, high, label in role.outcome_bands:
        if low <= total_score <= high:
            return label
    raise ValueError(f"Total Score {total_score} is outside the 0-{role.total_max} range.")


def validate_output_row(row: dict[str, Any], role_key: str = "design") -> list[str]:
    role = get_role_profile(role_key)
    errors: list[str] = []
    missing = [column for column in role.output_columns if column not in row]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")

    category_scores = []
    for column, maximum in role.category_scores.items():
        score = _as_int(row.get(column), column, errors)
        if score is None:
            continue
        allowed = role.allowed_scores.get(column)
        if allowed and score not in allowed:
            errors.append(f"{column} must be one of {sorted(allowed)}; got {score}.")
        elif score < 0 or score > maximum:
            errors.append(f"{column} must be between 0 and {maximum}; got {score}.")
        category_scores.append(score)

    total = _as_int(row.get("Total Score"), "Total Score", errors)
    if total is not None:
        if total > role.total_max:
            errors.append(f"Total Score must be no more than {role.total_max}; got {total}.")
        if len(category_scores) == len(role.category_scores) and total != sum(category_scores):
            errors.append(f"Total Score must equal category score sum {sum(category_scores)}; got {total}.")
        try:
            expected = expected_outcome(total, role)
            actual = row.get(role.outcome_column)
            if actual != expected:
                errors.append(f"{role.outcome_column} must be {expected!r} for Total Score {total}; got {actual!r}.")
        except ValueError as exc:
            errors.append(str(exc))

    evidence_values = [row.get(f"Strongest Evidence {i}", "") for i in range(1, 4)]
    nonempty_evidence = [value for value in evidence_values if str(value or "").strip()]
    if len(nonempty_evidence) > 3:
        errors.append("Strongest Evidence has more than three items.")

    rationale = str(row.get("Score Rationale", "") or "")
    if _word_count(rationale) > 75:
        errors.append(f"Score Rationale must be no longer than 75 words; got {_word_count(rationale)}.")

    return errors


def coerce_fixed_row(row: dict[str, Any], role_key: str = "design") -> dict[str, Any]:
    role = get_role_profile(role_key)
    fixed = {column: row.get(column, "") for column in role.output_columns}
    for column in list(role.category_scores) + ["Total Score"]:
        if fixed[column] != "":
            fixed[column] = int(fixed[column])
    return fixed


def _as_int(value: Any, name: str, errors: list[str]) -> Optional[int]:
    try:
        if isinstance(value, bool):
            raise ValueError
        return int(value)
    except (TypeError, ValueError):
        errors.append(f"{name} must be a whole number; got {value!r}.")
        return None


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))
