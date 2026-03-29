const BASE = import.meta.env.DEV ? 'http://localhost:8080' : '';

async function request(
	path: string,
	options: RequestInit = {},
	raw = false
): Promise<Response> {
	const res = await fetch(`${BASE}${path}`, {
		credentials: 'include',
		...options,
		headers: {
			'Content-Type': 'application/json',
			...options.headers
		}
	});

	if (!raw && res.status === 401 && !window.location.pathname.startsWith('/login')) {
		window.location.href = '/login';
		throw new Error('Unauthorized');
	}

	return res;
}

export const api = {
	get: (path: string) => request(path),
	post: (path: string, body?: unknown) =>
		request(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
	patch: (path: string, body?: unknown) =>
		request(path, { method: 'PATCH', body: body ? JSON.stringify(body) : undefined }),
	put: (path: string, body?: unknown) =>
		request(path, { method: 'PUT', body: body ? JSON.stringify(body) : undefined }),
	delete: (path: string) => request(path, { method: 'DELETE' })
};
