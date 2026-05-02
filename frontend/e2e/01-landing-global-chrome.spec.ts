/**
 * feature.md — Landing + global chrome (Header / theme).
 * Surfaces: Landing, Header theme, entry into main app.
 */
import { test, expect } from '@playwright/test';
import { goHomeLoggedOut, enterAppFromLanding } from './helpers/app';

test.describe('Landing & global chrome', () => {
  test.beforeEach(async ({ page }) => {
    await goHomeLoggedOut(page);
  });

  test('landing shows hero and primary CTA', async ({ page }) => {
    await expect(page.getByText(/Master GATE Aerospace/i).first()).toBeVisible();
    await expect(
      page.getByRole('button', { name: /Start 7-Day Free Trial/i }).first(),
    ).toBeVisible();
  });

  test('theme toggle on landing does not crash', async ({ page }) => {
    const themeBtn = page.getByRole('button', { name: /Toggle Theme/i });
    await themeBtn.click();
    await page.waitForTimeout(200);
    await themeBtn.click();
  });

  test('Start 7-Day Free Trial leaves landing (view home)', async ({ page }) => {
    await enterAppFromLanding(page)
    await expect(page.getByRole('button', { name: 'Practice by Year' })).toBeVisible()
  })

  test('Sign Up opens auth UI (email path when env enabled)', async ({ page }) => {
    await page.getByRole('button', { name: /Sign Up/i }).click();
    await expect(page.getByRole('heading', { name: /Create Account/i })).toBeVisible({
      timeout: 15_000,
    });
    const emailField = page.locator('#auth-email');
    if ((await emailField.count()) === 0) {
      test.skip(
        true,
        'Email fields require VITE_ENABLE_EMAIL_LOGIN=true at Vite dev startup (playwright webServer sets this)',
      );
    }
    await expect(emailField).toBeVisible({ timeout: 10_000 });
  });
});
