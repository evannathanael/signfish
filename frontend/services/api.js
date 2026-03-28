import { API_BASE_URL, TINYFISH_API_URL } from '../utils/constants';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || 'Request failed');
  }

  return response.json();
}

export async function inferSign(frameBase64, expectedSign) {
  const response = await fetch(TINYFISH_API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ frame: frameBase64, expectedSign })
  });

  if (!response.ok) {
    throw new Error('TinyFish inference failed');
  }

  return response.json();
}

export function fetchLeaderboard() {
  return request('/leaderboard');
}

export function submitScore(payload) {
  return request('/leaderboard', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export function fetchUserSettings() {
  return request('/settings');
}

export function saveUserSettings(payload) {
  return request('/settings', {
    method: 'PUT',
    body: JSON.stringify(payload)
  });
}
