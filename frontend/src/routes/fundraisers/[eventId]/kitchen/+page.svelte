<script lang="ts">
	import { _ } from 'svelte-i18n';
	import { getAuth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { api } from '$lib/api';

	const auth = getAuth();
	let eventId = $derived(page.params.eventId);

	interface KitchenItem {
		menu_item_name: string;
		variant_name: string;
		dine_in: number;
		to_go: number;
		total: number;
	}

	let items = $state<KitchenItem[]>([]);
	let loading = $state(true);
	let eventName = $state('');

	let hasAccess = $derived(auth.user?.is_admin || !!auth.user?.sections?.fundraisers);

	$effect(() => {
		if (auth.checked && !hasAccess) goto('/');
	});

	$effect(() => {
		if (auth.checked && hasAccess) {
			loadData();
			const interval = setInterval(loadData, 30000);
			return () => clearInterval(interval);
		}
	});

	async function loadData() {
		const [kitchenRes, eventRes] = await Promise.all([
			api.get(`/api/fundraisers/events/${eventId}/kitchen`),
			api.get(`/api/fundraisers/events/${eventId}`)
		]);
		if (kitchenRes.ok) items = await kitchenRes.json();
		if (eventRes.ok) {
			const event = await eventRes.json();
			eventName = event.name;
		}
		loading = false;
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
					<h1 class="text-2xl font-bold">{$_('fr.kitchen.title')}</h1>
					<p class="text-sm text-gray-500">{eventName}</p>
				</div>
				<a
					href="/fundraisers/{eventId}"
					class="rounded bg-gray-200 px-3 py-2 text-sm text-gray-700"
				>
					{$_('fr.back_event')}
				</a>
			</div>

			{#if items.length === 0}
				<p class="text-gray-500">{$_('fr.kitchen.no_items')}</p>
			{:else}
				<div class="grid gap-4">
					{#each items as item}
						<div class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
							<div class="mb-3">
								<h2 class="text-xl font-bold">
									{item.menu_item_name}
									{#if item.variant_name !== 'default'}
										<span class="text-base font-normal text-gray-500">— {item.variant_name}</span>
									{/if}
								</h2>
							</div>
							<div class="grid grid-cols-3 gap-4 text-center">
								<div class="rounded-lg bg-blue-50 p-3">
									<div class="text-3xl font-bold text-blue-700">{item.dine_in}</div>
									<div class="text-sm text-blue-600">{$_('fr.kitchen.dine_in')}</div>
								</div>
								<div class="rounded-lg bg-amber-50 p-3">
									<div class="text-3xl font-bold text-amber-700">{item.to_go}</div>
									<div class="text-sm text-amber-600">{$_('fr.kitchen.to_go')}</div>
								</div>
								<div class="rounded-lg bg-gray-100 p-3">
									<div class="text-3xl font-bold text-gray-800">{item.total}</div>
									<div class="text-sm text-gray-600">{$_('fr.kitchen.total')}</div>
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>
{/if}
