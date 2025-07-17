import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Comprehensive Accessibility Compliance', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the homepage before each test
    await page.goto('/');
    // Wait for initial load
    await page.waitForLoadState('networkidle');
  });

  test('should not have any automatically detectable accessibility issues on homepage', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should support keyboard navigation through all interactive elements', async ({ page }) => {
    // Start from first focusable element
    await page.keyboard.press('Tab');
    
    // Should focus on skip link first
    const focused = page.locator(':focus');
    await expect(focused).toHaveText(/Skip to main content/);
    
    // Continue tabbing through navigation
    await page.keyboard.press('Tab'); // Skip to navigation link
    await page.keyboard.press('Tab'); // First nav item
    
    // Verify focus is visible
    await expect(page.locator(':focus')).toBeVisible();
    
    // Test Enter key activation
    await page.keyboard.press('Enter');
    // Should navigate or activate the focused element
  });

  test('should have proper skip links that appear on focus', async ({ page }) => {
    // Press Tab to reveal skip links
    await page.keyboard.press('Tab');
    
    const skipLink = page.locator('.skip-link:focus');
    await expect(skipLink).toBeVisible();
    await expect(skipLink).toHaveText('Skip to main content');
    
    // Test skip link functionality
    await page.keyboard.press('Enter');
    
    // Should jump to main content
    const mainContent = page.locator('#main-content');
    await expect(mainContent).toBeFocused();
  });

  test('should announce navigation changes to screen readers', async ({ page }) => {
    const announcer = page.locator('[data-testid="accessibility-announcer"]');
    
    // Should have proper ARIA attributes
    await expect(announcer).toHaveAttribute('aria-live', 'polite');
    await expect(announcer).toHaveAttribute('aria-atomic', 'true');
    await expect(announcer).toHaveAttribute('role', 'status');
  });

  test('should meet WCAG 2.1 AA color contrast requirements', async ({ page }) => {
    const contrastScanResults = await new AxeBuilder({ page })
      .withTags(['wcag21aa'])
      .include('color-contrast')
      .analyze();
    
    expect(contrastScanResults.violations).toEqual([]);
  });

  test('should have proper heading hierarchy', async ({ page }) => {
    const headingScanResults = await new AxeBuilder({ page })
      .withRules(['heading-order'])
      .analyze();
    
    expect(headingScanResults.violations).toEqual([]);
    
    // Check that h1 exists and is unique
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBe(1);
  });

  test('should have proper ARIA labels and descriptions', async ({ page }) => {
    const ariaScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a'])
      .withRules(['aria-valid-attr', 'aria-valid-attr-value', 'button-name', 'link-name'])
      .analyze();
    
    expect(ariaScanResults.violations).toEqual([]);
  });

  test('should support screen reader navigation landmarks', async ({ page }) => {
    // Check for proper landmarks
    await expect(page.locator('header[role="banner"], header')).toBeVisible();
    await expect(page.locator('nav[role="navigation"], nav')).toBeVisible();
    await expect(page.locator('main[role="main"], main')).toBeVisible();
    
    const landmarkScanResults = await new AxeBuilder({ page })
      .withRules(['landmark-unique', 'region'])
      .analyze();
    
    expect(landmarkScanResults.violations).toEqual([]);
  });

  test('should handle focus management in modals', async ({ page }) => {
    // Navigate to settings page
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
    
    // Open accessibility help modal
    await page.click('button:has-text("Accessibility Help")');
    
    // Modal should be visible and focused
    const modal = page.locator('[data-testid="modal"]');
    await expect(modal).toBeVisible();
    
    // Focus should be trapped within modal
    await page.keyboard.press('Tab');
    const focusedElement = page.locator(':focus');
    
    // Should be within the modal
    await expect(modal).toContainText(await focusedElement.textContent() || '');
    
    // Test escape key closes modal
    await page.keyboard.press('Escape');
    await expect(modal).not.toBeVisible();
  });

  test('should provide alternative text for images and icons', async ({ page }) => {
    const imageScanResults = await new AxeBuilder({ page })
      .withRules(['image-alt'])
      .analyze();
    
    expect(imageScanResults.violations).toEqual([]);
    
    // Check that decorative icons have aria-hidden
    const decorativeIcons = page.locator('[aria-hidden="true"]');
    expect(await decorativeIcons.count()).toBeGreaterThan(0);
  });

  test('should support zoom up to 200% without loss of functionality', async ({ page }) => {
    // Set zoom to 200%
    await page.setViewportSize({ width: 640, height: 480 }); // Simulate zoom
    
    // Check that content is still accessible
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('nav')).toBeVisible();
    
    // Check that interactive elements are still clickable
    const navLinks = page.locator('nav a');
    const firstLink = navLinks.first();
    await expect(firstLink).toBeVisible();
    await firstLink.click();
  });
});

test.describe('Settings Page Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
  });

  test('should not have accessibility violations on settings page', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should announce theme changes', async ({ page }) => {
    const announcer = page.locator('[data-testid="accessibility-announcer"]');
    
    // Toggle theme
    await page.click('input[type="checkbox"][aria-label*="Toggle"]');
    
    // Wait for announcement
    await page.waitForTimeout(200);
    
    // Should announce theme change
    const announcementText = await announcer.textContent();
    expect(announcementText).toMatch(/theme changed/i);
  });

  test('should provide accessible color contrast audit', async ({ page }) => {
    // Show contrast audit
    await page.click('button:has-text("Show Color Contrast Audit")');
    
    const auditSection = page.locator('#contrast-audit');
    await expect(auditSection).toBeVisible();
    
    // Run audit
    await page.click('button:has-text("Run Audit")');
    
    // Should show results
    await expect(page.locator('.color-contrast-audit')).toBeVisible();
  });
});

test.describe('Keyboard Navigation', () => {
  test('should navigate through all pages using only keyboard', async ({ page }) => {
    await page.goto('/');
    
    // Navigate to each main section using keyboard
    const sections = ['Dashboard', 'Conversations', 'Projects', 'Analytics', 'Settings'];
    
    for (const section of sections) {
      // Find and activate navigation link
      await page.keyboard.press('Tab');
      while (true) {
        const focused = page.locator(':focus');
        const text = await focused.textContent();
        if (text === section) {
          await page.keyboard.press('Enter');
          break;
        }
        await page.keyboard.press('Tab');
      }
      
      // Verify navigation worked
      await page.waitForLoadState('networkidle');
      const currentUrl = page.url();
      if (section !== 'Dashboard') {
        expect(currentUrl).toContain(section.toLowerCase());
      }
    }
  });

  test('should handle arrow key navigation in menus', async ({ page }) => {
    await page.goto('/');
    
    // Focus on navigation menu
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab'); // Skip to navigation
    
    // Use arrow keys to navigate menu items
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('ArrowDown');
    
    // Should focus on different menu items
    const focused = page.locator(':focus');
    await expect(focused).toBeVisible();
  });
});