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

	it('should display loading spinner with descriptive text during initial data fetch', () => {
		// Given: A main page component that needs to fetch dashboard data on mount
		// When: The component is initially loading (isLoading state is true)
		// Then: A loading spinner with descriptive text is displayed to provide user feedback during data fetch

		// Loading spinner component provides visual feedback during data loading with accessible text
		expect(componentContent).toContain('<LoadingSpinner size="lg" text="Loading dashboard..." />');

		// Loading state conditional rendering structure shows loading UI when isLoading is true
		expect(componentContent).toContain('{#if isLoading}');
		expect(componentContent).toContain('<div class="flex items-center justify-center h-full">');

		// Loading spinner is properly imported for use in the component
		expect(componentContent).toContain(
			"import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';"
		);
	});

	it('should call API connection test on mount', () => {
		// Given: A main page component that needs to verify backend connectivity
		// When: The component mounts and initializes the dashboard
		// Then: The apiClient.testConnection() method is called once to verify backend availability

		// onMount lifecycle function is imported from svelte for component initialization
		expect(componentContent).toContain("import { onMount } from 'svelte';");

		// API client is imported for backend communication
		expect(componentContent).toContain("import { apiClient } from '$lib/api/client';");

		// onMount function is defined to handle component initialization
		expect(componentContent).toContain('onMount(async () => {');

		// API connection test is called to verify backend connectivity
		expect(componentContent).toContain('const isConnected = await apiClient.testConnection();');

		// Connection failure is handled with error throwing for user feedback
		expect(componentContent).toContain('if (!isConnected) {');
		expect(componentContent).toContain("throw new Error('Cannot connect to backend API');");
	});

	it('should load projects data during initialization', () => {
		// Given: A main page component that needs to display project information
		// When: The component successfully connects to the backend API
		// Then: The apiClient.getProjects() method is called and projects data is stored in the projects store

		// Projects store is imported for state management
		expect(componentContent).toContain(
			"import { projects, conversations, connectionStatus } from '$lib/stores/conversations';"
		);

		// loadData function is defined to handle data fetching
		expect(componentContent).toContain('async function loadData() {');

		// Projects data is fetched from the API
		expect(componentContent).toContain('const projectsData = await apiClient.getProjects();');

		// Projects data is stored in the store for reactive updates
		expect(componentContent).toContain('projects.set(projectsData);');

		// loadData function is called after successful connection test
		expect(componentContent).toContain('await loadData();');
	});

	it('should load conversations data during initialization', () => {
		// Given: A main page component that needs to display recent conversations
		// When: The component loads data after successful API connection
		// Then: The apiClient.getConversations() method is called to fetch recent conversations and store them in conversations store

		// Recent conversations are fetched using pagination (page 1, limit 10)
		expect(componentContent).toContain(
			'const conversationsData = await apiClient.getConversations(1, 10);'
		);

		// Conversations data is stored in the conversations store for reactive updates
		expect(componentContent).toContain('conversations.set(conversationsData.data);');

		// Conversations fetching is part of the loadData function
		expect(componentContent).toContain('// Load recent conversations');
	});

	it('should load analytics data during initialization', () => {
		// Given: A main page component that needs to display dashboard analytics
		// When: The component loads data after successful API connection
		// Then: The apiClient.getAnalytics() method is called to fetch dashboard analytics and store them in analytics variable

		// Analytics data is fetched from the API
		expect(componentContent).toContain('const analyticsData = await apiClient.getAnalytics();');

		// Analytics data is stored in the analytics variable for reactive updates
		expect(componentContent).toContain('analytics = analyticsData;');

		// Analytics fetching is part of the loadData function
		expect(componentContent).toContain('// Load analytics');
	});
});
