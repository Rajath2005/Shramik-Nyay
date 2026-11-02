import { createConstructionTrafficNoise, createTelephonyBandpass } from './audio-dsp.js'

// Downsamples mic audio to 8 kHz mono Int16 and emits exactly 512 samples (1024 bytes) per message.
class Pcm8k extends AudioWorkletProcessor {
  constructor() {
    super()
    this.ratio = sampleRate / 8000
    this.pos = 0; this.acc = 0; this.n = 0
    this.out = new Int16Array(512); this.k = 0
    this.noiseLevel = 0
    this.ambientNoise = createConstructionTrafficNoise(sampleRate)
    this.bandpass = createTelephonyBandpass(sampleRate)
    this.port.onmessage = (e) => {
      const level = e.data?.level
      if (Number.isFinite(level)) this.noiseLevel = Math.max(0, Math.min(100, level)) / 100
    }
  }
  process(inputs) {
    const ch = inputs[0][0]
    if (!ch) return true
    for (let i = 0; i < ch.length; i++) {
      const noise = this.noiseLevel > 0 ? this.ambientNoise() * this.noiseLevel * 0.8 : 0
      const mixed = ch[i] + noise
      this.acc += this.bandpass(mixed)
      this.n++; this.pos++
      if (this.pos >= this.ratio) {            // box-filter average = cheap anti-alias
        this.pos -= this.ratio
        const v = Math.max(-1, Math.min(1, this.acc / this.n))
        this.acc = 0; this.n = 0
        this.out[this.k++] = v < 0 ? v * 32768 : v * 32767
        if (this.k === 512) { this.port.postMessage(this.out.buffer.slice(0)); this.k = 0 }
      }
    }
    return true
  }
}
registerProcessor('pcm-8k', Pcm8k)
