import { useState } from 'react';
import SettingsMenu from '../components/SettingsMenu';
import TypingTest from '../components/TypingTest';
import { DEFAULT_DIFFICULTY } from '../utils/constants';

export default function HomePage() {
  const [difficulty, setDifficulty] = useState(DEFAULT_DIFFICULTY);

  return (
    <div className="space-y-4">
      <SettingsMenu difficulty={difficulty} onChange={setDifficulty} />
      <TypingTest difficulty={difficulty} />
    </div>
  );
}
