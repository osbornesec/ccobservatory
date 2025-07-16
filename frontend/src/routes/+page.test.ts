import { describe, it, expect, beforeEach } from 'vitest';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Main Page Component', () => {
	let componentContent: string;

	beforeEach(() => {
		const componentPath = join(__dirname, '+page.svelte');
		componentContent = readFileSync(componentPath, 'utf-8');
	});

	it('should contain essential navigation landmarks for screen reader accessibility', () => {
		// Given: A main page component that serves as the application dashboard
		// When: The component template structure is examined for accessibility landmarks
		// Then: Essential navigation components and semantic structure are present for users

		// Header component provides banner landmark and top navigation
		expect(componentContent).toContain('<Header />');

		// Sidebar component provides navigation landmark and menu structure
		expect(componentContent).toContain('<Sidebar />');

		// Main element provides main content landmark for primary content
		expect(componentContent).toContain('<main class="flex-1 overflow-auto">');

		// Root container provides proper layout structure
		expect(componentContent).toContain('<div class="min-h-screen bg-base-100">');
		expect(componentContent).toContain('<div class="flex h-[calc(100vh-4rem)]">');
	});

	it('should provide descriptive page title and meta description for user orientation and discoverability', () => {
		// Given: A main page component that serves as the dashboard entry point
		// When: A user navigates to the page or shares it on social media
		// Then: The page provides clear identification through title and description for user orientation and search discovery

		// Page title describes the application's purpose in browser tab for user orientation (WCAG 2.4.2)
		expect(componentContent).toContain('<title>Claude Code Observatory</title>');

		// Meta description summarizes the application's value for search engines and social sharing
		expect(componentContent).toContain(
			'<meta name="description" content="Real-time observability for Claude Code interactions" />'
		);

		// HTML head metadata is properly structured within Svelte head block
		expect(componentContent).toContain('<svelte:head>');
		expect(componentContent).toContain('</svelte:head>');
	});

	it('should display welcome section with clear application identification and value proposition for user orientation', () => {
		// Given: A main page component that serves as the dashboard entry point
		// When: A user views the page content after successful load
		// Then: The welcome section provides clear application identification and explains the system's value proposition for user understanding

		// Primary heading identifies the application clearly following WCAG 2.4.6 (Headings and Labels)
		expect(componentContent).toContain('<h1');
		expect(componentContent).toContain('Welcome to Claude Code Observatory');

		// Descriptive paragraph explains the application's purpose and value to users
		expect(componentContent).toContain('<p');
		expect(componentContent).toContain(
			'Monitor and analyze your Claude Code interactions in real-time'
		);

		// Welcome section structure provides logical content organization within main landmark
		expect(componentContent).toContain('<!-- Welcome Section -->');
		expect(componentContent).toContain('<div class="mb-8">');
	});
});
