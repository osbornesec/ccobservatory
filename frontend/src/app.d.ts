// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

// Environment variables declaration
declare module '$env/static/public' {
	export const PUBLIC_SUPABASE_URL: string;
	export const PUBLIC_SUPABASE_ANON_KEY: string;
	export const PUBLIC_API_BASE_URL: string;
	export const PUBLIC_WS_URL: string;
	export const PUBLIC_DEV_MODE: string;
	export const PUBLIC_ENABLE_DEBUG_LOGS: string;
	export const PUBLIC_ENABLE_ANALYTICS: string;
	export const PUBLIC_ENABLE_REAL_TIME: string;
	export const PUBLIC_ENABLE_SEARCH: string;
	export const PUBLIC_REQUEST_TIMEOUT: string;
	export const PUBLIC_RECONNECT_INTERVAL: string;
	export const PUBLIC_MAX_RECONNECT_ATTEMPTS: string;
}

export {};
