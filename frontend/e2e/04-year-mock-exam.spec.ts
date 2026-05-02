/**
 * feature.md — Practice by year → Gate CBT workflow (login → instructions → exam).
 */
import { test, expect } from '@playwright/test';
import { goHomeLoggedOut, enterAppFromLanding } from './helpers/app';

test.describe.configure({ mode: 'serial' });

test.describe('Practice by Year → mock GATE shell', () => {
  test.beforeEach(async ({ page }) => {
    await goHomeLoggedOut(page);
    await enterAppFromLanding(page);
    await page.getByRole('button', { name: 'Practice by Year' }).click();
    await expect(page.getByRole('heading', { name: /Practice by Year/i })).toBeVisible();
  });

  test('year card opens full-screen workflow', async ({ page }) => {
    await page.getByRole('heading', { name: '2024' }).click()
    await expect(page.getByText(/Mock Exam|Sign In|GRADUATE APTITUDE TEST/i).first()).toBeVisible({
      timeout: 20_000,
    })
  })

  test('Exit mock exam returns to year grid', async ({ page }) => {
    await page.getByRole('heading', { name: '2025' }).click()
    await expect(page.getByText(/GRADUATE APTITUDE TEST/i).first()).toBeVisible({
      timeout: 25_000,
    })
    await expect(
      page.getByRole('button', { name: /Exit mock exam/i }),
    ).toBeVisible({ timeout: 30_000 })
    await page.getByRole('button', { name: /Exit mock exam/i }).click()
    await expect(page.getByRole('heading', { name: /Practice by Year/i })).toBeVisible({
      timeout: 15_000,
    });
  });
});
