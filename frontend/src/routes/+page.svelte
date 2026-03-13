<script lang="ts">
	import { _ } from 'svelte-i18n';
	import { getAuth, logout } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import LangSwitcher from '$lib/components/LangSwitcher.svelte';

	const auth = getAuth();

	$effect(() => {
		if (auth.checked && !auth.user) {
			goto('/login');
		}
	});
</script>

{#if auth.loading}
	<div class="flex min-h-screen items-center justify-center">
		<p class="text-gray-500">{$_('dashboard.loading')}</p>
	</div>
{:else if auth.user}
	<div class="flex min-h-screen flex-col items-center justify-center gap-6">
		{#if auth.user.picture}
			<img
				src={auth.user.picture}
				alt={auth.user.name}
				class="h-20 w-20 rounded-full"
			/>
		{/if}
		<h1 class="text-2xl font-bold">{$_('dashboard.welcome', { values: { name: auth.user.name } })}</h1>
		<p class="text-gray-600">{auth.user.email}</p>
		<div class="flex gap-3">
			{#if auth.user.is_admin}
				<a
					href="/admin"
					class="rounded bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200"
				>
					{$_('nav.admin')}
				</a>
			{/if}
			<button
				onclick={() => logout()}
				class="rounded bg-primary px-4 py-2 text-white hover:bg-primary-dark"
			>
				{$_('dashboard.logout')}
			</button>
		</div>
		<LangSwitcher />
	</div>
{/if}
