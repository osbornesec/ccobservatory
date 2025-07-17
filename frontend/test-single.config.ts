import { defineConfig } from 'vitest/config';

export default defineConfig({
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}'],
		exclude: ['tests/e2e/**'],
		environment: 'jsdom',
		globals: true,
		setupFiles: ['./src/test-setup.ts']
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
});
