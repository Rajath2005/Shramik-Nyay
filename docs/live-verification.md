# Gnani live API verification

This is an opt-in, one-shot diagnostic. Do not run it repeatedly: the Timbre
synthesis and Prisma transcription may consume API credits. No live API calls
were made while preparing this document.

## What the repository currently configures

| API | Endpoint and request |
|---|---|
| Evon chat completions | The current default is `https://api.vachana.ai/llm/evon-v3.3/chat/completions`; `EVON_ENDPOINT_URL` overrides it, or `GNANI_API_BASE_URL` supplies the base URL. The request model is `gnani/gnani-evon-v3.3-30B-A3B` in [`backend/evon_legal_engine.py`](../backend/evon_legal_engine.py). These are repository configuration values, not verified by Gnani's speech API quick-start. |
| Prisma v3.0 WebSocket STT | `wss://api.vachana.ai/stt/v3/stream`. Round 2 passed the cumulative set: `x-api-key-id`, `x-model`, `lang_code: indic-auto`, `x-sample-rate`, VAD, `x-format`, ITN, max-speech, and JSON `x-bias-list`. Single `hi-IN`, `kn-IN`, and `en-IN` values passed; comma-separated language values closed with 1008. Re-run `python backend/diagnose_prisma.py` after provider changes. |
| Prisma word-bias update | Send the JSON text frame `{"type":"update_settings","bias":{"list":["Peenya","Thekedar","Dihadi","Ramesh"],"score":2.0}}`. A successful update returns `{"type":"settings_updated","timestamp":"<ISO-8601>","config":{...}}`; documented config keys include `language_code`, `format`, `itn_native_numerals`, `substitution_enabled`, `bias_word_count`, and `bias_score`. The verifier checks the timestamp, these config fields, and the expected count and score. |
| Timbre v3.0 WebSocket TTS | `wss://api.vachana.ai/api/v1/tts`, with `x-api-key-id` and `Content-Type: application/json`. The payload uses `text`, `voice: "Shivani"`, `model: "timbre-v3.0"`, `language`, `speed`, and `audio_config` (`sample_rate: 8000`, mono, 16-bit `linear_pcm`, `wav`). Audio tags such as `<pauses>` and `<slow>` are inline scope markers, not HTML tags. |

[`backend/verify_live_apis.py`](../backend/verify_live_apis.py) checks Hugging Face model-repository access, then runs
one Timbre synthesis and one Prisma transcription. It does **not** make an Evon
chat-completions request, so it cannot establish that the configured Evon URL
or model is accepted by the provider.

## Session pipeline telemetry

The live session emits `pipeline_latency` JSON events with `stage` and
`latency_ms` for `prisma_segment`, `evon_stage_a`, `evon_stage_b`, and
`timbre_first_audio_chunk`. Prisma timing is measured from the `commit` frame
(or the last streamed PCM frame for VAD-finalized segments) until the transcript
arrives. The Evon timings cover each request, and the Timbre timing stops when
the first non-empty audio chunk arrives. These values are also shown in the
audio telemetry panel.

Locality word pills remain amber while awaiting Prisma's `settings_updated`
event. A pill turns green only when the confirmation's bias count and score
match the pending request; failed or unconfirmed updates never appear as
confirmed.

## Prepare before the one run

1. Create `backend/.env` from [`backend/.env.example`](../backend/.env.example) if it does not already
   exist; do not overwrite an existing credentials file.
2. Set `GNANI_API_KEY`. `HF_TOKEN` is optional and is used only if Hugging Face
   requires authentication to access the Evon model repository.
3. Ensure the Python dependencies in `backend/requirements.txt` are installed
   in the Python environment that will execute the command.

From PowerShell, run this command sequence **once**:

```powershell
Set-Location "D:\DevWorkspace\Github_Repos\Shramik-Nyay\backend"
python .\verify_live_apis.py
```

The script loads `.env` from the backend directory, creates
`backend/fixtures/live_tts_8khz.wav`, and sends that synthesized audio to Prisma
in 1024-byte frames paced at 64 ms. It does not retry failed API requests.

## Deterministic recorded-call replay

The UI's **Replay recorded call** action is separate from this diagnostic. It
streams the committed `backend/fixtures/replay_recorded_call.pcm` fixture
through the same LIVE Prisma pacer, so it still exercises the provider path
without synthesizing audio or consuming a Timbre request at replay time. The
fixture is synthetic: its speech was generated once with Timbre v3.0 and mixed
with deterministic procedural site noise; it is not a real worker recording.

## Results

No live request was made for this documentation change. Fill in the result and
evidence columns after the single run; do not infer success from the configured
values alone.

| Check | Result | Evidence |
|---|---|---|
| Hugging Face Evon model repository access | Not run | Run output from `[1/3]` |
| Timbre v3.0 synthesis (`Shivani`) | Not run | Run output / generated WAV at `backend/fixtures/live_tts_8khz.wav` |
| Prisma v3.0 `settings_updated` confirmation and transcript | Not run | Run output showing `bias_word_count=4`, `bias_score=2.0`, and transcript |
| Evon chat-completions endpoint/model | Not exercised by this script | Values above are read from repository configuration only |

## Gnani documentation references

- [Quick Start](https://docs.gnani.ai/api/introduction/quick-start)
- [Prisma realtime WebSocket](https://docs.gnani.ai/api/STT/stt-websocket.md)
- [Timbre realtime WebSocket](https://docs.gnani.ai/api/TTS/tts-websocket.md)
- [Timbre audio tags](https://docs.gnani.ai/api/TTS/tts-audio-tags.md)
