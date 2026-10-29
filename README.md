# Shramik-Nyay

Shramik-Nyay is a voice-led statutory wage redressal studio. The current implementation
provides a deterministic `MOCK_REPLAY` flow so the telemetry console can be developed
without consuming external Gnani credits.

## Run locally

### Backend

```powershell
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

The health endpoint is available at `http://127.0.0.1:8000/health`.

### Frontend

```powershell
cd frontend
npm run dev
```

Open the Vite URL, connect the bridge, and select **Run mock replay** to exercise the
synthetic e-Shram profile, Form-A slots, statutory audit, and Timbre read-back event.

## Modes

- `MOCK_REPLAY` uses synthetic records and local statutory arithmetic.
- `LIVE` is reserved for configured Gnani credentials and endpoint access. Credentials
  remain local in `backend/.env`, which is intentionally ignored by Git.

The Prisma bridge sends only raw mono `pcm_s16le` frames of 1024 bytes at a 64 ms
cadence and supports the documented `update_settings` bias control frame.
