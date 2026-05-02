import { expect, type Page } from '@playwright/test'

/** Clears SPA persisted state so tests start from landing/home predictably. */
export const resetSpaStorage = async (page: Page) => {
  await page.goto('/')
  await page.evaluate(() => {
    try {
      localStorage.removeItem('aerogate_state')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    } catch {
      /* ignore */
    }
    try {
      sessionStorage.clear()
    } catch {
      /* ignore */
    }
  })
}

export const goHomeLoggedOut = async (page: Page) => {
  await resetSpaStorage(page)
  await page.goto('/')
  await page.reload()
  await page.waitForLoadState('domcontentloaded')
}

/** Clicks landing hero CTA — wires to `onStart` → `setView('home')`. */
export const enterAppFromLanding = async (page: Page) => {
  await page.getByRole('button', { name: /Start 7-Day Free Trial/i }).first().click()
  await expect(page.getByRole('button', { name: 'Practice by Year' })).toBeVisible({
    timeout: 25_000,
  })
}

export const openAuthModalFromSidebar = async (page: Page) => {
  const loginBtn = page.getByRole('button', { name: /Log In \/ Sign Up/i })
  if (await loginBtn.isVisible().catch(() => false)) {
    await loginBtn.click()
    return
  }
  await page.getByRole('button', { name: /^Login$/i }).first().click()
}

/** Uses email/password when `VITE_ENABLE_EMAIL_LOGIN=true` (Playwright webServer sets this). */
export const loginWithEmailPassword = async (
  page: Page,
  email: string,
  password: string,
) => {
  await openAuthModalFromSidebar(page)
  await page.getByLabel(/^Email$/i).fill(email)
  await page.getByLabel(/^Password$/i).fill(password)
  await page.getByRole('button', { name: /Sign in with email/i }).click()
  await expect(page.getByText(email).first()).toBeVisible({ timeout: 25_000 })
}
