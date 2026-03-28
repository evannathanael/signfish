import {
  createUserWithEmailAndPassword,
  getAuth,
  GithubAuthProvider,
  GoogleAuthProvider,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut
} from 'firebase/auth';
import { initializeApp } from 'firebase/app';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID
};

let auth;

if (
  firebaseConfig.apiKey &&
  firebaseConfig.authDomain &&
  firebaseConfig.projectId &&
  firebaseConfig.appId
) {
  const app = initializeApp(firebaseConfig);
  auth = getAuth(app);
}

function requireAuth() {
  if (!auth) {
    throw new Error(
      'Firebase auth is not initialized. Set NEXT_PUBLIC_FIREBASE_API_KEY, NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN, NEXT_PUBLIC_FIREBASE_PROJECT_ID, and NEXT_PUBLIC_FIREBASE_APP_ID.'
    );
  }
}

export function registerWithEmail(email, password) {
  requireAuth();
  return createUserWithEmailAndPassword(auth, email, password);
}

export function loginWithEmail(email, password) {
  requireAuth();
  return signInWithEmailAndPassword(auth, email, password);
}

export function loginWithGoogle() {
  requireAuth();
  return signInWithPopup(auth, new GoogleAuthProvider());
}

export function loginWithGithub() {
  requireAuth();
  return signInWithPopup(auth, new GithubAuthProvider());
}

export function logout() {
  requireAuth();
  return signOut(auth);
}
