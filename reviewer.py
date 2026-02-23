"""
Smart Code Reviewer — AI-powered analysis engine.

Uses Groq (free tier) to review code for:
  • Readability
  • Structure
  • Maintainability
"""

from __future__ import annotations

import json
import re
import textwrap
from dataclasses import dataclass, field

from groq import Groq

# ── Models ──────────────────────────────────────────────────────────────────

REVIEW_CATEGORIES = ("Readability", "Structure", "Maintainability")


@dataclass
class CategoryFeedback:
    """Feedback for a single review category."""

    category: str
    score: int  # 1-10
    summary: str
    suggestions: list[str] = field(default_factory=list)


@dataclass
class ReviewResult:
    """Complete review result returned by the analyser."""

    language: str
    categories: list[CategoryFeedback]
    overall_score: float
    tldr: str
    raw_response: str = ""


# ── Prompt ──────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""\
    You are **Smart Code Reviewer**, an expert software-engineering assistant.

    Given a code snippet, analyse it across three dimensions and provide CLEAR TECHNICAL SUGGESTIONS.

    **Analysis Dimensions:**

    1. **Readability** – naming conventions, comments, formatting, clarity
       - Check: variable/function names descriptive? Comments explain WHY not WHAT?
       - Look for: magic numbers, unclear abbreviations, inconsistent naming

    2. **Structure** – separation of concerns, function/class organization, patterns
       - Check: single responsibility? Cohesion? Code reuse?
       - Look for: god functions, tight coupling, missing abstractions

    3. **Maintainability** – test-friendliness, coupling, complexity, error handling
       - Check: easy to test? Error handling? Cyclomatic complexity?
       - Look for: missing null checks, bare exceptions, hard-coded values

    **CRITICAL: For each suggestion, ALWAYS include:**
    • Specific line number(s) or function/variable name
    • What's wrong (anti-pattern, code smell)
    • Concrete example of how to fix it
    • Why it matters (security, performance, testability)

    **Return a valid JSON object with this schema:**

    {
      "language": "<detected programming language>",
      "categories": [
        {
          "category": "Readability",
          "score": <1-10>,
          "summary": "<2-3 sentence technical summary>",
          "suggestions": [
            "<Line X: 'variable_name' is unclear. Use 'fetch_user_response' instead of 'r'. This improves clarity and IDE autocomplete support.>",
            "<Lines 5-12: Function 'process()' does 3 things. Split into 'parse_input()', 'validate()', and 'execute()' for single responsibility.>"
          ]
        },
        {
          "category": "Structure",
          "score": <1-10>,
          "summary": "<2-3 sentence technical summary>",
          "suggestions": [
            "<Function 'fetch_data()' directly queries DB. Abstract into a DataRepository interface for testability and DI.>",
            "<The component couples API endpoint string. Use environment config or dependency injection instead.>"
          ]
        },
        {
          "category": "Maintainability",
          "score": <1-10>,
          "summary": "<2-3 sentence technical summary>",
          "suggestions": [
            "<Line 24: Bare except() silently fails. Catch specific exceptions (ValueError, NetworkError) and log with context.>",
            "<No null check on response.data. Add guard clause: if (!response?.data) throw new ValidationError('Missing data');>"
          ]
        }
      ],
      "overall_score": <average of three scores, rounded to 1 decimal>,
      "tldr": "<one-paragraph executive summary with key issues and impact>"
    }

    **Rules:**
    • EVERY suggestion MUST cite line numbers or symbol names
    • EVERY suggestion MUST include: WHAT, WHERE, HOW-TO-FIX, WHY
    • Be specific: name the pattern (e.g., "God Object", "N+1 Query", "Silent Catch")
    • Include concrete code examples when possible
    • Respond ONLY with the JSON object, nothing else.
    • If code is perfect in a category, set score to 9-10 and keep suggestions empty
""")



# ── Analyser ────────────────────────────────────────────────────────────────

_client: Groq | None = None


def configure_groq(api_key: str) -> None:
    """Create a Groq client with the given API key."""
    global _client
    _client = Groq(api_key=api_key)


def _extract_json(text: str) -> dict:
    """Best-effort extraction of JSON from the model's response."""
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = cleaned.strip().rstrip("`")
    return json.loads(cleaned)


def review_code(code: str, *, model_name: str = "llama-3.3-70b-versatile") -> ReviewResult:
    """Send *code* to Groq and return a structured ReviewResult."""
    if _client is None:
        raise RuntimeError("Call configure_groq(api_key) first.")

    response = _client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Review the following code:\n\n```\n{code}\n```"},
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    raw = response.choices[0].message.content
    data = _extract_json(raw)

    categories = [
        CategoryFeedback(
            category=cat["category"],
            score=int(cat["score"]),
            summary=cat["summary"],
            suggestions=cat.get("suggestions", []),
        )
        for cat in data["categories"]
    ]

    return ReviewResult(
        language=data.get("language", "Unknown"),
        categories=categories,
        overall_score=round(float(data["overall_score"]), 1),
        tldr=data.get("tldr", ""),
        raw_response=raw,
    )
