import { motion, AnimatePresence } from 'motion/react';
import { springs } from '../../lib/springs';
import styles from './QuestionCard.module.css';

interface Field {
  label: string;
  value: string | null;
  verified: boolean;
}

interface QuestionCardProps {
  question: string | null;
  fields: Field[];
  currentFieldIndex: number;
  totalFields: number;
  completedFields: number;
  online: boolean;
  connectionState: string;
  copy: {
    allDetailsCollected: string;
    readyToReview: string;
    progressLabel: string;
    connected: string;
    connecting: string;
    reconnecting: string;
  };
}

export function QuestionCard({
  question,
  fields,
  currentFieldIndex,
  totalFields,
  completedFields,
  online,
  connectionState,
  copy,
}: QuestionCardProps) {
  const progress = (completedFields / totalFields) * 100;

  const getStatusIcon = (index: number, verified: boolean) => {
    if (verified) return '✓';
    if (index === currentFieldIndex) return '◌';
    return '·';
  };

  const getConnectionLabel = () => {
    if (online) return copy.connected;
    if (connectionState === 'reconnecting') return copy.reconnecting;
    return copy.connecting;
  };

  return (
    <div className={styles.container}>
      <motion.div
        className={styles.questionCard}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={springs.smooth}
        layout
      >
        {/* Connection Status */}
        <div className={styles.connectionStatus}>
          <span className={`${styles.statusDot} ${!online ? styles.offline : ''}`} />
          <span>{getConnectionLabel()}</span>
        </div>

        <AnimatePresence mode="wait">
          {question ? (
            <motion.div
              key="question"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={springs.smooth}
            >
              {/* Question Header */}
              <div className={styles.questionHeader}>
                <h1 className={styles.questionText}>{question}</h1>

                {/* Progress */}
                <div className={styles.progressContainer}>
                  <span className={styles.progressText}>
                    {completedFields}/{totalFields}
                  </span>
                  <div className={styles.progressBar}>
                    <motion.div
                      className={styles.progressFill}
                      initial={{ width: 0 }}
                      animate={{ width: `${progress}%` }}
                      transition={springs.smooth}
                    />
                  </div>
                </div>
              </div>

              {/* Fields List */}
              <div className={styles.fieldsList}>
                {fields.map((field, index) => {
                  const isActive = index === currentFieldIndex && !field.verified;
                  const isCompleted = field.verified;

                  return (
                    <motion.div
                      key={index}
                      className={`${styles.fieldItem} ${
                        isActive ? styles.active : ''
                      } ${isCompleted ? styles.completed : ''}`}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ ...springs.smooth, delay: index * 0.05 }}
                      layout
                    >
                      <div className={styles.fieldIcon}>
                        {isCompleted ? '✓' : index + 1}
                      </div>
                      <div className={styles.fieldContent}>
                        <div className={styles.fieldLabel}>{field.label}</div>
                        {field.value && (
                          <motion.div
                            className={styles.fieldValue}
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            transition={springs.snappy}
                          >
                            {field.value}
                          </motion.div>
                        )}
                      </div>
                      <span className={styles.fieldStatus}>
                        {getStatusIcon(index, isCompleted)}
                      </span>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="completion"
              className={styles.completionMessage}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={springs.bouncy}
            >
              <div className={styles.completionIcon}>🎉</div>
              <h2 className={styles.completionTitle}>{copy.allDetailsCollected}</h2>
              <p className={styles.completionDescription}>{copy.readyToReview}</p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
