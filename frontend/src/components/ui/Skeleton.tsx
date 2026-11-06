import * as React from 'react'

/**
 * Skeleton Component - Loading placeholder
 * 
 * Features:
 * - Animated shimmer effect
 * - Multiple variants (text, circular, rectangular)
 * - Customizable dimensions
 * - Respects reduced motion preference
 */

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
  lines?: number
}

export function Skeleton({
  className = '',
  variant = 'rectangular',
  width,
  height,
  lines = 1,
  style,
  ...props
}: SkeletonProps) {
  const baseStyles = `
    animate-pulse
    bg-[var(--neutral-200)]
    dark:bg-[var(--neutral-800)]
  `

  const variants = {
    text: 'rounded h-4 w-full',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  }

  const combinedClassName = `
    ${baseStyles}
    ${variants[variant]}
    ${className}
  `.replace(/\s+/g, ' ').trim()

  const inlineStyles: React.CSSProperties = {
    ...style,
    width: width || (variant === 'circular' ? height : undefined),
    height: height,
  }

  // For text variant with multiple lines
  if (variant === 'text' && lines > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={combinedClassName}
            style={{
              ...inlineStyles,
              width: index === lines - 1 ? '80%' : '100%',
            }}
            {...props}
          />
        ))}
      </div>
    )
  }

  return (
    <div className={combinedClassName} style={inlineStyles} {...props} />
  )
}

/**
 * Shimmer Wrapper - Adds animated shimmer effect to content
 */
export function ShimmerWrapper({
  className = '',
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`shimmer-wrapper ${className}`.trim()} {...props}>
      <div className="shimmer" />
      {children}
    </div>
  )
}
