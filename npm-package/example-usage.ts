/**
 * Example: Using smart-code-reviewer as an npm package
 */

import { initialize, reviewCode } from './dist/index';

async function example() {
  // Initialize with API key from .env
  initialize();

  const code = `
    function quickSort(arr) {
      if (arr.length <= 1) return arr;
      const pivot = arr[0];
      const left = [];
      const right = [];
      for (let i = 1; i < arr.length; i++) {
        arr[i] < pivot ? left.push(arr[i]) : right.push(arr[i]);
      }
      return [...quickSort(left), pivot, ...quickSort(right)];
    }
  `;

  const result = await reviewCode(code);
  
  console.log('🔍 Review Result:');
  console.log(`Language: ${result.language}`);
  console.log(`Overall Score: ${result.overall_score}/10`);
  console.log(`TL;DR: ${result.tldr}\n`);
  
  console.log('📊 Category Breakdown:');
  for (const cat of result.categories) {
    console.log(`\n${cat.category}: ${cat.score}/10`);
    console.log(`Summary: ${cat.summary}`);
    if (cat.suggestions.length > 0) {
      console.log('Suggestions:');
      cat.suggestions.forEach((s, i) => console.log(`  ${i + 1}. ${s}`));
    }
  }
}

example().catch(console.error);
