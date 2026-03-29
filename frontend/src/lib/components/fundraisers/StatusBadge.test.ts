import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { init, register, waitLocale } from 'svelte-i18n';
import StatusBadge from './StatusBadge.svelte';

beforeEach(async () => {
	register('en-CA', () =>
		Promise.resolve({
			fr: {
				status: {
					draft: 'Draft',
					open: 'Open',
					day_of: 'Day-of',
					closed: 'Closed'
				},
				orders: {
					status: {
						inquiring: 'Inquiring',
						confirmed: 'Confirmed',
						checked_in: 'Checked in',
						no_show: 'No-show',
						cancelled: 'Cancelled'
					}
				}
			}
		})
	);
	init({ fallbackLocale: 'en-CA', initialLocale: 'en-CA' });
	await waitLocale();
});

describe('StatusBadge', () => {
	it('renders event status text', () => {
		render(StatusBadge, { props: { status: 'draft' } });
		expect(screen.getByText('Draft')).toBeInTheDocument();
	});

	it('renders order status text when type is order', () => {
		render(StatusBadge, { props: { status: 'confirmed', type: 'order' } });
		expect(screen.getByText('Confirmed')).toBeInTheDocument();
	});

	it('applies the correct color class for open status', () => {
		render(StatusBadge, { props: { status: 'open' } });
		const badge = screen.getByText('Open');
		expect(badge.className).toContain('bg-green-100');
		expect(badge.className).toContain('text-green-700');
	});

	it('applies the correct color class for day_of status', () => {
		render(StatusBadge, { props: { status: 'day_of' } });
		const badge = screen.getByText('Day-of');
		expect(badge.className).toContain('bg-amber-100');
	});

	it('falls back to gray for unknown statuses', () => {
		render(StatusBadge, { props: { status: 'unknown_status' } });
		const badge = screen.getByText(/unknown_status/i);
		expect(badge.className).toContain('bg-gray-100');
	});
});
