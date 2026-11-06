import * as React from 'react'

/**
 * Card Components - Container elements with elevation
 * 
 * Features:
 * - Card (main container)
 * - CardHeader (title section)
 * - CardContent (body content)
 * - CardFooter (action section)
 * - Elevation variants
 * - Hover effects
 * - Interactive state
 */

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  elevation?: 'none' | 'sm' | 'md' | 'lg'
  interactive?: boolean
}

export function Card({
  className = '',
  elevation = 'sm',
  interactive = false,
  ...props
}: CardProps) {
  const baseStyles = `
    rounded-xl border border-[var(--line)]
    bg-[var(--raised)]
    transition-all duration-200
  `

  const elevations = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
  }

  const interactiveStyles = interactive
    ? 'hover:shadow-lg hover:border-[var(--line-strong)] cursor-pointer'
    : ''

  const combinedClassName = `
    ${baseStyles}
    ${elevations[elevation]}
    ${interactiveStyles}
    ${className}
  `.replace(/\s+/g, ' ').trim()

  return <div className={combinedClassName} {...props} />
}

export function CardHeader({
  className = '',
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`flex flex-col gap-1.5 p-6 ${className}`.trim()}
      {...props}
    />
  )
}

export function CardTitle({
  className = '',
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={`text-lg font-semibold leading-none tracking-tight text-[var(--ink)] ${className}`.trim()}
      {...props}
    />
  )
}

export function CardDescription({
  className = '',
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={`text-sm text-[var(--mute)] ${className}`.trim()}
      {...props}
    />
  )
}

export function CardContent({
  className = '',
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={`p-6 pt-0 ${className}`.trim()} {...props} />
}

export function CardFooter({
  className = '',
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`flex items-center p-6 pt-0 ${className}`.trim()}
      {...props}
    />
  )
}
