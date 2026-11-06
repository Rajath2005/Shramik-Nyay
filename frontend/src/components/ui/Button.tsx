import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'

/**
 * Button Component - Top-tier, production-ready button
 * Inspired by: shadcn/ui, Vercel, Stripe
 * 
 * Features:
 * - Multiple variants (primary, secondary, outline, ghost, destructive)
 * - Size options (xs, sm, md, lg, xl)
 * - Gradient backgrounds for primary actions
 * - Loading states
 * - Icon support
 * - Full keyboard accessibility
 * - Hover and focus states
 */

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'success'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  loading?: boolean
  icon?: React.ReactNode
  iconPosition?: 'left' | 'right'
  asChild?: boolean
  fullWidth?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className = '',
      variant = 'primary',
      size = 'md',
      loading = false,
      icon,
      iconPosition = 'left',
      asChild = false,
      fullWidth = false,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : 'button'

    // Base styles
    const baseStyles = `
      inline-flex items-center justify-center gap-2
      font-semibold rounded-xl
      transition-all duration-150
      focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2
      disabled:pointer-events-none disabled:opacity-50
      active:scale-[0.98]
    `

    // Variant styles
    const variants = {
      primary: `
        bg-gradient-to-br from-[var(--primary-500)] to-[var(--primary-600)]
        text-white shadow-sm
        hover:shadow-lg hover:shadow-[var(--primary-500)]/30
        focus-visible:ring-[var(--primary-500)]
      `,
      secondary: `
        bg-[var(--neutral-100)] text-[var(--neutral-900)]
        hover:bg-[var(--neutral-200)]
        dark:bg-[var(--neutral-800)] dark:text-[var(--neutral-100)]
        dark:hover:bg-[var(--neutral-700)]
        focus-visible:ring-[var(--neutral-400)]
        shadow-sm
      `,
      outline: `
        border-2 border-[var(--line-strong)]
        hover:bg-[var(--neutral-50)]
        dark:hover:bg-[var(--neutral-800)]
        focus-visible:ring-[var(--neutral-400)]
      `,
      ghost: `
        hover:bg-[var(--neutral-100)]
        dark:hover:bg-[var(--neutral-800)]
        focus-visible:ring-[var(--neutral-400)]
      `,
      destructive: `
        bg-gradient-to-br from-[var(--error-500)] to-[var(--error-600)]
        text-white shadow-sm
        hover:shadow-lg hover:shadow-[var(--error-500)]/30
        focus-visible:ring-[var(--error-500)]
      `,
      success: `
        bg-gradient-to-br from-[var(--success-500)] to-[var(--success-600)]
        text-white shadow-sm
        hover:shadow-lg hover:shadow-[var(--success-500)]/30
        focus-visible:ring-[var(--success-500)]
      `,
    }

    // Size styles
    const sizes = {
      xs: 'h-8 px-3 text-xs',
      sm: 'h-9 px-4 text-sm',
      md: 'h-11 px-6 text-base',
      lg: 'h-13 px-8 text-lg',
      xl: 'h-16 px-10 text-xl',
    }

    const combinedClassName = `
      ${baseStyles}
      ${variants[variant]}
      ${sizes[size]}
      ${fullWidth ? 'w-full' : ''}
      ${className}
    `.replace(/\s+/g, ' ').trim()

    return (
      <Comp
        ref={ref}
        className={combinedClassName}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg
            className="animate-spin h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {!loading && icon && iconPosition === 'left' && icon}
        {children}
        {!loading && icon && iconPosition === 'right' && icon}
      </Comp>
    )
  }
)

Button.displayName = 'Button'

export { Button, type ButtonProps }
