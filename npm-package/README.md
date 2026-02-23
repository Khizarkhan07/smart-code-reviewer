# Smart Code Reviewer — npm Package

AI-powered code review tool for Node.js/TypeScript projects. Analyzes code for **readability**, **structure**, and **maintainability** using Groq's Llama 3.3 70B model.

## Features

✨ **3-Dimension Analysis**
- 📖 **Readability** – naming, comments, formatting, clarity
- 🏗️ **Structure** – separation of concerns, design patterns, organization
- 🔧 **Maintainability** – testability, coupling, complexity, error handling

🎯 **Technical Suggestions**
- Specific line numbers and symbol names
- Concrete examples of how to fix issues
- Explains why each suggestion matters

🚀 **Pre-Commit Integration**
- Works seamlessly with `husky` + pre-commit hooks
- Configurable score thresholds
- Colorful, actionable CLI output

## Installation

```bash
npm install smart-code-reviewer
```

Or globally for CLI:
```bash
npm install -g smart-code-reviewer
```

## Setup

### 1. Get a Groq API Key
1. Go to https://console.groq.com/keys
2. Create an API key
3. Save it to your `.env` file

### 2. Create `.env` file
```bash
GROQ_API_KEY=your_api_key_here
CODE_REVIEW_THRESHOLD=6.0  # Optional (default: 6.0)
VERBOSE=1                   # Optional (default: 1)
```

### 3. (Optional) Add to `.gitignore`
```
.env
```

## Usage

### CLI

**Review a file:**
```bash
smart-code-reviewer src/app.ts
```

**Review multiple files:**
```bash
smart-code-reviewer src/**/*.ts
```

**Set threshold:**
```bash
CODE_REVIEW_THRESHOLD=8.0 smart-code-reviewer src/app.ts
```

**Verbose mode (shows detailed feedback):**
```bash
VERBOSE=1 smart-code-reviewer src/app.ts
```

### As NPM Package

```typescript
import { initialize, reviewCode } from 'smart-code-reviewer';

// Initialize with API key (reads from .env or argument)
initialize();  // Uses GROQ_API_KEY from .env
// OR
initialize('your_api_key_here');

// Review code
const result = await reviewCode(`
  function foo(a, b) {
    return a + b;
  }
`);

console.log(result.overall_score);  // 7.5
console.log(result.categories);     // [{ category: "Readability", score: 7, ... }]
console.log(result.tldr);           // "Overall good code with minor improvements..."
```

## Pre-Commit Hook Setup

### For Node.js/TypeScript Projects

**1. Install dependencies:**
```bash
npm install --save-dev smart-code-reviewer husky
npx husky install
```

**2. Create `.husky/pre-commit`:**
```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

smart-code-reviewer
```

**3. Make it executable:**
```bash
chmod +x .husky/pre-commit
```

**4. Create `.env` with API key:**
```bash
GROQ_API_KEY=your_api_key_here
CODE_REVIEW_THRESHOLD=7.0
```

### Alternative: Pre-Commit Framework

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: smart-code-reviewer
        name: Smart Code Review
        entry: smart-code-reviewer
        language: node
        types: [javascript, typescript]
        stages: [commit]
```

Then install:
```bash
pre-commit install
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | *(required)* | Your Groq API key from https://console.groq.com/keys |
| `CODE_REVIEW_THRESHOLD` | `6.0` | Minimum score (1-10) to pass review. Below this, commit is blocked |
| `VERBOSE` | `1` | Show detailed feedback (1 = yes, 0 = no) |

## Supported Languages

- JavaScript (`.js`)
- TypeScript (`.ts`, `.tsx`, `.jsx`)
- Python (`.py`)
- Go (`.go`)
- Rust (`.rs`)
- C/C++ (`.c`, `.cpp`)
- Java (`.java`)

## Example Output

```
🔍 Smart Code Reviewer (threshold: 7.0/10)

✅ src/api.ts
   Score: 7.5/10 (TypeScript)
   TL;DR: Good separation of concerns with proper error handling...

⚠️ src/utils.ts
   Score: 5.8/10 (TypeScript)
   TL;DR: Several naming issues and complex logic...

   📊 Detailed Feedback:

   🟡 Readability: 6/10
       Variable names are unclear and missing documentation.
       Suggestions to improve:
       1. Line 12: 'util_fn' should be 'calculateUserMetrics'
       2. Lines 5-20: Add JSDoc comments explaining parameters

   🔴 Maintainability: 4/10
       High cyclomatic complexity and missing error handling.
       Suggestions to improve:
       1. Line 34: Add null check for response.data
       2. Extract nested logic into separate function

────────────────────────────────────────────────────────────────────

❌ 1 FILE(S) BELOW THRESHOLD:

   src/utils.ts: 5.8/10

💡 Tip: Fix the issues above to improve your scores!
```

## API Reference

### `initialize(apiKey?: string): void`

Initialize Smart Code Reviewer with your Groq API key.

```typescript
initialize();  // Reads from GROQ_API_KEY env var
initialize('gsk_...');  // Use provided key
```

### `reviewCode(code: string, modelName?: string): Promise<ReviewResult>`

Review code and get structured feedback.

```typescript
const result = await reviewCode('function test() {}', 'llama-3.3-70b-versatile');
```

**Returns:**
```typescript
{
  language: 'JavaScript',
  overall_score: 7.2,
  tldr: 'Good structure but needs comments...',
  categories: [
    {
      category: 'Readability',
      score: 7,
      summary: 'Variable names are clear...',
      suggestions: ['Add function documentation...']
    },
    // ... Structure and Maintainability
  ]
}
```

## Troubleshooting

**Error: "GROQ_API_KEY not found"**
- Set `GROQ_API_KEY` environment variable
- Or create `.env` file with `GROQ_API_KEY=your_key`

**Error: "No such file" in pre-commit hook**
- Make sure `npm install smart-code-reviewer` ran successfully
- Check that `.env` file exists with `GROQ_API_KEY`

**Threshold too strict/loose**
- Adjust `CODE_REVIEW_THRESHOLD` environment variable
- Default is 6.0, try 5.0 for lenient or 8.0 for strict

## License

MIT

## Contributing

Contributions welcome! Open issues or PRs on [GitHub](https://github.com/Khizarkhan07/smart-code-reviewer)

## Links

- 🔗 [GitHub Repository](https://github.com/Khizarkhan07/smart-code-reviewer)
- 🌐 [Web UI Demo](https://smart-code-reviewer-demo.streamlit.app/)
- 📦 [npm Package](https://www.npmjs.com/package/smart-code-reviewer)
- 🐍 [Python Package](https://pypi.org/project/smart-code-reviewer/)
