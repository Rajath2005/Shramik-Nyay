import * as React from 'react'

/**
 * Badge Component - Status indicators and labels
 * 
 * Features:
 * - Multiple variants (success, warning, error, info, neutral)
 * - Size options (sm, md, lg)
 * - Gradient backgrounds
 * - Icon support
 * - Dot indicator
 */

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral'
  size?: 'sm' | 'md' | 'lg'
  dot?: boolean
  icon?: React.ReactNode
}

export function Badge({
  className = '',
  variant = 'neutral',
  size = 'md',
  dot = false,
  icon,
  children,
  ...props
}: BadgeProps) {
  const baseStyles = `
    inline-flex items-center gap-1.5
    font-semibold rounded-full
    transition-colors duration-150
  `

  const variants = {
    success: `
      bg-[var(--success-50)] text-[var(--success-700)]
      dark:bg-[var(--success-500)]/20 dark:text-[var(--success-400)]
    `,
    warning: `
      bg-[var(--warning-50)] text-[var(--warning-700)]
      dark:bg-[var(--warning-500)]/20 dark:text-[var(--warning-400)]
    `,
    error: `
      bg-[var(--error-50)] text-[var(--error-700)]
      dark:bg-[var(--error-500)]/20 dark:text-[var(--error-400)]
    `,
    info: `
      bg-[var(--primary-50)] text-[var(--primary-700)]
      dark:bg-[var(--primary-500)]/20 dark:text-[var(--primary-400)]
    `,
    neutral: `
      bg-[var(--neutral-100)] text-[var(--neutral-700)]
      dark:bg-[var(--neutral-800)] dark:text-[var(--neutral-300)]
    `,
  }

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm',
  }

  const dotColors = {
    success: 'bg-[var(--success-500)]',
    warning: 'bg-[var(--warning-500)]',
    error: 'bg-[var(--error-500)]',
    info: 'bg-[var(--primary-500)]',
    neutral: 'bg-[var(--neutral-500)]',
  }

  const combinedClassName = `
    ${baseStyles}
    ${variants[variant]}
    ${sizes[size]}
    ${className}
  `.replace(/\s+/g, ' ').trim()

  return (
    <span className={combinedClassName} {...props}>
      {dot && (
        <span
          className={`w-1.5 h-1.5 rounded-full ${dotColors[variant]}`}
          aria-hidden="true"
        />
      )}
      {icon && <span className="shrink-0">{icon}</span>}
      {children}
    </span>
  )
}
