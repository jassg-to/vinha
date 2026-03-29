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
		id?: string;
		name: string;
		price: number;
	}
	interface MenuItem {
		id?: string;
		name: string;
		category: string;
		variants: Variant[];
	}
	interface FundraiserEvent {
		id: string;
		name: string;
		date: string;
		description: string;
		status: string;
		menu_items: MenuItem[];
	}

	let event = $state<FundraiserEvent | null>(null);
	let loading = $state(true);
	let saving = $state(false);
	let savingMenu = $state(false);
	let feedback = $state<'saved' | 'error' | null>(null);
	let menuFeedback = $state<'saved' | 'error' | null>(null);

	let canManage = $derived(
		auth.user?.is_admin || auth.user?.sections?.fundraisers === 'manager'
	);
	let canEdit = $derived(
		auth.user?.is_admin ||
			auth.user?.sections?.fundraisers === 'editor' ||
			auth.user?.sections?.fundraisers === 'manager'
	);

	$effect(() => {
		if (auth.checked && !canManage) goto(`/fundraisers/${eventId}`);
	});

	$effect(() => {
		if (auth.checked && canManage) loadEvent();
	});

	async function loadEvent() {
		loading = true;
		const res = await api.get(`/api/fundraisers/events/${eventId}`);
		if (res.ok) {
			event = await res.json();
			// Ensure at least one menu item for new events
			if (event && event.menu_items.length === 0) {
				event.menu_items = [{ name: '', category: 'meal', variants: [{ name: 'default', price: 0 }] }];
			}
		} else {
			goto('/fundraisers');
		}
		loading = false;
	}

	async function saveEvent() {
		if (!event) return;
		saving = true;
		feedback = null;
		const res = await api.patch(`/api/fundraisers/events/${eventId}`, {
			name: event.name,
			date: event.date,
			description: event.description
		});
		feedback = res.ok ? 'saved' : 'error';
		saving = false;
		setTimeout(() => (feedback = null), 2000);
	}

	async function saveMenu() {
		if (!event) return;
		savingMenu = true;
		menuFeedback = null;
		// Filter out empty items
		const items = event.menu_items
			.filter((i) => i.name.trim())
			.map((i) => ({
				name: i.name,
				category: i.category,
				variants: i.variants.filter((v) => v.name.trim()).map((v) => ({
					name: v.name,
					price: Number(v.price) || 0
				}))
			}))
			.filter((i) => i.variants.length > 0);

		const res = await api.put(`/api/fundraisers/events/${eventId}/menu`, items);
		if (res.ok) {
			const updated = await res.json();
			event = updated;
			menuFeedback = 'saved';
		} else {
			menuFeedback = 'error';
		}
		savingMenu = false;
		setTimeout(() => (menuFeedback = null), 2000);
	}

	function addMenuItem() {
		if (!event) return;
		event.menu_items = [
			...event.menu_items,
			{ name: '', category: 'meal', variants: [{ name: 'default', price: 0 }] }
		];
	}

	function removeMenuItem(index: number) {
		if (!event) return;
		event.menu_items = event.menu_items.filter((_, i) => i !== index);
	}

	function addVariant(itemIndex: number) {
		if (!event) return;
		event.menu_items[itemIndex].variants = [
			...event.menu_items[itemIndex].variants,
			{ name: '', price: 0 }
		];
	}

	function removeVariant(itemIndex: number, varIndex: number) {
		if (!event) return;
		event.menu_items[itemIndex].variants = event.menu_items[itemIndex].variants.filter(
			(_, i) => i !== varIndex
		);
	}

	const CATEGORIES = ['meal', 'drink', 'dessert', 'other'];
</script>

{#if loading}
	<div class="flex min-h-screen items-center justify-center">
		<p class="text-gray-500">{$_('dashboard.loading')}</p>
	</div>
{:else if event}
	<div class="min-h-screen p-6">
		<div class="mx-auto max-w-4xl">
			<div class="mb-6 flex items-center justify-between">
				<h1 class="text-2xl font-bold">{$_('fr.event.edit')}</h1>
				<a
					href="/fundraisers/{eventId}"
					class="rounded bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200"
				>
					{$_('fr.back_event')}
				</a>
			</div>

			<!-- Event Details -->
			<div class="mb-8 rounded-lg border border-gray-200 bg-white p-6">
				<div class="grid gap-4 sm:grid-cols-2">
					<label class="flex flex-col gap-1 text-sm">
						<span class="font-medium text-gray-700">{$_('fr.event.name')}</span>
						<input
							type="text"
							bind:value={event.name}
							disabled={saving}
							class="rounded border border-gray-200 px-3 py-2"
						/>
					</label>
					<label class="flex flex-col gap-1 text-sm">
						<span class="font-medium text-gray-700">{$_('fr.event.date')}</span>
						<input
							type="date"
							bind:value={event.date}
							disabled={saving}
							class="rounded border border-gray-200 px-3 py-2"
						/>
					</label>
					<label class="flex flex-col gap-1 text-sm sm:col-span-2">
						<span class="font-medium text-gray-700">{$_('fr.event.description')}</span>
						<textarea
							bind:value={event.description}
							disabled={saving}
							rows="2"
							class="rounded border border-gray-200 px-3 py-2"
						></textarea>
					</label>
				</div>
				<div class="mt-4 flex items-center gap-3">
					<button
						onclick={saveEvent}
						disabled={saving}
						class="rounded bg-primary px-4 py-2 text-sm text-white hover:bg-primary-dark disabled:opacity-50"
					>
						{$_('fr.event.save')}
					</button>
					{#if feedback === 'saved'}
						<span class="text-sm text-green-600">{$_('fr.event.saved')}</span>
					{:else if feedback === 'error'}
						<span class="text-sm text-red-600">{$_('fr.event.error')}</span>
					{/if}
				</div>
			</div>

			<!-- Menu Editor -->
			<div class="rounded-lg border border-gray-200 bg-white p-6">
				<h2 class="mb-4 text-lg font-semibold">{$_('fr.menu.title')}</h2>

				{#each event.menu_items as item, itemIdx}
					<div class="mb-4 rounded border border-gray-100 bg-gray-50 p-4">
						<div class="mb-3 flex flex-wrap items-end gap-3">
							<label class="flex flex-1 flex-col gap-1 text-sm">
								<span class="font-medium text-gray-700">{$_('fr.menu.item_name')}</span>
								<input
									type="text"
									bind:value={item.name}
									class="rounded border border-gray-200 px-3 py-2"
									placeholder="Feijoada Tradicional"
								/>
							</label>
							<label class="flex flex-col gap-1 text-sm">
								<span class="font-medium text-gray-700">{$_('fr.menu.category')}</span>
								<select
									bind:value={item.category}
									class="rounded border border-gray-200 px-3 py-2"
								>
									{#each CATEGORIES as cat}
										<option value={cat}>{$_(`fr.menu.category.${cat}`)}</option>
									{/each}
								</select>
							</label>
							<button
								onclick={() => removeMenuItem(itemIdx)}
								class="rounded px-3 py-2 text-sm text-red-600 hover:bg-red-50"
							>
								✕
							</button>
						</div>

						<!-- Variants -->
						<div class="ml-4 space-y-2">
							{#each item.variants as variant, varIdx}
								<div class="flex items-center gap-2">
									<input
										type="text"
										bind:value={variant.name}
										class="flex-1 rounded border border-gray-200 px-3 py-1.5 text-sm"
										placeholder={$_('fr.menu.variant_name')}
									/>
									<div class="flex items-center gap-1">
										<span class="text-sm text-gray-500">$</span>
										<input
											type="number"
											bind:value={variant.price}
											step="0.01"
											min="0"
											class="w-20 rounded border border-gray-200 px-2 py-1.5 text-sm"
										/>
									</div>
									{#if item.variants.length > 1}
										<button
											onclick={() => removeVariant(itemIdx, varIdx)}
											class="text-sm text-red-500 hover:text-red-700"
										>
											✕
										</button>
									{/if}
								</div>
							{/each}
							<button
								onclick={() => addVariant(itemIdx)}
								class="text-sm text-primary hover:underline"
							>
								+ {$_('fr.menu.add_variant')}
							</button>
						</div>
					</div>
				{/each}

				<div class="mt-4 flex flex-wrap items-center gap-3">
					<button
						onclick={addMenuItem}
						class="rounded border border-gray-200 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
					>
						+ {$_('fr.menu.add_item')}
					</button>
					<button
						onclick={saveMenu}
						disabled={savingMenu}
						class="rounded bg-primary px-4 py-2 text-sm text-white hover:bg-primary-dark disabled:opacity-50"
					>
						{$_('fr.menu.save')}
					</button>
					{#if menuFeedback === 'saved'}
						<span class="text-sm text-green-600">{$_('fr.event.saved')}</span>
					{:else if menuFeedback === 'error'}
						<span class="text-sm text-red-600">{$_('fr.event.error')}</span>
					{/if}
				</div>
			</div>

			<div class="mt-6">
				<LangSwitcher />
			</div>
		</div>
	</div>
{/if}
