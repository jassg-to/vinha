<script lang="ts">
	import { _ } from 'svelte-i18n';
	import { getAuth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import StatusBadge from '$lib/components/fundraisers/StatusBadge.svelte';
	import LangSwitcher from '$lib/components/LangSwitcher.svelte';

	const auth = getAuth();
	let eventId = $derived(page.params.eventId);
	let orderId = $derived(page.params.orderId);

	interface OrderItem {
		menu_item_id: string;
		variant_id: string;
		name: string;
		price: number;
		quantity: number;
	}
	interface Payment {
		id: string;
		amount: number;
		method: string;
		recorded_at: string;
		recorded_by: string;
	}
	interface Order {
		id: string;
		person_id: string | null;
		customer_name: string;
		customer_phone: string;
		order_type: string;
		status: string;
		items: OrderItem[];
		total: number;
		payments: Payment[];
		amount_paid: number;
		notes: string;
		created_at: string;
	}

	let order = $state<Order | null>(null);
	let loading = $state(true);

	let hasAccess = $derived(auth.user?.is_admin || !!auth.user?.sections?.fundraisers);
	let canEdit = $derived(
		auth.user?.is_admin ||
			auth.user?.sections?.fundraisers === 'editor' ||
			auth.user?.sections?.fundraisers === 'manager'
	);

	$effect(() => {
		if (auth.checked && !hasAccess) goto('/');
	});

	$effect(() => {
		if (auth.checked && hasAccess) loadOrder();
	});

	async function loadOrder() {
		loading = true;
		const res = await api.get(`/api/fundraisers/events/${eventId}/orders/${orderId}`);
		if (res.ok) order = await res.json();
		else goto(`/fundraisers/${eventId}`);
		loading = false;
	}

	// Status actions
	let statusBusy = $state(false);

	async function setStatus(status: string) {
		statusBusy = true;
		const res = await api.patch(
			`/api/fundraisers/events/${eventId}/orders/${orderId}/status`,
			{ status }
		);
		if (res.ok) order = await res.json();
		statusBusy = false;
	}

	// Payment form
	let payAmount = $state(0);
	let payMethod = $state('cash');
	let payBusy = $state(false);

	let balance = $derived(order ? order.total - order.amount_paid : 0);

	$effect(() => {
		if (order && payAmount === 0) {
			payAmount = Math.max(0, Math.round((order.total - order.amount_paid) * 100) / 100);
		}
	});

	async function addPayment() {
		if (payAmount <= 0) return;
		payBusy = true;
		const res = await api.post(
			`/api/fundraisers/events/${eventId}/orders/${orderId}/payments`,
			{ amount: payAmount, method: payMethod }
		);
		if (res.ok) {
			order = await res.json();
			payAmount = Math.max(0, Math.round((order!.total - order!.amount_paid) * 100) / 100);
		}
		payBusy = false;
	}

	async function removePayment(paymentId: string) {
		const res = await api.delete(
			`/api/fundraisers/events/${eventId}/orders/${orderId}/payments/${paymentId}`
		);
		if (res.ok) order = await res.json();
	}

	function fmtMoney(n: number): string {
		return `$${n.toFixed(2)}`;
	}

	const METHODS = ['cash', 'square', 'etransfer', 'donation'] as const;

	// Status action buttons based on current status
	let statusActions = $derived.by(() => {
		if (!order) return [];
		const actions: { status: string; key: string; color: string }[] = [];
		if (order.status === 'inquiring')
			actions.push({ status: 'confirmed', key: 'fr.orders.action.confirm', color: 'bg-green-600 hover:bg-green-700' });
		if (order.status === 'confirmed') {
			actions.push({ status: 'checked_in', key: 'fr.orders.action.check_in', color: 'bg-emerald-600 hover:bg-emerald-700' });
			actions.push({ status: 'no_show', key: 'fr.orders.action.no_show', color: 'bg-red-500 hover:bg-red-600' });
		}
		if (order.status === 'checked_in')
			actions.push({ status: 'no_show', key: 'fr.orders.action.no_show', color: 'bg-red-500 hover:bg-red-600' });
		if (order.status !== 'cancelled' && order.status !== 'checked_in')
			actions.push({ status: 'cancelled', key: 'fr.orders.action.cancel', color: 'bg-gray-500 hover:bg-gray-600' });
		return actions;
	});
</script>

{#if loading}
	<div class="flex min-h-screen items-center justify-center">
		<p class="text-gray-500">{$_('dashboard.loading')}</p>
	</div>
{:else if order}
	<div class="min-h-screen p-6">
		<div class="mx-auto max-w-3xl">
			<!-- Header -->
			<div class="mb-6 flex flex-wrap items-center justify-between gap-3">
				<div>
					<div class="flex items-center gap-3">
						<h1 class="text-2xl font-bold">{order.customer_name}</h1>
						<StatusBadge status={order.status} type="order" />
					</div>
					{#if order.customer_phone}
						<p class="text-sm text-gray-500">{order.customer_phone}</p>
					{/if}
					<p class="text-sm text-gray-400">
						{$_(`fr.orders.type.${order.order_type}`)}
					</p>
				</div>
				<a
					href="/fundraisers/{eventId}"
					class="rounded bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200"
				>
					{$_('fr.back_event')}
				</a>
			</div>

			<!-- Status Actions -->
			{#if canEdit && statusActions.length > 0}
				<div class="mb-6 flex flex-wrap gap-2">
					{#each statusActions as action}
						<button
							onclick={() => setStatus(action.status)}
							disabled={statusBusy}
							class="rounded px-4 py-2 text-sm text-white disabled:opacity-50 {action.color}"
						>
							{$_(action.key)}
						</button>
					{/each}
				</div>
			{/if}

			<!-- Items -->
			<div class="mb-6 rounded-lg border border-gray-200 bg-white p-6">
				<h2 class="mb-3 text-lg font-semibold">{$_('fr.orders.items')}</h2>
				{#if order.items.length === 0}
					<p class="text-sm text-gray-500">{$_('fr.orders.status.inquiring')}</p>
				{:else}
					<div class="space-y-2">
						{#each order.items as item}
							<div class="flex justify-between text-sm">
								<span>{item.quantity}× {item.name}</span>
								<span class="text-gray-600">{fmtMoney(item.price * item.quantity)}</span>
							</div>
						{/each}
						<div class="border-t border-gray-100 pt-2">
							<div class="flex justify-between font-bold">
								<span>{$_('fr.orders.total')}</span>
								<span>{fmtMoney(order.total)}</span>
							</div>
						</div>
					</div>
				{/if}
				{#if order.notes}
					<div class="mt-3 rounded bg-gray-50 p-2 text-sm text-gray-600">
						{order.notes}
					</div>
				{/if}
			</div>

			<!-- Payments -->
			<div class="mb-6 rounded-lg border border-gray-200 bg-white p-6">
				<h2 class="mb-3 text-lg font-semibold">
					{$_('fr.orders.paid')}: {fmtMoney(order.amount_paid)}
					{#if balance > 0}
						<span class="text-base font-normal text-red-500">
							({$_('fr.orders.balance')}: {fmtMoney(balance)})
						</span>
					{/if}
				</h2>

				{#if order.payments.length > 0}
					<div class="mb-4 space-y-2">
						{#each order.payments as payment (payment.id)}
							<div class="flex items-center justify-between text-sm">
								<div>
									<span class="font-medium">{fmtMoney(payment.amount)}</span>
									<span class="ml-2 rounded bg-gray-100 px-2 py-0.5 text-xs">
										{$_(`fr.payment.method.${payment.method}`)}
									</span>
									<span class="ml-2 text-xs text-gray-400">
										{$_('fr.payment.recorded_by', { values: { name: payment.recorded_by } })}
									</span>
								</div>
								{#if canEdit}
									<button
										onclick={() => removePayment(payment.id)}
										class="text-xs text-red-500 hover:underline"
									>
										{$_('fr.payment.remove')}
									</button>
								{/if}
							</div>
						{/each}
					</div>
				{/if}

				{#if canEdit && balance > 0}
					<div class="flex flex-wrap items-end gap-3 border-t border-gray-100 pt-4">
						<label class="flex flex-col gap-1 text-sm">
							<span class="font-medium text-gray-700">{$_('fr.payment.amount')}</span>
							<div class="flex items-center gap-1">
								<span class="text-gray-500">$</span>
								<input
									type="number"
									bind:value={payAmount}
									step="0.01"
									min="0.01"
									class="w-24 rounded border border-gray-200 px-2 py-2"
								/>
							</div>
						</label>
						<label class="flex flex-col gap-1 text-sm">
							<span class="font-medium text-gray-700">{$_('fr.payment.method')}</span>
							<select
								bind:value={payMethod}
								class="rounded border border-gray-200 px-3 py-2"
							>
								{#each METHODS as m}
									<option value={m}>{$_(`fr.payment.method.${m}`)}</option>
								{/each}
							</select>
						</label>
						<button
							onclick={addPayment}
							disabled={payBusy || payAmount <= 0}
							class="rounded bg-primary px-4 py-2 text-sm text-white hover:bg-primary-dark disabled:opacity-50"
						>
							{$_('fr.payment.add')}
						</button>
					</div>
				{/if}
			</div>

			<div class="mt-6">
				<LangSwitcher />
			</div>
		</div>
	</div>
{/if}
