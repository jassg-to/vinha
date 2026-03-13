<script lang="ts">
	import { locale } from 'svelte-i18n';

	function toggle() {
		locale.set($locale === 'pt-BR' ? 'en-CA' : 'pt-BR');
	}
</script>

<button onclick={toggle} class="cursor-pointer text-sm text-gray-400 hover:text-gray-600">
	{$locale === 'pt-BR' ? 'EN' : 'PT'}
</button>
