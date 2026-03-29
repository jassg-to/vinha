<script lang="ts">
	import { _ } from 'svelte-i18n';

	let { status, type = 'event' }: { status: string; type?: 'event' | 'order' } = $props();

	const colors: Record<string, string> = {
		draft: 'bg-gray-100 text-gray-700',
		open: 'bg-green-100 text-green-700',
		day_of: 'bg-amber-100 text-amber-700',
		closed: 'bg-gray-200 text-gray-500',
		inquiring: 'bg-blue-100 text-blue-700',
		confirmed: 'bg-green-100 text-green-700',
		checked_in: 'bg-emerald-100 text-emerald-700',
		no_show: 'bg-red-100 text-red-700',
		cancelled: 'bg-gray-200 text-gray-500'
	};

	let prefix = $derived(type === 'event' ? 'fr.status' : 'fr.orders.status');
</script>

<span class="inline-block rounded-full px-2.5 py-0.5 text-xs font-medium {colors[status] ?? 'bg-gray-100 text-gray-700'}">
	{$_(`${prefix}.${status}`)}
</span>
