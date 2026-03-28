import { useEffect } from 'react';
import { useWebcam } from '../hooks/useWebcam';

const LIVE_CAPTURE_INTERVAL_MS = 900;

export default function Webcam({ onFrameCapture, disabled }) {
  const { videoRef, captureFrame, error } = useWebcam();

  useEffect(() => {
    if (disabled || !onFrameCapture) return undefined;

    const intervalId = setInterval(() => {
      onFrameCapture(captureFrame());
    }, LIVE_CAPTURE_INTERVAL_MS);

    return () => clearInterval(intervalId);
  }, [captureFrame, disabled, onFrameCapture]);

  return (
    <div className="panel space-y-3">
      <h3 className="text-lg font-semibold">Webcam Input</h3>
      <video ref={videoRef} autoPlay muted playsInline className="w-full rounded-lg border border-slate-700" />
      <p className="text-sm text-slate-300">
        {disabled
          ? 'Start a round to enable live sign recognition.'
          : 'Live sign recognition is running. Hold each gesture briefly in frame.'}
      </p>
      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  );
}
