import type { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
	console.log('🧹 Cleaning up after Playwright tests...');

	// Clean up any global resources
	// For example, close database connections, stop servers, etc.

	console.log('✅ Cleanup completed');
}

export default globalTeardown;
