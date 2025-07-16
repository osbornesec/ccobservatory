import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import ConnectionStatus from './ConnectionStatus.svelte';

describe('ConnectionStatus', () => {
	it('should show connected WebSocket status', () => {
		render(ConnectionStatus, { props: { connectionStatus: 'connected' } });

		expect(screen.getByText('Connection Status')).toBeInTheDocument();
		expect(screen.getByText('Connected')).toBeInTheDocument();
		expect(screen.getByText('WebSocket')).toBeInTheDocument();
	});

	it('should show disconnected WebSocket status', () => {
		render(ConnectionStatus, { props: { connectionStatus: 'disconnected' } });

		expect(screen.getByText('Disconnected')).toBeInTheDocument();
	});

	it('should show Backend API and File Monitor status', () => {
		render(ConnectionStatus, { props: { connectionStatus: 'connected' } });

		expect(screen.getByText('Backend API')).toBeInTheDocument();
		expect(screen.getByText('File Monitor')).toBeInTheDocument();
		expect(screen.getByText('Active')).toBeInTheDocument();
	});

	it('should have Settings link', () => {
		render(ConnectionStatus, { props: { connectionStatus: 'connected' } });

		const settingsLink = screen.getByRole('link', { name: 'Settings' });
		expect(settingsLink).toBeInTheDocument();
		expect(settingsLink).toHaveAttribute('href', '/settings');
	});
});