"""Runtime + scoring configuration."""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------
APP_ROOT = Path(__file__).parent.resolve()
DATA_DIR = APP_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "responses.sqlite"
SECRET_KEY_PATH = DATA_DIR / "secret_key"

PORT = int(os.environ.get("PORT", 2408))
HOST = os.environ.get("HOST", "0.0.0.0")

# Admin password for the dashboard. Set ADMIN_PASSWORD in the environment
# before exposing publicly. Defaults to "admin" with a loud warning.
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
ADMIN_PASSWORD_IS_DEFAULT = ADMIN_PASSWORD == "admin"

# Cookie names.
RESPONDENT_COOKIE = "claude_assessment_respondent"
ADMIN_COOKIE = "claude_assessment_admin"

# ---------------------------------------------------------------------------
# Scoring rubric
# ---------------------------------------------------------------------------
SELF_ASSESSMENT_MAX = 4  # Likert 1..5 -> 0..4 points (rating - 1)

# Q7 multi-select — 1 point per Claude-specific tool, cap at 2.
Q7_CLAUDE_TOKENS = ["claude code", "claude chat", "claude.ai"]
Q7_MAX = 2

# Q8 frequency ordinal.
Q8_SCORES = {
    "never used": 0,
    "tried once or twice": 1,
    "occasional": 2,
    "regular": 3,
    "daily driver": 4,
}

# Q9 ordinal.
Q9_SCORES = {
    "no, never": 0,
    "explored": 1,
    "built a small prototype": 3,
    "shipped": 5,
}

# Q10 multi-select — 1 point per item, cap at 8.
Q10_MAX = 8
Q10_NEGATIVE_TOKENS = ["none of the above", "none"]

# Knowledge check — 3 points per correct.
KNOWLEDGE_POINTS_PER_CORRECT = 3

# Max possible = 4+4+2+4+5+8+18 = 45
MAX_SCORE = 45

LEVEL_THRESHOLDS = [
    ("Beginner", 0, 15),
    ("Intermediate", 16, 30),
    ("Advanced", 31, 45),
]

# ---------------------------------------------------------------------------
# Grouping
# ---------------------------------------------------------------------------
DEFAULT_GROUP_SIZE = int(os.environ.get("GROUP_SIZE", 6))
GROUPING_SEED = int(os.environ.get("GROUPING_SEED", 42))
