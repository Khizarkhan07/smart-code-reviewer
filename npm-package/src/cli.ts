#!/usr/bin/env node

/**
 * CLI interface for Smart Code Reviewer
 * Usage: smart-code-reviewer [files...]
 */

import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";
import { initialize, reviewCode } from "./index";
import type { ReviewResult } from "./types";

// Load environment variables
dotenv.config();

// ANSI Colors
const colors = {
  reset: "\x1b[0m",
  bold: "\x1b[1m",
  red: "\x1b[91m",
  green: "\x1b[92m",
  yellow: "\x1b[93m",
  blue: "\x1b[94m",
  cyan: "\x1b[96m",
  white: "\x1b[97m",
  gray: "\x1b[90m",
  bgRed: "\x1b[101m",
};

function colored(text: string, color: string): string {
  return `${color}${text}${colors.reset}`;
}

/**
 * Review a single file
 */
async function reviewFile(
  filePath: string,
  threshold: number,
  verbose: boolean
): Promise<{ passed: boolean; message: string; score: number }> {
  if (!fs.existsSync(filePath)) {
    return {
      passed: true,
      message: `${colors.gray}⏭️  ${filePath} (skipped: not found)${colors.reset}`,
      score: 0,
    };
  }

  const codeExtensions = new Set([
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".cpp",
    ".c",
    ".java",
  ]);

  if (!codeExtensions.has(path.extname(filePath))) {
    return {
      passed: true,
      message: `${colors.gray}⏭️  ${filePath} (skipped: not code)${colors.reset}`,
      score: 0,
    };
  }

  try {
    const code = fs.readFileSync(filePath, "utf-8");

    if (!code.trim()) {
      return {
        passed: true,
        message: `${colors.gray}⏭️  ${filePath} (skipped: empty)${colors.reset}`,
        score: 0,
      };
    }

    const result = await reviewCode(code);
    const passed = result.overall_score >= threshold;

    const status = passed
      ? colored("✅", colors.green)
      : colored("⚠️", colors.red);
    const fileColor = passed ? colors.green : colors.yellow;
    const fileNameColored = colored(filePath, fileColor);
    const scoreColored = colored(`${result.overall_score}/10`, fileColor);

    let message = `\n${status} ${fileNameColored}\n`;
    message += `   Score: ${scoreColored} (${result.language})\n`;
    message += `   ${colors.cyan}TL;DR:${colors.reset} ${result.tldr}\n`;

    if (verbose && !passed) {
      message += `\n   ${colors.blue}📊 Detailed Feedback:${colors.reset}\n`;

      for (const cat of result.categories) {
        let scoreEmoji = colored("🟢", colors.green);
        if (cat.score < 7) {
          scoreEmoji = cat.score >= 5 ? colored("🟡", colors.yellow) : colored("🔴", colors.red);
        }

        const catName = colored(
          `${cat.category}: ${cat.score}/10`,
          colors.cyan
        );
        message += `\n   ${scoreEmoji} ${catName}\n`;
        message += `       ${cat.summary}\n`;

        if (cat.suggestions.length > 0) {
          message += `       ${colors.gray}Suggestions to improve:${colors.reset}\n`;
          cat.suggestions.forEach((suggestion, i) => {
            message += `       ${i + 1}. ${suggestion}\n`;
          });
        }
      }
    }

    return { passed, message, score: result.overall_score };
  } catch (error) {
    const errorMsg = colored(
      `❌ ${filePath}: Error — ${
        error instanceof Error ? error.message.substring(0, 80) : "Unknown error"
      }`,
      colors.red
    );
    return { passed: false, message: errorMsg, score: 0 };
  }
}

/**
 * Main CLI entry point
 */
async function main(): Promise<number> {
  const args = process.argv.slice(2);

  // Initialize API key
  try {
    initialize();
  } catch (error) {
    console.log(colored("❌ GROQ_API_KEY not set", colors.red));
    console.log(
      `   ${colors.gray}Please set GROQ_API_KEY environment variable or create .env file${colors.reset}`
    );
    return 1;
  }

  const threshold = parseFloat(process.env.CODE_REVIEW_THRESHOLD || "6.0");
  const verbose = process.env.VERBOSE !== "0";
  const files = args.length > 0 ? args : [];

  if (files.length === 0) {
    console.log(`${colors.blue}ℹ️  No files to review${colors.reset}`);
    return 0;
  }

  const header = `🔍 Smart Code Reviewer (threshold: ${colored(
    String(threshold),
    colors.cyan
  )}/10)`;
  console.log(`\n${colors.bold}${header}${colors.reset}\n`);

  const failedFiles: Array<[string, number]> = [];

  // Review all files
  for (const file of files) {
    const { passed, message, score } = await reviewFile(file, threshold, verbose);
    console.log(message);

    if (!passed) {
      failedFiles.push([file, score]);
    }
  }

  // Summary
  console.log(`\n${colors.bold}${colors.gray}${"─".repeat(70)}${colors.reset}`);

  if (failedFiles.length > 0) {
    const failedHeader = `${colors.bgRed}${colors.white}${colors.bold} ❌ ${
      failedFiles.length
    } FILE(S) BELOW THRESHOLD ${colors.reset}`;
    console.log(`\n${failedHeader}\n`);

    for (const [file, score] of failedFiles) {
      const fileLine = `${colors.bgRed}${colors.white}${colors.bold} ${file}: ${score}/10 ${colors.reset}`;
      console.log(`   ${fileLine}`);
    }

    console.log(
      `\n${colors.yellow}💡 Tip: Fix the issues above to improve your scores!${colors.reset}\n`
    );
    return 1;
  }

  const successMsg = colored("✅ All files passed review!", colors.green);
  console.log(`\n${colors.bold}${successMsg}${colors.reset}\n`);
  return 0;
}

// Run CLI
main().then((code) => process.exit(code));
