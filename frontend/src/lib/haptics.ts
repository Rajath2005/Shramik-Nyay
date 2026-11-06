/**
 * Haptic feedback patterns for mobile devices
 * Provides tactile feedback for user interactions
 */

interface HapticPattern {
  pattern: number | number[]
  description: string
}

const patterns: Record<string, HapticPattern> = {
  // Light tap - subtle feedback for button presses
  light: {
    pattern: 10,
    description: 'Light tap for minor interactions',
  },
  
  // Medium tap - standard feedback for primary actions
  medium: {
    pattern: 20,
    description: 'Medium tap for standard actions',
  },
  
  // Heavy tap - strong feedback for important actions
  heavy: {
    pattern: [30, 10, 30],
    description: 'Heavy double-tap for significant actions',
  },
  
  // Success - celebration pattern for completed actions
  success: {
    pattern: [20, 50, 20],
    description: 'Success pattern with pause',
  },
  
  // Error - warning pattern for errors or failures
  error: {
    pattern: [50, 100, 50, 100, 50],
    description: 'Error pattern with long pauses',
  },
  
  // Selection - subtle feedback for item selection
  selection: {
    pattern: 15,
    description: 'Quick tap for selections',
  },
  
  // Long press - sustained vibration for long press
  longPress: {
    pattern: [0, 300, 100],
    description: 'Delayed vibration for long press',
  },
}

/**
 * Check if device supports haptic feedback
 */
function supportsHaptics(): boolean {
  return 'vibrate' in navigator && typeof navigator.vibrate === 'function'
}

/**
 * Trigger haptic feedback
 */
export function triggerHaptic(patternKey: keyof typeof patterns): void {
  if (!supportsHaptics()) {
    console.debug('Haptics not supported on this device')
    return
  }
  
  const pattern = patterns[patternKey]
  if (!pattern) {
    console.warn(`Unknown haptic pattern: ${patternKey}`)
    return
  }
  
  try {
    navigator.vibrate(pattern.pattern)
  } catch (error) {
    console.error('Failed to trigger haptic:', error)
  }
}

/**
 * Haptic feedback API
 */
export const haptics = {
  // Basic patterns
  light: () => triggerHaptic('light'),
  medium: () => triggerHaptic('medium'),
  heavy: () => triggerHaptic('heavy'),
  
  // Contextual patterns
  success: () => triggerHaptic('success'),
  error: () => triggerHaptic('error'),
  selection: () => triggerHaptic('selection'),
  longPress: () => triggerHaptic('longPress'),
  
  // Utility
  isSupported: supportsHaptics,
  
  // Cancel all haptics
  cancel: () => {
    if (supportsHaptics()) {
      navigator.vibrate(0)
    }
  },
}

/**
 * React hook for haptic feedback
 * Usage: const { trigger } = useHaptics()
 *        trigger('success')
 */
export function useHaptics() {
  return {
    trigger: triggerHaptic,
    isSupported: supportsHaptics(),
    patterns: Object.keys(patterns),
  }
}
