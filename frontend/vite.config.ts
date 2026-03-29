import { execSync } from 'child_process';
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import istanbul from 'vite-plugin-istanbul';

function getRepoUrl(): string {
	try {
		const remote = execSync('git remote get-url origin', { encoding: 'utf-8' }).trim();
		if (remote.startsWith('git@')) {
			return remote.replace(/^git@([^:]+):/, 'https://$1');
		}
		return remote.replace(/\.git$/, '');
	} catch {
		throw new Error(
			'Could not determine repository URL from git remote. ' +
			'AGPL-3.0 requires a source code link. Set a git remote or define REPO_URL env var.'
		);
	}
}

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit(),
		...(process.env.E2E_COVERAGE
			? [
					istanbul({
						include: 'src/**/*',
						exclude: ['node_modules', 'src/tests/**', 'e2e/**'],
						requireEnv: false,
						checkProd: false
					})
				]
			: [])
	],
	define: {
		__REPO_URL__: JSON.stringify(getRepoUrl())
	},
	resolve: process.env.VITEST
		? { conditions: ['browser'] }
		: undefined,
	test: {
		environment: 'jsdom',
		setupFiles: ['./src/tests/setup.ts'],
		include: ['src/**/*.test.ts'],
		alias: {
			$lib: new URL('./src/lib', import.meta.url).pathname
		},
		coverage: {
			include: ['src/lib/**', 'src/routes/**'],
			exclude: ['src/tests/**'],
			reporter: ['json', 'text'],
			reportsDirectory: 'coverage/unit'
		}
	}
});
