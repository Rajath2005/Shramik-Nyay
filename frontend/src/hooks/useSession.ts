import { useCallback, useEffect, useRef, useState } from 'react'
import { isLanguagePreference, type LanguagePreference } from '../language'

export type Slots = Record<string, string | number | null>
export type Check = { id: string; label: string; status: string; detail: string }
export type Audit = {
  principal_arrears_inr: number
  gross_wages_inr: number
  max_compensation_inr: number | null
  checks: Check[]
  legal_audit_summary: string
  form_a_clauses: string[]
  timbre_v3_readback_script: string
  notice: string
}
export type Ev = { type: string; [key: string]: unknown }
export type AudioTelemetry = {
  frameBytes?: number
  cadenceMs?: number
  sampleRateHz?: number
  vadThreshold?: number
  latencyMs?: number
  source?: string
}
export type PipelineLatencyStage =
  | 'prisma_segment'
  | 'evon_stage_a'
  | 'evon_stage_b'
  | 'timbre_first_audio_chunk'

const WS_URL: string = import.meta.env.VITE_WS_URL ?? 'ws://127.0.0.1:8000/ws/session'
export const API_BASE = WS_URL.replace(/^ws/, 'http').replace(/\/ws\/session$/, '')

function numberField(event: Ev, key: string): number | undefined {
  const value = event[key]
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
}

export function useSession() {
  const ws = useRef<WebSocket | null>(null)
  const [online, setOnline] = useState(false)
  const [mode, setMode] = useState('')
  const [slots, setSlots] = useState<Slots>({})
  const [followup, setFollowup] = useState('')
  const [audit, setAudit] = useState<Audit | null>(null)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [heard, setHeard] = useState<string[]>([])
  const [events, setEvents] = useState<Ev[]>([])
  const [biasWords, setBiasWords] = useState<string[]>([])
  const [biasSettingsUpdated, setBiasSettingsUpdated] = useState(false)
  const [biasBoostFailed, setBiasBoostFailed] = useState(false)
  const [pipelineLatencies, setPipelineLatencies] = useState<Partial<Record<PipelineLatencyStage, number>>>({})
  const biasRequestRef = useRef<string | null>(null)
  const confirmedBiasRequestRef = useRef<string | null>(null)
  const [latency, setLatency] = useState<number | null>(null)
  const [signalLevels, setSignalLevels] = useState<number[]>([])
  const [telemetry, setTelemetry] = useState<AudioTelemetry | null>(null)
  const [transcript, setTranscript] = useState('')
  const [detectedLanguage, setDetectedLanguage] = useState('')
  const [effectiveLanguage, setEffectiveLanguage] = useState('')
  const [languagePreference, setLanguagePreferenceState] = useState<LanguagePreference>('auto')
  const languagePreferenceRef = useRef<LanguagePreference>('auto')
  const [readback, setReadback] = useState('')
  const [jsonUrl, setJsonUrl] = useState<string | null>(null)
  const [timbreAudioUrl, setTimbreAudioUrl] = useState<string | null>(null)
  const [timbreUnavailable, setTimbreUnavailable] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    let closed = false
    let sock: WebSocket
    const handle = (e: Ev) => {
      setEvents((cur) => [...cur.slice(-39), e])
      switch (e.type) {
        case 'session_started':
          setMode(String(e.mode)); setSlots({}); setAudit(null); setPdfUrl(null); setJsonUrl(null)
          setHeard([]); setFollowup(''); setMessage(''); setTranscript(''); setDetectedLanguage('')
          setEffectiveLanguage('')
          setSignalLevels([]); setTelemetry(null); setReadback(''); setBiasWords([]); setLatency(null)
          setBiasSettingsUpdated(false); setBiasBoostFailed(false); setPipelineLatencies({})
          biasRequestRef.current = null; confirmedBiasRequestRef.current = null
          setTimbreAudioUrl(null); setTimbreUnavailable(false)
          break
        case 'evon_stage_a':
          setSlots(e.slots as Slots); setFollowup(String(e.followup ?? ''))
          break
        case 'evon_stage_b_complete':
          setAudit(e as unknown as Audit)
          break
        case 'prisma_transcript':
          setTranscript(String(e.text ?? ''))
          setDetectedLanguage(String(e.detected_language_code ?? ''))
          if (typeof e.effective_language === 'string') setEffectiveLanguage(e.effective_language)
          setHeard((cur) => [...cur.slice(-5), String(e.text ?? '')])
          setLatency(numberField(e, 'latency') ?? null)
          break
        case 'language_status':
          {
            const preference = typeof e.language_preference === 'string' && isLanguagePreference(e.language_preference)
              ? e.language_preference
              : 'auto'
            setLanguagePreferenceState(preference)
            languagePreferenceRef.current = preference
          }
          setEffectiveLanguage(typeof e.effective_language === 'string' ? e.effective_language : '')
          break
        case 'prisma_telemetry': {
          const waveform = Array.isArray(e.waveform)
            ? e.waveform.filter((value): value is number => typeof value === 'number' && Number.isFinite(value))
              .map((value) => Math.max(0, Math.min(1, value)))
            : []
          if (waveform.length) setSignalLevels(waveform)
          const latencyMs = numberField(e, 'latency_ms')
          setTelemetry({
            frameBytes: numberField(e, 'frame_bytes'),
            cadenceMs: numberField(e, 'cadence_ms'),
            sampleRateHz: numberField(e, 'sample_rate_hz'),
            vadThreshold: numberField(e, 'vad_threshold'),
            latencyMs,
            source: typeof e.source === 'string' ? e.source : undefined,
          })
          if (latencyMs !== undefined) setLatency(latencyMs)
          break
        }
        case 'pipeline_latency': {
          const stages: PipelineLatencyStage[] = [
            'prisma_segment', 'evon_stage_a', 'evon_stage_b', 'timbre_first_audio_chunk',
          ]
          if (stages.includes(e.stage as PipelineLatencyStage)) {
            const latencyMs = numberField(e, 'latency_ms')
            if (latencyMs !== undefined) {
              setPipelineLatencies((current) => ({
                ...current,
                [e.stage as PipelineLatencyStage]: latencyMs,
              }))
            }
          }
          break
        }
        case 'bias_boost_triggered':
          {
            const requestId = typeof e.request_id === 'string' ? e.request_id : null
            biasRequestRef.current = requestId
            setBiasWords(Array.isArray(e.words) ? e.words.filter((word): word is string => typeof word === 'string') : [])
            setBiasSettingsUpdated(Boolean(requestId && confirmedBiasRequestRef.current === requestId))
            setBiasBoostFailed(false)
          }
          break
        case 'bias_boost_failed':
          if (typeof e.request_id === 'string' && biasRequestRef.current === e.request_id) {
            setBiasBoostFailed(true)
          }
          break
        case 'prisma_settings_updated': {
          const requestId = typeof e.request_id === 'string' ? e.request_id : null
          const config = e.config
          const confirmedWords = Array.isArray(e.confirmed_words)
            ? e.confirmed_words.filter((word): word is string => typeof word === 'string')
            : []
          if (
            requestId &&
            config !== null &&
            typeof config === 'object' &&
            'bias_word_count' in config &&
            config.bias_word_count === confirmedWords.length &&
            'bias_score' in config &&
            config.bias_score === 2.0
          ) {
            confirmedBiasRequestRef.current = requestId
            if (biasRequestRef.current === requestId) {
              setBiasWords(confirmedWords)
              setBiasSettingsUpdated(true)
            }
          }
          break
        }
        case 'timbre_audio':
          setReadback(String(e.script ?? ''))
          break
        case 'timbre_audio_unavailable':
          setTimbreUnavailable(true)
          setMessage(`Timbre read-back unavailable: ${String(e.message ?? 'No audio was returned.')}`)
          break
        case 'claim_ready':
          setPdfUrl(API_BASE + String(e.pdf_url))
          setJsonUrl(API_BASE + String(e.json_url))
          break
        case 'uan_result':
          if (!e.found) setMessage('UAN not found in the demo registry.')
          break
        case 'notice': case 'error':
          setMessage(String(e.message))
          break
      }
    }
    const open = () => {
      sock = new WebSocket(WS_URL)
      sock.binaryType = 'arraybuffer'
      ws.current = sock
      sock.onopen = () => {
        setOnline(true)
        sock.send(JSON.stringify({ type: 'set_language', language: languagePreferenceRef.current }))
      }
      sock.onclose = () => { setOnline(false); if (!closed) window.setTimeout(open, 1500) }
      sock.onmessage = (m) => {
        if (typeof m.data === 'string') {
          handle(JSON.parse(m.data))
          return
        }
        const audio = m.data instanceof Blob ? m.data : new Blob([m.data], { type: 'audio/wav' })
        setTimbreAudioUrl((current) => {
          if (current) URL.revokeObjectURL(current)
          return URL.createObjectURL(audio)
        })
      }
    }
    open()
    return () => { closed = true; sock.close() }
  }, [])

  useEffect(() => () => {
    if (timbreAudioUrl) URL.revokeObjectURL(timbreAudioUrl)
  }, [timbreAudioUrl])

  const send = useCallback((cmd: object) => {
    if (ws.current?.readyState === WebSocket.OPEN) ws.current.send(JSON.stringify(cmd))
    else setMessage('Not connected to the claim service. Wait for reconnection and try again.')
  }, [])
  const setLanguagePreference = useCallback((language: LanguagePreference) => {
    languagePreferenceRef.current = language
    setLanguagePreferenceState(language)
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'set_language', language }))
    }
  }, [])
  const sendAudio = useCallback((buf: ArrayBuffer) => {
    if (ws.current?.readyState === WebSocket.OPEN) ws.current.send(buf)
  }, [])

  return {
    online, mode, slots, followup, audit, pdfUrl, jsonUrl, heard, events, biasWords,
    biasSettingsUpdated, biasBoostFailed, pipelineLatencies,
    latency, signalLevels, telemetry, transcript, detectedLanguage, effectiveLanguage,
    languagePreference, setLanguagePreference, readback, timbreAudioUrl,
    timbreUnavailable, message, send, sendAudio,
  }
}
