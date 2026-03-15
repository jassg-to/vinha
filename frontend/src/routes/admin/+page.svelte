<script lang="ts">
	import { _ } from 'svelte-i18n';
	import { getAuth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import LangSwitcher from '$lib/components/LangSwitcher.svelte';

	const auth = getAuth();

	const ROLES = ['viewer', 'editor', 'manager'] as const;

	interface UserRow {
		email: string;
		emails: string[];
		name: string;
		picture: string;
		is_admin: boolean;
		sections: Record<string, string>;
	}

	let users = $state<UserRow[]>([]);
	let sections = $state<string[]>([]);
	let saving = $state<Record<string, boolean>>({});
	let feedback = $state<Record<string, 'saved' | 'error'>>({});

	let merging = $state(false);
	let mergePrimary = $state('');
	let mergeSecondary = $state('');
	let mergeBusy = $state(false);
	let mergeFeedback = $state<'success' | 'error' | null>(null);

	$effect(() => {
		if (auth.checked && (!auth.user || !auth.user.is_admin)) {
			goto('/');
		}
	});

	$effect(() => {
		if (auth.checked && auth.user?.is_admin) {
			loadData();
		}
	});

	async function loadData() {
		const [usersRes, sectionsRes] = await Promise.all([
			api.get('/api/admin/users'),
			api.get('/api/admin/sections')
		]);
		if (usersRes.ok) users = await usersRes.json();
		if (sectionsRes.ok) sections = await sectionsRes.json();
	}

	async function updatePermissions(user: UserRow) {
		saving[user.email] = true;
		feedback[user.email] = undefined!;
		try {
			const res = await api.patch(
				`/api/admin/users/${encodeURIComponent(user.email)}/permissions`,
				{
					is_admin: user.is_admin,
					sections: user.sections
				}
			);
			if (res.ok) {
				const updated = await res.json();
				const idx = users.findIndex((u) => u.email === user.email);
				if (idx !== -1) users[idx] = updated;
				feedback[user.email] = 'saved';
			} else {
				feedback[user.email] = 'error';
			}
		} catch {
			feedback[user.email] = 'error';
		} finally {
			saving[user.email] = false;
			setTimeout(() => {
				feedback[user.email] = undefined!;
			}, 2000);
		}
	}

	function toggleAdmin(user: UserRow) {
		user.is_admin = !user.is_admin;
		updatePermissions(user);
	}

	function setRole(user: UserRow, section: string, role: string) {
		if (role === '') {
			const { [section]: _, ...rest } = user.sections;
			user.sections = rest;
		} else {
			user.sections = { ...user.sections, [section]: role };
		}
		updatePermissions(user);
	}

	function isSelf(email: string): boolean {
		return auth.user?.email === email;
	}

	function openMerge() {
		merging = true;
		mergePrimary = '';
		mergeSecondary = '';
		mergeFeedback = null;
	}

	function closeMerge() {
		merging = false;
		mergeFeedback = null;
	}

	async function submitMerge() {
		if (!mergePrimary || !mergeSecondary || mergePrimary === mergeSecondary) return;
		mergeBusy = true;
		mergeFeedback = null;
		try {
			const res = await api.post('/api/admin/users/merge', {
				primary_email: mergePrimary,
				secondary_email: mergeSecondary
			});
			if (res.ok) {
				mergeFeedback = 'success';
				await loadData();
				setTimeout(closeMerge, 1500);
			} else {
				mergeFeedback = 'error';
			}
		} catch {
			mergeFeedback = 'error';
		} finally {
			mergeBusy = false;
		}
	}
</script>

{#if auth.loading}
	<div class="flex min-h-screen items-center justify-center">
		<p class="text-gray-500">{$_('dashboard.loading')}</p>
	</div>
{:else if auth.user?.is_admin}
	<div class="min-h-screen p-6">
		<div class="mx-auto max-w-5xl">
			<div class="mb-6 flex items-center justify-between">
				<h1 class="text-2xl font-bold">{$_('admin.title')}</h1>
				<div class="flex gap-2">
					<button
						onclick={openMerge}
						class="rounded bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200"
					>
						{$_('admin.merge')}
					</button>
					<a
						href="/"
						class="rounded bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200"
					>
						{$_('admin.back')}
					</a>
				</div>
			</div>

			{#if merging}
				<div class="mb-6 rounded border border-gray-200 bg-gray-50 p-4">
					<p class="mb-3 text-sm text-gray-600">{$_('admin.merge.description')}</p>
					<div class="flex flex-wrap items-end gap-3">
						<label class="flex flex-col gap-1 text-sm">
							<span class="font-medium text-gray-700">{$_('admin.merge.primary')}</span>
							<select
								bind:value={mergePrimary}
								disabled={mergeBusy}
								class="rounded border border-gray-200 px-3 py-2 text-sm"
							>
								<option value="">—</option>
								{#each users as u (u.email)}
									{#if u.email !== mergeSecondary}
										<option value={u.email}>{u.name} ({u.email})</option>
									{/if}
								{/each}
							</select>
						</label>
						<label class="flex flex-col gap-1 text-sm">
							<span class="font-medium text-gray-700">{$_('admin.merge.secondary')}</span>
							<select
								bind:value={mergeSecondary}
								disabled={mergeBusy}
								class="rounded border border-gray-200 px-3 py-2 text-sm"
							>
								<option value="">—</option>
								{#each users as u (u.email)}
									{#if u.email !== mergePrimary}
										<option value={u.email}>{u.name} ({u.email})</option>
									{/if}
								{/each}
							</select>
						</label>
						<button
							onclick={submitMerge}
							disabled={mergeBusy || !mergePrimary || !mergeSecondary}
							class="rounded bg-primary px-4 py-2 text-sm text-white hover:bg-primary-dark disabled:opacity-50"
						>
							{$_('admin.merge.submit')}
						</button>
						<button
							onclick={closeMerge}
							disabled={mergeBusy}
							class="rounded px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
						>
							{$_('admin.merge.cancel')}
						</button>
						{#if mergeFeedback === 'success'}
							<span class="text-sm text-green-600">{$_('admin.merge.success')}</span>
						{:else if mergeFeedback === 'error'}
							<span class="text-sm text-red-600">{$_('admin.error')}</span>
						{/if}
					</div>
				</div>
			{/if}

			{#if users.length === 0}
				<p class="text-gray-500">{$_('admin.no_users')}</p>
			{:else}
				<div class="overflow-x-auto rounded border border-gray-200">
					<table class="w-full text-left text-sm">
						<thead class="bg-gray-50 text-gray-600">
							<tr>
								<th class="px-4 py-3">{$_('admin.name')}</th>
								<th class="px-4 py-3">{$_('admin.email')}</th>
								<th class="px-4 py-3 text-center">{$_('admin.admin')}</th>
								{#each sections as section}
									<th class="px-4 py-3 text-center">{$_(`admin.section.${section}`)}</th>
								{/each}
								<th class="w-16 px-4 py-3"></th>
							</tr>
						</thead>
						<tbody>
							{#each users as user (user.email)}
								<tr class="border-t border-gray-100">
									<td class="px-4 py-3">
										<div class="flex items-center gap-2">
											{#if user.picture}
												<img
													src={user.picture}
													alt={user.name}
													class="h-8 w-8 rounded-full"
												/>
											{/if}
											<span>{user.name}</span>
										</div>
									</td>
									<td class="px-4 py-3 text-gray-600">
										<div>{user.email}</div>
										{#if user.emails && user.emails.length > 1}
											<div class="mt-1 text-xs text-gray-400" title={$_('admin.emails')}>
												{user.emails.filter((e) => e !== user.email).join(', ')}
											</div>
										{/if}
									</td>
									<td class="px-4 py-3 text-center">
										<button
											onclick={() => toggleAdmin(user)}
											disabled={isSelf(user.email) || saving[user.email]}
											class="inline-flex h-6 w-11 items-center rounded-full transition-colors
												{user.is_admin ? 'bg-primary' : 'bg-gray-300'}
												{isSelf(user.email) ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}"
											title={isSelf(user.email) ? $_('admin.self_demote') : ''}
										>
											<span
												class="inline-block h-4 w-4 rounded-full bg-white transition-transform
													{user.is_admin ? 'translate-x-6' : 'translate-x-1'}"
											></span>
										</button>
									</td>
									{#each sections as section}
										<td class="px-4 py-3 text-center">
											<select
												value={user.sections[section] ?? ''}
												onchange={(e) => setRole(user, section, e.currentTarget.value)}
												disabled={saving[user.email]}
												class="rounded border border-gray-200 px-2 py-1 text-sm"
											>
												<option value="">{$_('admin.role.none')}</option>
												{#each ROLES as role}
													<option value={role}>{$_(`admin.role.${role}`)}</option>
												{/each}
											</select>
										</td>
									{/each}
									<td class="px-4 py-3 text-center text-xs">
										{#if saving[user.email]}
											<span class="text-gray-400">…</span>
										{:else if feedback[user.email] === 'saved'}
											<span class="text-green-600">{$_('admin.saved')}</span>
										{:else if feedback[user.email] === 'error'}
											<span class="text-red-600">{$_('admin.error')}</span>
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}

			<div class="mt-6">
				<LangSwitcher />
			</div>
		</div>
	</div>
{/if}
