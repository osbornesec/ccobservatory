/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				primary: {
					50: '#eff6ff',
					100: '#dbeafe',
					200: '#bfdbfe',
					300: '#93c5fd',
					400: '#60a5fa',
					500: '#3b82f6',
					600: '#2563eb',
					700: '#1d4ed8',
					800: '#1e40af',
					900: '#1e3a8a'
				}
			}
		}
	},
	plugins: [require('@tailwindcss/typography'), require('daisyui')],
	daisyui: {
		themes: [
			{
				light: {
					primary: '#3b82f6',
					secondary: '#f59e0b',
					accent: '#10b981',
					neutral: '#374151',
					'base-100': '#ffffff',
					'base-200': '#f9fafb',
					'base-300': '#f3f4f6',
					info: '#06b6d4',
					success: '#10b981',
					warning: '#f59e0b',
					error: '#ef4444'
				},
				dark: {
					primary: '#60a5fa',
					secondary: '#fbbf24',
					accent: '#34d399',
					neutral: '#1f2937',
					'base-100': '#111827',
					'base-200': '#1f2937',
					'base-300': '#374151',
					info: '#0891b2',
					success: '#059669',
					warning: '#d97706',
					error: '#dc2626'
				}
			}
		]
	}
};
