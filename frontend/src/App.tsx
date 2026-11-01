import { useCallback, useEffect, useState } from 'react'
import './App.css'
import { useMicrophone } from './hooks/useMicrophone'
import { useSession } from './hooks/useSession'
import type { Audit } from './hooks/useSession'

const FIELDS: [string, string, string][] = [
  ['worker_name', 'नाम', 'Your name'],
  ['worksite_locality_and_sphere', 'काम की जगह', 'Worksite'],
  ['contractor_name_and_phone', 'ठेकेदार', 'Contractor'],
  ['principal_employer_name', 'कंपनी / मालिक', 'Company or owner'],
  ['wage_period_start', 'शुरू की तारीख', 'Start date'],
  ['wage_period_end', 'आख़िरी तारीख', 'Last day'],
  ['days_worked', 'काम के दिन', 'Days worked'],
  ['agreed_daily_wage_inr', 'रोज़ की दिहाड़ी', 'Daily wage'],
  ['advance_received_inr', 'अब तक मिले रुपये', 'Already paid'],
]
const ICON: Record<string, string> = { pass: '✓', fail: '✕', warn: '!', unknown: '–' }
const inr = (n: number) => `₹${n.toLocaleString('en-IN')}`
const plain = (s: string) => s.replace(/<[^>]+>/g, ' ')

function speak(text: string) {          // preview voice; replace with Timbre audio once relayed
  if (!text || !('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(plain(text))
  u.lang = 'hi-IN'
  window.speechSynthesis.speak(u)
}

function Result({ audit, onConfirm, pdfUrl }: { audit: Audit; onConfirm: () => void; pdfUrl: string | null }) {
  return (
    <section className="card result" aria-live="polite">
      <p className="hint">आपकी बकाया मज़दूरी / Wages owed to you</p>
      <p className="amount">{inr(audit.principal_arrears_inr)}</p>
      <ul className="checks">
        {audit.checks.map((c) => (
          <li key={c.id} className={c.status}><b aria-hidden>{ICON[c.status]}</b> {c.label}<small> — {c.status}: {c.detail}</small></li>
        ))}
      </ul>
      <p className="notice">{audit.notice}</p>
      {pdfUrl ? <a className="btn primary" href={pdfUrl}>फ़ॉर्म A डाउनलोड करें · Download Form A</a>
        : <button className="btn primary" onClick={onConfirm}>हाँ, शिकायत तैयार करें · Yes, prepare my claim</button>}
    </section>
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
  const mic = useMicrophone({
    onFrame: sendAudio,
    onStart: useCallback(() => send({ type: 'start_mic' }), [send]),
    onStop: useCallback(() => send({ type: 'stop_mic' }), [send]),
  })

  useEffect(() => { document.documentElement.dataset.theme = dark ? 'dark' : 'light' }, [dark])
  useEffect(() => { if (voice) speak(s.followup) }, [s.followup, voice])
  useEffect(() => { if (voice && s.audit) speak(s.audit.timbre_v3_readback_script) }, [s.audit, voice])

  const done = FIELDS.filter(([k]) => s.slots[k] !== null && s.slots[k] !== undefined).length
  const question = s.followup || (done === 0 ? 'अपनी बात अपने शब्दों में बताइए।' : 'धन्यवाद।')

  return (
    <main className="app">
      <header className="top">
        <h1>श्रमिक-न्याय <span>Shramik-Nyay</span></h1>
        <div className="tools">
          <span className={`pill ${s.online ? 'ok' : 'wait'}`}>{s.online ? `Connected · ${s.mode}` : 'Reconnecting…'}</span>
          <button className="btn" onClick={() => setVoice(!voice)} aria-pressed={voice}>Voice {voice ? 'on' : 'off'}</button>
          <button className="btn" onClick={() => setDark(!dark)}>{dark ? 'Light theme' : 'Dark theme'}</button>
          <button className="btn" onClick={() => setEngineer(!engineer)} aria-pressed={engineer}>Engineer view</button>
        </div>
      </header>

      <div className="body">
        <div className="main">
          {s.audit ? <Result audit={s.audit} pdfUrl={s.pdfUrl} onConfirm={() => s.send({ type: 'confirm' })} /> : (
            <section className="card ask">
              <p className="hint">{done === 0 ? 'शुरू करें / Start here' : `${done} of ${FIELDS.length} answered`}</p>
              <p className="question" lang="hi">{question}</p>
              <div className="wave" aria-hidden>{mic.levels.map((l, i) => <i key={i} style={{ height: `${8 + l * 92}%` }} />)}</div>
              <button className={`btn big ${mic.live ? 'stop' : 'primary'}`} disabled={(!s.online || s.mode !== 'LIVE') && !mic.live} onClick={() => (mic.live ? mic.stop() : void mic.start(noise))}>
                {mic.live ? 'रोकें · Stop' : '🎤 बोलना शुरू करें · Start speaking'}
              </button>
              {s.online && s.mode !== 'LIVE' && <p className="hint" role="status">Live speech recognition is off in {s.mode || 'mock'} mode. Type your answer or use the sample claim. To enable microphone transcription, set SHRAMIK_MODE=LIVE in backend/.env.</p>}
              {mic.error && <p className="error" role="alert">{mic.error}</p>}
              <form className="row" onSubmit={(e) => { e.preventDefault(); if (typed.trim()) { s.send({ type: 'utterance', text: typed }); setTyped('') } }}>
                <input value={typed} onChange={(e) => setTyped(e.target.value)} placeholder="या यहाँ लिखिए · Or type your answer" aria-label="Type your answer" />
                <button className="btn" disabled={!s.online}>Send</button>
              </form>
              <form className="row" onSubmit={(e) => { e.preventDefault(); s.send({ type: 'uan', value: uan }) }}>
                <input value={uan} onChange={(e) => setUan(e.target.value)} inputMode="numeric" placeholder="e-Shram UAN (optional, 12 digits)" aria-label="e-Shram UAN" />
                <button className="btn" disabled={!s.online}>Check</button>
              </form>
              <div className="row">
                <button className="btn" disabled={!s.online} onClick={() => s.send({ type: 'demo' })}>Run sample claim</button>
                <label className="check"><input type="checkbox" checked={noise} onChange={(e) => setNoise(e.target.checked)} /> Simulate construction-site line</label>
              </div>
              {s.message && <p className="error" role="status">{s.message}</p>}
            </section>
          )}
        </div>

        <aside className="card list" aria-label="Claim details">
          <h2>आपकी जानकारी <small>Your details</small></h2>
          <ul>
            {FIELDS.map(([k, hi, en]) => {
              const v = s.slots[k]
              const ok = v !== null && v !== undefined
              return <li key={k} className={ok ? 'ok' : ''}><b aria-hidden>{ok ? '✓' : '○'}</b><span lang="hi">{hi}<small> {en}</small></span><em>{ok ? String(v) : 'बाकी · pending'}</em></li>
            })}
          </ul>
        </aside>

        {engineer && (
          <aside className="card tech" aria-label="Engineer view">
            <h2>Pipeline <small>8 kHz · 1024 B / 64 ms · VAD 0.72</small></h2>
            <p>Prisma latency: <b>{s.latency ?? '—'} ms</b></p>
            <p>Boosted words: {s.biasWords.join(', ') || '—'}</p>
            <p>Heard: {s.heard.slice(-2).join(' | ') || '—'}</p>
            <ol className="events">{s.events.slice(-8).reverse().map((e, i) => <li key={i}><b>{e.type}</b> <code>{JSON.stringify(e).slice(0, 90)}</code></li>)}</ol>
          </aside>
        )}
      </div>
    </main>
  )
}
