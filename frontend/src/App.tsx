import { useCallback, useEffect, useRef, useState } from 'react'
import './App.css'
import styles from './App.module.css'
import AudioLine from './components/AudioLine'
import ClaimSlots from './components/ClaimSlots'
import ConsentBar from './components/ConsentBar'
import Header from './components/Header'
import PaperForm from './components/PaperForm'
import Transcript from './components/Transcript'
import { MicrophoneButton } from './components/ui/MicrophoneButton'
import { TypeInputField } from './components/ui/TypeInputField'
import { useMicrophone } from './hooks/useMicrophone'
import { useCountUp } from './hooks/useCountUp'
import { useSession } from './hooks/useSession'
import {
  COPY,
  FIELD_LABELS,
  LANGUAGE_LABELS,
  type SupportedLanguage,
} from './language'
import { FIELD_KEYS, isSlotVerified } from './claimSlots'
import type { ViewMode } from './components/types'

const EMPTY_WAVEFORM = Array.from({ length: 28 }, () => 0)
const STUDIO_WIDTH = 1920
const STUDIO_HEIGHT = 1080
const plain = (text: string) => text.replace(/<[^>]+>/g, ' ')

function AcousticOrb({
  active,
  levels,
  label,
}: {
  active: boolean
  levels: number[]
  label: string
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const context = canvas.getContext('2d')
    if (!context) return
    let frame = 0
    let animationFrame = 0
    const render = () => {
      const dpr = window.devicePixelRatio || 1
      const size = 260
      if (canvas.width !== size * dpr) {
        canvas.width = size * dpr
        canvas.height = size * dpr
        canvas.style.width = `${size}px`
        canvas.style.height = `${size}px`
      }
      context.setTransform(dpr, 0, 0, dpr, 0, 0)
      context.clearRect(0, 0, size, size)
      const center = size / 2
      const average = levels.length ? levels.reduce((sum, level) => sum + level, 0) / levels.length : 0
      for (let index = 0; index < 36; index += 1) {
        const angle = (index / 36) * Math.PI * 2 - Math.PI / 2
        const source = levels[index % Math.max(levels.length, 1)] || 0
        const wave = active ? Math.abs(Math.sin(frame * 0.045 + index * 0.7)) * 0.55 : 0
        const magnitude = 7 + (active ? source * 22 + wave * 14 : 4 + Math.sin(frame * 0.018 + index) * 2)
        const inner = 105
        const outer = inner + magnitude
        const x1 = center + Math.cos(angle) * inner
        const y1 = center + Math.sin(angle) * inner
        const x2 = center + Math.cos(angle) * outer
        const y2 = center + Math.sin(angle) * outer
        context.beginPath()
        context.moveTo(x1, y1)
        context.lineTo(x2, y2)
        context.lineWidth = index % 3 === 0 ? 2.4 : 1.4
        context.lineCap = 'round'
        context.strokeStyle = active
          ? `rgba(16, 185, 129, ${0.38 + Math.min(source + wave, 0.5)})`
          : `rgba(59, 130, 246, ${0.34 + Math.max(average, 0.08)})`
        context.stroke()
      }
      frame += 1
      animationFrame = window.requestAnimationFrame(render)
    }
    render()
    return () => window.cancelAnimationFrame(animationFrame)
  }, [active, levels])

  return <canvas ref={canvasRef} className={styles.orbCanvas} aria-label={label} role="img" />
}

function Preloader({ onSkip }: { onSkip: () => void }) {
  const [progress, setProgress] = useState(0)
  const [visible, setVisible] = useState(true)
  useEffect(() => {
    const isTest = import.meta.env.MODE === 'test'
      || (typeof window !== 'undefined' && window.navigator.userAgent.includes('jsdom'))
    if (isTest) {
      onSkip()
      return
    }
    const started = performance.now()
    let animationFrame = 0
    const update = (now: number) => {
      const next = Math.min(100, ((now - started) / 1400) * 100)
      setProgress(next)
      if (next < 100) animationFrame = window.requestAnimationFrame(update)
    }
    animationFrame = window.requestAnimationFrame(update)
    const timer = window.setTimeout(() => setVisible(false), 1450)
    return () => {
      window.cancelAnimationFrame(animationFrame)
      window.clearTimeout(timer)
    }
  }, [onSkip])

  if (!visible) return null
  return (
    <div className="preloader" role="status" aria-label="Loading acoustic telemetry">
      <div className="preloader-grid" />
      <button className="skip-button" type="button" onClick={onSkip}>SKIP →</button>
      <div className="preloader-card">
        <span className="hud-crosshair hud-crosshair-top-left" aria-hidden="true">+</span>
        <span className="hud-crosshair hud-crosshair-top-right" aria-hidden="true">+</span>
        <span className="hud-crosshair hud-crosshair-bottom-left" aria-hidden="true">+</span>
        <span className="hud-crosshair hud-crosshair-bottom-right" aria-hidden="true">+</span>
        <div className="preloader-header">
          <div className="preloader-mark">
            <span className="brand-logo-mark" aria-hidden="true">
              <img src="/logo-icon.png" alt="" />
            </span>
            <b>श्रमिक-न्याय</b>
          </div>
          <span className="preloader-system-state"><i aria-hidden="true" /> CALIBRATION ACTIVE</span>
        </div>
        <div className="preloader-intro">
          <p className="preloader-kicker">VOICE WORKSPACE</p>
          <h1>Preparing your voice workspace</h1>
          <p>We're getting everything ready to help you begin your wage claim.</p>
        </div>
        <div className="boot-readout">
          <strong>{Math.round(progress).toString().padStart(3, '0')}<small>%</small></strong>
          <span>8KHZ ACOUSTIC TELEMETRY</span>
        </div>
        <div className="boot-progress" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(progress)}>
          <span style={{ width: `${progress}%` }} />
        </div>
        <svg className="boot-wave" viewBox="0 0 520 132" aria-hidden="true" preserveAspectRatio="none">
          <defs>
            <pattern id="frequency-grid" width="26" height="22" patternUnits="userSpaceOnUse">
              <path d="M 26 0 L 0 0 0 22" fill="none" stroke="rgba(148,163,184,.16)" strokeWidth="1" />
            </pattern>
            <filter id="wave-glow" x="-20%" y="-50%" width="140%" height="200%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          </defs>
          <rect width="520" height="132" fill="url(#frequency-grid)" />
          <path className="boot-wave-secondary" d="M0 70 C26 70 28 42 52 42 S78 98 104 98 130 58 156 58 182 84 208 84 234 28 260 28 286 72 312 72 338 108 364 108 390 54 416 54 442 87 468 87 494 67 520 67" />
          <path className="boot-wave-primary" d="M0 64 C26 64 28 26 52 26 S78 106 104 106 130 48 156 48 182 80 208 80 234 18 260 18 286 64 312 64 338 116 364 116 390 42 416 42 442 94 468 94 494 58 520 58" />
        </svg>
        <div className="boot-statuses">
          <div className={progress > 22 ? 'boot-status boot-status-ready' : 'boot-status'}>
            <span className="status-dot" aria-hidden="true" /><span>8000 Hz PCM Pacer</span><b>LOCKED</b>
          </div>
          <div className={progress > 52 ? 'boot-status boot-status-ready' : 'boot-status'}>
            <span className="status-dot" aria-hidden="true" /><span>Prisma v3.0 VAD 0.72</span><b>READY</b>
          </div>
          <div className={progress > 78 ? 'boot-status boot-status-ready' : 'boot-status'}>
            <span className="status-dot" aria-hidden="true" /><span>Evon v3.3 Form-A Engine</span><b>ONLINE</b>
          </div>
        </div>
        <p className="visually-hidden" aria-live="polite">
          {progress < 23 ? 'Calibrating audio pacer.' : progress < 53 ? 'Checking voice detection.' : progress < 79 ? 'Preparing legal voice assistant.' : 'Voice workspace ready.'}
        </p>
      </div>
    </div>
  )
}

function speak(text: string, language: string, onSpeakingChange?: (speaking: boolean) => void) {
  if (!text || !('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(plain(text))
  utterance.lang = language
  utterance.onstart = () => onSpeakingChange?.(true)
  utterance.onend = () => onSpeakingChange?.(false)
  utterance.onerror = () => onSpeakingChange?.(false)
  window.speechSynthesis.speak(utterance)
}

export default function App() {
  const [showPreloader, setShowPreloader] = useState(() => {
    const isTest = import.meta.env.MODE === 'test'
      || (typeof window !== 'undefined' && window.navigator.userAgent.includes('jsdom'))
    return !isTest
  })
  const session = useSession()
  const { send, sendAudio } = session
  const [mode, setMode] = useState<ViewMode>(() =>
    localStorage.getItem('shramik:view-mode') === 'studio' ? 'studio' : 'worker',
  )
  const [dark, setDark] = useState(() => {
    const preference = localStorage.getItem('shramik:theme')
    return preference === 'dark' || (preference !== 'light' && window.matchMedia('(prefers-color-scheme: dark)').matches)
  })
  const [readAloud, setReadAloud] = useState(true)
  const [typed, setTyped] = useState('')
  const [workerPhase, setWorkerPhase] = useState<'idle' | 'thinking' | 'speaking'>('idle')
  const [noiseLevel, setNoiseLevel] = useState(0)
  const [uan, setUan] = useState('')
  const [audioNotice, setAudioNotice] = useState('')
  const [studioScale, setStudioScale] = useState(1)
  const studioViewportRef = useRef<HTMLElement>(null)
  const readbackAudio = useRef<HTMLAudioElement>(null)
  const mic = useMicrophone({
    onFrame: sendAudio,
    onStart: useCallback(() => send({ type: 'start_mic' }), [send]),
    onStop: useCallback(() => send({ type: 'stop_mic' }), [send]),
  })

  const displayLanguage: SupportedLanguage = session.languagePreference !== 'auto'
    ? session.languagePreference
    : session.effectiveLanguage === 'kn-IN' || session.effectiveLanguage === 'en-IN' || session.effectiveLanguage === 'hi-IN'
      ? session.effectiveLanguage
      : 'hi-IN'
  const transcriptLanguage: SupportedLanguage =
    session.detectedLanguage === 'kn-IN' || session.detectedLanguage === 'en-IN' || session.detectedLanguage === 'hi-IN'
      ? session.detectedLanguage
      : displayLanguage
  const copy = COPY[displayLanguage]
  const fields = FIELD_LABELS[displayLanguage]
  const done = FIELD_KEYS.filter((key) => isSlotVerified(session.slots[key])).length
  const firstMissing = FIELD_KEYS.findIndex((key) => !isSlotVerified(session.slots[key]))
  const currentQuestion = session.followup
  const sample = session.mode === 'MOCK_REPLAY'
  const waveform = sample
    ? session.signalLevels
    : mic.live ? mic.levels : EMPTY_WAVEFORM
  const canUseMicrophone = session.online && session.mode === 'LIVE' && !session.serviceUnavailable
  const detectedLanguageLabel =
    session.detectedLanguage === 'kn-IN' || session.detectedLanguage === 'en-IN' || session.detectedLanguage === 'hi-IN'
      ? LANGUAGE_LABELS[session.detectedLanguage]
      : ''
  const arrearsDisplayValue = useCountUp(session.audit?.principal_arrears_inr ?? null)
  const lastEvent = session.events[session.events.length - 1]
  const uanMessage = lastEvent?.type === 'uan_result' ? session.message : ''
  const serviceMessage = lastEvent?.type === 'error'
    ? mode === 'studio'
      ? String(lastEvent.engineer_message ?? session.message ?? copy.apiError)
      : copy.apiError
    : lastEvent?.type === 'uan_result' || lastEvent?.type === 'timbre_audio_unavailable'
      ? ''
      : mode === 'studio' ? session.message : ''
  const timbreNotice = session.timbreUnavailable ? copy.timbreUnavailable : ''
  const workerError = mic.error || lastEvent?.type === 'error' || Boolean(serviceMessage)
  const orbActive = mic.live || workerPhase === 'speaking' || sample

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? 'dark' : 'light'
    document.documentElement.lang = displayLanguage
    localStorage.setItem('shramik:theme', dark ? 'dark' : 'light')
  }, [dark, displayLanguage])

  useEffect(() => {
    localStorage.setItem('shramik:view-mode', mode)
  }, [mode])

  useEffect(() => {
    const viewport = studioViewportRef.current
    if (!viewport) return
    const updateScale = () => {
      setStudioScale(Math.min(viewport.clientWidth / STUDIO_WIDTH, viewport.clientHeight / STUDIO_HEIGHT, 1))
    }
    updateScale()
    const observer = new ResizeObserver(updateScale)
    observer.observe(viewport)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (readAloud) {
      speak(currentQuestion, displayLanguage, (speaking) => {
        setWorkerPhase((phase) => speaking ? 'speaking' : phase === 'speaking' ? 'idle' : phase)
      })
    }
    return () => {
      if ('speechSynthesis' in window) window.speechSynthesis.cancel()
    }
  }, [currentQuestion, readAloud, displayLanguage])

  useEffect(() => {
    if (mode !== 'studio' || !readAloud || !session.timbreAudioUrl || !readbackAudio.current) return
    void readbackAudio.current.play().then(() => setAudioNotice('')).catch(() => {
      setAudioNotice(copy.audioReady)
    })
  }, [mode, session.timbreAudioUrl, readAloud, copy.audioReady])

  useEffect(() => {
    if (mode === 'studio' && readAloud && session.audit && (session.mode !== 'LIVE' || session.timbreUnavailable)) {
      speak(session.audit.timbre_v3_readback_script, displayLanguage)
    }
  }, [mode, session.audit, session.mode, session.timbreUnavailable, readAloud, displayLanguage])

  useEffect(() => {
    const latest = session.events[session.events.length - 1]
    if (
      latest?.type === 'session_started'
      || latest?.type === 'prisma_transcript'
      || latest?.type === 'evon_stage_a'
      || latest?.type === 'consent_status'
      || latest?.type === 'notice'
      || latest?.type === 'error'
    ) {
      const frame = window.requestAnimationFrame(() => {
        setWorkerPhase((phase) => phase === 'thinking' ? 'idle' : phase)
      })
      return () => window.cancelAnimationFrame(frame)
    }
  }, [session.events])

  const toggleMicrophone = () => {
    if (mic.live) {
      setWorkerPhase('thinking')
      mic.stop()
    } else {
      if (session.mode === 'LIVE') {
        const passcode = window.prompt('Enter the LIVE access passcode')
        if (!passcode) return
        send({ type: 'authenticate_live', passcode })
      }
      void mic.start(noiseLevel)
    }
  }
  const changeNoiseLevel = (value: number) => {
    setNoiseLevel(value)
    mic.updateNoiseLevel(value)
  }
  const prepareDraft = () => send({ type: 'confirm' })
  const playSample = () => {
    setWorkerPhase('thinking')
    send({ type: 'demo' })
  }
  const answerConsent = (accepted: boolean) => {
    setWorkerPhase('thinking')
    const answers: Record<SupportedLanguage, { yes: string; no: string }> = {
      'hi-IN': { yes: 'हाँ', no: 'ना' },
      'kn-IN': { yes: 'ಹೌದು', no: 'ಇಲ್ಲ' },
      'en-IN': { yes: 'Yes', no: 'No' },
    }
    send({ type: 'utterance', text: accepted ? answers[displayLanguage].yes : answers[displayLanguage].no })
  }

  if (mode === 'studio') {
    return (
      <>
        {showPreloader && <Preloader onSkip={() => setShowPreloader(false)} />}
        <main ref={studioViewportRef} className={`${styles.app} ${styles.studioApp}`}>
        <div
          className={styles.studioFrame}
          style={{ width: `${STUDIO_WIDTH * studioScale}px`, height: `${STUDIO_HEIGHT * studioScale}px` }}
        >
          <div className={styles.studioCanvas} style={{ transform: `scale(${studioScale})` }}>
          <Header
            mode={mode}
            onModeChange={setMode}
            dark={dark}
            onThemeChange={() => setDark((value) => !value)}
            language={session.languagePreference}
            onLanguageChange={session.setLanguagePreference}
            online={session.online}
            connectionState={session.connectionState}
            serviceMode={session.mode}
            copy={copy}
            studio
            liveUsage={session.liveUsage}
          />
            <section className={styles.studioGrid} aria-label={copy.studioMode}>
            <AudioLine
              className={styles.audioZone}
              copy={copy}
              theme={dark ? 'dark' : 'light'}
              levels={waveform}
              micLive={mic.live}
              micError={mic.error}
              sample={sample}
              online={session.online}
              serviceMode={session.mode}
              telemetry={session.telemetry}
              latency={session.latency}
              pipelineLatencies={session.pipelineLatencies}
              biasWords={session.biasWords}
              biasSettingsUpdated={session.biasSettingsUpdated}
              biasBoostFailed={session.biasBoostFailed}
              noiseLevel={noiseLevel}
              onNoiseLevelChange={changeNoiseLevel}
              onToggleMicrophone={toggleMicrophone}
              onPlaySample={playSample}
              onReplayRecordedCall={() => send({ type: 'replay_recorded_call' })}
              replayActive={session.replayActive}
            />
            <ClaimSlots
              className={styles.slotsZone}
              copy={copy}
              fields={fields}
              slots={session.slots}
              done={done}
              firstMissing={firstMissing}
              audit={session.audit}
              reasoning={session.reasoning}
              sample={sample}
              uan={uan}
              onUanChange={setUan}
              onSubmitUan={() => {
                if (uan.trim()) send({ type: 'uan', value: uan.trim() })
              }}
              online={session.online}
              uanMessage={uanMessage}
            />
            <Transcript
              className={styles.transcriptZone}
              copy={copy}
              language={transcriptLanguage}
              detectedLanguage={detectedLanguageLabel}
              latency={session.latency}
              transcript={session.transcript}
              boostedWords={session.biasWords}
              sample={sample}
              typedAnswer={typed}
              onTypedAnswerChange={setTyped}
              onSubmitAnswer={() => {
                if (typed.trim()) {
                  send({ type: 'utterance', text: typed.trim() })
                  setTyped('')
                }
              }}
              online={session.online}
            />
            <article className={styles.paperZone} aria-labelledby="paper-heading">
              <div className={styles.paperHeading}>
                <h2 id="paper-heading">{copy.formDraft}</h2>
                <span>{session.pdfUrl ? copy.filesReady : copy.draftOnly}</span>
              </div>
              <PaperForm
                copy={copy}
                fields={fields}
                slots={session.slots}
                audit={session.audit}
                sample={sample}
                studio
                arrearsDisplayValue={arrearsDisplayValue}
              />
              {session.audit && (
                <ConsentBar
                  copy={copy}
                  state={session.consentState}
                  voiceConsentRecorded={session.voiceConsentRecorded}
                  readback={session.readback}
                  language={displayLanguage}
                  audioUrl={session.timbreAudioUrl}
                  audioRef={readbackAudio}
                  audioNotice={audioNotice}
                  pdfUrl={session.pdfUrl}
                  jsonUrl={session.jsonUrl}
                  onPrepare={prepareDraft}
                  onDelete={session.deleteClaim}
                  deletingClaim={session.deletingClaim}
                />
              )}
              {timbreNotice && <p className={styles.paperError} role="status">{timbreNotice}</p>}
              {serviceMessage && <p className={styles.paperError} role="alert">{serviceMessage}</p>}
            </article>
            </section>
          </div>
        </div>
        </main>
      </>
    )
  }

  return (
    <>
      {showPreloader && <Preloader onSkip={() => setShowPreloader(false)} />}
      <main className={`${styles.app} ${styles.workerApp}`}>
      <Header
        mode={mode}
        onModeChange={setMode}
        dark={dark}
        onThemeChange={() => setDark((value) => !value)}
        language={session.languagePreference}
        workerLanguage={displayLanguage}
        onLanguageChange={session.setLanguagePreference}
        online={session.online}
        connectionState={session.connectionState}
        serviceMode={session.mode}
        copy={copy}
      />
      <section className={styles.workerFlow} aria-label={copy.workerMode}>
        <div className={styles.workerQuestion}>
          {!session.online && (
            <p className={styles.workerConnection} role="status" aria-live="polite">
              {session.connectionState === 'reconnecting' ? copy.reconnecting : copy.connecting}
            </p>
          )}
          {currentQuestion
            ? <h1 lang={displayLanguage} aria-live="polite" aria-atomic="true">{currentQuestion}</h1>
            : <p className={styles.workerCompletion} role="status">{copy.allDetailsCollected}</p>}
          <p className={styles.workerProgress}>{copy.progressValue(done, FIELD_KEYS.length)}</p>
          <div
            className={styles.progressTicks}
            role="progressbar"
            aria-label={copy.progressLabel}
            aria-valuemin={0}
            aria-valuemax={FIELD_KEYS.length}
            aria-valuenow={done}
          >
            {FIELD_KEYS.map((key, index) => (
              <span
                className={index < done ? styles.progressTickDone : index === firstMissing ? styles.progressTickCurrent : undefined}
                key={key}
                aria-hidden="true"
              />
            ))}
          </div>
          <div className={styles.miniLedger} aria-label={copy.progressLabel}>
            {FIELD_KEYS.map((key, index) => {
              const value = session.slots[key]
              const verified = isSlotVerified(value)
              const active = !verified && index === firstMissing
              return (
                <div className={`${styles.miniSlot}${verified ? ` ${styles.miniSlotDone}` : ''}${active ? ` ${styles.miniSlotActive}` : ''}`} key={key}>
                  <span className={styles.miniSlotNumber}>{String(index + 1).padStart(2, '0')}</span>
                  <span className={styles.miniSlotLabel}>{fields[index][0]}</span>
                  <span className={styles.miniSlotState} aria-hidden="true">{verified ? '✓' : active ? '◌' : '·'}</span>
                  {verified && <span className={styles.miniSlotValue}>{String(value)}</span>}
                </div>
              )
            })}
          </div>
        </div>

        <div className={styles.telemetryStatusRow} aria-label="Telemetry status">
          <div className={styles.telemetryChip}>8000 Hz • MONO</div>
          <div className={styles.telemetryChip}>1024 B / 64 ms</div>
          <div className={styles.telemetryChip}>VAD 0.72</div>
        </div>
        <div className={`${styles.voiceCore}${orbActive ? ` ${styles.voiceCoreActive}` : ''}`}>
          <span className={styles.voiceHalo} aria-hidden="true" />
          <span className={styles.voiceHaloInner} aria-hidden="true" />
          <AcousticOrb active={orbActive} levels={waveform} label={copy.speakAnswer} />
          <MicrophoneButton
            isRecording={mic.live}
            disabled={(!canUseMicrophone && !mic.live) || workerPhase === 'thinking'}
            state={workerError ? 'error' : mic.live ? 'listening' : workerPhase as 'idle' | 'thinking' | 'speaking'}
            onClick={toggleMicrophone}
            ariaLabel={mic.live ? copy.stopRecording : copy.speakAnswer}
          />
        </div>
        <p className={styles.workerState} role="status" aria-live="polite">
          {mic.live
            ? copy.workerListening
            : workerPhase === 'thinking'
              ? copy.workerThinking
              : workerPhase === 'speaking'
                ? copy.workerSpeaking
                : copy.workerReady}
        </p>
        {sample && session.consentState !== 'awaiting'
          ? <p className={styles.workerMicHint}>{copy.sampleMicHint}</p>
          : session.consentState !== 'awaiting' && !mic.live && workerPhase === 'idle' && <p className={styles.workerMicHint}>{copy.micHint}</p>}
        {session.consentState !== 'awaiting' && (sample || session.mode === 'LIVE') && (
          <details className={styles.demoMenu}>
            <summary><span>{copy.demoMenu}</span><small>Sample Ready</small></summary>
            <div className={styles.demoContent}>
              {sample && (
                <>
                  <p>{copy.sampleDetails}</p>
                  <button type="button" disabled={!session.online} onClick={playSample}>{copy.playSample}</button>
                </>
              )}
              {session.mode === 'LIVE' && (
                <>
                  <p>{copy.replaySyntheticHint}</p>
                  <button type="button" disabled={!session.online || session.replayActive} onClick={() => send({ type: 'replay_recorded_call' })}>
                    {session.replayActive ? copy.replayActive : copy.replayRecordedCall}
                  </button>
                </>
              )}
            </div>
          </details>
        )}
        {session.audit && session.consentState === 'awaiting' && (
          <ConsentBar
            copy={copy}
            state={session.consentState}
            voiceConsentRecorded={session.voiceConsentRecorded}
            readback={session.readback || session.audit.timbre_v3_readback_script}
            language={displayLanguage}
            audioUrl={session.timbreAudioUrl}
            audioRef={readbackAudio}
            audioNotice={audioNotice}
            pdfUrl={session.pdfUrl}
            jsonUrl={session.jsonUrl}
            onPrepare={prepareDraft}
            onDelete={session.deleteClaim}
            deletingClaim={session.deletingClaim}
            onConsentAnswer={session.online ? answerConsent : undefined}
            isSpeaking={workerPhase === 'speaking'}
            onSpeakingChange={(speaking) => setWorkerPhase((phase) => speaking ? 'speaking' : phase === 'speaking' ? 'idle' : phase)}
            onAudioNotice={setAudioNotice}
            worker
          />
        )}
        {mic.error && <p className={styles.workerError} role="alert">{copy.microphoneError}</p>}
        {timbreNotice && session.consentState === 'awaiting' && (
          <p className={styles.workerNotice} role="status">{timbreNotice}</p>
        )}
        {serviceMessage && <p className={styles.workerError} role="alert">{serviceMessage}</p>}
        {session.serviceUnavailable && (
          <p className={styles.workerError} role="alert">
            Voice service unavailable. Continue with typed answers; live-collected details are retained.
          </p>
        )}
        {session.audit?.draft_warning && (
          <p className={styles.workerNotice} role="alert">
            Drafting incomplete: {session.audit.draft_warning}
          </p>
        )}

        {session.consentState !== 'awaiting' && <div className={styles.workerTyping}>
          <TypeInputField
            value={typed}
            onChange={setTyped}
            onSubmit={() => {
              if (!typed.trim()) return
              setWorkerPhase('thinking')
              send({ type: 'utterance', text: typed.trim() })
              setTyped('')
            }}
            placeholder={copy.typeAnswer}
            disabled={!session.online || session.serviceUnavailable}
            copy={{ typeInstead: copy.typeInstead, typeAnswer: copy.typeAnswer, sendAnswer: copy.sendAnswer }}
          />
        </div>}

        {session.consentState !== 'awaiting' && <details className={styles.workerPaperPreview}>
          <summary><span>{copy.paperPreview}</span><small>Section 15(2) Draft</small></summary>
          <PaperForm
            copy={copy}
            fields={fields}
            slots={session.slots}
            audit={session.audit}
            sample={sample}
            compact
            arrearsDisplayValue={arrearsDisplayValue}
          />
        </details>}
        {session.consentState !== 'awaiting' && (
          <div className={styles.workerFooter}>
            <label className={styles.readAloudToggle}>
              <input type="checkbox" checked={readAloud} onChange={(event) => setReadAloud(event.target.checked)} />
              <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 10v4h4l5 4V6l-5 4H4Zm13.5-2a6 6 0 1 1 0 8M16 5a10 10 0 1 1 0 14" /></svg>
              <span>{copy.readQuestionsAloud}</span>
            </label>
          </div>
        )}
        {session.audit && session.consentState !== 'awaiting' && (
          <ConsentBar
            copy={copy}
            state={session.consentState}
            voiceConsentRecorded={session.voiceConsentRecorded}
            readback={session.readback || session.audit.timbre_v3_readback_script}
            language={displayLanguage}
            audioUrl={session.timbreAudioUrl}
            audioRef={readbackAudio}
            audioNotice={audioNotice}
            pdfUrl={session.pdfUrl}
            jsonUrl={session.jsonUrl}
            onPrepare={prepareDraft}
            onDelete={session.deleteClaim}
            deletingClaim={session.deletingClaim}
            onConsentAnswer={session.online ? answerConsent : undefined}
            isSpeaking={workerPhase === 'speaking'}
            onSpeakingChange={(speaking) => setWorkerPhase((phase) => speaking ? 'speaking' : phase === 'speaking' ? 'idle' : phase)}
            onAudioNotice={setAudioNotice}
            worker
          />
        )}
      </section>
      </main>
    </>
  )
}
