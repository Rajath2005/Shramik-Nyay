import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Utility function to merge Tailwind CSS classes
 * Combines clsx for conditional classes and tailwind-merge to handle conflicts
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format currency in Indian Rupees
 */
export function formatCurrency(amount: number): string {
  return `₹${amount.toLocaleString('en-IN')}`
}

/**
 * Debounce function for performance optimization
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }
    
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Throttle function for rate limiting
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  
  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

/**
 * Check if device supports haptic feedback
 */
export function supportsHaptics(): boolean {
  return 'vibrate' in navigator
}

/**
 * Check if running on mobile device
 */
export function isMobile(): boolean {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  )
}

/**
 * Get safe area insets for notched devices
 */
export function getSafeAreaInsets() {
  return {
    top: parseInt(getComputedStyle(document.documentElement).getPropertyValue('--safe-area-top') || '0'),
    bottom: parseInt(getComputedStyle(document.documentElement).getPropertyValue('--safe-area-bottom') || '0'),
    left: parseInt(getComputedStyle(document.documentElement).getPropertyValue('--safe-area-left') || '0'),
    right: parseInt(getComputedStyle(document.documentElement).getPropertyValue('--safe-area-right') || '0'),
  }
}
