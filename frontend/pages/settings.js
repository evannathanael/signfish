import { useEffect, useState } from 'react';
import SettingsMenu from '../components/SettingsMenu';
import { saveUserSettings } from '../services/api';
import { DEFAULT_DIFFICULTY } from '../utils/constants';

export default function SettingsPage() {
  const [difficulty, setDifficulty] = useState(DEFAULT_DIFFICULTY);
  const [status, setStatus] = useState('');

  useEffect(() => {
    setStatus('');
  }, [difficulty]);

  async function persistSettings() {
    try {
      await saveUserSettings({ difficulty });
      setStatus('Settings saved.');
    } catch {
      setStatus('Could not save settings (backend unavailable).');
    }
  }

  return (
    <div className="space-y-4">
      <SettingsMenu difficulty={difficulty} onChange={setDifficulty} />
      <button
        type="button"
        onClick={persistSettings}
        className="rounded-md bg-mint px-4 py-2 text-sm font-semibold text-ink"
      >
        Save preferences
      </button>
      {status && <p className="text-sm text-slate-300">{status}</p>}
    </div>
  );
}
