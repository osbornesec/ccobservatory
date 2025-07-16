import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: 5173,
		strictPort: false,
		host: true
	},
	preview: {
		port: 4173,
		strictPort: false,
		host: true
	},
	optimizeDeps: {
		include: ['lucide-svelte', '@supabase/supabase-js']
	},
	build: {
		target: 'esnext',
		sourcemap: true
	}
});
