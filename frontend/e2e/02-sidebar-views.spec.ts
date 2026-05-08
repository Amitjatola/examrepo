/**
 * feature.md — Website map: Dashboard, Practice by Year, Practice by Concepts, Smart Planner.
 * Code: MainContent `view` + Sidebar `activeTab`.
 */
import { test, expect } from '@playwright/test'
import {
  goHomeLoggedOut,
  enterAppFromLanding,
  loginWithEmailPassword,
} from './helpers/app'

test.describe('Sidebar navigation (guest vs auth)', () => {
  test.beforeEach(async ({ page }) => {
    await goHomeLoggedOut(page);
    await enterAppFromLanding(page);
  });

  test('Practice by Year tab shows year grid heading', async ({ page }) => {
    await page.getByRole('button', { name: 'Practice by Year' }).click();
    await expect(page.getByRole('heading', { name: /Practice by Year/i })).toBeVisible();
  });

  test('Practice by Concepts opens concept/syllabus selection', async ({ page }) => {
    const btn = page.getByRole('button', { name: /Practice by Concepts/i });
    await btn.first().click();
    await expect(page.getByRole('heading', { name: /Practice by Concepts/i })).toBeVisible({
      timeout: 20_000,
    });
  });

  test('Smart Planner entry exists when logged in only', async ({ page }) => {
    const planner = page.getByRole('button', { name: /Smart Planner/i });
    if (process.env.E2E_EMAIL && process.env.E2E_PASSWORD) {
      await loginWithEmailPassword(page, process.env.E2E_EMAIL, process.env.E2E_PASSWORD)
      await expect(planner).toBeVisible({ timeout: 15_000 })
      await planner.click()
      await expect(
        page.getByText(/Scheduling upgrades are coming|Smart Planner/i).first(),
      ).toBeVisible({ timeout: 15_000 })
    } else {
      await expect(planner).toHaveCount(0);
    }
  });
});
