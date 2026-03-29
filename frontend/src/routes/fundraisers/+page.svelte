<script lang="ts">
	import { _ } from 'svelte-i18n';
	import { getAuth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import StatusBadge from '$lib/components/fundraisers/StatusBadge.svelte';
	import LangSwitcher from '$lib/components/LangSwitcher.svelte';

	const auth = getAuth();

	interface Event {
		id: string;
		name: string;
		date: string;
		description: string;
		status: string;
		menu_items: unknown[];
	}

	let events = $state<Event[]>([]);
	let loading = $state(true);

	let canManage = $derived(
		auth.user?.is_admin ||
			auth.user?.sections?.fundraisers === 'manager'
	);
	let hasAccess = $derived(
		auth.user?.is_admin || !!auth.user?.sections?.fundraisers
	);

	$effect(() => {
		if (auth.checked && !hasAccess) goto('/');
	});

	$effect(() => {
		if (auth.checked && hasAccess) loadEvents();
	});

	async function loadEvents() {
		loading = true;
		const res = await api.get('/api/fundraisers/events');
		if (res.ok) events = await res.json();
		loading = false;
	}

	// New event form
	let creating = $state(false);
	let newName = $state('');
	let newDate = $state('');
	let createBusy = $state(false);

	async function createEvent() {
		if (!newName || !newDate) return;
		createBusy = true;
		const res = await api.post('/api/fundraisers/events', {
			name: newName,
			date: newDate
		});
		if (res.ok) {
			const event = await res.json();
			goto(`/fundraisers/${event.id}/edit`);
		}
		createBusy = false;
	}
</script>

{#if auth.loading || loading}
	<div class="flex min-h-screen items-center justify-center">
		<p class="text-gray-500">{$_('dashboard.loading')}</p>
	</div>
{:else}
	<div class="min-h-screen p-6">
		<div class="mx-auto max-w-4xl">
			<div class="mb-6 flex items-center justify-between">
				<h1 class="text-2xl font-bold">{$_('fr.title')}</h1>
				<div class="flex gap-2">
					{#if canManage}
						<button
							onclick={() => (creating = !creating)}
							class="rounded bg-primary px-4 py-2 text-sm text-white hover:bg-primary-dark"
						>
							{$_('fr.new_event')}
						</button>
					{/if}
					<a
						href="/"
						class="rounded bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200"
					>
						{$_('fr.back')}
					</a>
				</div>
			</div>

			{#if creating}
				<div class="mb-6 rounded border border-gray-200 bg-gray-50 p-4">
					<div class="flex flex-wrap items-end gap-3">
						<label class="flex flex-col gap-1 text-sm">
							<span class="font-medium text-gray-700">{$_('fr.event.name')}</span>
							<input
								type="text"
								bind:value={newName}
								disabled={createBusy}
								class="rounded border border-gray-200 px-3 py-2 text-sm"
								placeholder="Feijoada de Março"
							/>
						</label>
						<label class="flex flex-col gap-1 text-sm">
							<span class="font-medium text-gray-700">{$_('fr.event.date')}</span>
							<input
								type="date"
								bind:value={newDate}
								disabled={createBusy}
								class="rounded border border-gray-200 px-3 py-2 text-sm"
							/>
						</label>
						<button
							onclick={createEvent}
							disabled={createBusy || !newName || !newDate}
							class="rounded bg-primary px-4 py-2 text-sm text-white hover:bg-primary-dark disabled:opacity-50"
						>
							{$_('fr.event.create')}
						</button>
					</div>
				</div>
			{/if}

			{#if events.length === 0}
				<p class="text-gray-500">{$_('fr.no_events')}</p>
			{:else}
				<div class="grid gap-4">
					{#each events as event (event.id)}
						<a
							href="/fundraisers/{event.id}"
							class="block rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
						>
							<div class="flex items-center justify-between">
								<div>
									<h2 class="text-lg font-semibold">{event.name}</h2>
									<p class="text-sm text-gray-500">{event.date}</p>
								</div>
								<StatusBadge status={event.status} />
							</div>
							{#if event.description}
								<p class="mt-2 text-sm text-gray-600">{event.description}</p>
							{/if}
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
