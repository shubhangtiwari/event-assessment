"""Score a single submission (dict of answers) against the rubric.

All scoring functions return an int. Multi-select answers are expected as a
list of strings. Single-select answers are expected as a single string (the
option label). Likert answers are ints 1..5.
"""
from __future__ import annotations

from typing import Any

from core.config import (
    KNOWLEDGE_POINTS_PER_CORRECT,
    LEVEL_THRESHOLDS,
    Q7_CLAUDE_TOKENS,
    Q7_MAX,
    Q8_SCORES,
    Q9_SCORES,
    Q10_MAX,
    Q10_NEGATIVE_TOKENS,
    SELF_ASSESSMENT_MAX,
)
from core.questions import CORRECT_ANSWERS, ALL_QUESTIONS


# ---------------------------------------------------------------------------
# Low-level scorers
# ---------------------------------------------------------------------------

def _score_likert(value: Any) -> int:
    try:
        rating = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(SELF_ASSESSMENT_MAX, rating - 1))


def _score_q7(selected: list[str] | None) -> int:
    if not selected:
        return 0
    lowered = [s.lower() for s in selected]
    points = sum(
        1 for token in Q7_CLAUDE_TOKENS
        if any(token in s for s in lowered)
    )
    return min(Q7_MAX, points)


def _score_ordinal(value: str | None, scale: dict[str, int]) -> int:
    if not value:
        return 0
    v = value.strip().lower()
    # Longest key first so "tried once or twice" beats "tried".
    for key in sorted(scale.keys(), key=len, reverse=True):
        if key in v:
            return scale[key]
    return 0


def _score_q10(selected: list[str] | None) -> int:
    if not selected:
        return 0
    usable = []
    for item in selected:
        low = item.strip().lower()
        if any(neg in low for neg in Q10_NEGATIVE_TOKENS):
            continue
        usable.append(item)
    return min(Q10_MAX, len(usable))


def _score_mcq(answer: str | None, correct_letter: str, question_key: str) -> int:
    """Grade a knowledge-check answer. We accept either a letter (A/B/C/D/E)
    or the full option text (as the survey submits)."""
    if not answer:
        return 0
    answer = answer.strip()
    # Letter input.
    if len(answer) == 1 and answer.upper() in {"A", "B", "C", "D", "E"}:
        return KNOWLEDGE_POINTS_PER_CORRECT if answer.upper() == correct_letter else 0
    # Full option-text input: look up the index of the matching option and
    # convert to letter.
    options = ALL_QUESTIONS[question_key]["options"]
    try:
        idx = options.index(answer)
    except ValueError:
        # Fallback: case-insensitive substring.
        idx = None
        low = answer.lower()
        for i, opt in enumerate(options):
            if opt.lower() == low:
                idx = i
                break
    if idx is None:
        return 0
    letter = "ABCDE"[idx]
    return KNOWLEDGE_POINTS_PER_CORRECT if letter == correct_letter else 0


# ---------------------------------------------------------------------------
# Level classification
# ---------------------------------------------------------------------------

def classify_level(score: int) -> str:
    for name, lo, hi in LEVEL_THRESHOLDS:
        if lo <= score <= hi:
            return name
    return LEVEL_THRESHOLDS[-1][0]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_submission(data: dict[str, Any]) -> tuple[int, str, dict[str, int]]:
    """Score one submission.

    Args:
        data: {
            "q5": 1..5,
            "q6": 1..5,
            "q7": [list of selected options],
            "q8": "option label",
            "q9": "option label",
            "q10": [list],
            "q11".."q16": "option label" or "A"/"B"/...,
        }

    Returns:
        (total_score, level_name, breakdown_dict)
    """
    breakdown: dict[str, int] = {}

    breakdown["Q5 self AI-coding"]   = _score_likert(data.get("q5"))
    breakdown["Q6 self agentic"]     = _score_likert(data.get("q6"))
    breakdown["Q7 tool experience"]  = _score_q7(data.get("q7") or [])
    breakdown["Q8 Claude Code use"]  = _score_ordinal(data.get("q8"), Q8_SCORES)
    breakdown["Q9 API/SDK"]          = _score_ordinal(data.get("q9"), Q9_SCORES)
    breakdown["Q10 hands-on"]        = _score_q10(data.get("q10") or [])
    for qk, correct in CORRECT_ANSWERS.items():
        breakdown[f"{qk.upper()} knowledge"] = _score_mcq(data.get(qk), correct, qk)

    total = sum(breakdown.values())
    level = classify_level(total)
    return total, level, breakdown
