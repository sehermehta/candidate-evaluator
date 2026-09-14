from __future__ import annotations

import os
from pathlib import Path

DEFAULT_MODEL = "gpt-5.5"
DEFAULT_PARALLEL_OPENAI_CALLS = 5

MODEL_OPTIONS = {
    "GPT-5.5": "gpt-5.5",
    "GPT-5.5 Thinking": "gpt-5.5-thinking",
    "GPT-5.5 Mini": "gpt-5.5-mini",
    "GPT-5.3": "gpt-5.3",
    "GPT-5.3 Thinking": "gpt-5.3-thinking",
    "GPT-5.3 Mini": "gpt-5.3-mini",
    "GPT-4.1": "gpt-4.1",
    "GPT-4.1 Mini": "gpt-4.1-mini",
    "GPT-4.1 Nano": "gpt-4.1-nano",
    "GPT-4o": "gpt-4o",
    "GPT-4o Mini": "gpt-4o-mini",
    "O4 Mini": "o4-mini",
    "O3": "o3",
    "O3 Mini": "o3-mini",
    "O1": "o1",
    "O1 Mini": "o1-mini",
    "Custom": "",
}

SOURCE_COLUMNS = [
    "LinkedIn Profile ID",
    "LinkedIn URL",
    "Candidate Name",
    "Headline",
    "Experience 0",
    "Experience 1",
    "Education 0",
    "Education 1",
    "About",
    "Website",
]

DATA_DIR = Path(os.environ.get("CANDIDATE_DATA_DIR", "."))
RUNS_DIR = str(DATA_DIR / "work" / "runs")
OUTPUTS_DIR = str(DATA_DIR / "outputs")
