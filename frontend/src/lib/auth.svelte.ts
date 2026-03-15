import { signOut } from 'firebase/auth';
import { firebaseAuth } from './firebase';
import { api } from './api';

interface User {
	email: string;
	name: string;
	picture: string;
	is_admin: boolean;
	sections: Record<string, string>;
}

let user = $state<User | null>(null);
let loading = $state(true);
let checked = $state(false);

export function getAuth() {
	return {
		get user() {
			return user;
		},
		get loading() {
			return loading;
		},
		get checked() {
			return checked;
		}
	};
}

export async function checkAuth(): Promise<void> {
	try {
		const res = await api.get('/api/auth/me');
		if (res.ok) {
			user = await res.json();
		} else {
			user = null;
		}
	} catch {
		user = null;
	} finally {
		loading = false;
		checked = true;
	}
}

export async function logout(): Promise<void> {
	await api.post('/api/auth/logout');
	await signOut(firebaseAuth);
	user = null;
	window.location.href = '/login';
}
