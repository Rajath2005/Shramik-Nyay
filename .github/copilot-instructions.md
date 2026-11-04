# Shramik-Nyay Project Rules for GitHub Copilot

1. **Gnani Prisma v3.0 WebSocket STT (`wss://api.vachana.ai/stt/v3/stream`):**
   - NEVER send container headers (.wav/.mp3) mid-stream. Send ONLY raw `pcm_s16le` mono binary frames of EXACTLY `1024` bytes.
   - At `8000` Hz, pace frames at 1 frame every `64ms` (`0.064s`).
   - Use handshake headers: `x-api-key-id`, `model: prisma-v3.0`, `language_code: hi-IN,en-IN`, `x-sample-rate: 8000`, `format: transcribe`, optional `keyterms` for initial vocabulary, `itn_native_numerals: false`, `x-vad-threshold: 0.72`, `x-min-speech-ms: 200`, `x-min-silence-ms: 700`, `x-min-segment-ms: 150`. The legacy `x-model`, `lang_code`, and `x-format` spellings are accepted, but prefer the current names.
   - Mid-session word boosting uses JSON text frame: `{"type": "update_settings", "bias": {"list": [...], "score": 2.0}}`. A successful update returns `{"type": "settings_updated", "timestamp": "<ISO-8601>", "config": {"language_code": "...", "format": "...", "itn_native_numerals": false, "substitution_enabled": false, "bias_word_count": 1, "bias_score": 2.0}}`.

2. **Gnani Evon v3.3 (`gnani/gnani-evon-v3.3-30B-A3B`):**
   - Stage A (Turn-by-turn slot extraction): pass `"chat_template_kwargs": {"enable_thinking": false}`, `temperature: 0.6`, `top_p: 0.95`, `repetition_penalty: 1.1`, `max_tokens: 2048`.
   - Stage B (Final statutory audit): pass `"chat_template_kwargs": {"enable_thinking": true}`, `temperature: 0.6`, `top_p: 0.95`, `repetition_penalty: 1.0`, `max_tokens: 16384`.
   - System prompt must include: `"Respond in the same language and script as the question."`

3. **Gnani Timbre v3.0 TTS (`wss://api.vachana.ai/api/v1/tts`):**
   - Use `"model": "timbre-v3.0"` and `"voice": "Shivani"`.
   - Expand all numbers and currency into spoken words before synthesis, and use inline tags `<pauses>` and `<slow>`. Tags apply through the next tag or end of text; do not use HTML-style closing tags.


