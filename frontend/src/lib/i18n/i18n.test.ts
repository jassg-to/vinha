import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('detectLocale', () => {
	beforeEach(() => {
		localStorage.clear();
		vi.resetModules();
	});

	it('returns saved locale from localStorage when valid', async () => {
		localStorage.setItem('locale', 'pt-BR');

		// Re-import to pick up fresh localStorage
		vi.doMock('svelte-i18n', () => ({
			register: vi.fn(),
			init: vi.fn(),
			getLocaleFromNavigator: vi.fn(() => 'en-CA'),
			locale: { subscribe: vi.fn() }
		}));

		const { initI18n } = await import('./index');
		const { init } = await import('svelte-i18n');
		initI18n();

		expect(init).toHaveBeenCalledWith(
			expect.objectContaining({ initialLocale: 'pt-BR' })
		);
	});

	it('falls back to pt-BR when navigator locale is unsupported', async () => {
		vi.doMock('svelte-i18n', () => ({
			register: vi.fn(),
			init: vi.fn(),
			getLocaleFromNavigator: vi.fn(() => 'de-DE'),
			locale: { subscribe: vi.fn() }
		}));

		const { initI18n } = await import('./index');
		const { init } = await import('svelte-i18n');
		initI18n();

		expect(init).toHaveBeenCalledWith(
			expect.objectContaining({ initialLocale: 'pt-BR' })
		);
	});

	it('detects pt-BR from a navigator locale starting with pt', async () => {
		vi.doMock('svelte-i18n', () => ({
			register: vi.fn(),
			init: vi.fn(),
			getLocaleFromNavigator: vi.fn(() => 'pt-PT'),
			locale: { subscribe: vi.fn() }
		}));

		const { initI18n } = await import('./index');
		const { init } = await import('svelte-i18n');
		initI18n();

		expect(init).toHaveBeenCalledWith(
			expect.objectContaining({ initialLocale: 'pt-BR' })
		);
	});
});
