import { useCallback, useEffect, useRef, useState } from 'react';

export function useTimer(initialSeconds = 30) {
  const [timeLeft, setTimeLeft] = useState(initialSeconds);
  const [isRunning, setIsRunning] = useState(false);
  const onCompleteRef = useRef(null);

  const start = useCallback((onComplete) => {
    onCompleteRef.current = onComplete || null;
    setTimeLeft(initialSeconds);
    setIsRunning(true);
  }, [initialSeconds]);

  const stop = useCallback(() => {
    setIsRunning(false);
  }, []);

  const reset = useCallback(() => {
    setIsRunning(false);
    setTimeLeft(initialSeconds);
  }, [initialSeconds]);

  useEffect(() => {
    if (!isRunning || timeLeft <= 0) return;

    const id = setTimeout(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);

    return () => clearTimeout(id);
  }, [isRunning, timeLeft]);

  useEffect(() => {
    if (isRunning && timeLeft <= 0) {
      setIsRunning(false);
      onCompleteRef.current?.();
    }
  }, [isRunning, timeLeft]);

  return { timeLeft, isRunning, start, stop, reset };
}
