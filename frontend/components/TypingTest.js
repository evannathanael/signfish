import { useMemo, useState } from 'react';
import Webcam from './Webcam';
import StatsPanel from './StatsPanel';
import { useTimer } from '../hooks/useTimer';
import { inferSign, submitScore } from '../services/api';
import {
  DEFAULT_DIFFICULTY,
  PROMPTS_BY_DIFFICULTY,
  ROUND_TIME_SECONDS
} from '../utils/constants';
import { calculateAccuracy, calculateConsistency, calculateWpm } from '../utils/helpers';

function pickPrompt(difficulty) {
  const list = PROMPTS_BY_DIFFICULTY[difficulty] || PROMPTS_BY_DIFFICULTY[DEFAULT_DIFFICULTY];
  return list[Math.floor(Math.random() * list.length)];
}

export default function TypingTest({ difficulty = DEFAULT_DIFFICULTY }) {
  const [currentPrompt, setCurrentPrompt] = useState(() => pickPrompt(difficulty));
  const [attempted, setAttempted] = useState(0);
  const [correct, setCorrect] = useState(0);
  const [recentOutcomes, setRecentOutcomes] = useState([]);
  const [status, setStatus] = useState('Click start to begin your 30-second sign race.');
  const { timeLeft, isRunning, start, stop, reset } = useTimer(ROUND_TIME_SECONDS);

  const wpm = useMemo(
    () => calculateWpm(correct, ROUND_TIME_SECONDS - timeLeft),
    [correct, timeLeft]
  );
  const accuracy = useMemo(() => calculateAccuracy(correct, attempted), [correct, attempted]);
  const consistency = useMemo(() => calculateConsistency(recentOutcomes), [recentOutcomes]);

  async function finishRound() {
    setStatus('Round finished. Saving your score...');
    try {
      await submitScore({ wpm, accuracy, consistency, mode: difficulty, date: new Date().toISOString() });
      setStatus('Score saved. Start another round anytime.');
    } catch {
      setStatus('Round complete. Could not save score (backend unavailable).');
    }
  }

  async function handleFrameCapture(frameBase64) {
    if (!isRunning || !frameBase64) return;

    setAttempted((prev) => prev + 1);

    try {
      const result = await inferSign(frameBase64, currentPrompt);
      const isCorrect = Boolean(result?.match);
      if (isCorrect) {
        setCorrect((prev) => prev + 1);
      }
      setRecentOutcomes((prev) => [...prev.slice(-19), isCorrect ? 100 : 0]);
      setCurrentPrompt(pickPrompt(difficulty));
      setStatus(isCorrect ? 'Correct sign recognized!' : 'Not quite. Try the next sign.');
    } catch {
      setStatus('Inference service unavailable. Showing offline behavior.');
      const offlineCorrect = Math.random() > 0.3;
      if (offlineCorrect) {
        setCorrect((prev) => prev + 1);
      }
      setRecentOutcomes((prev) => [...prev.slice(-19), offlineCorrect ? 100 : 0]);
      setCurrentPrompt(pickPrompt(difficulty));
    }
  }

  function handleStart() {
    reset();
    setAttempted(0);
    setCorrect(0);
    setRecentOutcomes([]);
    setCurrentPrompt(pickPrompt(difficulty));
    setStatus('Round started. Show the sign in front of your webcam.');
    start(finishRound);
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
      <div className="space-y-4">
        <div className="panel">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-2xl font-bold">Sign Race</h2>
            <button
              type="button"
              onClick={isRunning ? stop : handleStart}
              className="rounded-md bg-mint px-4 py-2 text-sm font-semibold text-ink"
            >
              {isRunning ? 'Pause' : 'Start 30s round'}
            </button>
          </div>
          <p className="mb-2 text-sm text-slate-300">Difficulty: <span className="capitalize">{difficulty}</span></p>
          <p className="mb-4 text-lg">Current target sign: <span className="font-bold text-neon">{currentPrompt}</span></p>
          <p className="text-sm text-slate-300">{status}</p>
        </div>
        <Webcam onFrameCapture={handleFrameCapture} disabled={!isRunning} />
      </div>

      <StatsPanel
        wpm={wpm}
        accuracy={accuracy}
        consistency={consistency}
        correct={correct}
        attempted={attempted}
        timeLeft={timeLeft}
      />
    </div>
  );
}
