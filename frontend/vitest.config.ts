import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig(({ mode }) => ({
	plugins: mode === 'test' ? [svelte({ hot: !process.env.VITEST })] : [sveltekit()],
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
				lines: 90,
				functions: 90,
				branches: 90,
				statements: 90
			}
		}
	},
	define: {
		'import.meta.env.VITEST': true
	},
	resolve: {
		alias: {
			$lib: new URL('./src/lib', import.meta.url).pathname,
			'$app/environment': new URL('./src/mocks/app-environment.ts', import.meta.url).pathname,
			'$app/stores': new URL('./src/mocks/app-stores.ts', import.meta.url).pathname,
			'$env/dynamic/public': new URL('./src/mocks/env-dynamic-public.ts', import.meta.url).pathname,
			'$env/static/public': new URL('./src/mocks/env-static-public.ts', import.meta.url).pathname
		}
	}
}));
