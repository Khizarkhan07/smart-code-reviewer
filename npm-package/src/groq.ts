/**
 * Groq client wrapper for Smart Code Reviewer
 */

import Groq from "groq-sdk";
import { ReviewResult, CategoryFeedback } from "./types";

const SYSTEM_PROMPT = `You are **Smart Code Reviewer**, an expert software-engineering assistant.

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
• If code is perfect in a category, set score to 9-10 and keep suggestions empty`;

let groqClient: Groq | null = null;

/**
 * Configure Groq client with API key
 */
export function configureGroq(apiKey: string): void {
  groqClient = new Groq({ apiKey });
}

/**
 * Get or initialize Groq client
 */
function getGroqClient(): Groq {
  if (!groqClient) {
    throw new Error(
      "Groq not configured. Call configureGroq(apiKey) first or set GROQ_API_KEY environment variable."
    );
  }
  return groqClient;
}

/**
 * Extract JSON from model response
 */
function extractJSON(text: string): Record<string, any> {
  // Strip markdown code fences if present
  let cleaned = text.replace(/```(?:json)?\s*/g, "");
  cleaned = cleaned.trim().replace(/`+$/, "");
  return JSON.parse(cleaned);
}

/**
 * Review code using Groq LLM
 */
export async function reviewCode(
  code: string,
  modelName: string = "llama-3.3-70b-versatile"
): Promise<ReviewResult> {
  const client = getGroqClient();

  const response = await client.chat.completions.create({
    model: modelName,
    messages: [
      { role: "system", content: SYSTEM_PROMPT },
      {
        role: "user",
        content: `Review the following code:\n\n\`\`\`\n${code}\n\`\`\``,
      },
    ],
    temperature: 0.3,
    max_tokens: 4096,
  });

  const raw =
    response.choices[0].message.content || "No response from Groq";
  const data = extractJSON(raw);

  const categories: CategoryFeedback[] = data.categories.map(
    (cat: any) => ({
      category: cat.category,
      score: parseInt(cat.score),
      summary: cat.summary,
      suggestions: cat.suggestions || [],
    })
  );

  return {
    language: data.language || "Unknown",
    categories,
    overall_score: Math.round(parseFloat(data.overall_score) * 10) / 10,
    tldr: data.tldr || "",
    raw_response: raw,
  };
}
