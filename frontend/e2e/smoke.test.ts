import { test, expect } from './coverage';

test('login page loads', async ({ page }) => {
	await page.goto('/login');
	await expect(page).toHaveTitle(/e-Vinha/i);
});
