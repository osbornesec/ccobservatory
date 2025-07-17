import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import GettingStarted from './GettingStarted.svelte';

describe('GettingStarted', () => {
	it('should render getting started section', () => {
		render(GettingStarted);

		expect(screen.getByText('Getting Started')).toBeInTheDocument();
	});

	it('should display all three steps', () => {
		render(GettingStarted);

		expect(screen.getByText('Start a Claude Code session')).toBeInTheDocument();
		expect(screen.getByText('Monitor real-time activity')).toBeInTheDocument();
		expect(screen.getByText('Analyze patterns')).toBeInTheDocument();
	});

	it('should show step numbers', () => {
		render(GettingStarted);

		expect(screen.getByText('1')).toBeInTheDocument();
		expect(screen.getByText('2')).toBeInTheDocument();
		expect(screen.getByText('3')).toBeInTheDocument();
	});

	it('should have View Conversations link', () => {
		render(GettingStarted);

		const conversationsLink = screen.getByRole('link', { name: 'View Conversations' });
		expect(conversationsLink).toBeInTheDocument();
		expect(conversationsLink).toHaveAttribute('href', '/conversations');
	});

	it('should show step descriptions', () => {
		render(GettingStarted);

		expect(screen.getByText(/Files will be automatically detected/)).toBeInTheDocument();
		expect(screen.getByText(/Watch conversations and tool usage/)).toBeInTheDocument();
		expect(screen.getByText(/Use analytics to understand/)).toBeInTheDocument();
	});
});