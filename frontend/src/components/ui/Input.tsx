import * as React from 'react'

/**
 * Input Component - Enhanced text input
 * 
 * Features:
 * - Focus ring with offset
 * - Error state
 * - Icon support (left/right)
 * - Full width option
 * - Label integration
 * - Helper text
 */

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean
  helperText?: string
  label?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  fullWidth?: boolean
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className = '',
      error = false,
      helperText,
      label,
      leftIcon,
      rightIcon,
      fullWidth = false,
      id,
      ...props
    },
    ref
  ) => {
    const generatedId = React.useId()
    const inputId = id || `input-${generatedId}`

    const baseStyles = `
      flex h-12 w-full rounded-xl
      border-2
      bg-[var(--raised)]
      px-4 text-base
      transition-all duration-200
      placeholder:text-[var(--mute)]
      focus:outline-none focus:ring-4
      disabled:cursor-not-allowed disabled:opacity-50
    `

    const normalStyles = `
      border-[var(--line)]
      focus:border-[var(--primary-500)]
      focus:ring-[var(--primary-500)]/10
    `

    const errorStyles = `
      border-[var(--error-500)]
      focus:border-[var(--error-500)]
      focus:ring-[var(--error-500)]/10
    `

    const inputClassName = `
      ${baseStyles}
      ${error ? errorStyles : normalStyles}
      ${leftIcon ? 'pl-11' : ''}
      ${rightIcon ? 'pr-11' : ''}
      ${className}
    `.replace(/\s+/g, ' ').trim()

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-semibold text-[var(--ink)] mb-2"
          >
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--mute)]">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={inputClassName}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--mute)]">
              {rightIcon}
            </div>
          )}
        </div>
        {helperText && (
          <p
            className={`mt-2 text-sm ${
              error ? 'text-[var(--error-500)]' : 'text-[var(--mute)]'
            }`}
          >
            {helperText}
          </p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export { Input, type InputProps }
