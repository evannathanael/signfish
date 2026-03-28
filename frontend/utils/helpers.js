export function calculateAccuracy(correct, attempted) {
  if (!attempted) return 100;
  return Math.max(0, Math.round((correct / attempted) * 100));
}

export function calculateWpm(correctSigns, elapsedSeconds) {
  if (!elapsedSeconds) return 0;
  return Math.round((correctSigns / elapsedSeconds) * 60);
}

export function calculateConsistency(results) {
  if (!results.length) return 100;
  const avg = results.reduce((acc, value) => acc + value, 0) / results.length;
  const variance =
    results.reduce((acc, value) => acc + (value - avg) ** 2, 0) / Math.max(1, results.length);
  return Math.max(0, Math.round(100 - Math.sqrt(variance)));
}

export function formatDate(isoDate) {
  return new Date(isoDate).toLocaleDateString();
}
