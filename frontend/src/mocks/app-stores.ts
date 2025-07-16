// Mock for $app/stores
import { writable } from 'svelte/store';

export const page = writable({
	url: { pathname: '/' },
	params: {},
	route: { id: null },
	error: null,
	data: {},
	form: null
});

export const navigating = writable(null);
export const updated = writable(false);
