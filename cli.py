"""Command-line interface for Smart Code Reviewer pre-commit hook."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from reviewer import configure_groq, review_code

# Load API key from .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def review_file(file_path: str, threshold: float = 6.0, verbose: bool = True) -> tuple[bool, str]:
    """Review a single file and return (passed, message)."""
    if not Path(file_path).exists():
        return True, f"⏭️  {file_path} (skipped: not found)"

    # Skip non-code files
    code_extensions = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".cpp", ".c", ".java"}
    if Path(file_path).suffix not in code_extensions:
        return True, f"⏭️  {file_path} (skipped: not code)"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        if not code.strip():
            return True, f"⏭️  {file_path} (skipped: empty)"

        result = review_code(code)

        # Check if it passes threshold
        passed = result.overall_score >= threshold
        status = "✅" if passed else "⚠️"
        
        # Build detailed message
        message = f"\n{status} {file_path}\n"
        message += f"   Overall Score: {result.overall_score}/10 ({result.language})\n"
        message += f"   TL;DR: {result.tldr}\n"
        
        if verbose and not passed:
            message += "\n   📊 Detailed Feedback:\n"
            for cat in result.categories:
                score_emoji = "🟢" if cat.score >= 7 else "🟡" if cat.score >= 5 else "🔴"
                message += f"\n   {score_emoji} {cat.category}: {cat.score}/10\n"
                message += f"       {cat.summary}\n"
                if cat.suggestions:
                    message += "       Suggestions to improve:\n"
                    for i, suggestion in enumerate(cat.suggestions, 1):
                        message += f"       {i}. {suggestion}\n"
        
        return passed, message

    except Exception as e:
        return False, f"❌ {file_path}: Error — {str(e)[:80]}"


def main(argv: list[str] | None = None) -> int:
    """Entry point for pre-commit hook."""
    if argv is None:
        argv = sys.argv[1:]

    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not set in .env")
        print("   Please add your Groq API key to .env file")
        return 1

    configure_groq(GROQ_API_KEY)

    # Get threshold from environment or use default
    threshold = float(os.getenv("CODE_REVIEW_THRESHOLD", "6.0"))
    
    # Verbose mode (show all details for failures)
    verbose = os.getenv("VERBOSE", "1") == "1"

    failed_files = []
    file_paths = argv if argv else []

    if not file_paths:
        print("ℹ️  No files to review")
        return 0

    print(f"\n🔍 Smart Code Reviewer (threshold: {threshold}/10)\n")

    for file_path in file_paths:
        passed, message = review_file(file_path, threshold, verbose=verbose)
        print(message)

        if not passed:
            failed_files.append(file_path)

    if failed_files:
        print(f"\n❌ {len(failed_files)} file(s) failed review")
        print("💡 Tip: Fix the issues above to improve your scores!\n")
        return 1

    print("✅ All files passed review!\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
