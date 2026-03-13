<script lang="ts">
	import { getAuth, logout } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';

	const auth = getAuth();

	$effect(() => {
		if (auth.checked && !auth.user) {
			goto('/login');
		}
	});
</script>

{#if auth.loading}
	<div class="flex min-h-screen items-center justify-center">
		<p class="text-gray-500">Loading...</p>
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
		<h1 class="text-2xl font-bold">Welcome, {auth.user.name}</h1>
		<p class="text-gray-600">{auth.user.email}</p>
		<button
			onclick={() => logout()}
			class="rounded bg-primary px-4 py-2 text-white hover:bg-primary-dark"
		>
			Logout
		</button>
	</div>
{/if}
