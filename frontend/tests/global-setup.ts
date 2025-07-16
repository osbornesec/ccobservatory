import { chromium } from '@playwright/test';
import type { FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
	console.log('🎭 Setting up Playwright tests...');

	// Start browser for shared context if needed
	const browser = await chromium.launch();
	const page = await browser.newPage();

	// Wait for application to be ready
	const baseURL = config.projects[0].use.baseURL || 'http://localhost:4173';

	try {
		await page.goto(baseURL);
		await page.waitForLoadState('networkidle');
		console.log('✅ Application is ready for testing');
	} catch (error) {
		console.error('❌ Failed to reach application:', error);
		throw error;
	} finally {
		await browser.close();
	}
}

export default globalSetup;
