import { defineConfig } from '@playwright/test';

export default defineConfig({
	testDir: './e2e',
	webServer: {
		command: 'E2E_COVERAGE=true npm run dev',
		port: 5173,
		reuseExistingServer: true
	},
	use: {
		baseURL: 'http://localhost:5173'
	}
});
