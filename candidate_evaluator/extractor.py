from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Union

from .constants import SOURCE_COLUMNS


ALLOWED_EXPERIENCE_FIELDS = [
    "companyName",
    "position",
    "title",
    "description",
    "employmentType",
    "startDate",
    "endDate",
    "duration",
]


def load_profiles_from_text(text: str) -> list[dict[str, Any]]:
    data = json.loads(text)
    if isinstance(data, list):
        profiles = data
    elif isinstance(data, dict):
        profiles = _find_profile_list(data)
    else:
        raise ValueError("JSON root must be a list of profiles or an object containing a profile list.")
    if not all(isinstance(item, dict) for item in profiles):
        raise ValueError("Every candidate profile must be a JSON object.")
    return profiles


def load_profiles(path: Union[str, Path]) -> list[dict[str, Any]]:
    return load_profiles_from_text(Path(path).read_text(encoding="utf-8"))


def _find_profile_list(data: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("items", "profiles", "data", "results"):
        value = data.get(key)
        if isinstance(value, list) and all(isinstance(item, dict) for item in value):
            return value
    for value in data.values():
        if isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            return value
    raise ValueError("Could not find a list of candidate profiles in the JSON object.")


def normalize_candidate(profile: dict[str, Any], index: int) -> dict[str, Any]:
    experiences = [_normalize_experience(exp, i) for i, exp in enumerate(profile.get("experience") or []) if isinstance(exp, dict)]
    education = [_format_education(edu) for edu in (profile.get("education") or []) if isinstance(edu, dict)]
    candidate = {
        "source_index": index,
        "linkedin_profile_id": _first_nonempty(profile.get("publicIdentifier"), profile.get("id"), f"candidate-{index + 1}"),
        "linkedin_url": _clean(profile.get("linkedinUrl")),
        "candidate_name": _candidate_name(profile),
        "headline": _clean(profile.get("headline")),
        "about": _clean(profile.get("about")),
        "website": _first_website(profile.get("websites")),
        "education": education,
        "experiences": experiences,
    }
    candidate["source_row"] = build_source_row(candidate)
    return candidate


def normalize_candidates(profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [normalize_candidate(profile, index) for index, profile in enumerate(profiles)]


def build_source_row(candidate: dict[str, Any]) -> dict[str, str]:
    experiences = candidate.get("experiences") or []
    education = candidate.get("education") or []
    row = {
        "LinkedIn Profile ID": candidate.get("linkedin_profile_id", ""),
        "LinkedIn URL": candidate.get("linkedin_url", ""),
        "Candidate Name": candidate.get("candidate_name", ""),
        "Headline": candidate.get("headline", ""),
        "Experience 0": _format_experience_for_cell(experiences[0]) if len(experiences) > 0 else "",
        "Experience 1": _format_experience_for_cell(experiences[1]) if len(experiences) > 1 else "",
        "Education 0": education[0] if len(education) > 0 else "",
        "Education 1": education[1] if len(education) > 1 else "",
        "About": candidate.get("about", ""),
        "Website": candidate.get("website", ""),
    }
    return {column: row.get(column, "") for column in SOURCE_COLUMNS}


def preview_candidates(candidates: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    preview = []
    for candidate in candidates[:limit]:
        item = dict(candidate["source_row"])
        item["Experience Entries Detected"] = len(candidate.get("experiences") or [])
        for i, exp in enumerate(candidate.get("experiences") or []):
            item[f"experience/{i}"] = _format_experience_for_cell(exp)
        preview.append(item)
    return preview


def _normalize_experience(exp: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "index": index,
        "company_name": _clean(exp.get("companyName")),
        "position_or_title": _clean(_first_nonempty(exp.get("position"), exp.get("title"))),
        "description": _clean(exp.get("description")),
        "employment_type": _clean(exp.get("employmentType")),
        "start_date": _format_date(exp.get("startDate")),
        "end_date": _format_date(exp.get("endDate")),
        "duration": _clean(exp.get("duration")),
    }


def _format_experience_for_cell(exp: dict[str, Any]) -> str:
    parts = [
        exp.get("position_or_title"),
        exp.get("company_name"),
        exp.get("employment_type"),
        _date_range(exp.get("start_date"), exp.get("end_date")),
        exp.get("duration"),
        exp.get("description"),
    ]
    return " | ".join(str(part).strip() for part in parts if _clean(part))


def _format_education(edu: dict[str, Any]) -> str:
    parts = [edu.get("schoolName"), edu.get("degree"), edu.get("fieldOfStudy"), edu.get("period")]
    return " | ".join(_clean(part) for part in parts if _clean(part))


def _format_date(value: Any) -> str:
    if isinstance(value, dict):
        return _clean(value.get("text")) or " ".join(_clean(value.get(k)) for k in ("month", "year") if _clean(value.get(k)))
    return _clean(value)


def _date_range(start: str, end: str) -> str:
    if start and end:
        return f"{start} - {end}"
    return start or end or ""


def _candidate_name(profile: dict[str, Any]) -> str:
    first_last = " ".join(part for part in [_clean(profile.get("firstName")), _clean(profile.get("lastName"))] if part)
    return _first_nonempty(first_last, profile.get("fullName"), profile.get("name"), profile.get("publicIdentifier"), "")


def _first_website(value: Any) -> str:
    if isinstance(value, list):
        return _clean(value[0]) if value else ""
    return _clean(value)


def _first_nonempty(*values: Any) -> str:
    for value in values:
        cleaned = _clean(value)
        if cleaned:
            return cleaned
    return ""


def _clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return " ".join(value.split())
    return str(value)
