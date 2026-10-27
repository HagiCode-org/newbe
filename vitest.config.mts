import { defineConfig } from 'vitest/config';

export default defineConfig({
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
