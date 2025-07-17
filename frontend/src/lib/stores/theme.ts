import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function createThemeStore() {
	const { subscribe, set, update } = writable<string>('light');

	return {
		subscribe,
		set: (value: string) => {
			if (browser) {
				localStorage.setItem('theme', value);
			}
			set(value);
		},
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
		},
		toggle: () => {
			update(current => {
				const newTheme = current === 'light' ? 'dark' : 'light';
				if (browser) {
					localStorage.setItem('theme', newTheme);
				}
				return newTheme;
			});
		}
	};
}

export const themeStore = createThemeStore();