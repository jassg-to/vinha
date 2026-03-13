<script lang="ts">
	import '../app.css';
	import { checkAuth } from '$lib/auth.svelte';
	import { onMount } from 'svelte';

	let { children } = $props();

	onMount(() => {
		checkAuth();
	});
</script>

{@render children()}
