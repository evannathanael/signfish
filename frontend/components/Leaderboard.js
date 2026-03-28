import { formatDate } from '../utils/helpers';

export default function Leaderboard({ rows = [], loading, error }) {
  return (
    <div className="panel overflow-x-auto">
      <h2 className="mb-4 text-xl font-bold">Global Leaderboard</h2>
      {loading && <p className="text-sm text-slate-300">Loading leaderboard...</p>}
      {error && <p className="text-sm text-red-400">{error}</p>}
      {!loading && !rows.length && <p className="text-sm text-slate-300">No scores yet.</p>}
      {!!rows.length && (
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 text-left text-slate-300">
              <th className="py-2">Player</th>
              <th>WPM</th>
              <th>Accuracy</th>
              <th>Consistency</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.username}-${row.date}`} className="border-b border-slate-800">
                <td className="py-2">{row.username}</td>
                <td>{row.wpm}</td>
                <td>{row.accuracy}%</td>
                <td>{row.consistency}%</td>
                <td>{formatDate(row.date)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
