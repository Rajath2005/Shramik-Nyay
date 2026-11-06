import { useState, type FormEvent } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { springs } from '../../lib/springs';
import styles from './TypeInputField.module.css';

interface TypeInputFieldProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  placeholder: string;
  disabled?: boolean;
  copy: {
    typeInstead: string;
    typeAnswer: string;
    sendAnswer: string;
  };
}

export function TypeInputField({
  value,
  onChange,
  onSubmit,
  placeholder,
  disabled = false,
  copy,
}: TypeInputFieldProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!value.trim() || disabled) return;
    onSubmit();
  };

  return (
    <div className={styles.container}>
      <AnimatePresence mode="wait">
        {!isExpanded ? (
          <motion.button
            key="toggle"
            className={styles.toggleButton}
            type="button"
            onClick={() => setIsExpanded(true)}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={springs.snappy}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="5" width="18" height="14" rx="2" />
              <path d="M7 9h.01M10 9h.01M13 9h.01M16 9h.01M7 13h.01M10 13h.01M13 13h.01M16 13h.01" />
            </svg>
            {copy.typeInstead}
          </motion.button>
        ) : (
          <motion.form
            key="form"
            className={styles.form}
            onSubmit={handleSubmit}
            initial={{ opacity: 0, y: 10, height: 0 }}
            animate={{ opacity: 1, y: 0, height: 'auto' }}
            exit={{ opacity: 0, y: -10, height: 0 }}
            transition={springs.smooth}
          >
            <label htmlFor="type-answer" className={styles.label}>
              {copy.typeAnswer}
            </label>
            <textarea
              id="type-answer"
              className={styles.textarea}
              rows={3}
              value={value}
              onChange={(e) => onChange(e.target.value)}
              placeholder={placeholder}
              disabled={disabled}
              autoFocus
            />
            <button
              type="submit"
              className={styles.submitButton}
              disabled={!value.trim() || disabled}
            >
              {copy.sendAnswer}
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="m5 12 14-7-3 14-3-6-8-1Z" />
              </svg>
            </button>
          </motion.form>
        )}
      </AnimatePresence>
    </div>
  );
}
