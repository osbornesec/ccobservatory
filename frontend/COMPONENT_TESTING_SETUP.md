# SvelteKit Component Testing Infrastructure Setup

## Overview

This document outlines the comprehensive component testing infrastructure setup for the Claude Code Observatory (CCO) frontend using SvelteKit, Vitest, and @testing-library/svelte.

## Dependencies Installed

### Testing Libraries

- **@testing-library/svelte** (v5.2.8) - DOM testing utilities for Svelte components
- **@testing-library/user-event** (v14.6.1) - Simulates user interactions
- **@testing-library/jest-dom** (v6.6.3) - Custom DOM matchers

### Testing Framework

- **vitest** (v1.6.0) - Fast unit testing framework
- **@vitest/coverage-v8** (v1.6.0) - Code coverage reporting
- **jsdom** (v23.0.0) - DOM environment for Node.js testing

## Configuration

### 1. Vitest Configuration (`vitest.config.ts`)

```typescript
import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig(({ mode }) => ({
	plugins: mode === 'test' ? [] : [sveltekit()],
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
```

### 2. Test Setup (`src/test-setup.ts`)

```typescript
import { vi } from 'vitest';
import '@testing-library/jest-dom/vitest';

// Mock browser APIs
Object.defineProperty(window, 'matchMedia', {
	writable: true,
	value: vi.fn().mockImplementation(query => ({
		matches: false,
		media: query,
		onchange: null,
		addListener: vi.fn(),
		removeListener: vi.fn(),
		addEventListener: vi.fn(),
		removeEventListener: vi.fn(),
		dispatchEvent: vi.fn()
	}))
});

// Mock WebSocket, ResizeObserver, IntersectionObserver, fetch, localStorage
// ... additional mocks
```

### 3. Package.json Scripts

```json
{
	"scripts": {
		"test": "vitest run --mode test",
		"test:watch": "vitest --mode test",
		"test:coverage": "vitest run --coverage --mode test"
	}
}
```

## Testing Infrastructure Validation

The setup includes a comprehensive validation test (`SimpleButton.test.ts`) that verifies:

1. **@testing-library/svelte integration** - Confirms render function is available
2. **jsdom environment** - Validates DOM APIs (window, document) are available
3. **jest-dom matchers** - Tests custom matchers like `toBeInTheDocument()`
4. **user-event library** - Verifies user interaction simulation capabilities
5. **fireEvent integration** - Confirms DOM event simulation works
6. **screen queries** - Tests DOM querying capabilities

## Component Testing Patterns

### Basic Test Structure

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import MyComponent from './MyComponent.svelte';

describe('MyComponent', () => {
	beforeEach(() => {
		// Clean up DOM before each test
		document.body.innerHTML = '';
	});

	afterEach(() => {
		// Clean up after each test
		cleanup();
		document.body.innerHTML = '';
	});

	it('renders component correctly', () => {
		render(MyComponent, { props: { title: 'Test Title' } });

		expect(screen.getByText('Test Title')).toBeInTheDocument();
	});

	it('handles user interactions', async () => {
		const user = userEvent.setup();
		render(MyComponent);

		const button = screen.getByRole('button');
		await user.click(button);

		// Assert expected behavior
	});
});
```

### Testing with Props and Stores

```typescript
import { vi } from 'vitest';

// Mock stores
vi.mock('$lib/stores/theme', () => ({
	themeStore: {
		subscribe: vi.fn(callback => {
			callback('light');
			return vi.fn(); // unsubscribe function
		}),
		toggle: vi.fn()
	}
}));

// Test component with props
render(MyComponent, {
	props: {
		size: 'lg',
		color: 'primary'
	}
});
```

## Current Limitations

### Svelte Component Compilation

- The current setup does not include Svelte plugin for test mode
- Direct Svelte component rendering requires additional configuration
- Svelte components can be imported but may not compile properly in tests

### Workaround

For now, use the existing pattern of testing component logic separately:

- Test component file content validation (as in `Header.test.ts`)
- Test component utilities and helper functions
- Use the infrastructure validation tests for @testing-library patterns

## Advanced Configuration (Future Enhancement)

To enable full Svelte component rendering in tests, add to `vitest.config.ts`:

```typescript
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { svelteTesting } from '@testing-library/svelte/vite';

export default defineConfig(({ mode }) => ({
	plugins:
		mode === 'test'
			? [
					svelte({
						compilerOptions: {
							hydratable: true
						}
					}),
					svelteTesting()
				]
			: [sveltekit()]
	// ... rest of config
}));
```

Note: This configuration may require additional setup to resolve plugin conflicts.

## Best Practices

1. **Use semantic queries** - Prefer `getByRole`, `getByLabelText`, `getByText` over `getByTestId`
2. **Test behavior, not implementation** - Focus on what users see and do
3. **Mock external dependencies** - Use `vi.mock()` for stores, APIs, external libraries
4. **Clean up between tests** - Use `beforeEach`/`afterEach` for DOM cleanup
5. **Use user-event over fireEvent** - More realistic user interaction simulation
6. **Write descriptive test names** - Clearly describe what behavior is being tested

## Coverage Requirements

The setup enforces high coverage standards:

- Lines: 90%
- Functions: 90%
- Branches: 90%
- Statements: 90%

## Running Tests

```bash
# Run all tests once
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage

# Run specific test file
npm test -- ComponentName.test.ts
```

## Conclusion

The component testing infrastructure is now properly configured with:

- ✅ @testing-library/svelte dependencies installed
- ✅ Vitest configured for component testing
- ✅ jsdom environment setup
- ✅ jest-dom matchers available
- ✅ Validation tests passing
- ⚠️ Full Svelte component rendering pending advanced configuration

The setup provides a solid foundation for comprehensive component testing following Testing Library best practices.
