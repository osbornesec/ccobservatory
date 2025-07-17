<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { accessibilityStore } from '$lib/stores/accessibility';

	// Component props
	export let currentPage: string = '';
	export let showNavigation: boolean = false;

	onMount(() => {
		if (browser) {
			// Announce page changes when header is updated
			if (currentPage) {
				accessibilityStore.announce(
					`Navigated to ${currentPage} page`,
					'polite'
				);
			}
		}
	});

	// Update announcements when page changes
	$: if (browser && currentPage) {
		accessibilityStore.announce(
			`Current page: ${currentPage}`,
			'polite'
		);
	}
</script>

<!-- Application header with proper ARIA landmarks and semantic structure -->
<header 
	id="page-header"
	class="bg-base-200 border-b border-base-300"
	role="banner"
	aria-label="Claude Code Observatory main header"
>
	<div class="container mx-auto px-6 py-4">
		<!-- Skip link target for header -->
		<div class="sr-only" aria-live="polite" aria-atomic="true">
			Header content updated
		</div>
		
		<!-- Main application title with proper heading hierarchy -->
		<div class="flex items-center justify-between">
			<h1 
				class="text-xl font-bold text-base-content"
				id="app-title"
				tabindex="-1"
			>
				<span class="sr-only">Welcome to </span>
				Claude Code Observatory
				{#if currentPage}
					<span class="sr-only"> - Current page: {currentPage}</span>
				{/if}
			</h1>
			
			{#if showNavigation}
				<!-- Primary navigation landmark -->
				<nav 
					id="primary-navigation"
					class="ml-auto"
					role="navigation"
					aria-label="Primary site navigation"
				>
					<ul class="flex space-x-4">
						<li>
							<a 
								href="/"
								class="text-base-content hover:text-primary focus:text-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded-sm px-2 py-1"
								aria-current={currentPage === 'Dashboard' ? 'page' : 'false'}
								tabindex="0"
							>
								Dashboard
							</a>
						</li>
						<li>
							<a 
								href="/conversations"
								class="text-base-content hover:text-primary focus:text-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded-sm px-2 py-1"
								aria-current={currentPage === 'Conversations' ? 'page' : 'false'}
								tabindex="0"
							>
								Conversations
							</a>
						</li>
						<li>
							<a 
								href="/settings"
								class="text-base-content hover:text-primary focus:text-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded-sm px-2 py-1"
								aria-current={currentPage === 'Settings' ? 'page' : 'false'}
								tabindex="0"
							>
								Settings
							</a>
						</li>
					</ul>
				</nav>
			{/if}
		</div>
		
		<!-- Breadcrumb navigation if on a sub-page -->
		{#if currentPage && currentPage !== 'Dashboard'}
			<nav 
				class="mt-2"
				role="navigation"
				aria-label="Breadcrumb navigation"
			>
				<ol class="flex items-center space-x-2 text-sm text-base-content/70">
					<li>
						<a 
							href="/"
							class="hover:text-primary focus:text-primary focus:outline-none focus:ring-1 focus:ring-primary rounded-sm"
							aria-label="Navigate to Dashboard home page"
						>
							Dashboard
						</a>
					</li>
					<li aria-hidden="true">/</li>
					<li>
						<span aria-current="page" class="font-medium text-base-content">
							{currentPage}
						</span>
					</li>
				</ol>
			</nav>
		{/if}
	</div>
</header>

<style>
	/* Screen reader only utility for visually hidden content */
	.sr-only {
		position: absolute !important;
		width: 1px !important;
		height: 1px !important;
		padding: 0 !important;
		margin: -1px !important;
		overflow: hidden !important;
		clip: rect(0, 0, 0, 0) !important;
		white-space: nowrap !important;
		border: 0 !important;
	}

	/* Enhanced focus styles for better accessibility */
	a:focus,
	h1:focus {
		outline: 2px solid theme('colors.primary');
		outline-offset: 2px;
	}

	/* High contrast mode support */
	@media (prefers-contrast: high) {
		header {
			border-bottom-width: 3px;
		}
		
		a:focus,
		h1:focus {
			outline: 3px solid Highlight;
			outline-offset: 2px;
		}
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		a {
			transition: none;
		}
	}

	/* Dark mode considerations */
	@media (prefers-color-scheme: dark) {
		a:focus,
		h1:focus {
			outline-color: theme('colors.primary-content');
		}
	}
</style>