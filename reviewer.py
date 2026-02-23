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

    Given a code snippet the user provides, analyse it across three dimensions:
    1. **Readability** – naming, comments, formatting, clarity.
    2. **Structure** – separation of concerns, function/class organisation,
       design-pattern usage, single-responsibility adherence.
    3. **Maintainability** – test-friendliness, coupling, complexity,
       extensibility, error handling.

    Return your analysis as a **valid JSON object** (no markdown fences) with
    exactly this schema:

    {
      "language": "<detected programming language>",
      "categories": [
        {
          "category": "Readability",
          "score": <1-10>,
          "summary": "<2-3 sentence summary>",
          "suggestions": ["<actionable suggestion 1>", "..."]
        },
        {
          "category": "Structure",
          "score": <1-10>,
          "summary": "<2-3 sentence summary>",
          "suggestions": ["<actionable suggestion 1>", "..."]
        },
        {
          "category": "Maintainability",
          "score": <1-10>,
          "summary": "<2-3 sentence summary>",
          "suggestions": ["<actionable suggestion 1>", "..."]
        }
      ],
      "overall_score": <average of the three scores, rounded to 1 decimal>,
      "tldr": "<one-paragraph executive summary of the review>"
    }

    Rules:
    • Be constructive and specific — cite line numbers or symbol names when possible.
    • Each category MUST have at least one suggestion unless the code is perfect.
    • Keep each suggestion to one sentence.
    • Respond ONLY with the JSON object, nothing else.
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
