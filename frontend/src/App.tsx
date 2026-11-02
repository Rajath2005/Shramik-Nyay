import { useCallback, useEffect, useRef, useState } from 'react'
import './App.css'
import { useMicrophone } from './hooks/useMicrophone'
import { useSession } from './hooks/useSession'
import {
  COPY,
  FIELD_LABELS,
  isLanguagePreference,
  LANGUAGE_LABELS,
  LANGUAGE_OPTIONS,
  type SupportedLanguage,
} from './language'

const FIELD_KEYS = [
  'worker_name',
  'worksite_locality_and_sphere',
  'contractor_name_and_phone',
  'principal_employer_name',
  'wage_period_start',
  'wage_period_end',
  'days_worked',
  'agreed_daily_wage_inr',
  'advance_received_inr',
]

const EMPTY_WAVEFORM = Array.from({ length: 28 }, () => 0.035)
const ICON: Record<string, string> = { pass: '✓', fail: '×', warn: '!', unknown: '–' }
const inr = (n: number) => `₹${n.toLocaleString('en-IN')}`
const plain = (s: string) => s.replace(/<[^>]+>/g, ' ')

function speak(text: string, language: string) {
  if (!text || !('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(plain(text))
  utterance.lang = language
  window.speechSynthesis.speak(utterance)
}

function PanelHeading({ title, detail }: { title: string; detail?: string }) {
  return (
    <div className="panel-heading">
      <h2>{title}</h2>
      {detail && <span>{detail}</span>}
    </div>
  )
}

export default function App() {
  const s = useSession()
  const { send, sendAudio } = s
  const [engineer, setEngineer] = useState(false)
  const [dark, setDark] = useState(() => window.matchMedia('(prefers-color-scheme: dark)').matches)
  const [voice, setVoice] = useState(true)
  const [noise, setNoise] = useState(false)
  const [typed, setTyped] = useState('')
  const [uan, setUan] = useState('')
  const [audioNotice, setAudioNotice] = useState('')
  const readbackAudio = useRef<HTMLAudioElement>(null)
  const mic = useMicrophone({
    onFrame: sendAudio,
    onStart: useCallback(() => send({ type: 'start_mic' }), [send]),
    onStop: useCallback(() => send({ type: 'stop_mic' }), [send]),
  })

  const displayLanguage: SupportedLanguage =
    s.effectiveLanguage === 'kn-IN' || s.effectiveLanguage === 'en-IN' || s.effectiveLanguage === 'hi-IN'
      ? s.effectiveLanguage
      : s.languagePreference === 'auto' ? 'hi-IN' : s.languagePreference
  const transcriptLanguage: SupportedLanguage =
    s.detectedLanguage === 'kn-IN' || s.detectedLanguage === 'en-IN' || s.detectedLanguage === 'hi-IN'
      ? s.detectedLanguage
      : displayLanguage
  const copy = COPY[displayLanguage]
  const fields = FIELD_LABELS[displayLanguage]

  useEffect(() => { document.documentElement.dataset.theme = dark ? 'dark' : 'light' }, [dark])
  useEffect(() => { if (voice) speak(s.followup, displayLanguage) }, [s.followup, voice, displayLanguage])
  useEffect(() => {
    if (voice && s.audit && (s.mode !== 'LIVE' || s.timbreUnavailable)) {
      speak(s.audit.timbre_v3_readback_script, displayLanguage)
    }
  }, [s.audit, s.mode, s.timbreUnavailable, voice, displayLanguage])
  useEffect(() => {
    if (!voice || !s.timbreAudioUrl || !readbackAudio.current) return
    void readbackAudio.current.play().then(() => setAudioNotice('')).catch(() => {
      setAudioNotice(copy.audioReady)
    })
  }, [s.timbreAudioUrl, voice, copy.audioReady])

  const done = FIELD_KEYS.filter((key) => s.slots[key] !== null && s.slots[key] !== undefined).length
  const question = s.followup || (done === 0 ? copy.welcome : copy.thankYou)
  const waveform = s.telemetry?.source === 'mock' ? s.signalLevels : mic.levels
  const levels = waveform.length ? waveform : EMPTY_WAVEFORM

  return (
    <main className="app">
      <header className="topbar">
        <div className="brand" aria-label="Shramik-Nyay">
          <span className="brand-mark" aria-hidden>श्रम</span>
          <span><strong>श्रमिक-न्याय</strong><small>{copy.studio}</small></span>
        </div>
        <div className="top-actions">
          <span className={`connection ${s.online ? 'connected' : ''}`}>
            <i aria-hidden />{s.online ? `Connected · ${s.mode}` : 'Connecting'}
          </span>
          <button className="quiet-button" onClick={() => setVoice(!voice)} aria-pressed={voice}>
            {copy.readAloud} {voice ? copy.on : copy.off}
          </button>
          <button className="quiet-button" onClick={() => setDark(!dark)}>
            {dark ? copy.lightTheme : copy.darkTheme}
          </button>
          <button className="quiet-button" onClick={() => setEngineer(!engineer)} aria-pressed={engineer}>
            {copy.engineer}
          </button>
        </div>
      </header>

      <section className="intake" aria-label="Claim conversation">
        <div className="intake-prompt">
          <p className="eyebrow">{copy.eyebrow}</p>
          <h1 lang={displayLanguage}>{question}</h1>
          <p className="intake-progress">{done}/{FIELD_KEYS.length} {copy.progress}</p>
        </div>
        <div className="intake-actions">
          <div className="language-control">
            <label htmlFor="language-choice">{copy.language}</label>
            <select
              id="language-choice"
              value={s.languagePreference}
              disabled={mic.live}
              onChange={(event) => {
                if (isLanguagePreference(event.target.value)) s.setLanguagePreference(event.target.value)
              }}
            >
              {LANGUAGE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.value === 'auto' ? copy.autoDetect : option.label}
                </option>
              ))}
            </select>
            <span className="language-status">
              {s.languagePreference === 'auto'
                ? s.effectiveLanguage ? `${copy.autoHint} ${LANGUAGE_LABELS[displayLanguage]}` : copy.autoHint
                : LANGUAGE_LABELS[displayLanguage]}
            </span>
          </div>
          <form className="text-entry" onSubmit={(event) => {
            event.preventDefault()
            if (typed.trim()) {
              s.send({ type: 'utterance', text: typed })
              setTyped('')
            }
          }}>
            <input value={typed} onChange={(event) => setTyped(event.target.value)} placeholder={copy.inputPlaceholder} aria-label={copy.inputPlaceholder} />
            <button className="action-button" type="submit" disabled={!s.online}>{copy.send}</button>
          </form>
          <div className="action-row">
            <form className="uan-entry" onSubmit={(event) => {
              event.preventDefault()
              s.send({ type: 'uan', value: uan })
            }}>
              <input value={uan} onChange={(event) => setUan(event.target.value)} inputMode="numeric" placeholder={copy.uanPlaceholder} aria-label={copy.uanPlaceholder} />
              <button className="quiet-button" type="submit" disabled={!s.online}>{copy.check}</button>
            </form>
            <button className="action-button replay-button" disabled={!s.online || s.mode !== 'MOCK_REPLAY'} onClick={() => s.send({ type: 'demo' })}>
              {s.mode === 'LIVE' ? copy.replayOff : copy.runSample}
            </button>
            <button
              className={`quiet-button mic-button ${mic.live ? 'is-live' : ''}`}
              disabled={(!s.online || s.mode !== 'LIVE') && !mic.live}
              onClick={() => (mic.live ? mic.stop() : void mic.start(noise))}
            >
              {mic.live ? copy.stopSpeaking : copy.startSpeaking}
            </button>
          </div>
          {s.online && s.mode !== 'LIVE' && <p className="mode-note">{copy.mockHint}</p>}
          {mic.error && <p className="inline-error" role="alert">{mic.error}</p>}
          {s.message && <p className="inline-error" role="status">{s.message}</p>}
          {s.mode === 'LIVE' && (
            <label className="noise-toggle">
              <input type="checkbox" checked={noise} onChange={(event) => setNoise(event.target.checked)} />
              {copy.simulateNoise}
            </label>
          )}
        </div>
      </section>

      <section className="studio-grid" aria-label="Claim processing studio">
        <article className="panel acoustic-panel">
          <PanelHeading title={copy.audioLine} detail={s.telemetry?.source === 'mock' ? copy.syntheticReplay : mic.live ? copy.microphoneLive : copy.waitingSpeech} />
          <div className="waveform" role="img" aria-label={mic.live ? 'Live microphone level' : 'Sample audio waveform'}>
            {levels.map((level, index) => <i key={index} style={{ height: `${Math.max(7, 8 + level * 92)}%` }} />)}
          </div>
          <div className="signal-caption"><span>8 kHz narrowband</span><span>{mic.live ? copy.inputActive : s.telemetry?.source === 'mock' ? copy.replayComplete : copy.noAudio}</span></div>
          <div className="telemetry-grid">
            <div><small>{copy.frameSize}</small><strong>{s.telemetry?.frameBytes ?? 1024} B</strong></div>
            <div><small>{copy.frameCadence}</small><strong>{s.telemetry?.cadenceMs ?? 64} ms</strong></div>
            <div><small>{copy.vadThreshold}</small><strong>{s.telemetry?.vadThreshold?.toFixed(2) ?? '0.72'}</strong></div>
            <div><small>{copy.transcriptLatency}</small><strong>{s.latency !== null ? `${s.latency} ms` : '—'}</strong></div>
          </div>
          <div className="pipeline-latencies" aria-label="Pipeline latency">
            {([
              ['Prisma segment', 'prisma_segment'],
              ['Evon Stage A', 'evon_stage_a'],
              ['Evon Stage B', 'evon_stage_b'],
              ['Timbre first audio', 'timbre_first_audio_chunk'],
            ] as const).map(([label, stage]) => (
              <div key={stage}><small>{label}</small><strong>{s.pipelineLatencies[stage] ?? '—'}{s.pipelineLatencies[stage] === undefined ? '' : ' ms'}</strong></div>
            ))}
          </div>
          <div className="bias-row">
            <span className="sub-label">{copy.recognizeWords}</span>
            <div className={`word-pills ${s.biasSettingsUpdated ? 'is-confirmed' : 'is-pending'}`}>
              {s.biasWords.length ? s.biasWords.map((word) => <span key={word}>{word}</span>) : <span className="muted">{copy.noBoostedWords}</span>}
              {s.biasWords.length > 0 && (
                <span className="bias-confirmation" role="status">
                  {s.biasSettingsUpdated
                    ? 'settings_updated'
                    : s.biasBoostFailed ? 'settings_update_failed' : 'awaiting settings_updated'}
                </span>
              )}
            </div>
          </div>
        </article>

        <article className="panel transcript-panel">
          <PanelHeading
            title={copy.workerWords}
            detail={s.languagePreference === 'auto'
              ? s.detectedLanguage || copy.audioWaiting
              : LANGUAGE_LABELS[displayLanguage]}
          />
          {s.transcript
            ? <p className="transcript-text" lang={transcriptLanguage}>{s.transcript}</p>
            : <p className="empty-copy">{copy.transcriptEmpty}</p>}
          <div className="transcript-foot">
            <span className={`status-dot ${s.transcript ? 'is-ready' : ''}`} />
            {s.transcript ? copy.transcriptCaptured : copy.waitingTranscript}
          </div>
        </article>

        <article className="panel claim-panel">
          <PanelHeading title={copy.claimDetails} detail={`${done}/${FIELD_KEYS.length} ${copy.collected}`} />
          <ul className="slot-ledger">
            {FIELD_KEYS.map((key, index) => {
              const value = s.slots[key]
              const filled = value !== null && value !== undefined
              return (
                <li key={key} className={filled ? 'is-filled' : ''}>
                  <span className="slot-check" aria-hidden>{filled ? '✓' : '·'}</span>
                  <span className="slot-name"><b lang={displayLanguage}>{fields[index][0]}</b><small>{fields[index][1]}</small></span>
                  <span className="slot-value">{filled ? String(value) : copy.notProvided}</span>
                </li>
              )
            })}
          </ul>
          {s.audit && (
            <div className="audit-block">
              <p className="sub-label">{copy.ruleChecks}</p>
              <ul className="audit-list">
                {s.audit.checks.map((check) => (
                  <li key={check.id} className={`audit-${['pass', 'fail', 'warn'].includes(check.status) ? check.status : 'unknown'}`}>
                    <span aria-hidden>{ICON[check.status] ?? ICON.unknown}</span>
                    <span><b>{check.label}</b><small>{check.detail}</small></span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </article>

        <article className="panel document-panel">
          <PanelHeading title={copy.formDraft} detail={s.pdfUrl ? copy.readyDownload : copy.notFiled} />
          <div className="paper-preview">
            <div className="paper-heading">
              <span>SHRAMIK-NYAY</span>
              <small>WAGE CLAIM · DRAFT</small>
            </div>
            <p className="paper-intro">{copy.claimTitle}</p>
            <div className="paper-person">
              <small>{copy.worker}</small>
              <strong>{String(s.slots.worker_name ?? copy.awaitingWorker)}</strong>
              <span>{String(s.slots.worksite_locality_and_sphere ?? copy.worksiteMissing)}</span>
            </div>
            <div className="paper-amount">
              <small>{copy.estimatedArrears}</small>
              <strong>{s.audit ? inr(s.audit.principal_arrears_inr) : '—'}</strong>
            </div>
            <p className="paper-employer">{String(s.slots.principal_employer_name ?? copy.employerMissing)}</p>
            {s.audit?.legal_audit_summary && <p className="paper-summary">{s.audit.legal_audit_summary}</p>}
          </div>
          {s.readback && (
            <details className="readback">
              <summary>{copy.readback}</summary>
              <p lang={displayLanguage}>{plain(s.readback)}</p>
            </details>
          )}
          {s.timbreAudioUrl && (
            <div className="audio-readback">
              <span className="sub-label">{copy.timbreReadback}</span>
              <audio ref={readbackAudio} controls src={s.timbreAudioUrl}>{copy.audioUnsupported}</audio>
            </div>
          )}
          {audioNotice && <p className="legal-notice" role="status">{audioNotice}</p>}
          {s.audit?.notice && <p className="legal-notice">{s.audit.notice}</p>}
          <div className="document-actions">
            {s.pdfUrl && s.jsonUrl ? (
              <>
                <a className="action-button" href={s.pdfUrl} download>{copy.downloadPdf}</a>
                <a className="quiet-button" href={s.jsonUrl} download>{copy.downloadJson}</a>
              </>
            ) : (
              <button className="action-button" disabled={!s.audit} onClick={() => s.send({ type: 'confirm' })}>
                {copy.prepareDraft}
              </button>
            )}
          </div>
          <p className="draft-only-note">{copy.draftOnly}</p>
        </article>
      </section>

      {engineer && (
        <aside className="panel engineer-panel" aria-label="Engineer view">
          <PanelHeading title={copy.pipelineEvents} detail={copy.lastMessages} />
          <ol className="events">{s.events.slice(-8).reverse().map((event, index) => (
            <li key={`${event.type}-${index}`}><b>{event.type}</b><code>{JSON.stringify(event).slice(0, 140)}</code></li>
          ))}</ol>
        </aside>
      )}
    </main>
  )
}
