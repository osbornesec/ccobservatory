<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { themeStore } from '$lib/stores/theme';
	import AccessibilityAnnouncer from '$lib/components/AccessibilityAnnouncer.svelte';
	import SkipLinks from '$lib/components/SkipLinks.svelte';
	import { accessibilityStore } from '$lib/stores/accessibility';

	// Apply theme changes to HTML element
	$: if (browser && $themeStore) {
		document.documentElement.setAttribute('data-theme', $themeStore);
	}

	onMount(() => {
		// Initialize theme from localStorage or system preference
		themeStore.init();

		// Detect and apply system accessibility preferences
		if (browser) {
			accessibilityStore.detectSystemPreferences();
			
			// Announce application load for screen readers
			accessibilityStore.announce(
				'Claude Code Observatory application loaded and ready',
				'polite'
			);
		}
	});

	// Custom skip link configuration for the application
	const skipLinks = [
		{ href: '#main-content', text: 'Skip to main content', priority: 1 },
		{ href: '#primary-navigation', text: 'Skip to navigation', priority: 2 },
		{ href: '#page-header', text: 'Skip to page header', priority: 3 }
	];
</script>

<!-- Skip Links for keyboard navigation -->
<SkipLinks links={skipLinks} position="top-left" />

<!-- Accessibility Announcer for screen reader announcements -->
<AccessibilityAnnouncer />

<!-- Main application container with proper semantic structure -->
<div 
	class="min-h-screen bg-base-100" 
	data-testid="layout-container"
	role="application"
	aria-label="Claude Code Observatory"
>
	<!-- Page wrapper with proper landmark structure -->
	<div class="flex flex-col min-h-screen">
		<!-- Main content area with skip link target -->
		<main 
			id="main-content"
			class="flex-1"
			role="main"
			aria-label="Main application content"
		>
			<slot />
		</main>
	</div>
</div>