import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
	test('should load the homepage successfully', async ({ page }) => {
		await page.goto('/');
		
		// Check that the page loads
		await expect(page).toHaveTitle(/Claude Code Observatory/);
		
		// Check for main header
		await expect(page.getByRole('heading', { name: /Claude Code Observatory/i })).toBeVisible();
	});

	test('should display navigation elements', async ({ page }) => {
		await page.goto('/');
		
		// Check for navigation elements
		await expect(page.getByRole('navigation')).toBeVisible();
	});

	test('should be responsive on mobile', async ({ page }) => {
		await page.setViewportSize({ width: 375, height: 667 });
		await page.goto('/');
		
		// Check that content is still visible on mobile
		await expect(page.getByRole('heading', { name: /Claude Code Observatory/i })).toBeVisible();
	});

	test('should handle loading states', async ({ page }) => {
		await page.goto('/');
		
		// Wait for any loading states to complete
		await page.waitForLoadState('networkidle');
		
		// Ensure no loading spinners are still visible
		const loadingSpinner = page.locator('[data-testid="loading-spinner"]');
		await expect(loadingSpinner).not.toBeVisible();
	});
});