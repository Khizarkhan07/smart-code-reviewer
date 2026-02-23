/**
 * Type definitions for Smart Code Reviewer
 */

export interface CategoryFeedback {
  category: "Readability" | "Structure" | "Maintainability";
  score: number; // 1-10
  summary: string;
  suggestions: string[];
}

export interface ReviewResult {
  language: string;
  categories: CategoryFeedback[];
  overall_score: number;
  tldr: string;
  raw_response?: string;
}

export interface ReviewerConfig {
  apiKey?: string;
  modelName?: string;
  temperature?: number;
  maxTokens?: number;
}

export interface CLIOptions {
  threshold?: number;
  verbose?: boolean;
  files: string[];
}
