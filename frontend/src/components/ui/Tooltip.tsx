import * as React from 'react'

/**
 * Tooltip Component - Contextual information on hover
 * 
 * Note: This is a simplified version.
 * For production, use @radix-ui/react-tooltip for:
 * - Proper positioning
 * - Portal rendering
 * - Accessibility
 * 
 * Usage:
 * <Tooltip content="Save changes">
 *   <Button>Save</Button>
 * </Tooltip>
 */

interface TooltipProps {
  content: React.ReactNode
  side?: 'top' | 'bottom' | 'left' | 'right'
  children: React.ReactElement
  delay?: number
}

export function Tooltip({
  content,
  side = 'top',
  children,
  delay = 200,
}: TooltipProps) {
  const [isVisible, setIsVisible] = React.useState(false)
  const timeoutRef = React.useRef<NodeJS.Timeout | undefined>(undefined)

  const handleMouseEnter = () => {
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true)
    }, delay)
  }

  const handleMouseLeave = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    setIsVisible(false)
  }

  const positions = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  }

  const arrows = {
    top: 'top-full left-1/2 -translate-x-1/2 border-t-[var(--neutral-800)]',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-[var(--neutral-800)]',
    left: 'left-full top-1/2 -translate-y-1/2 border-l-[var(--neutral-800)]',
    right: 'right-full top-1/2 -translate-y-1/2 border-r-[var(--neutral-800)]',
  }

  return (
    <div
      className="relative inline-flex"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      {isVisible && (
        <div
          className={`
            absolute z-[var(--z-tooltip)] ${positions[side]}
            px-3 py-2 rounded-lg
            bg-[var(--neutral-800)] text-white text-sm font-medium
            shadow-lg
            animate-fade-in
            whitespace-nowrap
          `.replace(/\s+/g, ' ').trim()}
          role="tooltip"
        >
          {content}
          <div
            className={`
              absolute w-0 h-0
              border-4 border-transparent
              ${arrows[side]}
            `.replace(/\s+/g, ' ').trim()}
          />
        </div>
      )}
    </div>
  )
}
