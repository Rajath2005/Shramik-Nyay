import { useEffect, useState } from 'react'

export function useCountUp(target: number | null, duration = 500): number | null {
  const [count, setCount] = useState({ target, value: target ?? 0 })

  useEffect(() => {
    if (target === null) return
    let frame = 0
    const update = (now: number, started: number) => {
      const progress = Math.min(1, (now - started) / duration)
      setCount({ target, value: Math.round(target * progress) })
      if (progress < 1) frame = requestAnimationFrame((time) => update(time, started))
    }
    frame = requestAnimationFrame((now) => {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || target <= 0) {
        setCount({ target, value: target })
        return
      }
      setCount({ target, value: 0 })
      update(now, now)
    })
    return () => cancelAnimationFrame(frame)
  }, [target, duration])

  if (target === null) return null
  return count.target === target ? count.value : 0
}
