import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import AuthForm from '../components/AuthForm';

const tabs = [
  { mode: 'login', label: 'Sign in' },
  { mode: 'register', label: 'Create account' }
];

export default function AuthPage() {
  const router = useRouter();
  const [mode, setMode] = useState('login');

  useEffect(() => {
    const queryMode = router.query.mode;
    if (queryMode === 'register' || queryMode === 'login') {
      setMode(queryMode);
    }
  }, [router.query.mode]);

  function handleModeChange(nextMode) {
    setMode(nextMode);
    router.replace(`/login?mode=${nextMode}`, undefined, { shallow: true });
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
      <main className="space-y-6">
        <div className="panel">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-400">SignFish access</p>
          <h1 className="mt-3 text-3xl font-black">One page for login and registration</h1>
          <p className="mt-4 text-slate-300">
            Choose a mode below, then sign in using an account or continue with Google / GitHub.
            This page is now the single entry point for authentication.
          </p>
          <div className="mt-6 flex flex-wrap gap-2 rounded-full bg-slate-900/90 p-1">
            {tabs.map((tab) => (
              <button
                key={tab.mode}
                type="button"
                onClick={() => handleModeChange(tab.mode)}
                className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                  mode === tab.mode
                    ? 'bg-neon text-ink shadow-lg'
                    : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <AuthForm mode={mode} />
      </main>

      <aside className="space-y-4">
        <div className="panel">
          <h2 className="text-xl font-semibold">Sign language ready</h2>
          <p className="mt-3 text-slate-300">
            Use this area to connect your sign detection flow and webcam feed. The app is now designed
            to hold authentication and sign language practice in one place.
          </p>
          <ul className="mt-4 space-y-3 text-sm text-slate-300">
            <li>• Add camera sign recognition here.</li>
            <li>• Link sign targets to typing and inference rounds.</li>
            <li>• Keep authentication simple with one form.</li>
          </ul>
        </div>

        <div className="panel bg-slate-900/90">
          <h3 className="text-lg font-semibold">How to start</h3>
          <ol className="mt-4 space-y-2 text-sm text-slate-300">
            <li>1. Select sign in or create account.</li>
            <li>2. Enter credentials or use social login.</li>
            <li>3. Return to the dashboard to begin sign practice.</li>
          </ol>
        </div>
      </aside>
    </div>
  );
}
