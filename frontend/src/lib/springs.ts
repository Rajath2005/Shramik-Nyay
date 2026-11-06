/**
 * Motion spring presets for consistent animations
 * Based on industry-standard spring physics from Linear, Stripe, Vercel
 */

export const springs = {
  // Snappy - Quick, responsive interactions (buttons, toggles)
  snappy: {
    type: "spring" as const,
    stiffness: 400,
    damping: 30,
    mass: 0.8,
  },
  
  // Smooth - Standard transitions (modals, pages, panels)
  smooth: {
    type: "spring" as const,
    stiffness: 300,
    damping: 30,
    mass: 1,
  },
  
  // Bouncy - Playful, celebratory (success states, checkmarks)
  bouncy: {
    type: "spring" as const,
    stiffness: 200,
    damping: 15,
    mass: 1,
  },
  
  // Gentle - Subtle, elegant (fades, reveals, tooltips)
  gentle: {
    type: "spring" as const,
    stiffness: 250,
    damping: 25,
    mass: 1.2,
  },
  
  // Stiff - Immediate, precise (focus indicators, cursors)
  stiff: {
    type: "spring" as const,
    stiffness: 500,
    damping: 35,
    mass: 0.5,
  },
}

/**
 * Easing curves for non-spring animations
 */
export const easings = {
  // Smooth deceleration
  easeOut: [0.16, 1, 0.3, 1] as [number, number, number, number],
  
  // Smooth acceleration and deceleration
  easeInOut: [0.45, 0, 0.55, 1] as [number, number, number, number],
  
  // Sharp deceleration (Material Design)
  sharpOut: [0.4, 0, 0.2, 1] as [number, number, number, number],
  
  // Sharp acceleration (Material Design)
  sharpIn: [0.4, 0, 1, 1] as [number, number, number, number],
  
  // Anticipation (slight backwards movement)
  anticipate: [0.36, 0, 0.66, -0.56] as [number, number, number, number],
}

/**
 * Duration presets (in milliseconds)
 */
export const durations = {
  instant: 0,
  fast: 150,
  normal: 250,
  slow: 350,
  slower: 500,
  slowest: 800,
}

/**
 * Stagger delay calculator for sequential animations
 */
export function getStaggerDelay(index: number, baseDelay = 0.05): number {
  return index * baseDelay
}

/**
 * Layout transition config for shared element animations
 */
export const layoutTransition = {
  type: "spring" as const,
  stiffness: 350,
  damping: 30,
  mass: 1,
}
