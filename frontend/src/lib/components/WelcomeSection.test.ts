import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import WelcomeSection from './WelcomeSection.svelte';

describe('WelcomeSection', () => {
	it('should render welcome heading', () => {
		render(WelcomeSection);

		expect(screen.getByRole('heading', { name: 'Welcome to Claude Code Observatory' })).toBeInTheDocument();
	});

	it('should display description text', () => {
		render(WelcomeSection);

		expect(screen.getByText('Monitor and analyze your Claude Code interactions in real-time')).toBeInTheDocument();
	});

	it('should have correct heading level', () => {
		render(WelcomeSection);

		const heading = screen.getByRole('heading', { level: 1 });
		expect(heading).toBeInTheDocument();
		expect(heading).toHaveTextContent('Welcome to Claude Code Observatory');
	});
});