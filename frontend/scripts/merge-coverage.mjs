import fs from 'fs';
import path from 'path';

const coverageDir = 'coverage';
const unitFile = path.join(coverageDir, 'unit', 'coverage-final.json');
const e2eDir = path.join(coverageDir, 'e2e');
const outDir = path.join(coverageDir, 'merged');

const merged = {};

// Load unit coverage (v8 format via vitest)
if (fs.existsSync(unitFile)) {
	const unit = JSON.parse(fs.readFileSync(unitFile, 'utf-8'));
	Object.assign(merged, unit);
	console.log(`Unit: ${Object.keys(unit).length} files`);
}

// Load and merge E2E coverage (Istanbul format)
if (fs.existsSync(e2eDir)) {
	const e2eFiles = fs.readdirSync(e2eDir).filter((f) => f.endsWith('.json'));
	for (const file of e2eFiles) {
		const data = JSON.parse(fs.readFileSync(path.join(e2eDir, file), 'utf-8'));
		for (const [filePath, fileCov] of Object.entries(data)) {
			if (!merged[filePath]) {
				merged[filePath] = fileCov;
			} else {
				// Merge statement, branch, and function counters
				const existing = merged[filePath];
				for (const [key, count] of Object.entries(fileCov.s ?? {})) {
					existing.s[key] = (existing.s[key] ?? 0) + count;
				}
				for (const [key, count] of Object.entries(fileCov.f ?? {})) {
					existing.f[key] = (existing.f[key] ?? 0) + count;
				}
				for (const [key, counts] of Object.entries(fileCov.b ?? {})) {
					if (!existing.b[key]) {
						existing.b[key] = counts;
					} else {
						existing.b[key] = existing.b[key].map((v, i) => v + (counts[i] ?? 0));
					}
				}
			}
		}
	}
	console.log(`E2E: ${e2eFiles.length} coverage files`);
}

fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, 'coverage-final.json'), JSON.stringify(merged));
console.log(`Merged: ${Object.keys(merged).length} files → ${outDir}/coverage-final.json`);
