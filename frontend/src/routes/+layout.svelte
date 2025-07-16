<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { themeStore } from '$lib/stores/theme';

	// Apply theme changes to HTML element
	$: if (browser && $themeStore) {
		document.documentElement.setAttribute('data-theme', $themeStore);
	}

	onMount(() => {
		// Initialize theme from localStorage or system preference
		themeStore.init();
	});
</script>

<div class="min-h-screen bg-base-100" data-testid="layout-container">
	<slot />
</div>
