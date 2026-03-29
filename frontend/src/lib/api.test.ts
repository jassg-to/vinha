import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock import.meta.env before importing api
vi.stubEnv('DEV', true);

const { api } = await import('./api');

describe('api', () => {
	let fetchSpy: ReturnType<typeof vi.fn>;

	beforeEach(() => {
		fetchSpy = vi.fn().mockResolvedValue(new Response('{}', { status: 200 }));
		vi.stubGlobal('fetch', fetchSpy);
		// Prevent actual navigation on 401
		Object.defineProperty(window, 'location', {
			value: { pathname: '/dashboard', href: '' },
			writable: true,
			configurable: true
		});
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	it('sends GET requests with credentials and JSON content-type', async () => {
		await api.get('/api/test');

		expect(fetchSpy).toHaveBeenCalledWith('http://localhost:8080/api/test', {
			credentials: 'include',
			headers: { 'Content-Type': 'application/json' }
		});
	});

	it('sends POST requests with a JSON body', async () => {
		await api.post('/api/items', { name: 'Thing' });

		expect(fetchSpy).toHaveBeenCalledWith('http://localhost:8080/api/items', {
			credentials: 'include',
			method: 'POST',
			body: JSON.stringify({ name: 'Thing' }),
			headers: { 'Content-Type': 'application/json' }
		});
	});

	it('sends PATCH requests with a JSON body', async () => {
		await api.patch('/api/items/1', { name: 'Updated' });

		expect(fetchSpy).toHaveBeenCalledWith('http://localhost:8080/api/items/1', {
			credentials: 'include',
			method: 'PATCH',
			body: JSON.stringify({ name: 'Updated' }),
			headers: { 'Content-Type': 'application/json' }
		});
	});

	it('sends PUT requests with a JSON body', async () => {
		await api.put('/api/items/1', { name: 'Replaced' });

		expect(fetchSpy).toHaveBeenCalledWith('http://localhost:8080/api/items/1', {
			credentials: 'include',
			method: 'PUT',
			body: JSON.stringify({ name: 'Replaced' }),
			headers: { 'Content-Type': 'application/json' }
		});
	});

	it('sends DELETE requests', async () => {
		await api.delete('/api/items/1');

		expect(fetchSpy).toHaveBeenCalledWith('http://localhost:8080/api/items/1', {
			credentials: 'include',
			method: 'DELETE',
			headers: { 'Content-Type': 'application/json' }
		});
	});

	it('sends POST with no body when body is omitted', async () => {
		await api.post('/api/trigger');

		expect(fetchSpy).toHaveBeenCalledWith('http://localhost:8080/api/trigger', {
			credentials: 'include',
			method: 'POST',
			body: undefined,
			headers: { 'Content-Type': 'application/json' }
		});
	});

	it('redirects to /login on 401 from a non-login page', async () => {
		fetchSpy.mockResolvedValueOnce(new Response('', { status: 401 }));

		await expect(api.get('/api/me')).rejects.toThrow('Unauthorized');
		expect(window.location.href).toBe('/login');
	});

	it('does NOT redirect on 401 when already on /login', async () => {
		window.location.pathname = '/login';
		fetchSpy.mockResolvedValueOnce(new Response('', { status: 401 }));

		const res = await api.get('/api/me');
		expect(res.status).toBe(401);
	});
});
