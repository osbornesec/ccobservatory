<script lang="ts">
	import { Activity, TrendingUp, MessageSquare, Clock } from 'lucide-svelte';

	export let analytics: {
		total_conversations: number;
		total_messages: number;
		total_tool_calls: number;
		avg_conversation_length: number;
	};
</script>

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