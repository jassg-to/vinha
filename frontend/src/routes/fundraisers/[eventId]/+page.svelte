<script lang="ts">
	import { _ } from 'svelte-i18n';
	import { getAuth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import StatusBadge from '$lib/components/fundraisers/StatusBadge.svelte';
	import SummaryCard from '$lib/components/fundraisers/SummaryCard.svelte';
	import LangSwitcher from '$lib/components/LangSwitcher.svelte';

	const auth = getAuth();
	let eventId = $derived(page.params.eventId);

	interface FundraiserEvent {
		id: string;
		name: string;
		date: string;
		description: string;
		status: string;
		menu_items: { id: string; name: string; variants: { id: string; name: string; price: number }[] }[];
	}
	interface Order {
		id: string;
		customer_name: string;
		customer_phone: string;
		order_type: string;
		status: string;
		items: { name: string; quantity: number; price: number }[];
		total: number;
		amount_paid: number;
		payments: unknown[];
		notes: string;
	}
	interface Summary {
		total_orders: number;
		total_meals: number;
		total_revenue: number;
		total_paid: number;
		total_outstanding: number;
		by_method: Record<string, number>;
		by_status: Record<string, number>;
	}

	let event = $state<FundraiserEvent | null>(null);
	let orders = $state<Order[]>([]);
	let summary = $state<Summary | null>(null);
	let loading = $state(true);

	let statusFilter = $state('');
	let typeFilter = $state('');
	let paymentFilter = $state('');

	let hasAccess = $derived(auth.user?.is_admin || !!auth.user?.sections?.fundraisers);
	let canManage = $derived(auth.user?.is_admin || auth.user?.sections?.fundraisers === 'manager');
	let canEdit = $derived(
		auth.user?.is_admin ||
			auth.user?.sections?.fundraisers === 'editor' ||
			auth.user?.sections?.fundraisers === 'manager'
	);

	$effect(() => {
		if (auth.checked && !hasAccess) goto('/');
	});

	$effect(() => {
		if (auth.checked && hasAccess) loadAll();
	});

	async function loadAll() {
		loading = true;
		const [eventRes, ordersRes, summaryRes] = await Promise.all([
			api.get(`/api/fundraisers/events/${eventId}`),
			api.get(`/api/fundraisers/events/${eventId}/orders`),
			api.get(`/api/fundraisers/events/${eventId}/summary`)
		]);
		if (eventRes.ok) event = await eventRes.json();
		else goto('/fundraisers');
		if (ordersRes.ok) orders = await ordersRes.json();
		if (summaryRes.ok) summary = await summaryRes.json();
		loading = false;
	}

	let filteredOrders = $derived.by(() => {
		let result = orders;
		if (statusFilter) result = result.filter((o) => o.status === statusFilter);
		if (typeFilter) result = result.filter((o) => o.order_type === typeFilter);
		if (paymentFilter === 'paid') result = result.filter((o) => o.amount_paid >= o.total);
		if (paymentFilter === 'unpaid') result = result.filter((o) => o.amount_paid < o.total);
		return result;
	});

	const STATUS_FLOW: Record<string, string> = {
		draft: 'open',
		open: 'day_of',
		day_of: 'closed'
	};
	const STATUS_BACK: Record<string, string> = {
		open: 'draft',
		day_of: 'open',
		closed: 'day_of'
	};
	const STATUS_ACTION_KEY: Record<string, string> = {
		open: 'fr.event.open',
		day_of: 'fr.event.start_day',
		closed: 'fr.event.close'
	};

	let statusBusy = $state(false);

	async function setEventStatus(status: string) {
		if (!event) return;
		statusBusy = true;
		const res = await api.patch(`/api/fundraisers/events/${eventId}`, { status });
		if (res.ok) {
			event = await res.json();
			await loadAll();
		}
		statusBusy = false;
	}

	function fmtMoney(n: number): string {
		return `$${n.toFixed(2)}`;
	}

	function itemSummary(order: Order): string {
		return order.items.map((i) => `${i.quantity}× ${i.name}`).join(', ');
	}
</script>

{#if loading}
	<div class="flex min-h-screen items-center justify-center">
		<p class="text-gray-500">{$_('dashboard.loading')}</p>
	</div>
{:else if event}
	<div class="min-h-screen p-6">
		<div class="mx-auto max-w-6xl">
			<!-- Header -->
			<div class="mb-6 flex flex-wrap items-center justify-between gap-3">
				<div>
					<div class="flex items-center gap-3">
						<h1 class="text-2xl font-bold">{event.name}</h1>
						<StatusBadge status={event.status} />
					</div>
					<p class="text-sm text-gray-500">{event.date}</p>
				</div>
				<div class="flex flex-wrap gap-2">
					{#if canManage && STATUS_BACK[event.status]}
						<button
							onclick={() => setEventStatus(STATUS_BACK[event.status])}
							disabled={statusBusy}
							class="rounded border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-50"
						>
							← {$_(`fr.status.${STATUS_BACK[event.status]}`)}
						</button>
					{/if}
					{#if canManage && STATUS_FLOW[event.status]}
						<button
							onclick={() => setEventStatus(STATUS_FLOW[event.status])}
							disabled={statusBusy}
							class="rounded bg-amber-500 px-4 py-2 text-sm text-white hover:bg-amber-600 disabled:opacity-50"
						>
							{$_(STATUS_ACTION_KEY[STATUS_FLOW[event.status]])}
						</button>
					{/if}
					{#if canEdit}
						<a
							href="/fundraisers/{eventId}/orders/new"
							class="rounded bg-primary px-4 py-2 text-sm text-white hover:bg-primary-dark"
						>
							{$_('fr.orders.new')}
						</a>
					{/if}
					{#if event.status === 'day_of' || event.status === 'open'}
						<a
							href="/fundraisers/{eventId}/kitchen"
							class="rounded bg-gray-100 px-3 py-2 text-sm text-gray-700 hover:bg-gray-200"
						>
							{$_('fr.kitchen.title')}
						</a>
						<a
							href="/fundraisers/{eventId}/cashier"
							class="rounded bg-gray-100 px-3 py-2 text-sm text-gray-700 hover:bg-gray-200"
						>
							{$_('fr.cashier.title')}
						</a>
					{/if}
					{#if canManage}
						<a
							href="/fundraisers/{eventId}/edit"
							class="rounded bg-gray-100 px-3 py-2 text-sm text-gray-700 hover:bg-gray-200"
						>
							{$_('fr.event.edit')}
						</a>
					{/if}
					<a
						href="/fundraisers"
						class="rounded bg-gray-100 px-3 py-2 text-sm text-gray-700 hover:bg-gray-200"
					>
						{$_('fr.back_events')}
					</a>
				</div>
			</div>

			<!-- Summary Cards -->
			{#if summary}
				<div class="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
					<SummaryCard label={$_('fr.summary.orders')} value={summary.total_orders} />
					<SummaryCard label={$_('fr.summary.meals')} value={summary.total_meals} />
					<SummaryCard label={$_('fr.summary.revenue')} value={fmtMoney(summary.total_revenue)} />
					<SummaryCard label={$_('fr.summary.paid')} value={fmtMoney(summary.total_paid)} />
					<SummaryCard
						label={$_('fr.summary.outstanding')}
						value={fmtMoney(summary.total_outstanding)}
					/>
				</div>
			{/if}

			<!-- Filters -->
			<div class="mb-4 flex flex-wrap gap-2">
				<select
					bind:value={statusFilter}
					class="rounded border border-gray-200 px-3 py-1.5 text-sm"
				>
					<option value="">{$_('fr.orders.status')}: {$_('fr.orders.filter.all')}</option>
					{#each ['inquiring', 'confirmed', 'checked_in', 'no_show', 'cancelled'] as s}
						<option value={s}>{$_(`fr.orders.status.${s}`)}</option>
					{/each}
				</select>
				<select
					bind:value={typeFilter}
					class="rounded border border-gray-200 px-3 py-1.5 text-sm"
				>
					<option value="">{$_('fr.orders.type')}: {$_('fr.orders.filter.all')}</option>
					<option value="dine_in">{$_('fr.orders.type.dine_in')}</option>
					<option value="to_go">{$_('fr.orders.type.to_go')}</option>
				</select>
				<select
					bind:value={paymentFilter}
					class="rounded border border-gray-200 px-3 py-1.5 text-sm"
				>
					<option value="">{$_('fr.orders.paid')}: {$_('fr.orders.filter.all')}</option>
					<option value="paid">{$_('fr.orders.filter.paid')}</option>
					<option value="unpaid">{$_('fr.orders.filter.unpaid')}</option>
				</select>
			</div>

			<!-- Orders Table -->
			{#if filteredOrders.length === 0}
				<p class="text-gray-500">{$_('fr.orders.no_orders')}</p>
			{:else}
				<!-- Desktop table -->
				<div class="hidden overflow-x-auto rounded border border-gray-200 md:block">
					<table class="w-full text-left text-sm">
						<thead class="bg-gray-50 text-gray-600">
							<tr>
								<th class="px-4 py-3">{$_('fr.orders.customer')}</th>
								<th class="px-4 py-3">{$_('fr.orders.type')}</th>
								<th class="px-4 py-3">{$_('fr.orders.items')}</th>
								<th class="px-4 py-3 text-right">{$_('fr.orders.total')}</th>
								<th class="px-4 py-3 text-right">{$_('fr.orders.paid')}</th>
								<th class="px-4 py-3 text-center">{$_('fr.orders.status')}</th>
							</tr>
						</thead>
						<tbody>
							{#each filteredOrders as order (order.id)}
								<tr
									class="cursor-pointer border-t border-gray-100 hover:bg-gray-50"
									onclick={() => goto(`/fundraisers/${eventId}/orders/${order.id}`)}
								>
									<td class="px-4 py-3">
										<div class="font-medium">{order.customer_name}</div>
										{#if order.customer_phone}
											<div class="text-xs text-gray-400">{order.customer_phone}</div>
										{/if}
									</td>
									<td class="px-4 py-3">{$_(`fr.orders.type.${order.order_type}`)}</td>
									<td class="max-w-xs truncate px-4 py-3 text-gray-600">{itemSummary(order)}</td>
									<td class="px-4 py-3 text-right">{fmtMoney(order.total)}</td>
									<td class="px-4 py-3 text-right">
										{fmtMoney(order.amount_paid)}
										{#if order.amount_paid < order.total}
											<span class="text-xs text-red-500">
												({fmtMoney(order.total - order.amount_paid)})
											</span>
										{/if}
									</td>
									<td class="px-4 py-3 text-center">
										<StatusBadge status={order.status} type="order" />
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>

				<!-- Mobile cards -->
				<div class="grid gap-3 md:hidden">
					{#each filteredOrders as order (order.id)}
						<a
							href="/fundraisers/{eventId}/orders/{order.id}"
							class="block rounded-lg border border-gray-200 bg-white p-4"
						>
							<div class="flex items-center justify-between">
								<div class="font-medium">{order.customer_name}</div>
								<StatusBadge status={order.status} type="order" />
							</div>
							<div class="mt-1 text-sm text-gray-500">
								{$_(`fr.orders.type.${order.order_type}`)} · {itemSummary(order)}
							</div>
							<div class="mt-2 flex justify-between text-sm">
								<span>{$_('fr.orders.total')}: {fmtMoney(order.total)}</span>
								<span>
									{$_('fr.orders.paid')}: {fmtMoney(order.amount_paid)}
									{#if order.amount_paid < order.total}
										<span class="text-red-500">({fmtMoney(order.total - order.amount_paid)})</span>
									{/if}
								</span>
							</div>
						</a>
					{/each}
				</div>
			{/if}

			<div class="mt-6">
				<LangSwitcher />
			</div>
		</div>
	</div>
{/if}
