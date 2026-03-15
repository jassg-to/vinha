import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
	apiKey: 'AIzaSyAgmrIxSjoPNrQjjF61hSb9Y6KbGIis39k',
	authDomain: 'e-vinha-test.web.app',
	projectId: 'e-vinha-test'
};

const app = initializeApp(firebaseConfig);
export const firebaseAuth = getAuth(app);
