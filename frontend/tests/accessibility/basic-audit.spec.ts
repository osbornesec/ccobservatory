import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility Audit', () => {
	test('should not have any automatically detectable accessibility issues', async ({ page }) => {
		await page.goto('/');
		
		const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
		
		expect(accessibilityScanResults.violations).toEqual([]);
	});

	test('should not have accessibility issues on dashboard page', async ({ page }) => {
		await page.goto('/');
		
		// Wait for page to load completely
		await page.waitForLoadState('networkidle');
		
		const accessibilityScanResults = await new AxeBuilder({ page })
			.withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
			.analyze();
		
		// Log violations for debugging
		if (accessibilityScanResults.violations.length > 0) {
			console.log('Accessibility violations found:');
			accessibilityScanResults.violations.forEach((violation) => {
				console.log(`- ${violation.id}: ${violation.description}`);
				console.log(`  Help: ${violation.helpUrl}`);
				console.log(`  Nodes: ${violation.nodes.length}`);
			});
		}
		
		expect(accessibilityScanResults.violations).toEqual([]);
	});

	test('should support keyboard navigation', async ({ page }) => {
		await page.goto('/');
		
		// Test Tab navigation through interactive elements
		await page.keyboard.press('Tab');
		
		// Check if first focusable element is highlighted
		const focused = await page.locator(':focus').first();
		await expect(focused).toBeVisible();
		
		// Continue tabbing through navigation
		for (let i = 0; i < 5; i++) {
			await page.keyboard.press('Tab');
			const currentFocus = await page.locator(':focus').first();
			await expect(currentFocus).toBeVisible();
		}
	});

	test('should have proper heading structure', async ({ page }) => {
		await page.goto('/');
		
		// Check for h1 element
		const h1 = page.locator('h1');
		await expect(h1).toBeVisible();
		await expect(h1).toHaveText('Claude Code Observatory');
		
		// Verify heading hierarchy (no skipped levels)
		const accessibilityScanResults = await new AxeBuilder({ page })
			.withRules(['heading-order'])
			.analyze();
		
		expect(accessibilityScanResults.violations).toEqual([]);
	});

	test('should have sufficient color contrast', async ({ page }) => {
		await page.goto('/');
		
		const accessibilityScanResults = await new AxeBuilder({ page })
			.withRules(['color-contrast'])
			.analyze();
		
		expect(accessibilityScanResults.violations).toEqual([]);
	});

	test('should have proper ARIA labels and roles', async ({ page }) => {
		await page.goto('/');
		
		const accessibilityScanResults = await new AxeBuilder({ page })
			.withRules(['aria-labels', 'button-name', 'link-name'])
			.analyze();
		
		expect(accessibilityScanResults.violations).toEqual([]);
	});
});