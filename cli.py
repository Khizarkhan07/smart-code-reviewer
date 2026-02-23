"""Command-line interface for Smart Code Reviewer pre-commit hook."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from reviewer import configure_groq, review_code

# Load API key from .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ANSI color codes
class Color:
    """ANSI color constants for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    BG_RED = "\033[101m"
    BG_YELLOW = "\033[103m"

def colored(text: str, color: str) -> str:
    """Return colored text for terminal output."""
    return f"{color}{text}{Color.RESET}"


def review_file(file_path: str, threshold: float = 6.0, verbose: bool = True) -> tuple[bool, str, float]:
    """Review a single file and return (passed, message, score)."""
    if not Path(file_path).exists():
        return True, f"{Color.GRAY}⏭️  {file_path} (skipped: not found){Color.RESET}", 0.0

    # Skip non-code files
    code_extensions = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".cpp", ".c", ".java"}
    if Path(file_path).suffix not in code_extensions:
        return True, f"{Color.GRAY}⏭️  {file_path} (skipped: not code){Color.RESET}", 0.0

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        if not code.strip():
            return True, f"{Color.GRAY}⏭️  {file_path} (skipped: empty){Color.RESET}", 0.0

        result = review_code(code)

        # Check if it passes threshold
        passed = result.overall_score >= threshold
        
        if passed:
            status = colored("✅", Color.GREEN)
            file_color = Color.GREEN
        else:
            status = colored("⚠️", Color.RED)
            file_color = Color.YELLOW
        
        # Build detailed message
        file_name_colored = colored(file_path, file_color)
        score_colored = colored(f"{result.overall_score}/10", file_color)
        message = f"\n{status} {file_name_colored}\n"
        message += f"   Score: {score_colored} ({result.language})\n"
        message += f"   {Color.CYAN}TL;DR:{Color.RESET} {result.tldr}\n"
        
        if verbose and not passed:
            message += f"\n   {Color.BLUE}📊 Detailed Feedback:{Color.RESET}\n"
            for cat in result.categories:
                if cat.score >= 7:
                    score_emoji = colored("🟢", Color.GREEN)
                elif cat.score >= 5:
                    score_emoji = colored("🟡", Color.YELLOW)
                else:
                    score_emoji = colored("🔴", Color.RED)
                
                cat_name = colored(f"{cat.category}: {cat.score}/10", Color.CYAN)
                message += f"\n   {score_emoji} {cat_name}\n"
                message += f"       {cat.summary}\n"
                if cat.suggestions:
                    message += f"       {Color.GRAY}Suggestions to improve:{Color.RESET}\n"
                    for i, suggestion in enumerate(cat.suggestions, 1):
                        message += f"       {i}. {suggestion}\n"
        
        return passed, message, result.overall_score

    except Exception as e:
        error_msg = colored(f"❌ {file_path}: Error — {str(e)[:80]}", Color.RED)
        return False, error_msg, 0.0


def main(argv: list[str] | None = None) -> int:
    """Entry point for pre-commit hook."""
    if argv is None:
        argv = sys.argv[1:]

    if not GROQ_API_KEY:
        print(colored("❌ GROQ_API_KEY not set in .env", Color.RED))
        print(f"   {Color.GRAY}Please add your Groq API key to .env file{Color.RESET}")
        return 1

    configure_groq(GROQ_API_KEY)

    # Get threshold from environment or use default
    threshold = float(os.getenv("CODE_REVIEW_THRESHOLD", "6.0"))
    
    # Verbose mode (show all details for failures)
    verbose = os.getenv("VERBOSE", "1") == "1"

    failed_files: list[tuple[str, float]] = []
    file_paths = argv if argv else []

    if not file_paths:
        print(f"{Color.BLUE}ℹ️  No files to review{Color.RESET}")
        return 0

    header = f"🔍 Smart Code Reviewer (threshold: {colored(str(threshold), Color.CYAN)}/10)"
    print(f"\n{Color.BOLD}{header}{Color.RESET}\n")

    for file_path in file_paths:
        passed, message, score = review_file(file_path, threshold, verbose=verbose)
        print(message)

        if not passed:
            failed_files.append((file_path, score))

    # Summary section
    print(f"\n{Color.BOLD}{'─' * 70}{Color.RESET}")
    
    if failed_files:
        # Red highlighted header
        failed_header = f"{Color.BG_RED}{Color.WHITE}{Color.BOLD} ❌ {len(failed_files)} FILE(S) BELOW THRESHOLD {Color.RESET}"
        print(f"\n{failed_header}\n")
        
        for file_path, score in failed_files:
            # Red background for each failed file line
            file_line = f"{Color.BG_RED}{Color.WHITE}{Color.BOLD} {file_path}: {score}/10 {Color.RESET}"
            print(f"   {file_line}")
        
        print(f"\n{Color.YELLOW}💡 Tip: Fix the issues above to improve your scores!{Color.RESET}\n")
        return 1

    success_msg = colored("✅ All files passed review!", Color.GREEN)
    print(f"\n{Color.BOLD}{success_msg}{Color.RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
