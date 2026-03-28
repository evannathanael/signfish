import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
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

const MIN_INFERENCE_CONFIDENCE = 0.8;
const MIN_SCORING_INTERVAL_MS = 1200;

function pickPrompt(difficulty) {
  const list = PROMPTS_BY_DIFFICULTY[difficulty] || PROMPTS_BY_DIFFICULTY[DEFAULT_DIFFICULTY];
  return list[Math.floor(Math.random() * list.length)];
}

export default function TypingTest({ difficulty = DEFAULT_DIFFICULTY }) {
  const fallbackPrompt =
    PROMPTS_BY_DIFFICULTY[difficulty]?.[0] || PROMPTS_BY_DIFFICULTY[DEFAULT_DIFFICULTY][0];
  const [currentPrompt, setCurrentPrompt] = useState(fallbackPrompt);
  const [letterStatuses, setLetterStatuses] = useState(fallbackPrompt.split('').map(() => 'pending'));
  const [currentLetterIndex, setCurrentLetterIndex] = useState(0);
  const [attempted, setAttempted] = useState(0);
  const [correct, setCorrect] = useState(0);
  const [recentOutcomes, setRecentOutcomes] = useState([]);
  const [status, setStatus] = useState('Click start to begin your 30-second sign race.');
  const { timeLeft, isRunning, start, reset } = useTimer(ROUND_TIME_SECONDS);
  const isInferencingRef = useRef(false);
  const lastScoredAtRef = useRef(0);

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

  const handleFrameCapture = useCallback(async (frameBase64) => {
    if (!isRunning || !frameBase64) return;
    if (isInferencingRef.current) return;

    isInferencingRef.current = true;

    try {
      const result = await inferSign(frameBase64, currentPrompt);
      const confidence = Number(result?.confidence || 0);
      const predictedLetter = String(result?.predicted_letter || '').trim();
      const now = Date.now();

      if (!predictedLetter || confidence < MIN_INFERENCE_CONFIDENCE) {
        setStatus('No confident sign detected yet. Hold your gesture steady for a moment.');
        return;
      }

      if (now - lastScoredAtRef.current < MIN_SCORING_INTERVAL_MS) {
        return;
      }
      lastScoredAtRef.current = now;

      setAttempted((prev) => prev + 1);
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
      setStatus('Inference service unavailable. Waiting for model connection...');
    } finally {
      isInferencingRef.current = false;
    }
  }, [currentLetterIndex, currentPrompt, difficulty, isRunning, promptLetters.length]);

  function handleStart() {
    if (isRunning) return;

    const newPrompt = pickPrompt(difficulty);
    reset();
    setAttempted(0);
    setCorrect(0);
    setRecentOutcomes([]);
    setCurrentPrompt(newPrompt);
    setLetterStatuses(newPrompt.split('').map(() => 'pending'));
    setCurrentLetterIndex(0);
    lastScoredAtRef.current = 0;
    setStatus('Round started. Show the sign in front of your webcam.');
    start(finishRound);
  }

  useEffect(() => {
    const newPrompt = pickPrompt(difficulty);
    setCurrentPrompt(newPrompt);
    setLetterStatuses(newPrompt.split('').map(() => 'pending'));
    setCurrentLetterIndex(0);
    setStatus(`Difficulty changed to ${difficulty}. New target loaded.`);
  }, [difficulty]);

  return (
    <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
      <div className="space-y-4">
        <div className="panel">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-2xl font-bold">Sign Race</h2>
            <button
              type="button"
              onClick={handleStart}
              disabled={isRunning}
              className={`rounded-md bg-mint px-4 py-2 text-sm font-semibold text-ink ${isRunning ? 'cursor-not-allowed opacity-50' : ''}`}
            >
              Start 30s round
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
