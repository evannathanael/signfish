import { useState } from 'react';
import { loginWithEmail, loginWithGithub, loginWithGoogle, registerWithEmail } from '../services/auth';
import { isStrongPassword, isValidEmail } from '../utils/validators';

export default function AuthForm({ mode = 'login' }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    setError('');

    if (!isValidEmail(email)) {
      setError('Please enter a valid email.');
      return;
    }

    if (mode === 'register' && !isStrongPassword(password)) {
      setError('Password needs 8+ chars, one uppercase letter, and one number.');
      return;
    }

    setLoading(true);
    try {
      if (mode === 'register') {
        await registerWithEmail(email, password);
      } else {
        await loginWithEmail(email, password);
      }
    } catch (err) {
      setError(err.message || 'Authentication failed.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel max-w-md">
      <h2 className="mb-4 text-xl font-bold capitalize">{mode}</h2>
      <form className="space-y-3" onSubmit={onSubmit}>
        <input
          className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2"
          type="email"
          placeholder="Email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
        <input
          className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-neon px-3 py-2 font-semibold text-ink disabled:opacity-50"
        >
          {loading ? 'Please wait...' : mode === 'register' ? 'Create account' : 'Sign in'}
        </button>
      </form>
      <div className="mt-4 grid grid-cols-2 gap-2">
        <button
          type="button"
          className="rounded-md bg-slate-700 px-3 py-2 text-sm"
          onClick={loginWithGoogle}
        >
          Continue with Google
        </button>
        <button
          type="button"
          className="rounded-md bg-slate-700 px-3 py-2 text-sm"
          onClick={loginWithGithub}
        >
          Continue with GitHub
        </button>
      </div>
      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
    </div>
  );
}
