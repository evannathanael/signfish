export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
export const TINYFISH_API_URL = process.env.NEXT_PUBLIC_TINYFISH_API_URL || `${API_BASE_URL}/api/infer`;

export const DIFFICULTY_LEVELS = {
  EASY: 'easy',
  NORMAL: 'normal',
  HARD: 'hard'
};

export const DEFAULT_DIFFICULTY = DIFFICULTY_LEVELS.NORMAL;
export const ROUND_TIME_SECONDS = 30;

export const PROMPTS_BY_DIFFICULTY = {
  easy: ['hello', 'thanks', 'yes', 'no', 'please'],
  normal: ['morning', 'friend', 'school', 'water', 'family'],
  hard: ['community', 'understand', 'responsibility', 'communication', 'opportunity']
};
