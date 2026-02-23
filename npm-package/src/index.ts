/**
 * Main reviewer module - exports public API
 */

export { reviewCode, configureGroq } from "./groq";
export type {
  CategoryFeedback,
  ReviewResult,
  ReviewerConfig,
  CLIOptions,
} from "./types";

import { configureGroq } from "./groq";
import * as dotenv from "dotenv";

/**
 * Initialize with API key (from env or provided)
 */
export function initialize(apiKey?: string): void {
  // Load from .env if not provided
  dotenv.config();

  const key = apiKey || process.env.GROQ_API_KEY;

  if (!key) {
    throw new Error(
      "GROQ_API_KEY not found. Provide it as argument or set GROQ_API_KEY environment variable."
    );
  }

  configureGroq(key);
}
