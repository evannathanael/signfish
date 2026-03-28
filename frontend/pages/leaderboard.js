import Leaderboard from '../components/Leaderboard';
import { useLeaderboard } from '../hooks/useLeaderboard';

export default function LeaderboardPage() {
  const { rows, loading, error } = useLeaderboard();

  return <Leaderboard rows={rows} loading={loading} error={error} />;
}
