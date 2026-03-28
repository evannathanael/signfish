export default function StatsPanel({ wpm, accuracy, consistency, correct, attempted, timeLeft }) {
  return (
    <div className="panel">
      <h3 className="mb-3 text-lg font-semibold">Live Stats</h3>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <p>Time Left</p>
        <p className="text-right font-semibold">{timeLeft}s</p>
        <p>WPM</p>
        <p className="text-right font-semibold">{wpm}</p>
        <p>Accuracy</p>
        <p className="text-right font-semibold">{accuracy}%</p>
        <p>Consistency</p>
        <p className="text-right font-semibold">{consistency}%</p>
        <p>Correct</p>
        <p className="text-right font-semibold">{correct}</p>
        <p>Attempted</p>
        <p className="text-right font-semibold">{attempted}</p>
      </div>
    </div>
  );
}
