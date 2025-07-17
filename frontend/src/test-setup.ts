import { vi, expect, beforeEach, afterEach } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as matchers from 'jest-axe';

// Extend Vitest's expect with jest-axe matchers for accessibility testing
expect.extend(matchers);

// Mock browser APIs
Object.defineProperty(window, 'matchMedia', {
	writable: true,
	value: vi.fn().mockImplementation(query => ({
		matches: false,
		media: query,
		onchange: null,
		addListener: vi.fn(), // deprecated
		removeListener: vi.fn(), // deprecated
		addEventListener: vi.fn(),
		removeEventListener: vi.fn(),
		dispatchEvent: vi.fn()
	}))
});

// Mock WebSocket
global.WebSocket = vi.fn().mockImplementation(() => ({
	send: vi.fn(),
	close: vi.fn(),
	addEventListener: vi.fn(),
	removeEventListener: vi.fn(),
	readyState: 1
})) as any;

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
	observe: vi.fn(),
	unobserve: vi.fn(),
	disconnect: vi.fn()
}));

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
	observe: vi.fn(),
	unobserve: vi.fn(),
	disconnect: vi.fn()
}));

// Mock fetch if needed
global.fetch = vi.fn();

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
	value: {
		getItem: vi.fn(),
		setItem: vi.fn(),
		removeItem: vi.fn(),
		clear: vi.fn()
	},
	writable: true
});

// Setup console spy
global.console = {
	...console,
	// Suppress console.log in tests unless explicitly needed
	log: vi.fn(),
	warn: vi.fn(),
	error: vi.fn()
};

// Mock SvelteKit modules
vi.mock('$app/environment', () => ({
	browser: true,
	dev: true,
	building: false,
	version: '1.0.0'
}));

vi.mock('$app/stores', () => ({
	page: {
		subscribe: vi.fn()
	},
	updated: {
		subscribe: vi.fn()
	}
}));

vi.mock('$app/state', () => ({
	page: {
		subscribe: vi.fn()
	}
}));

vi.mock('$app/navigation', () => ({
	goto: vi.fn(),
	invalidate: vi.fn(),
	invalidateAll: vi.fn(),
	preloadData: vi.fn(),
	preloadCode: vi.fn(),
	beforeNavigate: vi.fn(),
	afterNavigate: vi.fn(),
	pushState: vi.fn(),
	replaceState: vi.fn()
}));

// Mock requestAnimationFrame for focus management animations
global.requestAnimationFrame = vi.fn((cb) => setTimeout(cb, 16));
global.cancelAnimationFrame = vi.fn((id) => clearTimeout(id));

// Setup for accessibility testing - ensure we have a clean DOM
beforeEach(() => {
	// Clear any existing accessibility violations highlights
	document.querySelectorAll('[data-contrast-violation]').forEach(el => {
		el.removeAttribute('data-contrast-violation');
		(el as HTMLElement).style.outline = '';
		(el as HTMLElement).style.outlineOffset = '';
	});

	// Clear local storage mocks
	vi.clearAllMocks();
});

// Cleanup after tests
afterEach(() => {
	// Cleanup any focus traps or event listeners that might persist
	document.body.style.overflow = '';
	
	// Clear any timers that might be running
	vi.clearAllTimers();
	
	// Reset DOM
	document.body.innerHTML = '';
});

// Global test utilities for accessibility testing
export const a11yTestUtils = {
	/**
	 * Helper to test WCAG 2.1 AA compliance specifically
	 */
	async checkWCAG21AA(container: HTMLElement) {
		const { axe } = await import('jest-axe');
		const results = await axe(container, {
			runOnly: {
				type: 'tag',
				values: ['wcag21aa']
			}
		});
		expect(results).toHaveNoViolations();
		return results;
	},

	/**
	 * Helper to test specific accessibility rules
	 */
	async checkSpecificRules(container: HTMLElement, rules: string[]) {
		const { axe } = await import('jest-axe');
		const results = await axe(container, {
			runOnly: {
				type: 'rule',
				values: rules
			}
		});
		expect(results).toHaveNoViolations();
		return results;
	},

	/**
	 * Helper to simulate keyboard navigation
	 */
	simulateKeypress(element: HTMLElement, key: string, options: Partial<KeyboardEventInit> = {}) {
		const event = new KeyboardEvent('keydown', {
			key,
			code: key,
			bubbles: true,
			cancelable: true,
			...options
		});
		element.dispatchEvent(event);
		return event;
	},

	/**
	 * Helper to test focus management
	 */
	async testFocusManagement(container: HTMLElement) {
		const focusableElements = container.querySelectorAll(
			'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
		);

		// Test that all focusable elements can receive focus
		for (const element of focusableElements) {
			(element as HTMLElement).focus();
			expect(document.activeElement).toBe(element);
		}

		return focusableElements;
	},

	/**
	 * Helper to test ARIA attributes
	 */
	testAriaAttributes(element: HTMLElement, expectedAttributes: Record<string, string>) {
		Object.entries(expectedAttributes).forEach(([attr, value]) => {
			expect(element).toHaveAttribute(attr, value);
		});
	},

	/**
	 * Mock system accessibility preferences
	 */
	mockAccessibilityPreferences(preferences: {
		reducedMotion?: boolean;
		highContrast?: boolean;
	}) {
		window.matchMedia = vi.fn().mockImplementation(query => {
			let matches = false;
			if (query === '(prefers-reduced-motion: reduce)' && preferences.reducedMotion) {
				matches = true;
			}
			if (query === '(prefers-contrast: high)' && preferences.highContrast) {
				matches = true;
			}
			return {
				matches,
				media: query,
				onchange: null,
				addListener: vi.fn(),
				removeListener: vi.fn(),
				addEventListener: vi.fn(),
				removeEventListener: vi.fn(),
				dispatchEvent: vi.fn(),
			};
		});
	}
};
