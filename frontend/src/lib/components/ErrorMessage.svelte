<script lang="ts">
	export let title: string;
	export let message: string;
	export let retryAction: (() => void) | undefined = undefined;
</script>

<div class="alert alert-error">
	<div>
		<h3 class="font-bold">{title}</h3>
		<div class="text-sm">{message}</div>
	</div>
	{#if retryAction}
		<div>
			<button class="btn btn-sm btn-outline" on:click={retryAction}>
				Retry
			</button>
		</div>
	{/if}
</div>