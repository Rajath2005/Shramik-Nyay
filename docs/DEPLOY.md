# Deployment

The backend must run on a host that supports long-lived WebSocket connections.
The steps below use Render; Fly.io and Railway work with the same container and
environment variables.

See the editable [production deployment topology](diagrams/deployment-topology.drawio)
and [request and safety flow](diagrams/runtime-flow.drawio) diagrams before
configuring a public deployment. The [system architecture](diagrams/system-architecture.drawio)
diagram explains the application boundaries and data paths.

## 1. Deploy the backend to Render

1. Create a **Web Service** from this repository.
2. Set **Root Directory** to `backend`.
3. Choose **Docker** as the runtime. Render uses [backend/Dockerfile](../backend/Dockerfile).
4. Add these environment variables in Render (never commit them):

   ```text
   SHRAMIK_MODE=MOCK_REPLAY
   SHRAMIK_CORS_ORIGINS=https://your-frontend-domain.example
   SHRAMIK_LIVE_PASSCODE=<long-random-value>
   SHRAMIK_CLAIM_TTL_SECONDS=86400
   SHRAMIK_LIVE_EVON_CAP=20
   SHRAMIK_LIVE_TIMBRE_CAP=5
   SHRAMIK_LIVE_PRISMA_CAP=20
   GNANI_API_KEY=<server-only-provider-key>
   GNANI_API_BASE_URL=https://api.vachana.ai
   GNANI_STT_WS_URL=wss://api.vachana.ai/stt/v3/stream
   GNANI_TTS_API_URL=wss://api.vachana.ai/api/v1/tts
   ```

   Keep `SHRAMIK_MODE=MOCK_REPLAY` until live provider access has been verified.
   The public demo works without a provider key. Set `SHRAMIK_MODE=LIVE` only
   when the passcode, provider key, and quotas are ready.
5. Deploy and verify `https://<render-service>.onrender.com/health` returns
   `{"status":"ok",...}`. Do not put the API key in frontend variables.

Render's HTTPS endpoint supports the browser's secure WebSocket upgrade at
`wss://<render-service>.onrender.com/ws/session`. Do not use a serverless
function for this process.

## 2. Deploy the frontend

Create a Vercel, Netlify, or Cloudflare Pages project from this repository:

- **Root directory:** `frontend`
- **Build command:** `npm run build`
- **Output directory:** `dist`
- **Environment variable:** `VITE_WS_URL=wss://<render-service>.onrender.com/ws/session`

`VITE_WS_URL` is intentionally public configuration. It must contain only the
WebSocket URL; `GNANI_API_KEY` and `SHRAMIK_LIVE_PASSCODE` belong only to the
backend environment. HTTPS is required for microphone permission, so use the
provider's HTTPS domain and do not test production microphone access over HTTP.

After the frontend is deployed, replace `SHRAMIK_CORS_ORIGINS` with its exact
HTTPS origin, redeploy the backend, and test both the sample replay and the
WebSocket connection.

## Runtime safety

- Visitors start in `MOCK_REPLAY`, which uses the recorded/synthetic replay and
  does not spend provider credits.
- LIVE microphone and recorded-provider replay require the backend passcode.
- WebSocket connection attempts are rate-limited per source IP. Provider calls
  also use the per-session caps configured above.
- Claim files are local ephemeral artifacts. `SHRAMIK_CLAIM_TTL_SECONDS` removes
  expired claim directories during startup and in a cleanup loop; use a
  persistent disk only if this retention model is acceptable.
- The backend Docker healthcheck calls `/health`.
