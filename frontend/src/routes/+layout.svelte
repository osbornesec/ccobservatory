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
	<!-- Skip links for keyboard navigation -->
	<div class="sr-only">
		<a href="#main-content" class="skip-link focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-content focus:rounded">
			Skip to main content
		</a>
		<a href="#navigation-menu" class="skip-link focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-content focus:rounded">
			Skip to navigation
		</a>
	</div>
	
	<slot />
</div>
