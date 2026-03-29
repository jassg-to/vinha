<script lang="ts">
	import { _ } from 'svelte-i18n';
	import { getAuth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import LangSwitcher from '$lib/components/LangSwitcher.svelte';

	const auth = getAuth();
	let eventId = $derived(page.params.eventId);

	interface Variant {
		id: string;
		name: string;
		price: number;
	}
	interface MenuItem {
		id: string;
		name: string;
		category: string;
		variants: Variant[];
	}
	interface Person {
		id: string;
		name: string;
		phone: string;
	}

	let menuItems = $state<MenuItem[]>([]);
	let people = $state<Person[]>([]);
	let loading = $state(true);
	let saving = $state(false);

	// Order form state
	let customerName = $state('');
	let customerPhone = $state('');
	let personId = $state<string | null>(null);
	let orderType = $state<'dine_in' | 'to_go'>('dine_in');
	let orderStatus = $state<'confirmed' | 'inquiring'>('confirmed');
	let notes = $state('');
	let quantities = $state<Record<string, number>>({});

	// People search
	let peopleQuery = $state('');
	let showPeopleDropdown = $state(false);
	let filteredPeople = $derived(
		peopleQuery.length >= 2
			? people.filter(
					(p) =>
						p.name.toLowerCase().includes(peopleQuery.toLowerCase()) ||
						p.phone.includes(peopleQuery)
				)
			: []
	);

	let canEdit = $derived(
		auth.user?.is_admin ||
			auth.user?.sections?.fundraisers === 'editor' ||
			auth.user?.sections?.fundraisers === 'manager'
	);

	$effect(() => {
		if (auth.checked && !canEdit) goto(`/fundraisers/${eventId}`);
	});

	$effect(() => {
		if (auth.checked && canEdit) loadData();
	});

	async function loadData() {
		loading = true;
		const [eventRes, peopleRes] = await Promise.all([
			api.get(`/api/fundraisers/events/${eventId}`),
			api.get('/api/fundraisers/people')
		]);
		if (eventRes.ok) {
			const event = await eventRes.json();
			menuItems = event.menu_items;
		} else {
			goto('/fundraisers');
		}
		if (peopleRes.ok) people = await peopleRes.json();
		loading = false;
	}

	function selectPerson(person: Person) {
		personId = person.id;
		customerName = person.name;
		customerPhone = person.phone;
		peopleQuery = person.name;
		showPeopleDropdown = false;
	}

	function clearPerson() {
		personId = null;
		customerName = '';
		customerPhone = '';
		peopleQuery = '';
	}

	function qtyKey(itemId: string, variantId: string): string {
		return `${itemId}:${variantId}`;
	}

	function getQty(itemId: string, variantId: string): number {
		return quantities[qtyKey(itemId, variantId)] || 0;
	}

	function setQty(itemId: string, variantId: string, val: number) {
		const key = qtyKey(itemId, variantId);
		if (val <= 0) {
			const { [key]: _, ...rest } = quantities;
			quantities = rest;
		} else {
			quantities = { ...quantities, [key]: val };
		}
	}

	let orderTotal = $derived(
		Object.entries(quantities).reduce((sum, [key, qty]) => {
			const [itemId, variantId] = key.split(':');
			const item = menuItems.find((i) => i.id === itemId);
			const variant = item?.variants.find((v) => v.id === variantId);
			return sum + (variant?.price || 0) * qty;
		}, 0)
	);

	async function submit() {
		if (!customerName) return;
		saving = true;

		// Create person if new
		let pid = personId;
		if (!pid && customerName) {
			const res = await api.post('/api/fundraisers/people', {
				name: customerName,
				phone: customerPhone
			});
			if (res.ok) {
				const person = await res.json();
				pid = person.id;
			}
		}

		const items = Object.entries(quantities)
			.filter(([, qty]) => qty > 0)
			.map(([key, qty]) => {
				const [menu_item_id, variant_id] = key.split(':');
				return { menu_item_id, variant_id, quantity: qty };
			});

		const res = await api.post(`/api/fundraisers/events/${eventId}/orders`, {
			person_id: pid,
			customer_name: customerName,
			customer_phone: customerPhone,
			order_type: orderType,
			status: orderStatus,
			items,
			notes
		});

		if (res.ok) {
			const order = await res.json();
			goto(`/fundraisers/${eventId}/orders/${order.id}`);
		}
		saving = false;
	}
</script>

{#if loading}
	<div class="flex min-h-screen items-center justify-center">
		<p class="text-gray-500">{$_('dashboard.loading')}</p>
	</div>
{:else}
	<div class="min-h-screen p-6">
		<div class="mx-auto max-w-3xl">
			<div class="mb-6 flex items-center justify-between">
				<h1 class="text-2xl font-bold">{$_('fr.orders.new')}</h1>
				<a
					href="/fundraisers/{eventId}"
					class="rounded bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200"
				>
					{$_('fr.back_event')}
				</a>
			</div>

			<!-- Customer -->
			<div class="mb-6 rounded-lg border border-gray-200 bg-white p-6">
				<h2 class="mb-4 text-lg font-semibold">{$_('fr.orders.customer')}</h2>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="relative">
						<label class="flex flex-col gap-1 text-sm">
							<span class="font-medium text-gray-700">{$_('fr.orders.customer')}</span>
							<input
								type="text"
								bind:value={peopleQuery}
								oninput={() => {
									showPeopleDropdown = true;
									customerName = peopleQuery;
									personId = null;
								}}
								onfocus={() => (showPeopleDropdown = true)}
								onblur={() => setTimeout(() => (showPeopleDropdown = false), 200)}
								class="rounded border border-gray-200 px-3 py-2"
								placeholder={$_('fr.people.search')}
							/>
						</label>
						{#if showPeopleDropdown && filteredPeople.length > 0}
							<div
								class="absolute z-10 mt-1 w-full rounded border border-gray-200 bg-white shadow-lg"
							>
								{#each filteredPeople.slice(0, 8) as person (person.id)}
									<button
										class="w-full px-3 py-2 text-left text-sm hover:bg-gray-50"
										onmousedown={() => selectPerson(person)}
									>
										<div class="font-medium">{person.name}</div>
										{#if person.phone}
											<div class="text-xs text-gray-400">{person.phone}</div>
										{/if}
									</button>
								{/each}
							</div>
						{/if}
					</div>
					<label class="flex flex-col gap-1 text-sm">
						<span class="font-medium text-gray-700">{$_('fr.orders.phone')}</span>
						<input
							type="tel"
							bind:value={customerPhone}
							class="rounded border border-gray-200 px-3 py-2"
						/>
					</label>
				</div>
			</div>

			<!-- Type & Status -->
			<div class="mb-6 rounded-lg border border-gray-200 bg-white p-6">
				<div class="flex flex-wrap gap-6">
					<div class="flex flex-col gap-1 text-sm">
						<span class="font-medium text-gray-700">{$_('fr.orders.type')}</span>
						<div class="flex gap-2">
							<button
								onclick={() => (orderType = 'dine_in')}
								class="rounded px-4 py-2 text-sm {orderType === 'dine_in'
									? 'bg-primary text-white'
									: 'bg-gray-100 text-gray-700'}"
							>
								{$_('fr.orders.type.dine_in')}
							</button>
							<button
								onclick={() => (orderType = 'to_go')}
								class="rounded px-4 py-2 text-sm {orderType === 'to_go'
									? 'bg-primary text-white'
									: 'bg-gray-100 text-gray-700'}"
							>
								{$_('fr.orders.type.to_go')}
							</button>
						</div>
					</div>
					<div class="flex flex-col gap-1 text-sm">
						<span class="font-medium text-gray-700">{$_('fr.orders.status')}</span>
						<div class="flex gap-2">
							<button
								onclick={() => (orderStatus = 'confirmed')}
								class="rounded px-4 py-2 text-sm {orderStatus === 'confirmed'
									? 'bg-primary text-white'
									: 'bg-gray-100 text-gray-700'}"
							>
								{$_('fr.orders.status.confirmed')}
							</button>
							<button
								onclick={() => (orderStatus = 'inquiring')}
								class="rounded px-4 py-2 text-sm {orderStatus === 'inquiring'
									? 'bg-primary text-white'
									: 'bg-gray-100 text-gray-700'}"
							>
								{$_('fr.orders.status.inquiring')}
							</button>
						</div>
					</div>
				</div>
			</div>

			<!-- Menu Items -->
			<div class="mb-6 rounded-lg border border-gray-200 bg-white p-6">
				<h2 class="mb-4 text-lg font-semibold">{$_('fr.orders.items')}</h2>
				{#if menuItems.length === 0}
					<p class="text-gray-500">{$_('fr.menu.no_items')}</p>
				{:else}
					<div class="space-y-4">
						{#each menuItems as item (item.id)}
							<div>
								<h3 class="mb-2 font-medium text-gray-700">{item.name}</h3>
								<div class="ml-4 space-y-2">
									{#each item.variants as variant (variant.id)}
										<div class="flex items-center gap-3">
											<span class="w-32 text-sm text-gray-600">
												{variant.name === 'default' ? item.name : variant.name}
											</span>
											<span class="text-sm text-gray-500">${variant.price.toFixed(2)}</span>
											<div class="flex items-center gap-1">
												<button
													onclick={() =>
														setQty(item.id, variant.id, getQty(item.id, variant.id) - 1)}
													disabled={getQty(item.id, variant.id) === 0}
													class="h-8 w-8 rounded border border-gray-200 text-center text-lg leading-none hover:bg-gray-50 disabled:opacity-30"
												>
													−
												</button>
												<span class="w-8 text-center text-sm font-medium">
													{getQty(item.id, variant.id)}
												</span>
												<button
													onclick={() =>
														setQty(item.id, variant.id, getQty(item.id, variant.id) + 1)}
													class="h-8 w-8 rounded border border-gray-200 text-center text-lg leading-none hover:bg-gray-50"
												>
													+
												</button>
											</div>
										</div>
									{/each}
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>

			<!-- Notes -->
			<div class="mb-6 rounded-lg border border-gray-200 bg-white p-6">
				<label class="flex flex-col gap-1 text-sm">
					<span class="font-medium text-gray-700">{$_('fr.orders.notes')}</span>
					<textarea
						bind:value={notes}
						rows="2"
						class="rounded border border-gray-200 px-3 py-2"
					></textarea>
				</label>
			</div>

			<!-- Submit -->
			<div class="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-6">
				<div class="text-xl font-bold">{$_('fr.orders.total')}: ${orderTotal.toFixed(2)}</div>
				<button
					onclick={submit}
					disabled={saving || !customerName}
					class="rounded bg-primary px-6 py-3 text-white hover:bg-primary-dark disabled:opacity-50"
				>
					{$_('fr.orders.save')}
				</button>
			</div>

			<div class="mt-6">
				<LangSwitcher />
			</div>
		</div>
	</div>
{/if}
