import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import './App.css'
import styles from './App.module.css'
import AudioLine, { MicIcon } from './components/AudioLine'
import ClaimSlots from './components/ClaimSlots'
import ConsentBar from './components/ConsentBar'
import Header from './components/Header'
import PaperForm from './components/PaperForm'
import Transcript from './components/Transcript'
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
  const [showTyping, setShowTyping] = useState(false)
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

  const submitAnswer = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!typed.trim()) return
    setWorkerPhase('thinking')
    send({ type: 'utterance', text: typed.trim() })
    setTyped('')
  }
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
    )
  }

  return (
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
                className={index < done ? styles.progressTickDone : undefined}
                key={key}
                aria-hidden="true"
              />
            ))}
          </div>
        </div>

        <button
          className={`${styles.workerMic}${mic.live ? ` ${styles.recording}` : ''}`}
          type="button"
          disabled={(!canUseMicrophone && !mic.live) || workerPhase === 'thinking'}
          onClick={toggleMicrophone}
          aria-label={mic.live ? copy.stopRecording : copy.speakAnswer}
          data-state={workerError ? 'error' : mic.live ? 'listening' : workerPhase}
        >
          <MicIcon />
        </button>
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
            <summary>{copy.demoMenu}</summary>
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
          {!showTyping && !session.serviceUnavailable ? (
            <button className={styles.textToggle} type="button" onClick={() => setShowTyping(true)}>{copy.typeInstead}</button>
          ) : (
            <form className={styles.workerTextEntry} onSubmit={submitAnswer}>
              <label className="visually-hidden" htmlFor="worker-answer">{copy.typeAnswer}</label>
              <textarea
                id="worker-answer"
                rows={2}
                value={typed}
                onChange={(event) => setTyped(event.target.value)}
                placeholder={copy.typeAnswer}
                autoFocus
              />
              <button type="submit" disabled={!session.online || !typed.trim()}>{copy.sendAnswer}</button>
            </form>
          )}
        </div>}

        {session.consentState !== 'awaiting' && <details className={styles.workerPaperPreview}>
          <summary>{copy.paperPreview}</summary>
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
      <footer className={styles.workerFooter}>
        <label className={styles.readAloudToggle}>
          <input type="checkbox" checked={readAloud} onChange={(event) => setReadAloud(event.target.checked)} />
          {copy.readQuestionsAloud}
        </label>
      </footer>
    </main>
  )
}
