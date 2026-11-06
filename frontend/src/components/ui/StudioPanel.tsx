import type { ReactNode } from 'react';
import { motion } from 'motion/react';
import { springs } from '../../lib/springs';
import styles from './StudioPanel.module.css';

interface StudioPanelProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  actions?: ReactNode;
  footer?: ReactNode;
  variant?: 'elevated' | 'flat' | 'glass';
  compact?: boolean;
  loading?: boolean;
  emptyState?: {
    icon: string;
    title: string;
    description: string;
  };
  className?: string;
}

export function StudioPanel({
  title,
  subtitle,
  children,
  actions,
  footer,
  variant,
  compact = false,
  loading = false,
  emptyState,
  className,
}: StudioPanelProps) {
  const panelClass = [
    styles.panel,
    variant && styles[variant],
    compact && styles.compact,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <motion.div
      className={panelClass}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={springs.smooth}
    >
      {(title || subtitle || actions) && (
        <div className={styles.header}>
          <div className={styles.headerContent}>
            {title && <h2 className={styles.title}>{title}</h2>}
            {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
          </div>
          {actions && <div className={styles.headerActions}>{actions}</div>}
        </div>
      )}

      <div className={styles.content}>
        {loading ? (
          <div className={styles.loading}>
            <div className={styles.spinner} role="status" aria-label="Loading" />
          </div>
        ) : emptyState ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>{emptyState.icon}</div>
            <h3 className={styles.emptyTitle}>{emptyState.title}</h3>
            <p className={styles.emptyDescription}>{emptyState.description}</p>
          </div>
        ) : (
          children
        )}
      </div>

      {footer && <div className={styles.footer}>{footer}</div>}
    </motion.div>
  );
}

interface StudioGridProps {
  children: ReactNode;
  columns?: 1 | 2 | 3 | 4;
  gap?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function StudioGrid({
  children,
  columns = 2,
  gap = 'md',
  className,
}: StudioGridProps) {
  const gapSize = {
    sm: 'var(--spacing-4)',
    md: 'var(--spacing-6)',
    lg: 'var(--spacing-8)',
  }[gap];

  return (
    <div
      className={className}
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap: gapSize,
      }}
    >
      {children}
    </div>
  );
}
