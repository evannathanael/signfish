import { useWebcam } from '../hooks/useWebcam';

export default function Webcam({ onFrameCapture, disabled }) {
  const { videoRef, captureFrame, error } = useWebcam();

  return (
    <div className="panel space-y-3">
      <h3 className="text-lg font-semibold">Webcam Input</h3>
      <video ref={videoRef} autoPlay muted playsInline className="w-full rounded-lg border border-slate-700" />
      <button
        type="button"
        onClick={() => onFrameCapture?.(captureFrame())}
        disabled={disabled}
        className="rounded-md bg-neon px-3 py-2 text-sm font-semibold text-ink disabled:opacity-40"
      >
        Capture sign frame
      </button>
      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  );
}
