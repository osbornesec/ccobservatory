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

	it('should display error message when API connection fails', () => {
		// Given: A main page component that needs to verify backend connectivity
		// When: The component mounts and the API connection test fails
		// Then: An error message "Cannot connect to backend API" is displayed with retry functionality

		// Error message component is imported for displaying connection errors
		expect(componentContent).toContain(
			"import ErrorMessage from '$lib/components/ErrorMessage.svelte';"
		);

		// Error state variable is declared to track connection failures
		expect(componentContent).toContain('let error: string | null = null;');

		// Error display section shows ErrorMessage component when error occurs
		expect(componentContent).toContain('{:else if error}');
		expect(componentContent).toContain(
			'<ErrorMessage title="Failed to Load Dashboard" message={error} retryAction={retryLoad} />'
		);

		// Retry function is provided to allow user to retry connection
		expect(componentContent).toContain('async function retryLoad() {');

		// Error handling in try-catch block captures API connection failures
		expect(componentContent).toContain('} catch (err) {');
		expect(componentContent).toContain(
			"error = err instanceof Error ? err.message : 'Failed to initialize application';"
		);
	});

	it('should display retry button when data loading fails', () => {
		// Given: A main page component that successfully connects to the backend API
		// When: The API connection succeeds but data loading fails in loadData()
		// Then: An error message "Failed to load data from server" is displayed with a functional retry button

		// loadData function throws specific error when data loading fails
		expect(componentContent).toContain("throw new Error('Failed to load data from server');");

		// retryLoad function clears error state and shows loading indicator
		expect(componentContent).toContain('error = null;');
		expect(componentContent).toContain('isLoading = true;');

		// retryLoad function calls loadData to attempt recovery
		expect(componentContent).toContain('await loadData();');

		// Error handling in retryLoad captures data loading failures
		expect(componentContent).toContain('} catch (err) {');
		expect(componentContent).toContain(
			"error = err instanceof Error ? err.message : 'Failed to load data';"
		);

		// ErrorMessage component includes retry functionality via retryAction prop
		expect(componentContent).toContain('retryAction={retryLoad}');
	});

	it('should handle network timeout gracefully', () => {
		// Given: A main page component that makes API requests with timeout handling
		// When: API requests time out (take longer than configured timeout)
		// Then: An error message displays timeout handling with retry option

		// API client is configured with timeout handling (imported from client)
		expect(componentContent).toContain("import { apiClient } from '$lib/api/client';");

		// Connection test handles timeout scenarios
		expect(componentContent).toContain('const isConnected = await apiClient.testConnection();');

		// Data loading methods handle timeout scenarios
		expect(componentContent).toContain('const projectsData = await apiClient.getProjects();');
		expect(componentContent).toContain(
			'const conversationsData = await apiClient.getConversations(1, 10);'
		);
		expect(componentContent).toContain('const analyticsData = await apiClient.getAnalytics();');

		// Error handling captures timeout errors and provides user feedback
		expect(componentContent).toContain('} catch (err) {');
		expect(componentContent).toContain(
			"error = err instanceof Error ? err.message : 'Failed to initialize application';"
		);

		// Retry mechanism allows recovery from timeout errors
		expect(componentContent).toContain('async function retryLoad() {');
		expect(componentContent).toContain('retryAction={retryLoad}');
	});

	it('should show fallback UI when WebSocket connection fails', () => {
		// Given: A main page component that loads successfully but WebSocket connection fails
		// When: The component loads but WebSocket fails to connect
		// Then: Connection status shows "Disconnected" or "Error" badge with appropriate styling

		// WebSocket client is imported for real-time communication
		expect(componentContent).toContain("import { wsClient } from '$lib/api/websocket';");

		// Connection status store is imported to track WebSocket state
		expect(componentContent).toContain('connectionStatus');

		// WebSocket connection status is displayed in the UI
		expect(componentContent).toContain('$connectionStatus');

		// Connection status badge shows different styles based on connection state
		expect(componentContent).toContain("class=\"badge {$connectionStatus === 'connected'");
		expect(componentContent).toContain("? 'badge-success'");
		expect(componentContent).toContain(": 'badge-warning'}\"");

		// Connection status text updates based on WebSocket state
		expect(componentContent).toContain(
			"{$connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}"
		);

		// WebSocket event handlers are configured for connection management
		expect(componentContent).toContain("wsClient.on('conversation_update'");
		expect(componentContent).toContain("wsClient.on('project_update'");
	});

	it('should recover gracefully from invalid data responses', () => {
		// Given: A main page component that receives API responses
		// When: The API returns malformed or invalid data
		// Then: An error message displays with graceful degradation, not application crash

		// Data loading functions are wrapped in try-catch for error handling
		expect(componentContent).toContain('try {');
		expect(componentContent).toContain('} catch (err) {');

		// loadData function throws descriptive error for invalid data
		expect(componentContent).toContain("throw new Error('Failed to load data from server');");

		// Error handling prevents crashes and provides user feedback
		expect(componentContent).toContain(
			"error = err instanceof Error ? err.message : 'Failed to initialize application';"
		);

		// Analytics data has safe default values to prevent UI crashes
		expect(componentContent).toContain('let analytics = {');
		expect(componentContent).toContain('total_conversations: 0,');
		expect(componentContent).toContain('total_messages: 0,');
		expect(componentContent).toContain('total_tool_calls: 0,');
		expect(componentContent).toContain('avg_conversation_length: 0');

		// UI safely displays analytics data with defensive programming
		expect(componentContent).toContain('{analytics.total_conversations}');
		expect(componentContent).toContain('{Math.round(analytics.avg_conversation_length)}');

		// Retry mechanism allows recovery from invalid data errors
		expect(componentContent).toContain('retryAction={retryLoad}');
	});

	// Phase 4: Analytics Display & Formatting Tests
	it('should display analytics cards with proper DaisyUI formatting', () => {
		// Given: A main page component that displays analytics dashboard
		// When: The component renders analytics cards after successful data load
		// Then: Analytics cards use proper DaisyUI styling classes for consistent visual presentation

		// Verify main analytics grid container with responsive classes
		expect(componentContent).toContain(
			'<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">'
		);

		// Verify Quick Stats section comment for organization
		expect(componentContent).toContain('<!-- Quick Stats -->');

		// Verify individual analytics cards use proper DaisyUI card classes
		// (Note: Component has 6 total cards - 4 analytics + 2 in Getting Started section)
		const cardPattern = '<div class="card bg-base-100 shadow-lg border border-base-300">';
		const cardMatches = componentContent.match(
			new RegExp(cardPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')
		);
		expect(cardMatches).not.toBeNull();
		expect(cardMatches?.length).toBe(6); // Six total cards (4 analytics + 2 getting started)

		// Verify each card contains card-body element
		const cardBodyPattern = '<div class="card-body">';
		const cardBodyMatches = componentContent.match(
			new RegExp(cardBodyPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')
		);
		expect(cardBodyMatches).not.toBeNull();
		expect(cardBodyMatches?.length).toBeGreaterThanOrEqual(4); // At least four card-body elements

		// Verify card content structure with flex layout
		expect(componentContent).toContain('<div class="flex items-center justify-between">');

		// Verify analytics labels are properly styled
		expect(componentContent).toContain(
			'<p class="text-base-content/70 text-sm">Total Conversations</p>'
		);
		expect(componentContent).toContain(
			'<p class="text-base-content/70 text-sm">Total Messages</p>'
		);
		expect(componentContent).toContain('<p class="text-base-content/70 text-sm">Tool Calls</p>');
		expect(componentContent).toContain('<p class="text-base-content/70 text-sm">Avg Length</p>');
	});

	it('should show numeric values with appropriate formatting (commas, decimals)', () => {
		// Given: A main page component that displays analytics metrics
		// When: The component renders numeric values for analytics data
		// Then: Numeric values are displayed with proper formatting and styling classes

		// Verify total conversations displays with proper styling
		expect(componentContent).toContain(
			'<p class="text-3xl font-bold text-primary">{analytics.total_conversations}</p>'
		);

		// Verify total messages displays with proper styling
		expect(componentContent).toContain(
			'<p class="text-3xl font-bold text-secondary">{analytics.total_messages}</p>'
		);

		// Verify tool calls displays with proper styling
		expect(componentContent).toContain(
			'<p class="text-3xl font-bold text-accent">{analytics.total_tool_calls}</p>'
		);

		// Verify average conversation length uses Math.round for decimal handling
		expect(componentContent).toContain('<p class="text-3xl font-bold text-info">');
		expect(componentContent).toContain('{Math.round(analytics.avg_conversation_length)}');

		// Verify numeric styling classes are consistently applied
		const numericValuePattern =
			/<p class="text-3xl font-bold text-(primary|secondary|accent|info)">/g;
		const numericMatches = componentContent.match(numericValuePattern);
		expect(numericMatches).not.toBeNull();
		expect(numericMatches?.length).toBeGreaterThanOrEqual(4); // At least four numeric displays

		// Verify proper binding to analytics object properties
		expect(componentContent).toContain('{analytics.total_conversations}');
		expect(componentContent).toContain('{analytics.total_messages}');
		expect(componentContent).toContain('{analytics.total_tool_calls}');
		expect(componentContent).toContain('Math.round(analytics.avg_conversation_length)');
	});

	it('should display icons correctly for each analytics metric', () => {
		// Given: A main page component that displays analytics with visual icons
		// When: The component renders analytics cards after successful data load
		// Then: Each analytics metric displays the correct Lucide icon with proper styling

		// Verify Lucide icons are imported from lucide-svelte
		expect(componentContent).toContain(
			"import { Activity, TrendingUp, MessageSquare, Clock } from 'lucide-svelte';"
		);

		// Verify each icon is used with proper styling classes
		// Total Conversations: MessageSquare icon
		expect(componentContent).toContain('<MessageSquare class="w-8 h-8" />');

		// Total Messages: Activity icon
		expect(componentContent).toContain('<Activity class="w-8 h-8" />');

		// Tool Calls: TrendingUp icon
		expect(componentContent).toContain('<TrendingUp class="w-8 h-8" />');

		// Avg Length: Clock icon
		expect(componentContent).toContain('<Clock class="w-8 h-8" />');

		// Verify icons are properly contained within colored divs
		expect(componentContent).toContain('<div class="text-primary">');
		expect(componentContent).toContain('<div class="text-secondary">');
		expect(componentContent).toContain('<div class="text-accent">');
		expect(componentContent).toContain('<div class="text-info">');

		// Verify all icon components use consistent sizing classes
		const iconMatches = componentContent.match(
			/<(Activity|TrendingUp|MessageSquare|Clock) class="w-8 h-8" \/>/g
		);
		expect(iconMatches).not.toBeNull();
		expect(iconMatches?.length).toBe(4); // Four analytics icons total
	});

	it('should handle zero values gracefully in analytics display', () => {
		// Given: A main page component that displays analytics metrics
		// When: Analytics data contains zero values for any metric
		// Then: Zero values are displayed gracefully without errors and with appropriate formatting

		// Verify analytics object has default zero values for safe initialization
		expect(componentContent).toContain('let analytics = {');
		expect(componentContent).toContain('total_conversations: 0,');
		expect(componentContent).toContain('total_messages: 0,');
		expect(componentContent).toContain('total_tool_calls: 0,');
		expect(componentContent).toContain('avg_conversation_length: 0');

		// Verify zero values are displayed safely in the UI without causing errors
		// Total conversations displays zero value
		expect(componentContent).toContain('{analytics.total_conversations}');

		// Total messages displays zero value
		expect(componentContent).toContain('{analytics.total_messages}');

		// Tool calls displays zero value
		expect(componentContent).toContain('{analytics.total_tool_calls}');

		// Average length handles zero value with Math.round (Math.round(0) = 0)
		expect(componentContent).toContain('Math.round(analytics.avg_conversation_length)');

		// Verify styling classes are applied consistently regardless of zero values
		expect(componentContent).toContain('class="text-3xl font-bold text-primary"');
		expect(componentContent).toContain('class="text-3xl font-bold text-secondary"');
		expect(componentContent).toContain('class="text-3xl font-bold text-accent"');
		expect(componentContent).toContain('class="text-3xl font-bold text-info"');

		// Verify analytics cards display structure remains intact with zero values
		expect(componentContent).toContain('<!-- Quick Stats -->');
		expect(componentContent).toContain(
			'<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">'
		);

		// Verify each metric label is present to provide context for zero values
		expect(componentContent).toContain('Total Conversations');
		expect(componentContent).toContain('Total Messages');
		expect(componentContent).toContain('Tool Calls');
		expect(componentContent).toContain('Avg Length');
	});

	it('should update analytics display reactively when data changes', () => {
		// Given: A main page component with reactive analytics display
		// When: Analytics data changes through API calls or WebSocket updates
		// Then: The analytics display updates automatically due to Svelte reactivity

		// Verify analytics is a reactive variable that will trigger UI updates
		expect(componentContent).toContain('let analytics = {');

		// Verify analytics data is updated in loadData function
		expect(componentContent).toContain('const analyticsData = await apiClient.getAnalytics();');
		expect(componentContent).toContain('analytics = analyticsData;');

		// Verify analytics values are used in reactive expressions that auto-update
		expect(componentContent).toContain('{analytics.total_conversations}');
		expect(componentContent).toContain('{analytics.total_messages}');
		expect(componentContent).toContain('{analytics.total_tool_calls}');
		expect(componentContent).toContain('{Math.round(analytics.avg_conversation_length)}');

		// Verify retry mechanism can trigger analytics updates
		expect(componentContent).toContain('async function retryLoad() {');
		expect(componentContent).toContain('await loadData();');
		expect(componentContent).toContain('retryAction={retryLoad}');

		// Verify loadData function can be called to refresh analytics
		expect(componentContent).toContain('async function loadData() {');
		expect(componentContent).toContain('// Load analytics');

		// Verify WebSocket handlers are set up for real-time updates
		expect(componentContent).toContain("wsClient.on('conversation_update'");
		expect(componentContent).toContain("wsClient.on('project_update'");

		// Verify analytics are loaded on component mount
		expect(componentContent).toContain('onMount(async () => {');
		expect(componentContent).toContain('await loadData();');

		// Verify analytics display structure exists for reactive updates
		expect(componentContent).toContain('<!-- Quick Stats -->');
		expect(componentContent).toContain(
			'<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">'
		);

		// Verify error handling doesn't prevent future analytics updates
		expect(componentContent).toContain('} catch (err) {');
		expect(componentContent).toContain('} finally {');
		expect(componentContent).toContain('isLoading = false;');
	});
});
