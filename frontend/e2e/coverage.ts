import { test as base } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const COVERAGE_DIR = path.resolve('coverage/e2e');

export const test = base.extend({
	page: async ({ page }, use) => {
		await use(page);

		// Wait up to 2s for instrumented modules to populate __coverage__
		const coverage = await page.evaluate(() =>
			new Promise((resolve) => {
				let attempts = 0;
				const poll = () => {
					if ((window as any).__coverage__) {
						resolve((window as any).__coverage__);
					} else if (attempts++ < 20) {
						setTimeout(poll, 100);
					} else {
						resolve(null);
					}
				};
				poll();
			})
		).catch(() => null);

		if (coverage) {
			fs.mkdirSync(COVERAGE_DIR, { recursive: true });
			const id = crypto.randomUUID();
			fs.writeFileSync(
				path.join(COVERAGE_DIR, `${id}.json`),
				JSON.stringify(coverage)
			);
			console.log(`Coverage saved: ${Object.keys(coverage as any).length} files`);
		} else {
			console.log('No coverage data collected for this test');
		}
	}
});

export { expect } from '@playwright/test';
