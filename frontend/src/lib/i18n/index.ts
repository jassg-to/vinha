import { register, init, getLocaleFromNavigator, locale } from 'svelte-i18n';

register('en-CA', () => import('./en-CA.json'));
register('pt-BR', () => import('./pt-BR.json'));

const SUPPORTED = ['en-CA', 'pt-BR'];

function detectLocale(): string {
	const nav = getLocaleFromNavigator() ?? 'en-CA';
	return (
		SUPPORTED.find((l) => nav === l) ??
		SUPPORTED.find((l) => nav.startsWith(l.split('-')[0])) ??
		'en-CA'
	);
}

export function initI18n() {
	init({
		fallbackLocale: 'en-CA',
		initialLocale: detectLocale()
	});

	locale.subscribe((l) => {
		if (l) document.documentElement.lang = l;
	});
}
