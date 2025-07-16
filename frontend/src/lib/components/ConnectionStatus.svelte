<script lang="ts">
	export let connectionStatus: 'connected' | 'disconnected';
</script>

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
					class="badge {connectionStatus === 'connected'
						? 'badge-success'
						: 'badge-warning'}"
				>
					{connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
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