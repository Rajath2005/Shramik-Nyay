import { useCallback, useEffect, useRef, useState } from 'react'

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

const WS_URL: string = import.meta.env.VITE_WS_URL ?? 'ws://127.0.0.1:8000/ws/session'
export const API_BASE = WS_URL.replace(/^ws/, 'http').replace(/\/ws\/session$/, '')

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
  const [latency, setLatency] = useState<number | null>(null)
  const [message, setMessage] = useState('')

  useEffect(() => {
    let closed = false
    let sock: WebSocket
    const handle = (e: Ev) => {
      setEvents((cur) => [...cur.slice(-39), e])
      switch (e.type) {
        case 'session_started':
          setMode(String(e.mode)); setSlots({}); setAudit(null); setPdfUrl(null); setHeard([]); setFollowup(''); setMessage('')
          break
        case 'evon_stage_a':
          setSlots(e.slots as Slots); setFollowup(String(e.followup ?? ''))
          break
        case 'evon_stage_b_complete':
          setAudit(e as unknown as Audit)
          break
        case 'prisma_transcript':
          setHeard((cur) => [...cur.slice(-5), String(e.text)]); setLatency(Number(e.latency ?? 0))
          break
        case 'bias_boost_triggered':
          setBiasWords(e.words as string[])
          break
        case 'claim_ready':
          setPdfUrl(API_BASE + String(e.pdf_url))
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
      ws.current = sock
      sock.onopen = () => setOnline(true)
      sock.onclose = () => { setOnline(false); if (!closed) window.setTimeout(open, 1500) }
      sock.onmessage = (m) => handle(JSON.parse(m.data))
    }
    open()
    return () => { closed = true; sock.close() }
  }, [])

  const send = useCallback((cmd: object) => {
    if (ws.current?.readyState === WebSocket.OPEN) ws.current.send(JSON.stringify(cmd))
    else setMessage('Not connected to the claim service. Wait for reconnection and try again.')
  }, [])
  const sendAudio = useCallback((buf: ArrayBuffer) => {
    if (ws.current?.readyState === WebSocket.OPEN) ws.current.send(buf)
  }, [])

  return { online, mode, slots, followup, audit, pdfUrl, heard, events, biasWords, latency, message, send, sendAudio }
}
