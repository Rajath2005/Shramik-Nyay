/**
 * Progress Component - Progress bars and indicators
 * 
 * Features:
 * - Linear and circular variants
 * - Animated fill
 * - Color variants
 * - Label support
 */

interface ProgressProps {
  value: number
  max?: number
  variant?: 'primary' | 'success' | 'warning' | 'error'
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  className?: string
}

export function Progress({
  value,
  max = 100,
  variant = 'primary',
  size = 'md',
  showLabel = false,
  className = '',
}: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)

  const heights = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  }

  const colors = {
    primary: 'bg-gradient-to-r from-[var(--primary-500)] to-[var(--primary-600)]',
    success: 'bg-gradient-to-r from-[var(--success-500)] to-[var(--success-600)]',
    warning: 'bg-gradient-to-r from-[var(--warning-500)] to-[var(--warning-600)]',
    error: 'bg-gradient-to-r from-[var(--error-500)] to-[var(--error-600)]',
  }

  return (
    <div className={`w-full ${className}`.trim()}>
      {showLabel && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-[var(--ink)]">
            Progress
          </span>
          <span className="text-sm font-semibold text-[var(--ink)]">
            {Math.round(percentage)}%
          </span>
        </div>
      )}
      <div
        className={`
          w-full rounded-full overflow-hidden
          bg-[var(--neutral-200)] dark:bg-[var(--neutral-800)]
          ${heights[size]}
        `.replace(/\s+/g, ' ').trim()}
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={max}
        aria-valuenow={value}
      >
        <div
          className={`
            h-full transition-all duration-500 ease-out
            ${colors[variant]}
          `.replace(/\s+/g, ' ').trim()}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

/**
 * Circular Progress - Circular progress indicator
 */
interface CircularProgressProps {
  value: number
  max?: number
  size?: number
  strokeWidth?: number
  variant?: 'primary' | 'success' | 'warning' | 'error'
  showLabel?: boolean
  className?: string
}

export function CircularProgress({
  value,
  max = 100,
  size = 120,
  strokeWidth = 8,
  variant = 'primary',
  showLabel = true,
  className = '',
}: CircularProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (percentage / 100) * circumference

  return (
    <div className={`relative inline-flex ${className}`.trim()}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="var(--neutral-200)"
          strokeWidth={strokeWidth}
          fill="none"
          className="dark:stroke-[var(--neutral-800)]"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={`var(--${variant}-500)`}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-500 ease-out"
        />
      </svg>
      {showLabel && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-bold text-[var(--ink)]">
            {Math.round(percentage)}%
          </span>
        </div>
      )}
    </div>
  )
}
