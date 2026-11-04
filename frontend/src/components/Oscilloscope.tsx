import { useEffect, useRef } from 'react'
import styles from './Oscilloscope.module.css'
import { getOscilloscopePoints, getSpeechSegments } from './oscilloscopeGeometry'

type Props = {
  levels: number[]
  threshold: number
  label: string
  theme: 'light' | 'dark'
}

export default function Oscilloscope({ levels, threshold, label, theme }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const draw = () => {
      const bounds = canvas.getBoundingClientRect()
      if (!bounds.width || !bounds.height) return
      const pixelRatio = window.devicePixelRatio || 1
      canvas.width = Math.round(bounds.width * pixelRatio)
      canvas.height = Math.round(bounds.height * pixelRatio)
      const context = canvas.getContext('2d')
      if (!context) return
      context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0)
      context.clearRect(0, 0, bounds.width, bounds.height)

      const rootStyle = getComputedStyle(document.documentElement)
      const blue = rootStyle.getPropertyValue('--blue').trim()
      const amber = rootStyle.getPropertyValue('--amber').trim()
      const mute = rootStyle.getPropertyValue('--mute').trim()
      const line = rootStyle.getPropertyValue('--line').trim()
      const safeThreshold = Math.max(0, Math.min(1, threshold))
      const points = getOscilloscopePoints(levels, bounds.width, bounds.height)
      const chartTop = 8
      const chartBottom = bounds.height - 8
      const chartHeight = Math.max(1, chartBottom - chartTop)
      const thresholdY = chartBottom - safeThreshold * chartHeight

      context.beginPath()
      context.setLineDash([4, 5])
      context.strokeStyle = amber
      context.lineWidth = 1
      context.moveTo(0, thresholdY)
      context.lineTo(bounds.width, thresholdY)
      context.stroke()
      context.setLineDash([])

      const values = levels.filter(Number.isFinite).map((level) => Math.max(0, Math.min(1, level)))
      const floor = values.length
        ? [...values].sort((a, b) => a - b)[Math.floor((values.length - 1) * 0.1)]
        : 0
      const noiseY = chartBottom - floor * chartHeight
      context.beginPath()
      context.globalAlpha = 0.42
      context.strokeStyle = mute
      context.lineWidth = 1
      context.moveTo(0, noiseY)
      context.lineTo(bounds.width, noiseY)
      context.stroke()
      context.globalAlpha = 1

      if (points.length < 2) {
        const idleY = chartBottom - (values[0] ?? 0) * chartHeight
        context.beginPath()
        context.strokeStyle = line
        context.lineWidth = 1.5
        context.moveTo(0, idleY)
        context.lineTo(bounds.width, idleY)
        context.stroke()
        return
      }

      context.beginPath()
      context.strokeStyle = blue
      context.lineWidth = 1.75
      context.lineJoin = 'round'
      context.lineCap = 'round'
      context.moveTo(points[0].x, points[0].y)
      for (const point of points.slice(1)) context.lineTo(point.x, point.y)
      context.stroke()

      context.beginPath()
      context.strokeStyle = amber
      context.lineWidth = 2.5
      context.lineJoin = 'round'
      context.lineCap = 'round'
      for (const [previous, current] of getSpeechSegments(points, safeThreshold)) {
        context.moveTo(previous.x, previous.y)
        context.lineTo(current.x, current.y)
      }
      context.stroke()
    }

    const observer = new ResizeObserver(draw)
    observer.observe(canvas)
    draw()
    return () => observer.disconnect()
  }, [levels, threshold, theme])

  return (
    <div className={styles.scope}>
      <canvas ref={canvasRef} role="img" aria-label={label} />
    </div>
  )
}
