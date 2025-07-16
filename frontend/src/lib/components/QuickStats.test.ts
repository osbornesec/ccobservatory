import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import QuickStats from './QuickStats.svelte';

describe('QuickStats', () => {
	const mockAnalytics = {
		total_conversations: 10,
		total_messages: 150,
		total_tool_calls: 25,
		avg_conversation_length: 15.5
	};

	it('should render all statistics cards', () => {
		render(QuickStats, { props: { analytics: mockAnalytics } });

		expect(screen.getByText('Total Conversations')).toBeInTheDocument();
		expect(screen.getByText('Total Messages')).toBeInTheDocument();
		expect(screen.getByText('Tool Calls')).toBeInTheDocument();
		expect(screen.getByText('Avg Length')).toBeInTheDocument();
	});

	it('should display correct analytics values', () => {
		render(QuickStats, { props: { analytics: mockAnalytics } });

		expect(screen.getByText('10')).toBeInTheDocument();
		expect(screen.getByText('150')).toBeInTheDocument(); 
		expect(screen.getByText('25')).toBeInTheDocument();
		expect(screen.getByText('16')).toBeInTheDocument(); // rounded from 15.5
	});

	it('should handle zero values', () => {
		const zeroAnalytics = {
			total_conversations: 0,
			total_messages: 0,
			total_tool_calls: 0,
			avg_conversation_length: 0
		};

		render(QuickStats, { props: { analytics: zeroAnalytics } });

		const zeros = screen.getAllByText('0');
		expect(zeros).toHaveLength(4);
	});
});