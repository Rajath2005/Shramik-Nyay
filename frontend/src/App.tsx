import { useEffect, useMemo, useRef, useState } from 'react'
import './App.css'

type SessionEvent = {
  type: string
  [key: string]: unknown
}

const slots = [
  ['worker_name', 'Worker'],
  ['eshram_uan', 'e-Shram UAN'],
  ['worksite_locality_and_sphere', 'Worksite'],
  ['contractor_name_and_phone', 'Contractor'],
  ['principal_employer_name', 'Principal employer'],
  ['wage_period_dates', 'Wage period'],
  ['days_worked', 'Days worked'],
  ['agreed_daily_wage_inr', 'Daily wage'],
]

function App() {
  const socket = useRef<WebSocket | null>(null)
  const [events, setEvents] = useState<SessionEvent[]>([])
  const [connected, setConnected] = useState(false)
  const [live, setLive] = useState(false)

  const latestSlots = useMemo(() => {
    const event = [...events].reverse().find((item) => item.type === 'evon_stage_a')
    return (event?.slots ?? {}) as Record<string, unknown>
  }, [events])

  useEffect(() => () => socket.current?.close(), [])

  function connect() {
    const next = new WebSocket('ws://127.0.0.1:8000/ws/session')
    next.onopen = () => setConnected(true)
    next.onclose = () => setConnected(false)
    next.onmessage = (message) => setEvents((current) => [...current.slice(-29), JSON.parse(message.data)])
    socket.current = next
  }

  function runDemo() {
    if (!socket.current || socket.current.readyState !== WebSocket.OPEN) connect()
    window.setTimeout(() => socket.current?.send('demo'), 250)
  }

  return (
    <main className="console">
      <header className="topbar">
        <div>
          <p className="eyebrow">SHRAMIK-NYAY / LEGAL REDRESSAL STUDIO</p>
          <h1>Voice-led wage claim telemetry</h1>
        </div>
        <div className="actions">
          <span className={`status ${connected ? 'online' : ''}`}><i /> {connected ? 'BRIDGE ONLINE' : 'BRIDGE OFFLINE'}</span>
          <button onClick={connect}>Connect</button>
          <button className="primary" onClick={runDemo}>Run mock replay</button>
        </div>
      </header>

      <section className="metrics">
        <Metric label="Pacer cadence" value="64 ms" tone="blue" />
        <Metric label="PCM frame" value="1024 B" tone="emerald" />
        <Metric label="STT model" value="PRISMA v3.0" tone="amber" />
        <Metric label="Reasoning" value="EVON v3.3" tone="blue" />
      </section>

      <section className="grid">
        <Panel title="01 / Prisma voice uplink" subtitle="Raw pcm_s16le · mono · 8 kHz">
          <div className="waveform">{Array.from({ length: 42 }, (_, index) => <span key={index} style={{ height: `${18 + ((index * 17) % 52)}%` }} />)}</div>
          <div className="telemetry-row"><span><i className="dot emerald" />AudioWorklet ready</span><strong>8,000 Hz</strong></div>
          <div className="telemetry-row"><span><i className="dot amber" />VAD threshold</span><strong>0.72</strong></div>
          <button className={live ? 'danger' : 'secondary'} onClick={() => setLive(!live)}>{live ? 'Stop microphone' : 'Start microphone'}</button>
        </Panel>

        <Panel title="02 / Form-A slot ledger" subtitle="Eight statutory facts captured in conversation">
          <div className="slot-list">{slots.map(([key, label]) => <div className="slot" key={key}><span>{label}</span><b className={latestSlots[key] ? 'filled' : ''}>{String(latestSlots[key] ?? 'awaiting')}</b></div>)}</div>
        </Panel>

        <Panel title="03 / Event stream" subtitle="Full-duplex bridge observability">
          <div className="event-list">{events.length === 0 ? <p className="empty">Run a mock replay to inspect the golden trace.</p> : events.slice(-7).reverse().map((event, index) => <div className="event" key={`${event.type}-${index}`}><span className="event-time">{String(event.type).replaceAll('_', ' ')}</span><code>{JSON.stringify(event).slice(0, 100)}</code></div>)}</div>
        </Panel>

        <Panel title="04 / Statutory audit" subtitle="Payment of Wages Act, 1936">
          <div className="audit-card">
            <span>Principal arrears</span>
            <strong>₹{String([...events].reverse().find((event) => event.type === 'evon_stage_b_complete')?.principal_arrears_inr ?? '—')}</strong>
          </div>
          <div className="audit-card">
            <span>Section 15(3) compensation</span>
            <strong>₹{String([...events].reverse().find((event) => event.type === 'evon_stage_b_complete')?.statutory_compensation_inr ?? '—')}</strong>
          </div>
          <p className="script">{String([...events].reverse().find((event) => event.type === 'timbre_audio')?.script ?? 'Timbre read-back script will appear here.')}</p>
        </Panel>
      </section>
    </main>
  )
}

function Metric({ label, value, tone }: { label: string; value: string; tone: string }) {
  return <div className="metric"><span className={`metric-icon ${tone}`} /><div><small>{label}</small><strong>{value}</strong></div></div>
}

function Panel({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return <article className="panel"><div className="panel-heading"><div><p className="eyebrow">{title}</p><h2>{subtitle}</h2></div><span className="panel-mark">●</span></div>{children}</article>
}

export default App
