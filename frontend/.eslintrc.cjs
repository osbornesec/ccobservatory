/** @type {import('eslint').Linter.Config} */
module.exports = {
	root: true,
	extends: [
		'eslint:recommended',
		'@typescript-eslint/recommended',
		'plugin:svelte/recommended',
		'prettier'
	],
	parser: '@typescript-eslint/parser',
	plugins: ['@typescript-eslint'],
	parserOptions: {
		sourceType: 'module',
		ecmaVersion: 2020,
		extraFileExtensions: ['.svelte']
	},
	env: {
		browser: true,
		es2017: true,
		node: true
	},
	overrides: [
		{
			files: ['*.svelte'],
			parser: 'svelte-eslint-parser',
			parserOptions: {
				parser: '@typescript-eslint/parser'
			}
		}
	],
	rules: {
		// TypeScript rules
		'@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
		'@typescript-eslint/no-explicit-any': 'warn',
		'@typescript-eslint/explicit-function-return-type': 'off',
		'@typescript-eslint/explicit-module-boundary-types': 'off',
		'@typescript-eslint/prefer-const': 'error',
		
		// General rules
		'no-console': ['warn', { allow: ['warn', 'error'] }],
		'no-debugger': 'error',
		'prefer-const': 'error',
		'no-var': 'error',
		
		// Svelte rules
		'svelte/no-at-html-tags': 'warn',
		'svelte/no-target-blank': 'error'
	},
	ignorePatterns: [
		'*.cjs',
		'.svelte-kit/',
		'build/',
		'node_modules/',
		'coverage/',
		'playwright-report/',
		'test-results/'
	]
};