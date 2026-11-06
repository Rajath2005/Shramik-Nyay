import type { ReactNode } from 'react';
import { motion } from 'motion/react';
import { springs } from '../../lib/springs';
import styles from './InfoCard.module.css';

interface InfoCardProps {
  label: string;
  value: string | number | null;
  icon?: ReactNode;
  status?: 'pending' | 'verified' | 'error';
  hint?: string;
  mono?: boolean;
  large?: boolean;
  loading?: boolean;
  onClick?: () => void;
}

export function InfoCard({
  label,
  value,
  icon,
  status,
  hint,
  mono = false,
  large = false,
  loading = false,
  onClick,
}: InfoCardProps) {
  const isInteractive = Boolean(onClick);

  const statusClass = status ? styles[status] : '';
  const sizeClass = large ? styles.large : '';
  const interactiveClass = isInteractive ? styles.interactive : '';

  return (
    <motion.div
      className={`${styles.card} ${statusClass} ${sizeClass} ${interactiveClass}`}
      onClick={onClick}
      whileHover={isInteractive ? { y: -2 } : {}}
      transition={springs.snappy}
      role={isInteractive ? 'button' : undefined}
      tabIndex={isInteractive ? 0 : undefined}
    >
      <div className={styles.header}>
        <span className={styles.label}>{label}</span>
        {status && (
          <span className={`${styles.statusIndicator} ${styles[status]}`}>
            {status === 'verified' && '✓'}
            {status === 'pending' && '◌'}
            {status === 'error' && '✕'}
          </span>
        )}
        {icon && <span className={styles.icon}>{icon}</span>}
      </div>

      <div className={styles.content}>
        {loading ? (
          <div className={styles.skeleton} />
        ) : value !== null && value !== undefined ? (
          <p className={`${styles.value} ${mono ? styles.mono : ''}`}>
            {value}
          </p>
        ) : (
          <p className={styles.empty}>—</p>
        )}
      </div>

      {hint && (
        <motion.p
          className={styles.hint}
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={springs.smooth}
        >
          {hint}
        </motion.p>
      )}
    </motion.div>
  );
}

interface InfoCardGridProps {
  children: ReactNode;
  columns?: 2 | 3 | 4;
}

export function InfoCardGrid({ children, columns = 3 }: InfoCardGridProps) {
  return (
    <div
      className={styles.grid}
      style={{
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
      }}
    >
      {children}
    </div>
  );
}
