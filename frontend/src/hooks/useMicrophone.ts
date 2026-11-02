import { useCallback, useRef, useState } from 'react'

type Options = { onFrame: (buf: ArrayBuffer) => void; onStart: () => void; onStop: () => void }

export function useMicrophone({ onFrame, onStart, onStop }: Options) {
  const [live, setLive] = useState(false)
  const [levels, setLevels] = useState<number[]>(() => Array(28).fill(0))
  const [error, setError] = useState('')
  const parts = useRef<{ ctx: AudioContext; stream: MediaStream; node: AudioWorkletNode } | null>(null)

  const stop = useCallback(() => {
    const p = parts.current
    if (!p) return
    p.node.disconnect(); p.stream.getTracks().forEach((t) => t.stop()); void p.ctx.close()
    parts.current = null; setLive(false); onStop()
  }, [onStop])

  const noiseLevel = useRef(0)
  const updateNoiseLevel = useCallback((level: number) => {
    if (!Number.isFinite(level)) return
    noiseLevel.current = Math.max(0, Math.min(100, level))
    parts.current?.node.port.postMessage({ level: noiseLevel.current })
  }, [])

  const start = useCallback(async (initialNoiseLevel: number) => {
    updateNoiseLevel(initialNoiseLevel)
    setError('')
    let stream: MediaStream | undefined
    let ctx: AudioContext | undefined
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, echoCancellation: true } })
      ctx = new AudioContext()
      await ctx.resume()
      await ctx.audioWorklet.addModule('/pcm-worklet.js')
      const node = new AudioWorkletNode(ctx, 'pcm-8k')
      const mute = ctx.createGain()
      mute.gain.value = 0
      node.port.postMessage({ level: noiseLevel.current })
      node.port.onmessage = (e: MessageEvent<ArrayBuffer>) => {
        onFrame(e.data)
        const pcm = new Int16Array(e.data)
        let sum = 0
        for (const v of pcm) sum += v * v
        const rms = Math.min(1, Math.sqrt(sum / pcm.length) / 6000)
        setLevels((cur) => [...cur.slice(1), rms])
      }
      ctx.createMediaStreamSource(stream).connect(node)
      node.connect(mute).connect(ctx.destination)
      parts.current = { ctx, stream, node }
      setLive(true); onStart()
    } catch {
      stream?.getTracks().forEach((track) => track.stop())
      if (ctx && ctx.state !== 'closed') await ctx.close()
      setError('Microphone blocked. Allow microphone access in the browser, or type the answer instead.')
    }
  }, [onFrame, onStart, updateNoiseLevel])

  return { live, levels, error, start, stop, updateNoiseLevel }
}
