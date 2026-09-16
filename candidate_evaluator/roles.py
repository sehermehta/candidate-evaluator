from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Optional

from .constants import SOURCE_COLUMNS


@dataclass(frozen=True)
class RoleProfile:
    key: str
    label: str
    role_name: str
    grading_columns: list[str]
    category_scores: OrderedDict[str, float]
    allowed_scores: dict[str, set[float]]
    total_column: str
    total_max: float
    outcome_column: str
    outcome_bands: list[tuple[float, float, str]]
    evidence_confidence_values: list[str]
    system_prompt: str
    instructions: list[str]
    internal_role_flag_name: str
    internal_role_evidence_name: str
    export_columns: Optional[list[str]] = None
    numeric_scores: bool = False
    ranked: bool = False
    column_enums: Optional[dict[str, list[str]]] = None
    ranking_tiebreaker_columns: Optional[list[str]] = None
    strongest_evidence_columns: Optional[list[str]] = None
    rationale_min_words: int = 0

    @property
    def output_columns(self) -> list[str]:
        return self.export_columns or (SOURCE_COLUMNS + self.grading_columns)


DESIGN_GRADING_COLUMNS = [
    "Total Relevant Design Experience — Months",
    "Total Relevant Design Experience — Years and Months",
    "Total Weighted Relevant Design Experience — Months",
    "Total Weighted Relevant Design Experience — Years and Months",
    "Weighted Design-Agency Experience — Months",
    "Weighted Design-Agency Experience — Years and Months",
    "UX/Product Design Experience and Career Depth — Score",
    "User Research, Insight and Synthesis — Score",
    "UX Craft and Complex Workflow Design — Score",
    "Product Thinking, UX Strategy and Ownership — Score",
    "Validation, Behavioural Data and Outcomes — Score",
    "Design Systems, Engineering and Accessibility — Score",
    "Design-Agency Experience and Breadth — Score",
    "Total Score",
    "Ranking",
    "Evidence Confidence",
    "Strongest Evidence 1",
    "Strongest Evidence 2",
    "Strongest Evidence 3",
    "Missing or Unclear Information",
    "Score Rationale",
]

DESIGN_CATEGORY_SCORES = OrderedDict(
    [
        ("UX/Product Design Experience and Career Depth — Score", 15),
        ("User Research, Insight and Synthesis — Score", 12),
        ("UX Craft and Complex Workflow Design — Score", 10),
        ("Product Thinking, UX Strategy and Ownership — Score", 9),
        ("Validation, Behavioural Data and Outcomes — Score", 5),
        ("Design Systems, Engineering and Accessibility — Score", 4),
        ("Design-Agency Experience and Breadth — Score", 5),
    ]
)

QA_GRADING_COLUMNS = [
    "Total Relevant QA Experience — Months",
    "Total Relevant QA Experience — Years and Months",
    "Total Weighted Relevant QA Experience — Months",
    "Total Weighted Relevant QA Experience — Years and Months",
    "Rest Assured / API Automation — Score",
    "Manual API / Postman — Score",
    "Python Automation — Score",
    "Java Proficiency — Score",
    "Selenium UI Automation — Score",
    "SQL and Data Validation — Score",
    "CI/CD and Pipelines — Score",
    "Total Score",
    "Decision",
    "Evidence Confidence",
    "Strongest Evidence 1",
    "Strongest Evidence 2",
    "Strongest Evidence 3",
    "Missing or Unclear Information",
    "Score Rationale",
]

QA_CATEGORY_SCORES = OrderedDict(
    [
        ("Rest Assured / API Automation — Score", 35),
        ("Manual API / Postman — Score", 15),
        ("Python Automation — Score", 15),
        ("Java Proficiency — Score", 15),
        ("Selenium UI Automation — Score", 15),
        ("SQL and Data Validation — Score", 10),
        ("CI/CD and Pipelines — Score", 5),
    ]
)

QA_ALLOWED_SCORES = {
    "Rest Assured / API Automation — Score": {0, 10, 18, 26, 35},
    "Manual API / Postman — Score": {0, 5, 10, 15},
    "Python Automation — Score": {0, 5, 10, 15},
    "Java Proficiency — Score": {0, 5, 10, 15},
    "Selenium UI Automation — Score": {0, 5, 10, 15},
    "SQL and Data Validation — Score": {0, 3, 6, 10},
    "CI/CD and Pipelines — Score": {0, 2, 3, 5},
}


BACKEND_GRADING_COLUMNS = [
    "Current Company",
    "Current Title",
    "PHP Score (/20)",
    "Python Score (/20)",
    "Laravel Score (/12)",
    "AWS Score (/8)",
    "Final Score (/60)",
    "PHP Unverified",
    "Python Unverified",
    "Backend Relevance Unverified",
    "Seniority Unverified",
    "Date-Quality Warning",
    "Strongest Evidence",
    "Missing or Unclear Information",
    "Score Rationale",
    # These are retained internally for deterministic ranking tie-breaks.
    "Weighted Recency Subtotal",
    "Weighted Duration Subtotal",
    "Weighted Evidence Subtotal",
]

BACKEND_OUTPUT_COLUMNS = [
    "Rank Number",
    "Candidate",
    "Profile URL",
    "Current Company",
    "Current Title",
    "PHP Score (/20)",
    "Python Score (/20)",
    "Laravel Score (/12)",
    "AWS Score (/8)",
    "Final Score (/60)",
    "PHP Unverified",
    "Python Unverified",
    "Backend Relevance Unverified",
    "Seniority Unverified",
    "Date-Quality Warning",
    "Strongest Evidence",
    "Missing or Unclear Information",
    "Score Rationale",
]

BACKEND_CATEGORY_SCORES = OrderedDict(
    [
        ("PHP Score (/20)", 20),
        ("Python Score (/20)", 20),
        ("Laravel Score (/12)", 12),
        ("AWS Score (/8)", 8),
    ]
)

BACKEND_WARNING_ENUMS = {
    "PHP Unverified": ["Yes", "No"],
    "Python Unverified": ["Yes", "No"],
    "Backend Relevance Unverified": ["Yes", "No"],
    "Seniority Unverified": ["Yes", "No"],
    "Date-Quality Warning": ["Yes", "No"],
}


ROLE_PROFILES = {
    "design": RoleProfile(
        key="design",
        label="Design / Product UX",
        role_name="senior Product/UX Designer",
        grading_columns=DESIGN_GRADING_COLUMNS,
        category_scores=DESIGN_CATEGORY_SCORES,
        allowed_scores={},
        total_column="Total Score",
        total_max=60,
        outcome_column="Ranking",
        outcome_bands=[
            (45, 60, "Strong relevance"),
            (32, 44, "Good relevance"),
            (20, 31, "Limited relevance"),
            (0, 19, "Low relevance"),
        ],
        evidence_confidence_values=["High", "Medium", "Low"],
        system_prompt=(
            "You are a strict candidate evaluator for senior Product/UX Designer profiles. "
            "Score only from the supplied candidate fields and the supplied rubric. "
            "Use all experience entries, not only the first three. "
            "Use whole-number category scores and obey the supplied category maxima. "
            "Total Score must equal the sum of category scores and must not exceed 60. "
            "Ranking bands are: 45-60 Strong relevance, 32-44 Good relevance, "
            "20-31 Limited relevance, 0-19 Low relevance. "
            "Strongest Evidence must contain no more than three material evidence points. "
            "Score Rationale must be 50 to 75 words and no longer than 75 words."
        ),
        instructions=[
            "Use every experience entry supplied in candidate.experiences for scoring.",
            "Treat every experience index as a separate role, including multiple roles at the same company.",
            "Ignore skills, projects, courses, certifications, images, logos, followers, connections, IDs other than LinkedIn Profile ID, extra URLs, and scraper metadata.",
            "Return only fields required by the JSON schema.",
        ],
        internal_role_flag_name="relevant_design_role",
        internal_role_evidence_name="design_evidence_extracted",
    ),
    "qa": RoleProfile(
        key="qa",
        label="QA Automation Engineer",
        role_name="Senior QA Automation Engineer",
        grading_columns=QA_GRADING_COLUMNS,
        category_scores=QA_CATEGORY_SCORES,
        allowed_scores=QA_ALLOWED_SCORES,
        total_column="Total Score",
        total_max=100,
        outcome_column="Decision",
        outcome_bands=[
            (70, 100, "Shortlist"),
            (55, 69, "Hold"),
            (0, 54, "Reject"),
        ],
        evidence_confidence_values=["High", "Medium", "Low"],
        system_prompt=(
            "You are a strict candidate evaluator for Senior QA Automation Engineer profiles. "
            "Score only explicit evidence from the supplied professional experience entries and supplied rubric. "
            "Use all available experience entries supplied in candidate.experiences. "
            "Do not use headline, about, skills, education, certifications, projects, courses, recommendations, posts, or external assumptions for QA scoring. "
            "Use only allowed discrete category scores from the schema. "
            "Total Score must equal the sum of category scores and must not exceed 100. "
            "Decision bands are: 70-100 Shortlist, 55-69 Hold, 0-54 Reject. "
            "Strongest Evidence must contain no more than three material evidence points. "
            "Score Rationale must be 50 to 75 words and no longer than 75 words."
        ),
        instructions=[
            "Use every professional experience entry supplied in candidate.experiences for QA scoring.",
            "Count an experience only if title or description shows QA, test automation, software testing, SDET, or test engineering work.",
            "Ignore headline, about, skills, education, certifications, projects, courses, recommendations, posts, currentPosition, and external information for scoring.",
            "Score Python and Java separately; do not infer one from the other.",
            "Return only fields required by the JSON schema.",
        ],
        internal_role_flag_name="counted_for_qa_scoring",
        internal_role_evidence_name="qa_evidence_extracted",
    ),
    "backend": RoleProfile(
        key="backend",
        label="Backend Engineer",
        role_name="Senior Backend Engineer",
        grading_columns=BACKEND_GRADING_COLUMNS,
        category_scores=BACKEND_CATEGORY_SCORES,
        allowed_scores={},
        total_column="Final Score (/60)",
        total_max=60,
        outcome_column="Rank Number",
        outcome_bands=[],
        evidence_confidence_values=["High", "Medium", "Low"],
        system_prompt=(
            "You are a strict LinkedIn evidence evaluator for Senior Backend Engineer profiles. "
            "Score PHP, Python, Laravel, and AWS independently using only the supplied rubric and permitted candidate fields. "
            "Use all available experience entries. Do not infer PHP from Laravel, and do not infer Python from Django, Flask, or FastAPI. "
            "Use the strongest evidence source without stacking evidence points. Apply recency and duration independently per technology, "
            "including the rubric's Tier A, B, and C duration caps and non-overlapping duration rules. "
            "Technology scores and Final Score may contain one decimal place. Final Score must equal the four technology scores and must not exceed 60. "
            "Warnings do not change the score. Use 'Unverified' neutrally when evidence is absent. "
            "Return no more than three strongest evidence points in the single Strongest Evidence field, separated by ' | '. "
            "Score Rationale must contain 50 to 75 words."
        ),
        instructions=[
            "Use Headline, About, experience title, description, dates, duration, and experience-level skills only as permitted by the rubric.",
            "Do not use global skills, education, certifications, projects, courses, recommendations, followers, connections, or external information.",
            "Treat duplicate experience records as one record for evidence and duration; otherwise evaluate every experience entry.",
            "Current Company and Current Title are identification fields only and do not earn points.",
            "For year-only dates, use 6 months when start and end year match; otherwise use 12 x (end year - start year - 1) + 8 months.",
            "Calculate each hidden weighted subtotal by multiplying the PHP, Python, Laravel, and AWS raw component by 2.0, 2.0, 1.2, and 0.8 respectively, then summing. Return the recency, duration, and evidence subtotals for ranking tie-breaks only; do not add them to Final Score again.",
            "Return only fields required by the JSON schema.",
        ],
        internal_role_flag_name="relevant_backend_role",
        internal_role_evidence_name="backend_evidence_extracted",
        export_columns=BACKEND_OUTPUT_COLUMNS,
        numeric_scores=True,
        ranked=True,
        column_enums=BACKEND_WARNING_ENUMS,
        ranking_tiebreaker_columns=[
            "PHP Score (/20)",
            "Python Score (/20)",
            "Laravel Score (/12)",
            "AWS Score (/8)",
            "Weighted Recency Subtotal",
            "Weighted Duration Subtotal",
            "Weighted Evidence Subtotal",
        ],
        strongest_evidence_columns=["Strongest Evidence"],
        rationale_min_words=50,
    ),
}


DEFAULT_ROLE_KEY = "design"


def role_options() -> dict[str, str]:
    return {profile.label: profile.key for profile in ROLE_PROFILES.values()}


def get_role_profile(role_key: Optional[str]) -> RoleProfile:
    return ROLE_PROFILES.get(role_key or DEFAULT_ROLE_KEY, ROLE_PROFILES[DEFAULT_ROLE_KEY])


def prepare_output_rows(rows: list[dict], role_key: Optional[str]) -> list[dict]:
    role = get_role_profile(role_key)
    prepared = [dict(row) for row in rows]
    if role.ranked:
        tie_columns = role.ranking_tiebreaker_columns or []

        def rank_key(row: dict) -> tuple:
            numeric = [-_number(row.get(role.total_column))]
            numeric.extend(-_number(row.get(column)) for column in tie_columns)
            return (*numeric, str(row.get("Candidate", "")).casefold())

        prepared.sort(key=rank_key)
        for index, row in enumerate(prepared, start=1):
            row[role.outcome_column] = index
    return [{column: row.get(column, "") for column in role.output_columns} for row in prepared]


def _number(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0
