import { execSync } from 'child_process';
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

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
	plugins: [tailwindcss(), sveltekit()],
	define: {
		__REPO_URL__: JSON.stringify(getRepoUrl())
	}
});
