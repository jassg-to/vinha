<script lang="ts">
	import '../app.css';
	import { initI18n } from '$lib/i18n';
	import { isLoading } from 'svelte-i18n';
	import { checkAuth } from '$lib/auth.svelte';
	import { onMount } from 'svelte';

	let { children } = $props();

	initI18n();

	onMount(() => {
		checkAuth();
	});
</script>

{#if $isLoading}
	<div class="flex min-h-screen items-center justify-center">
		<p class="text-gray-500">…</p>
	</div>
{:else}
	{@render children()}
{/if}
