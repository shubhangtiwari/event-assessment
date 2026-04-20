"""
Single source of truth for all assessment questions.

The survey template renders from QUESTIONS; the scorer grades from the same
dict. Change an option label or add a question here and it flows through.
"""

# Correct answers for the 6 knowledge-check questions.
CORRECT_ANSWERS = {
    "q11": "C",  # CLAUDE.md purpose
    "q12": "A",  # MCP
    "q13": "D",  # Subagent
    "q14": "D",  # ADR
    "q15": "C",  # Agentic behavior
    "q16": "D",  # Enforcing coding standards
}

# Profile questions — not scored, but captured.
PROFILE_QUESTIONS = [
    {
        "key": "name",
        "type": "text",
        "label": "Full name",
        "required": True,
        "placeholder": "Lena Schmitz",
    },
    {
        "key": "email",
        "type": "email",
        "label": "Work email",
        "required": True,
        "placeholder": "lena.schmitz@telekom.de",
    },
    {
        "key": "role",
        "type": "single",
        "label": "Primary role",
        "required": True,
        "options": [
            "Software Engineer / Developer",
            "Staff / Principal Engineer",
            "Solution Architect / Enterprise Architect",
            "Engineering Manager / Tech Lead",
            "DevOps / SRE / Platform",
            "Data / ML Engineer",
            "Security / Compliance",
            "Product Manager",
            "Other",
        ],
    },
    {
        "key": "years_exp",
        "type": "single",
        "label": "Years of hands-on software / engineering experience",
        "required": True,
        "options": ["0–1", "2–5", "6–10", "10+"],
    },
]

# Self-assessment questions — Likert 1..5.
SELF_ASSESSMENT_QUESTIONS = [
    {
        "key": "q5",
        "type": "likert",
        "label": "How would you rate your overall experience with AI coding assistants "
                 "(Claude Code, Copilot, Cursor, etc.)?",
        "sublabel": "1 = never used · 5 = daily power user",
        "required": True,
    },
    {
        "key": "q6",
        "type": "likert",
        "label": "How would you rate your experience with agentic AI systems "
                 "(agents that plan, call tools, iterate)?",
        "sublabel": "1 = new to it · 5 = I've shipped production agents",
        "required": True,
    },
]

# Tool experience questions.
TOOL_EXPERIENCE_QUESTIONS = [
    {
        "key": "q7",
        "type": "multi",
        "label": "Which AI tools have you used in the last 6 months?",
        "sublabel": "Select all that apply.",
        "required": False,
        "options": [
            "Claude Code",
            "Claude chat (claude.ai / desktop / mobile)",
            "GitHub Copilot",
            "Cursor",
            "ChatGPT / Codex",
            "Gemini / Google AI",
            "Other",
            "None",
        ],
    },
    {
        "key": "q8",
        "type": "single",
        "label": "How often do you use Claude Code?",
        "required": True,
        "options": [
            "Never used",
            "Tried once or twice",
            "Occasional (a few times a month)",
            "Regular (weekly)",
            "Daily driver",
        ],
    },
    {
        "key": "q9",
        "type": "single",
        "label": "Have you built software using the Claude API or the Claude Agent SDK?",
        "required": True,
        "options": [
            "No, never",
            "Explored the docs / examples but haven't built anything",
            "Built a small prototype or internal tool",
            "Shipped something in production",
        ],
    },
    {
        "key": "q10",
        "type": "multi",
        "label": "Which of the following have you hands-on used (not just read about)?",
        "sublabel": "Select all that apply.",
        "required": False,
        "options": [
            "CLAUDE.md / project context files",
            "MCP (Model Context Protocol) servers",
            "Claude Skills",
            "Subagents in Claude Code",
            "The Claude Agent SDK",
            "Artifacts",
            "Hooks / custom slash commands",
            "Plan mode",
            "None of the above",
        ],
    },
]

# Knowledge-check questions. Letter in CORRECT_ANSWERS maps to option index:
# A=0, B=1, C=2, D=3, E=4.
KNOWLEDGE_QUESTIONS = [
    {
        "key": "q11",
        "type": "single",
        "label": "What is the primary purpose of a CLAUDE.md file?",
        "required": True,
        "options": [
            "A license file required by Anthropic",
            "A log of all Claude interactions",
            "Persistent project context and instructions that Claude Code reads automatically",
            "Configuration for API keys",
            "I don't know",
        ],
    },
    {
        "key": "q12",
        "type": "single",
        "label": "MCP (Model Context Protocol) primarily allows you to:",
        "required": True,
        "options": [
            "Standardize how LLM applications connect to external tools and data sources",
            "Compile Claude models locally",
            "Multiply the context window at runtime",
            "Encrypt Claude's responses",
            "I don't know",
        ],
    },
    {
        "key": "q13",
        "type": "single",
        "label": "In Claude Code, a subagent is best described as:",
        "required": True,
        "options": [
            "A background daemon that auto-commits code",
            "A smaller, local model that runs offline",
            "A monitoring tool for Claude usage",
            "A specialized delegate with its own context window, system prompt, and tool set",
            "I don't know",
        ],
    },
    {
        "key": "q14",
        "type": "single",
        "label": "An Architecture Decision Record (ADR) is:",
        "required": True,
        "options": [
            "A security audit log",
            "A CI/CD pipeline artifact",
            "A database schema definition",
            "A lightweight document capturing a significant architecture decision, its context, and its consequences",
            "I don't know",
        ],
    },
    {
        "key": "q15",
        "type": "single",
        "label": "Which best describes \"agentic\" behavior in an LLM-powered system?",
        "required": True,
        "options": [
            "The model streams responses token-by-token",
            "The model has been fine-tuned on company data",
            "The model autonomously plans, calls tools, and iterates toward a multi-step goal",
            "The model runs on dedicated GPUs",
            "I don't know",
        ],
    },
    {
        "key": "q16",
        "type": "single",
        "label": "You need Claude Code to consistently follow an internal coding standard "
                 "across an entire repository. The most idiomatic approach is:",
        "required": True,
        "options": [
            "Paste the standard into every prompt",
            "Fine-tune a custom Claude model on the standard",
            "Email the standard to your teammates and hope for the best",
            "Encode it as a Skill or in CLAUDE.md so it's loaded automatically in context",
            "I don't know",
        ],
    },
]

SECTIONS = [
    {"title": "About you",        "questions": PROFILE_QUESTIONS},
    {"title": "Self-assessment",  "questions": SELF_ASSESSMENT_QUESTIONS},
    {"title": "Tool experience",  "questions": TOOL_EXPERIENCE_QUESTIONS},
    {"title": "Knowledge check",  "questions": KNOWLEDGE_QUESTIONS,
     "note": "Pick the best answer. \"I don't know\" is encouraged if you're unsure — "
             "it helps us place you with the right teammates."},
]

# Flat dict for quick lookup by key.
ALL_QUESTIONS = {
    q["key"]: q
    for section in SECTIONS
    for q in section["questions"]
}

# Required keys for form validation.
REQUIRED_KEYS = [q["key"] for q in ALL_QUESTIONS.values() if q.get("required")]
