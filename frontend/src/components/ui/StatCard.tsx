import type { ReactNode } from 'react';
import { motion } from 'motion/react';
import { springs } from '../../lib/springs';
import styles from './StatCard.module.css';

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  iconVariant?: 'primary' | 'success' | 'warning' | 'error';
  change?: {
    value: number;
    label: string;
  };
  footer?: string;
  loading?: boolean;
  accent?: boolean;
  onClick?: () => void;
}

export function StatCard({
  label,
  value,
  icon,
  iconVariant = 'primary',
  change,
  footer,
  loading = false,
  accent = false,
  onClick,
}: StatCardProps) {
  const isInteractive = Boolean(onClick);

  return (
    <motion.div
      className={`${styles.card} ${accent ? styles.accent : ''} ${
        isInteractive ? styles.interactive : ''
      }`}
      onClick={onClick}
      whileHover={isInteractive ? { scale: 1.02 } : {}}
      whileTap={isInteractive ? { scale: 0.98 } : {}}
      transition={springs.snappy}
      role={isInteractive ? 'button' : undefined}
      tabIndex={isInteractive ? 0 : undefined}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className={styles.header}>
        {icon && (
          <div className={`${styles.iconContainer} ${styles[iconVariant]}`}>
            {icon}
          </div>
        )}
        {change && (
          <div
            className={`${styles.badge} ${
              change.value < 0 ? styles.negative : ''
            }`}
          >
            {change.value > 0 ? '↑' : '↓'}
            {Math.abs(change.value)}%
          </div>
        )}
      </div>

      <div className={styles.content}>
        {loading ? (
          <div className={styles.skeleton} />
        ) : (
          <motion.h3
            className={styles.value}
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ ...springs.bouncy, delay: 0.1 }}
          >
            {value}
          </motion.h3>
        )}
        <p className={styles.label}>{label}</p>
      </div>

      {(change || footer) && (
        <div className={styles.footer}>
          {change && (
            <span
              className={`${styles.trend} ${
                change.value > 0 ? styles.up : styles.down
              }`}
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                {change.value > 0 ? (
                  <path d="M7 14l5-5 5 5H7z" />
                ) : (
                  <path d="M7 10l5 5 5-5H7z" />
                )}
              </svg>
              {change.label}
            </span>
          )}
          {footer && <span>{footer}</span>}
        </div>
      )}
    </motion.div>
  );
}

interface StatCardGridProps {
  children: ReactNode;
  columns?: 2 | 3 | 4;
}

export function StatCardGrid({ children, columns = 4 }: StatCardGridProps) {
  return (
    <div
      className={styles.statsGrid}
      style={{
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
      }}
    >
      {children}
    </div>
  );
}
