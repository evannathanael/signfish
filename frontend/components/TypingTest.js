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
  const initialPrompt = pickPrompt(difficulty);
  const [currentPrompt, setCurrentPrompt] = useState(initialPrompt);
  const [letterStatuses, setLetterStatuses] = useState(initialPrompt.split('').map(() => 'pending'));
  const [currentLetterIndex, setCurrentLetterIndex] = useState(0);
  const [attempted, setAttempted] = useState(0);
  const [correct, setCorrect] = useState(0);
  const [recentOutcomes, setRecentOutcomes] = useState([]);
  const [status, setStatus] = useState('Click start to begin your 30-second sign race.');
  const { timeLeft, isRunning, start, stop, reset } = useTimer(ROUND_TIME_SECONDS);

  const promptLetters = currentPrompt.split('');
  const windowStart = Math.max(0, Math.min(currentLetterIndex, promptLetters.length - 10));
  const visibleLetters = promptLetters.slice(windowStart, windowStart + 10);

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

      setLetterStatuses((prevStatuses) => {
        const updated = [...prevStatuses];
        if (currentLetterIndex < updated.length) {
          updated[currentLetterIndex] = isCorrect ? 'correct' : 'wrong';
        }
        return updated;
      });

      const nextLetter = currentLetterIndex + 1;
      if (nextLetter >= promptLetters.length) {
        const nextPrompt = pickPrompt(difficulty);
        setCurrentPrompt(nextPrompt);
        setLetterStatuses(nextPrompt.split('').map(() => 'pending'));
        setCurrentLetterIndex(0);
        setStatus(isCorrect ? 'Correct letter! New sign loaded.' : 'Wrong letter. New sign loaded.');
      } else {
        setCurrentLetterIndex(nextLetter);
        setStatus(isCorrect ? 'Correct letter! Move to the next one.' : 'Wrong letter. Try the next letter.');
      }
    } catch {
      setStatus('Inference service unavailable. Showing offline behavior.');
      const offlineCorrect = Math.random() > 0.3;
      if (offlineCorrect) {
        setCorrect((prev) => prev + 1);
      }
      setRecentOutcomes((prev) => [...prev.slice(-19), offlineCorrect ? 100 : 0]);

      setLetterStatuses((prevStatuses) => {
        const updated = [...prevStatuses];
        if (currentLetterIndex < updated.length) {
          updated[currentLetterIndex] = offlineCorrect ? 'correct' : 'wrong';
        }
        return updated;
      });

      const nextLetter = currentLetterIndex + 1;
      if (nextLetter >= promptLetters.length) {
        const nextPrompt = pickPrompt(difficulty);
        setCurrentPrompt(nextPrompt);
        setLetterStatuses(nextPrompt.split('').map(() => 'pending'));
        setCurrentLetterIndex(0);
        setStatus(offlineCorrect ? 'Offline correct. New sign loaded.' : 'Offline wrong. New sign loaded.');
      } else {
        setCurrentLetterIndex(nextLetter);
        setStatus(offlineCorrect ? 'Offline correct. Move to next letter.' : 'Offline wrong. Try the next letter.');
      }
    }
  }

  function handleStart() {
    const newPrompt = pickPrompt(difficulty);
    reset();
    setAttempted(0);
    setCorrect(0);
    setRecentOutcomes([]);
    setCurrentPrompt(newPrompt);
    setLetterStatuses(newPrompt.split('').map(() => 'pending'));
    setCurrentLetterIndex(0);
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
          <div className="mb-4">
            <p className="mb-3 text-lg">Current target sign letters:</p>
            <div className="flex flex-wrap items-center gap-2 text-4xl font-black">
              {visibleLetters.map((letter, idx) => {
                const letterIndex = windowStart + idx;
                const statusClass =
                  letterStatuses[letterIndex] === 'correct'
                    ? 'text-emerald-400'
                    : letterStatuses[letterIndex] === 'wrong'
                    ? 'text-rose-400'
                    : 'text-slate-100';
                return (
                  <span
                    key={`${letter}-${letterIndex}`}
                    className={`${statusClass} inline-block mr-4`}
                  >
                    {letter}
                  </span>
                );
              })}
            </div>
            <p className="mt-2 text-sm text-slate-400">
              Showing {Math.min(10, promptLetters.length)} of {promptLetters.length} letters.
            </p>
          </div>
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
