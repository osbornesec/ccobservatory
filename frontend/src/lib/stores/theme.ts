import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function createThemeStore() {
	const { subscribe, set } = writable<string>('light');

	return {
		subscribe,
		set,
		init: () => {
			if (browser) {
				const stored = localStorage.getItem('theme');
				if (stored) {
					set(stored);
				} else {
					// Default to system preference
					const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
					set(prefersDark ? 'dark' : 'light');
				}
			}
		}
	};
}

export const themeStore = createThemeStore();