<script lang="ts">
	import { _ } from 'svelte-i18n';
	import { getAuth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import StatusBadge from '$lib/components/fundraisers/StatusBadge.svelte';

	const auth = getAuth();
	let eventId = $derived(page.params.eventId);

	interface Order {
		id: string;
		customer_name: string;
		customer_phone: string;
		order_type: string;
		status: string;
		total: number;
		amount_paid: number;
		items: { name: string; quantity: number }[];
	}

	let orders = $state<Order[]>([]);
	let loading = $state(true);
	let eventName = $state('');
	let busy = $state<Record<string, boolean>>({});

	let canEdit = $derived(
		auth.user?.is_admin ||
			auth.user?.sections?.fundraisers === 'editor' ||
			auth.user?.sections?.fundraisers === 'manager'
	);

	$effect(() => {
		if (auth.checked && !canEdit) goto(`/fundraisers/${eventId}`);
	});

	$effect(() => {
		if (auth.checked && canEdit) {
			loadData();
			const interval = setInterval(loadData, 30000);
			return () => clearInterval(interval);
		}
	});

	async function loadData() {
		const [ordersRes, eventRes] = await Promise.all([
			api.get(`/api/fundraisers/events/${eventId}/orders`),
			api.get(`/api/fundraisers/events/${eventId}`)
		]);
		if (ordersRes.ok) {
			const all: Order[] = await ordersRes.json();
			// Show orders with outstanding balance or not yet checked in
			orders = all.filter(
				(o) => o.status !== 'cancelled' && o.status !== 'no_show' && o.status !== 'inquiring'
			);
		}
		if (eventRes.ok) {
			const event = await eventRes.json();
			eventName = event.name;
		}
		loading = false;
	}

	async function quickPay(order: Order, method: string) {
		const balance = Math.round((order.total - order.amount_paid) * 100) / 100;
		if (balance <= 0) return;
		busy[order.id] = true;
		const res = await api.post(
			`/api/fundraisers/events/${eventId}/orders/${order.id}/payments`,
			{ amount: balance, method }
		);
		if (res.ok) {
			const updated = await res.json();
			const idx = orders.findIndex((o) => o.id === order.id);
			if (idx !== -1) orders[idx] = updated;
		}
		busy[order.id] = false;
	}

	async function checkIn(order: Order) {
		busy[order.id] = true;
		const res = await api.patch(
			`/api/fundraisers/events/${eventId}/orders/${order.id}/status`,
			{ status: 'checked_in' }
		);
		if (res.ok) {
			const updated = await res.json();
			const idx = orders.findIndex((o) => o.id === order.id);
			if (idx !== -1) orders[idx] = updated;
		}
		busy[order.id] = false;
	}

	function fmtMoney(n: number): string {
		return `$${n.toFixed(2)}`;
	}
</script>

{#if loading}
	<div class="flex min-h-screen items-center justify-center">
		<p class="text-gray-500">{$_('dashboard.loading')}</p>
	</div>
{:else}
	<div class="min-h-screen bg-gray-50 p-4">
		<div class="mx-auto max-w-2xl">
			<div class="mb-4 flex items-center justify-between">
				<div>
					<h1 class="text-2xl font-bold">{$_('fr.cashier.title')}</h1>
					<p class="text-sm text-gray-500">{eventName}</p>
				</div>
				<a
					href="/fundraisers/{eventId}"
					class="rounded bg-gray-200 px-3 py-2 text-sm text-gray-700"
				>
					{$_('fr.back_event')}
				</a>
			</div>

			{#if orders.length === 0}
				<p class="text-gray-500">{$_('fr.cashier.no_orders')}</p>
			{:else}
				<div class="grid gap-3">
					{#each orders as order (order.id)}
						{@const balance = Math.round((order.total - order.amount_paid) * 100) / 100}
						<div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
							<div class="flex items-center justify-between">
								<div>
									<span class="font-bold">{order.customer_name}</span>
									<StatusBadge status={order.status} type="order" />
								</div>
								<span class="text-sm text-gray-500">
									{$_(`fr.orders.type.${order.order_type}`)}
								</span>
							</div>

							<div class="mt-1 text-sm text-gray-500">
								{order.items.map((i) => `${i.quantity}× ${i.name}`).join(', ')}
							</div>

							<div class="mt-2 flex items-center justify-between">
								<div class="text-sm">
									<span>{$_('fr.orders.total')}: <strong>{fmtMoney(order.total)}</strong></span>
									{#if order.amount_paid > 0}
										<span class="ml-2 text-green-600">{$_('fr.orders.paid')}: {fmtMoney(order.amount_paid)}</span>
									{/if}
									{#if balance > 0}
										<span class="ml-2 font-bold text-red-600">{fmtMoney(balance)}</span>
									{/if}
								</div>
							</div>

							<div class="mt-3 flex flex-wrap gap-2">
								{#if order.status === 'confirmed'}
									<button
										onclick={() => checkIn(order)}
										disabled={busy[order.id]}
										class="rounded bg-emerald-600 px-3 py-2 text-sm text-white hover:bg-emerald-700 disabled:opacity-50"
									>
										{$_('fr.orders.action.check_in')}
									</button>
								{/if}
								{#if balance > 0}
									<button
										onclick={() => quickPay(order, 'cash')}
										disabled={busy[order.id]}
										class="rounded bg-green-600 px-3 py-2 text-sm text-white hover:bg-green-700 disabled:opacity-50"
									>
										{$_('fr.payment.method.cash')} {fmtMoney(balance)}
									</button>
									<button
										onclick={() => quickPay(order, 'square')}
										disabled={busy[order.id]}
										class="rounded bg-blue-600 px-3 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
									>
										{$_('fr.payment.method.square')} {fmtMoney(balance)}
									</button>
									<button
										onclick={() => quickPay(order, 'etransfer')}
										disabled={busy[order.id]}
										class="rounded bg-purple-600 px-3 py-2 text-sm text-white hover:bg-purple-700 disabled:opacity-50"
									>
										E-transfer {fmtMoney(balance)}
									</button>
								{/if}
								<a
									href="/fundraisers/{eventId}/orders/{order.id}"
									class="rounded bg-gray-100 px-3 py-2 text-sm text-gray-700 hover:bg-gray-200"
								>
									→
								</a>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>
{/if}
