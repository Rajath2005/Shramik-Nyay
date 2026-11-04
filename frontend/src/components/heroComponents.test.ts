import { describe, expect, it } from 'vitest'
import { getOscilloscopePoints, getSpeechSegments } from './oscilloscopeGeometry'
import { splitTranscriptByBoostedWords } from './transcriptHighlight'

describe('hero component data shaping', () => {
  it('keeps an idle oscilloscope as a flat baseline', () => {
    expect(getOscilloscopePoints([], 200, 80)).toEqual([])
    expect(getOscilloscopePoints([0], 200, 80)).toEqual([])
  })

  it('highlights only waveform segments that reach the VAD threshold', () => {
    const points = getOscilloscopePoints([0.2, 0.72, 0.9, 0.3], 200, 80)
    expect(getSpeechSegments(points, 0.72)).toEqual([
      [points[0], points[1]],
      [points[1], points[2]],
      [points[2], points[3]],
    ])
    expect(getSpeechSegments(points, 0.91)).toEqual([])
  })

  it('highlights boosted transcript words case-insensitively without matching substrings', () => {
    const parts = splitTranscriptByBoostedWords(
      'Peenya, Thekedar DihadiPeenya',
      ['Peenya', 'Thekedar', 'Dihadi'],
    )
    expect(parts.filter(({ boosted }) => boosted).map(({ text }) => text)).toEqual(['Peenya', 'Thekedar'])
  })
})
