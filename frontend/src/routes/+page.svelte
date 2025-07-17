<script lang="ts">
	import { onMount } from 'svelte';
	import Header from '$lib/components/Header.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import ErrorMessage from '$lib/components/ErrorMessage.svelte';
	import WelcomeSection from '$lib/components/WelcomeSection.svelte';
	import QuickStats from '$lib/components/QuickStats.svelte';
	import GettingStarted from '$lib/components/GettingStarted.svelte';
	import ConnectionStatus from '$lib/components/ConnectionStatus.svelte';
	import { dashboardService } from '$lib/api/dashboard';
	import { wsClient } from '$lib/api/websocket';
	import {
		projects,
		conversationsStore,
		connectionStatus
	} from '$lib/stores/conversations';
	import type { ConversationUpdateMessage, ProjectUpdateMessage } from '$lib/types';

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
			const result = await dashboardService.initialize();
			analytics = result.analytics;

			// Set up WebSocket message handlers with proper typing
			wsClient.on<ConversationUpdateMessage>('conversation_update', data => {
				conversationsStore.updateConversation(data.id, data);
			});

			wsClient.on<ProjectUpdateMessage>('project_update', data => {
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

	async function retryLoad() {
		error = null;
		isLoading = true;
		try {
			const analyticsData = await dashboardService.retryLoad();
			analytics = analyticsData;
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
					<LoadingSpinner size="lg" text="Loading dashboard..." />
				</div>
			{:else if error}
				<div class="p-8">
					<ErrorMessage title="Failed to Load Dashboard" message={error} retryAction={retryLoad} />
				</div>
			{:else}
				<div class="p-6">
					<WelcomeSection />
					<QuickStats {analytics} />

					<!-- Getting Started and Connection Status -->
					<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
						<GettingStarted />
						<ConnectionStatus connectionStatus={$connectionStatus} />
					</div>
				</div>
			{/if}
		</main>
	</div>
</div>
