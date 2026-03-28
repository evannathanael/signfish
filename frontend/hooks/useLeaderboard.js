import { useCallback, useEffect, useState } from 'react';
import { fetchLeaderboard } from '../services/api';

export function useLeaderboard() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchLeaderboard();
      setRows(data?.rows || []);
    } catch (err) {
      setError(err.message || 'Unable to load leaderboard');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { rows, loading, error, refresh };
}
