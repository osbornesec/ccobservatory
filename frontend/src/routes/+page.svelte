<script lang="ts">
	import { onMount } from 'svelte';
	import Header from '$lib/components/Header.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import ErrorMessage from '$lib/components/ErrorMessage.svelte';
	import { apiClient } from '$lib/api/client';
	import { wsClient } from '$lib/api/websocket';
	import { projects, conversations, connectionStatus } from '$lib/stores/conversations';
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
		} catch (err) {
			throw new Error('Failed to load data from server');
		}
	}

	async function retryLoad() {
		error = null;
		isLoading = true;
		try {
			await loadData();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load data';
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

		<main class="flex-1 overflow-auto">
			{#if isLoading}
				<div class="flex items-center justify-center h-full">
					<LoadingSpinner size="lg" />
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
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
						<div class="card bg-base-100 shadow-lg border border-base-300">
							<div class="card-body">
								<div class="flex items-center justify-between">
									<div>
										<p class="text-base-content/70 text-sm">Total Conversations</p>
										<p class="text-3xl font-bold text-primary">{analytics.total_conversations}</p>
									</div>
									<div class="text-primary">
										<MessageSquare class="w-8 h-8" />
									</div>
								</div>
							</div>
						</div>

						<div class="card bg-base-100 shadow-lg border border-base-300">
							<div class="card-body">
								<div class="flex items-center justify-between">
									<div>
										<p class="text-base-content/70 text-sm">Total Messages</p>
										<p class="text-3xl font-bold text-secondary">{analytics.total_messages}</p>
									</div>
									<div class="text-secondary">
										<Activity class="w-8 h-8" />
									</div>
								</div>
							</div>
						</div>

						<div class="card bg-base-100 shadow-lg border border-base-300">
							<div class="card-body">
								<div class="flex items-center justify-between">
									<div>
										<p class="text-base-content/70 text-sm">Tool Calls</p>
										<p class="text-3xl font-bold text-accent">{analytics.total_tool_calls}</p>
									</div>
									<div class="text-accent">
										<TrendingUp class="w-8 h-8" />
									</div>
								</div>
							</div>
						</div>

						<div class="card bg-base-100 shadow-lg border border-base-300">
							<div class="card-body">
								<div class="flex items-center justify-between">
									<div>
										<p class="text-base-content/70 text-sm">Avg Length</p>
										<p class="text-3xl font-bold text-info">
											{Math.round(analytics.avg_conversation_length)}
										</p>
									</div>
									<div class="text-info">
										<Clock class="w-8 h-8" />
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Getting Started -->
					<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
						<div class="card bg-base-100 shadow-lg border border-base-300">
							<div class="card-body">
								<h2 class="card-title text-base-content">Getting Started</h2>
								<div class="space-y-4">
									<div class="flex items-start gap-3">
										<div class="badge badge-primary">1</div>
										<div>
											<p class="font-medium">Start a Claude Code session</p>
											<p class="text-sm text-base-content/70">
												Files will be automatically detected from ~/.claude/projects/
											</p>
										</div>
									</div>
									<div class="flex items-start gap-3">
										<div class="badge badge-primary">2</div>
										<div>
											<p class="font-medium">Monitor real-time activity</p>
											<p class="text-sm text-base-content/70">
												Watch conversations and tool usage as they happen
											</p>
										</div>
									</div>
									<div class="flex items-start gap-3">
										<div class="badge badge-primary">3</div>
										<div>
											<p class="font-medium">Analyze patterns</p>
											<p class="text-sm text-base-content/70">
												Use analytics to understand your development workflow
											</p>
										</div>
									</div>
								</div>
								<div class="card-actions justify-end mt-4">
									<a href="/conversations" class="btn btn-primary">View Conversations</a>
								</div>
							</div>
						</div>

						<div class="card bg-base-100 shadow-lg border border-base-300">
							<div class="card-body">
								<h2 class="card-title text-base-content">Connection Status</h2>
								<div class="space-y-3">
									<div class="flex items-center justify-between">
										<span>Backend API</span>
										<div class="badge badge-success">Connected</div>
									</div>
									<div class="flex items-center justify-between">
										<span>WebSocket</span>
										<div
											class="badge {$connectionStatus === 'connected'
												? 'badge-success'
												: 'badge-warning'}"
										>
											{$connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
										</div>
									</div>
									<div class="flex items-center justify-between">
										<span>File Monitor</span>
										<div class="badge badge-info">Active</div>
									</div>
								</div>
								<div class="card-actions justify-end mt-4">
									<a href="/settings" class="btn btn-outline">Settings</a>
								</div>
							</div>
						</div>
					</div>
				</div>
			{/if}
		</main>
	</div>
</div>
