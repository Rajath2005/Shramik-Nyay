const TAU = Math.PI * 2
const BUTTERWORTH_Q = Math.SQRT1_2

function createBiquad(sampleRate, frequency, type) {
  const omega = TAU * frequency / sampleRate
  const cosine = Math.cos(omega)
  const alpha = Math.sin(omega) / (2 * BUTTERWORTH_Q)
  const a0 = 1 + alpha
  const a1 = -2 * cosine / a0
  const a2 = (1 - alpha) / a0
  const scale = type === 'lowpass' ? (1 - cosine) / 2 : (1 + cosine) / 2
  const b0 = scale / a0
  const b1 = (type === 'lowpass' ? 1 - cosine : -(1 + cosine)) / a0
  const b2 = b0
  let x1 = 0
  let x2 = 0
  let y1 = 0
  let y2 = 0

  return (input) => {
    const output = b0 * input + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
    x2 = x1
    x1 = input
    y2 = y1
    y1 = output
    return output
  }
}

export function createTelephonyBandpass(sampleRate, lowHz = 300, highHz = 3400) {
  if (
    !Number.isFinite(sampleRate) || sampleRate <= 0 ||
    !Number.isFinite(lowHz) || !Number.isFinite(highHz) ||
    lowHz <= 0 || highHz <= lowHz || highHz >= sampleRate / 2
  ) {
    throw new RangeError('Bandpass frequencies must be positive, ordered, and below Nyquist.')
  }

  const highpass = createBiquad(sampleRate, lowHz, 'highpass')
  const lowpass = createBiquad(sampleRate, highHz, 'lowpass')
  return (sample) => lowpass(highpass(sample))
}

export function createConstructionTrafficNoise(sampleRate, random = Math.random) {
  if (!Number.isFinite(sampleRate) || sampleRate <= 0) {
    throw new RangeError('Sample rate must be a positive finite number.')
  }

  let sampleIndex = 0
  let roadTexture = 0
  let clangSamplesLeft = 0
  let clangAge = 0
  let clangDuration = 0
  let clangPhase = 0
  let hornSamplesLeft = 0
  let hornAge = 0
  let hornDuration = 0
  let nextClang = sampleRate * (1.2 + random() * 2.8)
  let nextHorn = sampleRate * (7 + random() * 11)

  return () => {
    sampleIndex += 1
    roadTexture += 0.11 * ((random() * 2 - 1) - roadTexture)

    let clang = 0
    if (clangSamplesLeft <= 0) {
      nextClang -= 1
      if (nextClang <= 0) {
        clangDuration = Math.round(sampleRate * (0.12 + random() * 0.12))
        clangSamplesLeft = clangDuration
        clangAge = 0
        clangPhase = random() * TAU
        nextClang = Math.round(sampleRate * (1.2 + random() * 2.8))
      }
    }
    if (clangSamplesLeft > 0) {
      const envelope = Math.exp(-clangAge / (sampleRate * 0.045))
      const time = clangAge / sampleRate
      clang = envelope * (
        0.52 * Math.sin(clangPhase + TAU * 1130 * time) +
        0.31 * Math.sin(clangPhase * 1.7 + TAU * 1870 * time) +
        0.17 * Math.sin(clangPhase * 0.6 + TAU * 2710 * time)
      )
      clangAge += 1
      clangSamplesLeft -= 1
    }

    let horn = 0
    if (hornSamplesLeft <= 0) {
      if (nextHorn <= 0) {
        hornDuration = Math.round(sampleRate * (0.45 + random() * 0.5))
        hornSamplesLeft = hornDuration
        hornAge = 0
        nextHorn = Math.round(sampleRate * (7 + random() * 11))
      } else {
        nextHorn -= 1
      }
    }
    if (hornSamplesLeft > 0) {
      const progress = hornAge / hornDuration
      const envelope = Math.min(1, hornAge / (sampleRate * 0.04), (hornDuration - hornAge) / (sampleRate * 0.12))
      const wobble = 1 + 0.008 * Math.sin(TAU * 3 * progress)
      horn = envelope * (
        0.19 * Math.sin(TAU * 392 * wobble * hornAge / sampleRate) +
        0.13 * Math.sin(TAU * 494 * wobble * hornAge / sampleRate)
      )
      hornAge += 1
      hornSamplesLeft -= 1
    }

    const generatorHum =
      0.11 * Math.sin(TAU * 55 * sampleIndex / sampleRate) +
      0.055 * Math.sin(TAU * 110 * sampleIndex / sampleRate) +
      0.035 * Math.sin(TAU * 220 * sampleIndex / sampleRate) +
      0.022 * Math.sin(TAU * 330 * sampleIndex / sampleRate)
    const trafficRumble = 0.08 * Math.sin(TAU * 71 * sampleIndex / sampleRate) + 0.12 * roadTexture
    return generatorHum + trafficRumble + clang + horn
  }
}
