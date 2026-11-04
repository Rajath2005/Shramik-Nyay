export type OscilloscopePoint = { x: number; y: number; level: number }
export type SpeechSegment = [OscilloscopePoint, OscilloscopePoint]

export function getOscilloscopePoints(levels: number[], width: number, height: number): OscilloscopePoint[] {
  const values = levels.filter(Number.isFinite).map((level) => Math.max(0, Math.min(1, level)))
  if (values.length < 2) return []
  const bottom = height - 8
  const chartHeight = Math.max(1, height - 16)
  return values.map((level, index) => ({
    x: 8 + (width - 16) * index / (values.length - 1),
    y: bottom - level * chartHeight,
    level,
  }))
}

export function getSpeechSegments(points: OscilloscopePoint[], threshold: number): SpeechSegment[] {
  const segments: SpeechSegment[] = []
  for (let index = 1; index < points.length; index += 1) {
    const previous = points[index - 1]
    const current = points[index]
    if (previous.level >= threshold || current.level >= threshold) segments.push([previous, current])
  }
  return segments
}
