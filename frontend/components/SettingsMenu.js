import { DIFFICULTY_LEVELS } from '../utils/constants';

const options = Object.values(DIFFICULTY_LEVELS);

export default function SettingsMenu({ difficulty, onChange }) {
  return (
    <div className="panel">
      <h3 className="mb-2 text-lg font-semibold">Difficulty</h3>
      <p className="mb-4 text-sm text-slate-300">Normal matches Monkeytype style defaults.</p>
      <div className="flex gap-2">
        {options.map((level) => (
          <button
            key={level}
            type="button"
            onClick={() => onChange(level)}
            className={`rounded-md px-3 py-2 text-sm font-medium capitalize ${
              level === difficulty ? 'bg-mint text-ink' : 'bg-slate-800 text-slate-100'
            }`}
          >
            {level}
          </button>
        ))}
      </div>
    </div>
  );
}
