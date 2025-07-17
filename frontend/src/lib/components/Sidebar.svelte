<script lang="ts">
	import { onMount, createEventDispatcher } from 'svelte';
	import { browser } from '$app/environment';
	import { accessibilityStore } from '$lib/stores/accessibility';
	import { KeyboardNavigator } from '$lib/utils/accessibility';

	// Component props
	export let currentPage: string = '';
	export let collapsed: boolean = false;
	export let navigationItems: Array<{
		href: string;
		label: string;
		icon?: string;
		ariaLabel?: string;
		badge?: string;
	}> = [
		{ href: '/', label: 'Dashboard', ariaLabel: 'Navigate to Dashboard' },
		{ href: '/conversations', label: 'Conversations', ariaLabel: 'Navigate to Conversations' },
		{ href: '/settings', label: 'Settings', ariaLabel: 'Navigate to Settings' }
	];

	const dispatch = createEventDispatcher();

	let sidebarElement: HTMLElement;
	let focusTrapCleanup: (() => void) | null = null;

	onMount(() => {
		if (browser && sidebarElement) {
			// Set up keyboard navigation within sidebar
			focusTrapCleanup = KeyboardNavigator.trapFocus(sidebarElement);
			
			// Announce sidebar state changes
			accessibilityStore.announce(
				`Sidebar navigation ${collapsed ? 'collapsed' : 'expanded'}`,
				'polite'
			);
		}

		return () => {
			if (focusTrapCleanup) {
				focusTrapCleanup();
			}
		};
	});

	// Handle keyboard navigation
	function handleKeyDown(event: KeyboardEvent) {
		if (!browser) return;

		switch (event.key) {
			case 'Escape':
				// Allow escaping focus from sidebar
				if (document.activeElement && sidebarElement.contains(document.activeElement as Node)) {
					(document.activeElement as HTMLElement).blur();
					dispatch('escape-sidebar');
				}
				break;
			case 'Home':
				event.preventDefault();
				focusFirstNavItem();
				break;
			case 'End':
				event.preventDefault();
				focusLastNavItem();
				break;
		}
	}

	function focusFirstNavItem() {
		const firstNavItem = sidebarElement.querySelector('nav a:first-child') as HTMLElement;
		if (firstNavItem) {
			firstNavItem.focus();
		}
	}

	function focusLastNavItem() {
		const lastNavItem = sidebarElement.querySelector('nav a:last-child') as HTMLElement;
		if (lastNavItem) {
			lastNavItem.focus();
		}
	}

	function handleNavItemClick(item: typeof navigationItems[0]) {
		accessibilityStore.announce(
			`Navigating to ${item.label}`,
			'polite'
		);
		dispatch('navigate', { href: item.href, label: item.label });
	}

	// Toggle sidebar collapsed state
	function toggleSidebar() {
		collapsed = !collapsed;
		accessibilityStore.announce(
			`Sidebar ${collapsed ? 'collapsed' : 'expanded'}`,
			'assertive'
		);
		dispatch('toggle', { collapsed });
	}

	// Reactive announcement for collapsed state changes
	$: if (browser && typeof collapsed !== 'undefined') {
		accessibilityStore.announce(
			`Sidebar is now ${collapsed ? 'collapsed' : 'expanded'}`,
			'polite'
		);
	}
</script>

<!-- Sidebar navigation with proper ARIA landmarks and semantic structure -->
<aside 
	bind:this={sidebarElement}
	class="w-64 bg-base-200 border-r border-base-300 {collapsed ? 'w-16' : 'w-64'} transition-all duration-200"
	class:collapsed
	role="complementary"
	aria-label="Main site navigation sidebar"
	aria-expanded={!collapsed}
	on:keydown={handleKeyDown}
	data-testid="sidebar"
>
	<!-- Sidebar header with toggle button -->
	<div class="p-4 border-b border-base-300">
		<div class="flex items-center justify-between">
			{#if !collapsed}
				<h2 class="text-sm font-semibold text-base-content uppercase tracking-wide">
					Navigation
				</h2>
			{/if}
			
			<!-- Sidebar toggle button -->
			<button
				type="button"
				class="p-2 rounded-md text-base-content hover:bg-base-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
				aria-label={collapsed ? 'Expand sidebar navigation' : 'Collapse sidebar navigation'}
				aria-expanded={!collapsed}
				aria-controls="sidebar-nav"
				on:click={toggleSidebar}
			>
				<svg 
					class="w-4 h-4 transform transition-transform {collapsed ? 'rotate-180' : ''}"
					fill="none" 
					stroke="currentColor" 
					viewBox="0 0 24 24"
					aria-hidden="true"
				>
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
				</svg>
			</button>
		</div>
	</div>

	<!-- Main navigation -->
	<div class="p-4">
		<nav 
			id="sidebar-nav"
			class="space-y-2"
			role="navigation"
			aria-label="Sidebar navigation menu"
		>
			<!-- Navigation items list -->
			<ul class="space-y-1" role="list">
				{#each navigationItems as item, index}
					<li role="listitem">
						<a 
							href={item.href}
							class="group flex items-center px-4 py-2 text-sm font-medium text-base-content rounded-md hover:bg-base-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:bg-base-300 transition-colors"
							class:bg-primary={currentPage === item.label}
							class:text-primary-content={currentPage === item.label}
							aria-current={currentPage === item.label ? 'page' : 'false'}
							aria-label={item.ariaLabel || `Navigate to ${item.label}`}
							tabindex="0"
							role="link"
							on:click={() => handleNavItemClick(item)}
						>
							<!-- Icon placeholder -->
							{#if item.icon}
								<span class="mr-3 flex-shrink-0" aria-hidden="true">
									{item.icon}
								</span>
							{:else}
								<span class="mr-3 w-4 h-4 flex-shrink-0 bg-base-content/20 rounded" aria-hidden="true"></span>
							{/if}
							
							<!-- Navigation label -->
							{#if !collapsed}
								<span class="flex-1 truncate">
									{item.label}
								</span>
								
								<!-- Badge if present -->
								{#if item.badge}
									<span 
										class="ml-auto inline-block py-1 px-2 text-xs font-medium bg-primary text-primary-content rounded-full"
										aria-label="{item.badge} items"
									>
										{item.badge}
									</span>
								{/if}
								
								<!-- Screen reader current page indicator -->
								{#if currentPage === item.label}
									<span class="sr-only">(current page)</span>
								{/if}
							{:else}
								<!-- Tooltip for collapsed state -->
								<span class="sr-only">{item.label}</span>
								<div 
									class="absolute left-16 ml-2 px-2 py-1 bg-base-100 text-base-content text-sm rounded shadow-lg opacity-0 group-hover:opacity-100 group-focus:opacity-100 transition-opacity z-50 pointer-events-none"
									aria-hidden="true"
								>
									{item.label}
									{#if item.badge}
										<span class="text-xs text-base-content/70"> ({item.badge})</span>
									{/if}
								</div>
							{/if}
						</a>
					</li>
				{/each}
			</ul>
		</nav>

		<!-- Additional sidebar content area -->
		{#if !collapsed}
			<div class="mt-8">
				<h3 class="text-xs font-semibold text-base-content/70 uppercase tracking-wide mb-3">
					Quick Access
				</h3>
				<div class="space-y-1">
					<button
						type="button"
						class="w-full text-left px-4 py-2 text-sm text-base-content hover:bg-base-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded-md"
						aria-label="Open accessibility settings"
					>
						Accessibility Settings
					</button>
				</div>
			</div>
		{/if}
	</div>

	<!-- Sidebar footer with app info -->
	{#if !collapsed}
		<div class="absolute bottom-0 left-0 right-0 p-4 border-t border-base-300">
			<div class="text-xs text-base-content/70 text-center">
				<span class="sr-only">Application information: </span>
				Claude Code Observatory
			</div>
		</div>
	{/if}
</aside>

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
	aside button:focus,
	aside a:focus {
		box-shadow: 0 0 0 2px theme('colors.primary');
	}

	/* Collapsed sidebar specific styles */
	.collapsed {
		overflow: visible;
	}

	.collapsed nav a {
		justify-content: center;
		position: relative;
	}

	/* High contrast mode support */
	@media (prefers-contrast: high) {
		aside {
			border-right-width: 3px;
		}
		
		aside button:focus,
		aside a:focus {
			outline: 3px solid Highlight;
			outline-offset: 2px;
		}
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		aside,
		aside a,
		aside button {
			transition: none;
		}
		
		.collapsed nav a div {
			transition: none;
		}
	}

	/* Dark mode considerations */
	@media (prefers-color-scheme: dark) {
		aside button:focus,
		aside a:focus {
			box-shadow: 0 0 0 2px theme('colors.primary-content');
		}
	}

	/* Ensure tooltips are properly positioned */
	.collapsed nav a {
		position: relative;
	}

	.collapsed nav a div {
		position: absolute;
		left: 100%;
		top: 50%;
		transform: translateY(-50%);
		white-space: nowrap;
		z-index: 50;
	}
</style>