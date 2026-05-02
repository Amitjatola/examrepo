/**
 * feature.md — Search results (`view === 'results'`) needs backend + data.
 */
import { test, expect } from '@playwright/test'
import { goHomeLoggedOut, enterAppFromLanding } from './helpers/app'

test.describe('Search & API integration', () => {
  test('search from guest home hub shows results, empty state, or backend error', async ({
    page,
  }) => {
    await goHomeLoggedOut(page)
    await enterAppFromLanding(page)
    const search = page.getByPlaceholder(/Type a concept/i).first()
    await search.fill('fluid')
    await search.press('Enter')
    const backendMsg = page.getByText(/Make sure the backend is running/i).first()
    if (await backendMsg.isVisible({ timeout: 12_000 }).catch(() => false)) {
      test.skip(true, 'Start backend (e.g. localhost:8000) to exercise search end-to-end')
    }
    const okBlock = page.getByText(/Found \d+|No questions found for this search/i).first()
    await expect(okBlock).toBeVisible({ timeout: 25_000 })
  })
})
