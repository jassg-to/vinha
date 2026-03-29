<script lang="ts">
	let { label, value, sub = '' }: { label: string; value: string | number; sub?: string } = $props();
</script>

<div class="rounded-lg border border-gray-200 bg-white p-4">
	<p class="text-sm text-gray-500">{label}</p>
	<p class="mt-1 text-2xl font-bold">{value}</p>
	{#if sub}
		<p class="mt-0.5 text-xs text-gray-400">{sub}</p>
	{/if}
</div>
