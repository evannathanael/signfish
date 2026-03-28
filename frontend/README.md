# SignFish Frontend (trimmed)

This repository currently keeps frontend documentation only.

## Integration contract with backend
1. Capture webcam image from the active browser camera.
2. Send `POST /api/infer` with:
   - `frame` (base64 image payload)
   - `question` (target sign letter)
3. Consume backend response fields:
   - `predicted_letter`
   - `expected_letter`
   - `match`
   - `confidence`

## Notes
- Frontend app scaffold files (AuthForm/pages/hooks/services/components) were intentionally removed per latest request.
- If you want the UI restored, regenerate a minimal Next.js app and wire it to the backend contract above.
