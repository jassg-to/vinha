import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import SummaryCard from './SummaryCard.svelte';

describe('SummaryCard', () => {
	it('renders label and value', () => {
		render(SummaryCard, { props: { label: 'Total Orders', value: 42 } });
		expect(screen.getByText('Total Orders')).toBeInTheDocument();
		expect(screen.getByText('42')).toBeInTheDocument();
	});

	it('renders string values', () => {
		render(SummaryCard, { props: { label: 'Revenue', value: '$1,250.00' } });
		expect(screen.getByText('$1,250.00')).toBeInTheDocument();
	});

	it('renders the sub text when provided', () => {
		render(SummaryCard, { props: { label: 'Revenue', value: '$500', sub: '10 orders' } });
		expect(screen.getByText('10 orders')).toBeInTheDocument();
	});

	it('does not render sub text when not provided', () => {
		const { container } = render(SummaryCard, {
			props: { label: 'Revenue', value: '$500' }
		});
		const subElements = container.querySelectorAll('.text-xs.text-gray-400');
		expect(subElements.length).toBe(0);
	});
});
