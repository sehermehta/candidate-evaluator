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
    category_scores: OrderedDict[str, int]
    allowed_scores: dict[str, set[int]]
    total_max: int
    outcome_column: str
    outcome_bands: list[tuple[int, int, str]]
    evidence_confidence_values: list[str]
    system_prompt: str
    instructions: list[str]
    internal_role_flag_name: str
    internal_role_evidence_name: str

    @property
    def output_columns(self) -> list[str]:
        return SOURCE_COLUMNS + self.grading_columns


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


ROLE_PROFILES = {
    "design": RoleProfile(
        key="design",
        label="Design / Product UX",
        role_name="senior Product/UX Designer",
        grading_columns=DESIGN_GRADING_COLUMNS,
        category_scores=DESIGN_CATEGORY_SCORES,
        allowed_scores={},
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
}


DEFAULT_ROLE_KEY = "design"


def role_options() -> dict[str, str]:
    return {profile.label: profile.key for profile in ROLE_PROFILES.values()}


def get_role_profile(role_key: Optional[str]) -> RoleProfile:
    return ROLE_PROFILES.get(role_key or DEFAULT_ROLE_KEY, ROLE_PROFILES[DEFAULT_ROLE_KEY])
