<script lang="ts">
	import Header from '$lib/components/Header.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import ColorContrastAudit from '$lib/components/ColorContrastAudit.svelte';
	import Modal from '$lib/components/Modal.svelte';
	import { themeStore } from '$lib/stores/theme';
	import { accessibilityService } from '$lib/stores/accessibility';
	import { Settings, Palette, Eye, Keyboard, Monitor } from 'lucide-svelte';
	
	let showAccessibilityModal = false;
	let showContrastAudit = false;
	
	function toggleTheme() {
		themeStore.toggle();
		accessibilityService.announce(`Theme changed to ${$themeStore} mode`, 'polite');
	}
	
	function showAccessibilityHelp() {
		showAccessibilityModal = true;
		accessibilityService.announceModalOpened('Accessibility Help');
	}
	
	function closeAccessibilityModal() {
		showAccessibilityModal = false;
		accessibilityService.announceModalClosed('Accessibility Help');
	}
</script>

<svelte:head>
	<title>Settings - Claude Code Observatory</title>
	<meta name="description" content="Configure your Claude Code Observatory preferences and accessibility settings" />
</svelte:head>

<div class="min-h-screen bg-base-100">
	<Header />

	<div class="flex h-[calc(100vh-4rem)]">
		<Sidebar />

		<main class="flex-1 overflow-auto" id="main-content" aria-label="Settings page content">
			<div class="p-6">
				<!-- Page Header -->
				<div class="mb-8">
					<h1 class="text-3xl font-bold text-base-content mb-2 flex items-center gap-3">
						<Settings class="w-8 h-8" aria-hidden="true" />
						Settings
					</h1>
					<p class="text-base-content/70">
						Configure your preferences and accessibility options
					</p>
				</div>

				<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
					<!-- Appearance Settings -->
					<section aria-labelledby="appearance-heading">
						<div class="card bg-base-100 shadow-lg border border-base-300">
							<div class="card-body">
								<h2 id="appearance-heading" class="card-title flex items-center gap-2">
									<Palette class="w-5 h-5" aria-hidden="true" />
									Appearance
								</h2>
								
								<div class="form-control">
									<label class="label cursor-pointer">
										<span class="label-text">Theme</span>
										<input 
											type="checkbox" 
											class="toggle toggle-primary" 
											checked={$themeStore === 'dark'}
											on:change={toggleTheme}
											aria-label="Toggle between light and dark theme"
										/>
									</label>
									<div class="label">
										<span class="label-text-alt">Current: {$themeStore} mode</span>
									</div>
								</div>
								
								<div class="mt-4">
									<button 
										class="btn btn-outline btn-sm"
										on:click={() => showContrastAudit = !showContrastAudit}
										aria-expanded={showContrastAudit}
										aria-controls="contrast-audit"
									>
										<Eye class="w-4 h-4" aria-hidden="true" />
										{showContrastAudit ? 'Hide' : 'Show'} Color Contrast Audit
									</button>
								</div>
							</div>
						</div>
					</section>

					<!-- Accessibility Settings -->
					<section aria-labelledby="accessibility-heading">
						<div class="card bg-base-100 shadow-lg border border-base-300">
							<div class="card-body">
								<h2 id="accessibility-heading" class="card-title flex items-center gap-2">
									<Eye class="w-5 h-5" aria-hidden="true" />
									Accessibility
								</h2>
								
								<div class="space-y-4">
									<div class="form-control">
										<label class="label cursor-pointer">
											<span class="label-text">Reduce motion</span>
											<input type="checkbox" class="toggle" />
										</label>
									</div>
									
									<div class="form-control">
										<label class="label cursor-pointer">
											<span class="label-text">High contrast mode</span>
											<input type="checkbox" class="toggle" />
										</label>
									</div>
									
									<div class="form-control">
										<label class="label cursor-pointer">
											<span class="label-text">Screen reader announcements</span>
											<input type="checkbox" class="toggle" checked />
										</label>
									</div>
								</div>
								
								<div class="card-actions justify-end mt-4">
									<button 
										class="btn btn-primary btn-sm"
										on:click={showAccessibilityHelp}
									>
										<Keyboard class="w-4 h-4" aria-hidden="true" />
										Accessibility Help
									</button>
								</div>
							</div>
						</div>
					</section>

					<!-- Performance Settings -->
					<section aria-labelledby="performance-heading">
						<div class="card bg-base-100 shadow-lg border border-base-300">
							<div class="card-body">
								<h2 id="performance-heading" class="card-title flex items-center gap-2">
									<Monitor class="w-5 h-5" aria-hidden="true" />
									Performance
								</h2>
								
								<div class="space-y-4">
									<div class="form-control">
										<label class="label" for="update-frequency">
											<span class="label-text">Real-time updates</span>
										</label>
										<select id="update-frequency" class="select select-bordered" aria-label="Real-time update frequency">
											<option>Every second</option>
											<option selected>Every 5 seconds</option>
											<option>Every 10 seconds</option>
											<option>Manual refresh only</option>
										</select>
									</div>
									
									<div class="form-control">
										<label class="label cursor-pointer">
											<span class="label-text">Auto-refresh dashboard</span>
											<input type="checkbox" class="toggle" checked />
										</label>
									</div>
								</div>
							</div>
						</div>
					</section>

					<!-- Color Contrast Audit -->
					{#if showContrastAudit}
						<section aria-labelledby="contrast-audit" id="contrast-audit" class="lg:col-span-2">
							<ColorContrastAudit />
						</section>
					{/if}
				</div>
			</div>
		</main>
	</div>
</div>

<!-- Accessibility Help Modal -->
<Modal 
	bind:open={showAccessibilityModal} 
	title="Accessibility Features" 
	description="Learn about the accessibility features available in Claude Code Observatory"
>
	<div class="space-y-4">
		<div>
			<h3 class="font-semibold mb-2">Keyboard Navigation</h3>
			<ul class="text-sm space-y-1 text-base-content/70">
				<li>• Press <kbd class="kbd kbd-xs">Tab</kbd> to navigate between elements</li>
				<li>• Press <kbd class="kbd kbd-xs">Enter</kbd> or <kbd class="kbd kbd-xs">Space</kbd> to activate buttons</li>
				<li>• Press <kbd class="kbd kbd-xs">Esc</kbd> to close modals and menus</li>
				<li>• Use arrow keys to navigate within menus</li>
			</ul>
		</div>
		
		<div>
			<h3 class="font-semibold mb-2">Screen Reader Support</h3>
			<ul class="text-sm space-y-1 text-base-content/70">
				<li>• All content is properly labeled for screen readers</li>
				<li>• Status updates are announced automatically</li>
				<li>• Skip links allow jumping to main content</li>
				<li>• Proper heading structure for easy navigation</li>
			</ul>
		</div>
		
		<div>
			<h3 class="font-semibold mb-2">Visual Accessibility</h3>
			<ul class="text-sm space-y-1 text-base-content/70">
				<li>• High contrast mode available</li>
				<li>• Color information is not the only way to convey meaning</li>
				<li>• Focus indicators are clearly visible</li>
				<li>• Text can be zoomed up to 200% without losing functionality</li>
			</ul>
		</div>
	</div>
	
	<svelte:fragment slot="footer">
		<button class="btn btn-outline" on:click={closeAccessibilityModal}>
			Close
		</button>
		<a href="/lib/docs/accessibility.md" class="btn btn-primary" target="_blank">
			View Full Guide
		</a>
	</svelte:fragment>
</Modal>