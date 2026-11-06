import { useState, useRef } from 'react';
import { motion } from 'motion/react';
import { springs } from '../../lib/springs';
import { triggerHaptic } from '../../lib/haptics';
import styles from './MicrophoneButton.module.css';

interface Ripple {
  id: number;
  x: number;
  y: number;
}

interface MicrophoneButtonProps {
  isRecording: boolean;
  disabled?: boolean;
  state?: 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';
  onClick: () => void;
  ariaLabel?: string;
}

export function MicrophoneButton({
  isRecording,
  disabled = false,
  state = 'idle',
  onClick,
  ariaLabel,
}: MicrophoneButtonProps) {
  const [ripples, setRipples] = useState<Ripple[]>([]);
  const nextRippleId = useRef(0);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled) return;

    // Trigger haptic feedback
    triggerHaptic(isRecording ? 'medium' : 'light');

    // Create ripple effect
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const newRipple: Ripple = {
      id: nextRippleId.current++,
      x,
      y,
    };

    setRipples((prev) => [...prev, newRipple]);

    // Remove ripple after animation completes
    setTimeout(() => {
      setRipples((prev) => prev.filter((r) => r.id !== newRipple.id));
    }, 600);

    onClick();
  };

  return (
    <motion.button
      className={`${styles.button} ${isRecording ? styles.recording : ''} ${
        styles[state] || ''
      }`}
      onClick={handleClick}
      disabled={disabled}
      aria-label={ariaLabel}
      whileHover={!disabled ? { scale: 1.05 } : {}}
      whileTap={!disabled ? { scale: 0.95 } : {}}
      transition={springs.snappy}
    >
      {/* Pulse rings when recording */}
      {isRecording && (
        <>
          <motion.span
            className={styles.pulseRing}
            initial={{ scale: 1, opacity: 0.6 }}
            animate={{ scale: 1.5, opacity: 0 }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeOut',
            }}
          />
          <motion.span
            className={styles.pulseRing}
            initial={{ scale: 1, opacity: 0.6 }}
            animate={{ scale: 1.5, opacity: 0 }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeOut',
              delay: 0.75,
            }}
          />
        </>
      )}

      {/* Ripple effects */}
      {ripples.map((ripple) => (
        <motion.span
          key={ripple.id}
          className={styles.ripple}
          style={{ left: ripple.x, top: ripple.y }}
          initial={{ scale: 0, opacity: 0.6 }}
          animate={{ scale: 4, opacity: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        />
      ))}

      {/* Microphone Icon */}
      <motion.svg
        className={styles.icon}
        width="32"
        height="32"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        animate={
          isRecording
            ? {
                scale: [1, 1.1, 1],
              }
            : {}
        }
        transition={{
          duration: 0.5,
          repeat: isRecording ? Infinity : 0,
        }}
      >
        {isRecording ? (
          <>
            {/* Stop icon when recording */}
            <rect x="6" y="6" width="12" height="12" rx="2" />
          </>
        ) : (
          <>
            {/* Microphone icon when not recording */}
            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            <line x1="12" x2="12" y1="19" y2="22" />
          </>
        )}
      </motion.svg>

      {/* Recording indicator dot */}
      {isRecording && (
        <motion.span
          className={styles.recordingDot}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0 }}
          transition={springs.bouncy}
        />
      )}
    </motion.button>
  );
}

export function MicIcon() {
  return (
    <svg
      width="32"
      height="32"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" x2="12" y1="19" y2="22" />
    </svg>
  );
}
