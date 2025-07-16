import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
	plugins: [sveltekit()],
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}'],
		exclude: ['tests/e2e/**'],
		environment: 'jsdom',
		globals: true,
		setupFiles: ['./src/test-setup.ts'],
		coverage: {
			provider: 'v8',
			reporter: ['text', 'json', 'html', 'lcov'],
			exclude: [
				'node_modules/',
				'src/test-setup.ts',
				'**/*.d.ts',
				'**/*.config.*',
				'build/',
				'.svelte-kit/',
				'coverage/',
				'playwright-report/',
				'test-results/'
			],
			thresholds: {
				lines: 80,
				functions: 80,
				branches: 70,
				statements: 80
			}
		},
		reporters: ['verbose', 'junit'],
		outputFile: {
			junit: './test-results/unit-results.xml'
		}
	}
});