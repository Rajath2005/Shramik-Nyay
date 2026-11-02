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

Open the Vite URL, connect the bridge, and select **Run sample claim** to exercise the
synthetic worker profile, transcript, claim details, statutory checks, and read-back in the
four-panel studio. Select **Prepare draft PDF and JSON** to create downloadable claim
artifacts; this demo does not file anything with SAMADHAN.

Use the language selector to choose automatic detection or Hindi, Kannada, or English.
Automatic mode uses Prisma's `indic-auto` setting for live speech and detects the script
of typed text; Hindi is the fallback when the language is ambiguous. The sample replay,
follow-up questions, browser speech, number-to-words read-back, and Timbre request follow
the selected or detected language.

## Modes

- `MOCK_REPLAY` uses synthetic records and local statutory arithmetic.
- `LIVE` is reserved for configured Gnani credentials and endpoint access. Credentials
  remain local in `backend/.env`, which is intentionally ignored by Git.
- Configure `GNANI_API_BASE_URL`, `GNANI_STT_WS_URL`, and `GNANI_TTS_API_URL` in
  `backend/.env` for provider routing. `EVON_ENDPOINT_URL` is an optional full-URL
  override; otherwise the backend appends the Evon chat-completions path to the base URL.
- The sample replay is available only in `MOCK_REPLAY`; it does not call live Gnani
  services or a real worker registry. Claim artifacts are drafts for review, not submissions.

The microphone/Prisma speech-to-text path is available only in `LIVE` mode. In
`MOCK_REPLAY`, the backend and sample-claim flow work, but microphone transcription is
intentionally disabled to avoid external API calls and credit usage. To opt in, set
`SHRAMIK_MODE=LIVE` in `backend/.env` and configure valid Gnani credentials and endpoint
before restarting the backend. Live speech supports automatic detection and explicit
Hindi (`hi-IN`), Kannada (`kn-IN`), and English (`en-IN`) selection. The language can only
be changed while the microphone is stopped.

Wage calculations are deterministic in `backend/legal_rules.py`; the LLM only drafts
the narrative and does not calculate amounts. The rule module includes a legal-review
notice because statutory applicability and compensation limits must be verified before
filing. Run its focused tests from `backend` with `python -m unittest test_legal_rules`.

The Prisma bridge sends only raw mono `pcm_s16le` frames of 1024 bytes at a 64 ms
cadence and supports the documented `update_settings` bias control frame.
In `LIVE` mode, the review script is also sent to Timbre v3.0 (Shivani voice), and its
WAV read-back is delivered to the browser. If synthesis fails, the UI reports that and
falls back to the browser voice. Run the offline Prisma, Evon, and Timbre checks from
`backend` with `python -m unittest discover -p "test_*.py"`; these tests mock network
clients and do not call Gnani APIs or consume credits.

## Optional live API diagnostic

After confirming that the credentials in `backend/.env` are valid, run the opt-in
diagnostic from the backend directory:

```powershell
cd backend
.\venv\Scripts\activate
python verify_live_apis.py
```

It checks Hugging Face model access, synthesizes a short Timbre sample, and sends
that sample to Prisma using 1024-byte frames paced at 64 ms. The generated WAV is
ignored by Git. This diagnostic can consume API credits and should not be run
automatically.
