import { useState } from 'react';
import SettingsMenu from '../components/SettingsMenu';
import TypingTest from '../components/TypingTest';
import { DEFAULT_DIFFICULTY } from '../utils/constants';

export default function HomePage() {
  const [difficulty, setDifficulty] = useState(DEFAULT_DIFFICULTY);

  return (
    <div className="space-y-6">
      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <div className="panel">
            <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-slate-400">Training</p>
                <h2 className="mt-2 text-2xl font-bold">Sign recognition race</h2>
              </div>
              <div className="rounded-full bg-slate-900/90 px-4 py-2 text-sm text-slate-300">
                Current difficulty: <span className="font-semibold capitalize">{difficulty}</span>
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-3xl border border-slate-700 bg-slate-950/80 p-4">
                <p className="text-sm text-slate-400">Use the controls below to start and stop rounds.</p>
              </div>
              <div className="rounded-3xl border border-slate-700 bg-slate-950/80 p-4">
                <p className="text-sm text-slate-400">The right column shows live stats while you practice.</p>
              </div>
            </div>
          </div>

          <SettingsMenu difficulty={difficulty} onChange={setDifficulty} />
          <TypingTest difficulty={difficulty} />
        </div>

        <aside className="space-y-6">
          <div className="panel">
            <h3 className="text-xl font-semibold">Sign Language Guide</h3>
            <ul className="mt-4 space-y-3 text-sm text-slate-300">
              <li>• Focus on clear hand shape and movement.</li>
              <li>• Keep your palm visible to the camera.</li>
              <li>• Match each prompt with the corresponding sign.</li>
              <li>• Review recognition feedback after each round.</li>
            </ul>
          </div>

          <div className="panel bg-slate-900/90">
            <h3 className="text-xl font-semibold">Implementation space</h3>
            <p className="mt-3 text-slate-300">
              This dashboard is structured to accept sign detection components, additional camera widgets,
              and training modules. Use this area for your next sign language feature.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}
