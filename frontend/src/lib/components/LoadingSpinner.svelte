<script lang="ts">
	export let size: 'sm' | 'md' | 'lg' = 'md';
	export let text: string = 'Loading...';

	const sizeClasses = {
		sm: 'w-4 h-4',
		md: 'w-8 h-8', 
		lg: 'w-12 h-12'
	};
</script>

<div class="flex flex-col items-center justify-center gap-3">
	<div class="loading loading-spinner {sizeClasses[size]} text-primary"></div>
	{#if text}
		<p class="text-base-content/70">{text}</p>
	{/if}
</div>