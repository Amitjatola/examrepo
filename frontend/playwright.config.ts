import { defineConfig, devices } from '@playwright/test';

/**
 * E2E config — maps to feature.md "Where features live" (MainContent views).
 * @see /feature.md
 *
 * Default port 5174 avoids clobbering a human `vite` on 5173; stale bundles happen when
 * `reuseExistingServer` attaches to an old dev server (missing data-testid / new UI).
 */
const e2ePort = process.env.PLAYWRIGHT_E2E_PORT || '5174';
const baseURL = process.env.PLAYWRIGHT_BASE_URL || `http://localhost:${e2ePort}`;
/** Only set PW_REUSE_DEV_SERVER=1 when you already run `vite` on the same port as baseURL. */
const reuseDevServer = process.env.PW_REUSE_DEV_SERVER === '1';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  timeout: 60_000,
  expect: { timeout: 15_000 },
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'e2e-results/test-results.json' }],
  ],
  use: {
    baseURL,
    viewport: { width: 1400, height: 900 },
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 15_000,
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
      },
    },
    /** Use when Chromium headless shell is missing for your arch (`npx playwright install`). */
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
      },
    },
  ],
  webServer: process.env.PLAYWRIGHT_SKIP_WEBSERVER
    ? undefined
    : {
        command: `npm run dev -- --port ${e2ePort} --strictPort`,
        url: baseURL,
        /** Set PW_REUSE_DEV_SERVER=1 only if you intentionally run vite yourself on the same port. */
        reuseExistingServer: reuseDevServer,
        timeout: 120_000,
        env: {
          ...process.env,
          // Allow email login in auth modal for E2E (superuser / test accounts)
          VITE_ENABLE_EMAIL_LOGIN: 'true',
        },
      },
});
