/**
 * feature.md — Premium / Pro: `view === 'premium'` → PremiumPage; Header Go Pro.
 */
import { test, expect } from '@playwright/test';
import { goHomeLoggedOut, enterAppFromLanding, loginWithEmailPassword } from './helpers/app';

test.describe('Header Go Pro & Premium page', () => {
  test.beforeEach(async ({ page }) => {
    await goHomeLoggedOut(page);
    await enterAppFromLanding(page);
  });

  test('Go Pro navigates to pricing / PremiumPage', async ({ page }) => {
    // Prefer role+name: works even if a stale dev server omits data-testid on Header.
    const goPro = page.getByRole('button', { name: /View Pro pricing and benefits|Go Pro/i });
    await expect(goPro).toBeVisible();
    await goPro.click();
    await expect(page.getByText(/Unlock your full potential/i)).toBeVisible({ timeout: 25_000 });
    await expect(page.getByRole('button', { name: /Back to app/i })).toBeVisible();
  });

  test('Back to app returns from premium view', async ({ page }) => {
    await page.getByRole('button', { name: /View Pro pricing and benefits|Go Pro/i }).click();
    await page.getByRole('button', { name: /Back to app/i }).click();
    await expect(page.getByRole('button', { name: 'Practice by Year' })).toBeVisible({
      timeout: 15_000,
    });
  });

  test('Pro user: Go Pro hidden when E2E credentials are Pro', async ({ page }) => {
    test.skip(!process.env.E2E_EMAIL || !process.env.E2E_PASSWORD, 'Set E2E_EMAIL and E2E_PASSWORD');
    await loginWithEmailPassword(page, process.env.E2E_EMAIL!, process.env.E2E_PASSWORD!);
    await expect(page.getByRole('button', { name: /Go Pro/i })).toHaveCount(0);
  });
});
