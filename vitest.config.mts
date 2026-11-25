import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  // Docusaurus resolves `@site/...` to the site root; mirror it so image imports resolve under test.
  resolve: {
    alias: {
      '@site': fileURLToPath(new URL('.', import.meta.url)),
      // `@docusaurus/Link` exists only inside a Docusaurus build; tests get a plain anchor stand-in.
      '@docusaurus/Link': fileURLToPath(new URL('./src/testing/docusaurus-link.tsx', import.meta.url)),
    },
  },
  test: {
    // Memory bound: cap the worker count and give every worker a V8 heap ceiling, so a leaking test file fails with an OOM
    // instead of exhausting the machine.
    maxWorkers: 4,
    execArgv: ['--max-old-space-size=4096'],
    environment: 'jsdom',
    // Only the React/TypeScript sources. tests/*.test.cjs are node:test suites run by `node --test`.
    include: ['src/**/*.test.{ts,tsx}'],
    exclude: ['node_modules', 'build', '.docusaurus', '**/*.config.*'],
  },
});
