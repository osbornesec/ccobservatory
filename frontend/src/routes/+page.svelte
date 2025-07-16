<script lang="ts">
	import { onMount } from 'svelte';
	import Header from '$lib/components/Header.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import ErrorMessage from '$lib/components/ErrorMessage.svelte';
	import { apiClient } from '$lib/api/client';
	import { wsClient } from '$lib/api/websocket';
	import { projects, conversations, connectionStatus } from '$lib/stores/conversations';
	import { accessibilityService } from '$lib/stores/accessibility';
	import { Activity, TrendingUp, MessageSquare, Clock } from 'lucide-svelte';

	let isLoading = true;
	let error: string | null = null;
	let analytics = {
		total_conversations: 0,
		total_messages: 0,
		total_tool_calls: 0,
		avg_conversation_length: 0
	};

	onMount(async () => {
		try {
			// Test API connection
			const isConnected = await apiClient.testConnection();
			if (!isConnected) {
				throw new Error('Cannot connect to backend API');
			}

			// Load initial data
			await loadData();

			// Set up WebSocket message handlers
			wsClient.on('conversation_update', data => {
				conversations.updateConversation(data.id, data);
			});

			wsClient.on('project_update', data => {
				projects.update(currentProjects =>
					currentProjects.map(p => (p.id === data.id ? { ...p, ...data } : p))
				);
			});
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to initialize application';
			accessibilityService.announceDataError('dashboard', error);
		} finally {
			isLoading = false;
		}
	});

	async function loadData() {
		try {
			// Load projects
			const projectsData = await apiClient.getProjects();
			projects.set(projectsData);

			// Load recent conversations
			const conversationsData = await apiClient.getConversations(1, 10);
			conversations.set(conversationsData.data);

			// Load analytics
			const analyticsData = await apiClient.getAnalytics();
			analytics = analyticsData;
			
			// Announce successful data load
			accessibilityService.announceDataLoaded('dashboard data');
		} catch (err) {
			throw new Error('Failed to load data from server');
		}
	}

	async function retryLoad() {
		error = null;
		isLoading = true;
		accessibilityService.announce('Retrying to load dashboard data', 'polite');
		try {
			await loadData();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load data';
			accessibilityService.announceDataError('dashboard', error);
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Claude Code Observatory</title>
	<meta name="description" content="Real-time observability for Claude Code interactions" />
</svelte:head>

<div class="min-h-screen bg-base-100">
	<Header />

	<div class="flex h-[calc(100vh-4rem)]">
		<Sidebar />

		<main class="flex-1 overflow-auto" id="main-content" aria-label="Dashboard content">
			{#if isLoading}
				<div class="flex items-center justify-center h-full">
					<LoadingSpinner size="lg" text="Loading dashboard..." />
				</div>
			{:else if error}
				<div class="p-8">
					<ErrorMessage title="Failed to Load Dashboard" message={error} retryAction={retryLoad} />
				</div>
			{:else}
				<div class="p-6">
					<!-- Welcome Section -->
					<div class="mb-8">
						<h1 class="text-3xl font-bold text-base-content mb-2">
							Welcome to Claude Code Observatory
						</h1>
						<p class="text-base-content/70">
							Monitor and analyze your Claude Code interactions in real-time
						</p>
					</div>

					<!-- Quick Stats -->
					<section aria-labelledby="stats-heading">
						<h2 id="stats-heading" class="sr-only">Quick Statistics</h2>
						<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
							<div class="card bg-base-100 shadow-lg border border-base-300" role="region" aria-labelledby="conversations-stat">
								<div class="card-body">
									<div class="flex items-center justify-between">
										<div>
											<p class="text-base-content/70 text-sm" id="conversations-stat">Total Conversations</p>
											<p class="text-3xl font-bold text-primary" aria-describedby="conversations-stat">{analytics.total_conversations}</p>
										</div>
										<div class="text-primary" aria-hidden="true">
											<MessageSquare class="w-8 h-8" />
										</div>
									</div>
								</div>
							</div>

							<div class="card bg-base-100 shadow-lg border border-base-300" role="region" aria-labelledby="messages-stat">
								<div class="card-body">
									<div class="flex items-center justify-between">
										<div>
											<p class="text-base-content/70 text-sm" id="messages-stat">Total Messages</p>
											<p class="text-3xl font-bold text-secondary" aria-describedby="messages-stat">{analytics.total_messages}</p>
										</div>
										<div class="text-secondary" aria-hidden="true">
											<Activity class="w-8 h-8" />
										</div>
									</div>
								</div>
							</div>

							<div class="card bg-base-100 shadow-lg border border-base-300" role="region" aria-labelledby="tools-stat">
								<div class="card-body">
									<div class="flex items-center justify-between">
										<div>
											<p class="text-base-content/70 text-sm" id="tools-stat">Tool Calls</p>
											<p class="text-3xl font-bold text-accent" aria-describedby="tools-stat">{analytics.total_tool_calls}</p>
										</div>
										<div class="text-accent" aria-hidden="true">
											<TrendingUp class="w-8 h-8" />
										</div>
									</div>
								</div>
							</div>

							<div class="card bg-base-100 shadow-lg border border-base-300" role="region" aria-labelledby="length-stat">
								<div class="card-body">
									<div class="flex items-center justify-between">
										<div>
											<p class="text-base-content/70 text-sm" id="length-stat">Avg Length</p>
											<p class="text-3xl font-bold text-info" aria-describedby="length-stat">
												{Math.round(analytics.avg_conversation_length)}
											</p>
										</div>
										<div class="text-info" aria-hidden="true">
											<Clock class="w-8 h-8" />
										</div>
									</div>
								</div>
							</div>
						</div>
					</section>

					<!-- Getting Started and Status -->
					<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
						<section aria-labelledby="getting-started-heading">
							<div class="card bg-base-100 shadow-lg border border-base-300">
								<div class="card-body">
									<h2 class="card-title text-base-content" id="getting-started-heading">Getting Started</h2>
									<ol class="space-y-4 list-none">
										<li class="flex items-start gap-3">
											<div class="badge badge-primary" aria-hidden="true">1</div>
											<div>
												<p class="font-medium">Start a Claude Code session</p>
												<p class="text-sm text-base-content/70">
													Files will be automatically detected from ~/.claude/projects/
												</p>
											</div>
										</li>
										<li class="flex items-start gap-3">
											<div class="badge badge-primary" aria-hidden="true">2</div>
											<div>
												<p class="font-medium">Monitor real-time activity</p>
												<p class="text-sm text-base-content/70">
													Watch conversations and tool usage as they happen
												</p>
											</div>
										</li>
										<li class="flex items-start gap-3">
											<div class="badge badge-primary" aria-hidden="true">3</div>
											<div>
												<p class="font-medium">Analyze patterns</p>
												<p class="text-sm text-base-content/70">
													Use analytics to understand your development workflow
												</p>
											</div>
										</li>
									</ol>
									<div class="card-actions justify-end mt-4">
										<a 
											href="/conversations" 
											class="btn btn-primary"
											aria-label="Go to conversations page to view your Claude Code interactions"
										>
											View Conversations
										</a>
									</div>
								</div>
							</div>
						</section>

						<section aria-labelledby="connection-status-heading">
							<div class="card bg-base-100 shadow-lg border border-base-300">
								<div class="card-body">
									<h2 class="card-title text-base-content" id="connection-status-heading">Connection Status</h2>
									<div class="space-y-3" role="list">
										<div class="flex items-center justify-between" role="listitem">
											<span>Backend API</span>
											<div class="badge badge-success" role="status" aria-label="Backend API connection status: Connected">Connected</div>
										</div>
										<div class="flex items-center justify-between" role="listitem">
											<span>WebSocket</span>
											<div
												class="badge {$connectionStatus === 'connected'
													? 'badge-success'
													: 'badge-warning'}"
												role="status"
												aria-label="WebSocket connection status: {$connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}"
											>
												{$connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
											</div>
										</div>
										<div class="flex items-center justify-between" role="listitem">
											<span>File Monitor</span>
											<div class="badge badge-info" role="status" aria-label="File monitor status: Active">Active</div>
										</div>
									</div>
									<div class="card-actions justify-end mt-4">
										<a 
											href="/settings" 
											class="btn btn-outline"
											aria-label="Go to settings page to configure your preferences"
										>
											Settings
										</a>
									</div>
								</div>
							</div>
						</section>
					</div>
				</div>
			{/if}
		</main>
	</div>
</div>
