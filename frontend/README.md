# SignFish Frontend

Next.js + Tailwind implementation for a Monkeytype-style sign language racing app powered by TinyFish AI inference.

## Pages
- `/` - Sign race gameplay with webcam input and 30-second timer.
- `/leaderboard` - Global score list with WPM, accuracy, consistency, and date.
- `/settings` - Difficulty preferences (easy/normal/hard).
- `/login` - Email/password login + Google/GitHub OAuth buttons.
- `/register` - Registration form + OAuth options.

## Run
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_TINYFISH_API_URL=http://localhost:8000/api/infer
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
```
