import { describe, expect, it } from 'vitest'
import { createConstructionTrafficNoise, createTelephonyBandpass } from '../public/audio-dsp.js'

function rms(samples) {
  return Math.sqrt(samples.reduce((sum, sample) => sum + sample * sample, 0) / samples.length)
}

function filteredToneRms(frequency, sampleRate = 8000) {
  const filter = createTelephonyBandpass(sampleRate)
  const samples = []
  for (let index = 0; index < sampleRate * 2; index += 1) {
    const output = filter(Math.sin(2 * Math.PI * frequency * index / sampleRate))
    if (index >= sampleRate) samples.push(output)
  }
  return rms(samples)
}

describe('audio DSP helpers', () => {
  it('passes speech-band tones and attenuates frequencies outside 300–3400 Hz', () => {
    const speechBand = filteredToneRms(1000)
    expect(speechBand).toBeGreaterThan(0.65)
    expect(filteredToneRms(100)).toBeLessThan(speechBand * 0.15)
    expect(filteredToneRms(3800)).toBeLessThan(speechBand * 0.4)
  })

  it('rejects invalid bandpass frequencies', () => {
    expect(() => createTelephonyBandpass(8000, 3400, 300)).toThrow(RangeError)
    expect(() => createTelephonyBandpass(8000, 300, 4000)).toThrow(RangeError)
    expect(() => createTelephonyBandpass(8000, Number.NaN, 3400)).toThrow(RangeError)
  })

  it('generates repeatable, finite ambience with injected randomness', () => {
    const first = createConstructionTrafficNoise(8000, () => 0.5)
    const second = createConstructionTrafficNoise(8000, () => 0.5)
    const samples = Array.from({ length: 8000 * 4 }, () => first())
    const replay = Array.from({ length: samples.length }, () => second())

    expect(samples).toEqual(replay)
    expect(samples.every(Number.isFinite)).toBe(true)
    expect(samples.some((sample) => Math.abs(sample) > 0.3)).toBe(true)
  })

  it('emits only 512-sample, 1024-byte PCM messages', async () => {
    const postedFrames = []
    let Processor
    const previousGlobals = {
      AudioWorkletProcessor: globalThis.AudioWorkletProcessor,
      registerProcessor: globalThis.registerProcessor,
      sampleRate: globalThis.sampleRate,
    }

    class WorkletBase {
      port = { postMessage: (frame) => postedFrames.push(frame), onmessage: null }
    }

    globalThis.AudioWorkletProcessor = WorkletBase
    globalThis.registerProcessor = (name, processor) => {
      expect(name).toBe('pcm-8k')
      Processor = processor
    }
    globalThis.sampleRate = 48000

    try {
      await import('../public/pcm-worklet.js')
      const worklet = new Processor()
      worklet.process([[new Float32Array(3072)]])
      worklet.process([[new Float32Array(3072)]])

      expect(postedFrames).toHaveLength(2)
      for (const frame of postedFrames) {
        expect(frame).toBeInstanceOf(ArrayBuffer)
        expect(frame.byteLength).toBe(1024)
        expect(new Int16Array(frame)).toHaveLength(512)
      }
    } finally {
      if (previousGlobals.AudioWorkletProcessor === undefined) delete globalThis.AudioWorkletProcessor
      else globalThis.AudioWorkletProcessor = previousGlobals.AudioWorkletProcessor
      if (previousGlobals.registerProcessor === undefined) delete globalThis.registerProcessor
      else globalThis.registerProcessor = previousGlobals.registerProcessor
      if (previousGlobals.sampleRate === undefined) delete globalThis.sampleRate
      else globalThis.sampleRate = previousGlobals.sampleRate
    }
  })
})
