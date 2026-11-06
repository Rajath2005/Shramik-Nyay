import { motion } from 'motion/react';
import { springs } from '../../lib/springs';
import { Button } from './Button';
import { Card, CardDescription, CardHeader, CardTitle } from './Card';
import { Badge } from './Badge';
import styles from './WelcomeScreen.module.css';

interface WelcomeScreenProps {
  onGetStarted: () => void;
  language: string;
  copy: {
    welcomeTitle: string;
    welcomeDescription: string;
    getStarted: string;
    howItWorks: string;
    step1Title: string;
    step1Description: string;
    step2Title: string;
    step2Description: string;
    step3Title: string;
    step3Description: string;
  };
}

export function WelcomeScreen({ onGetStarted, language, copy }: WelcomeScreenProps) {
  const steps = [
    {
      number: 1,
      title: copy.step1Title,
      description: copy.step1Description,
      icon: '🎤',
      delay: 0.1,
    },
    {
      number: 2,
      title: copy.step2Title,
      description: copy.step2Description,
      icon: '📝',
      delay: 0.2,
    },
    {
      number: 3,
      title: copy.step3Title,
      description: copy.step3Description,
      icon: '✓',
      delay: 0.3,
    },
  ];

  return (
    <div className={styles.container}>
      <motion.div
        className={styles.content}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={springs.smooth}
      >
        {/* Hero Section */}
        <motion.div
          className={styles.hero}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ ...springs.smooth, delay: 0.1 }}
        >
          <div className={styles.logoContainer}>
            <motion.img
              src="/logo-icon.png"
              alt="Shramik Nyay Logo"
              className={styles.logo}
              initial={{ opacity: 0, rotate: -10 }}
              animate={{ opacity: 1, rotate: 0 }}
              transition={{ ...springs.bouncy, delay: 0.2 }}
            />
          </div>
          
          <motion.h1
            className={styles.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springs.smooth, delay: 0.3 }}
          >
            {copy.welcomeTitle}
          </motion.h1>
          
          <motion.p
            className={styles.description}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springs.smooth, delay: 0.4 }}
          >
            {copy.welcomeDescription}
          </motion.p>

          <motion.div
            className={styles.badges}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springs.smooth, delay: 0.5 }}
          >
            <Badge variant="success" size="lg">
              <span className={styles.badgeIcon}>🔒</span>
              Secure & Private
            </Badge>
            <Badge variant="info" size="lg">
              <span className={styles.badgeIcon}>🌐</span>
              {language === 'hi-IN' ? 'हिंदी' : language === 'kn-IN' ? 'ಕನ್ನಡ' : 'English'}
            </Badge>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springs.smooth, delay: 0.6 }}
          >
            <Button
              size="lg"
              onClick={onGetStarted}
              className={styles.ctaButton}
            >
              {copy.getStarted}
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </Button>
          </motion.div>
        </motion.div>

        {/* How It Works Section */}
        <motion.div
          className={styles.howItWorks}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ ...springs.smooth, delay: 0.7 }}
        >
          <h2 className={styles.sectionTitle}>{copy.howItWorks}</h2>
          
          <div className={styles.steps}>
            {steps.map((step) => (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ ...springs.smooth, delay: 0.7 + step.delay }}
              >
                <Card className={styles.stepCard}>
                  <CardHeader>
                    <div className={styles.stepHeader}>
                      <div className={styles.stepIcon}>{step.icon}</div>
                      <Badge variant="neutral">{step.number}</Badge>
                    </div>
                    <CardTitle className={styles.stepTitle}>{step.title}</CardTitle>
                    <CardDescription>{step.description}</CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Trust Indicators */}
        <motion.div
          className={styles.trustIndicators}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ ...springs.smooth, delay: 1.1 }}
        >
          <div className={styles.indicator}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
            </svg>
            <span>End-to-end encrypted</span>
          </div>
          <div className={styles.indicator}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
            </svg>
            <span>GDPR compliant</span>
          </div>
          <div className={styles.indicator}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17 8l-1.41 1.41L17.17 11H9v2h8.17l-1.58 1.58L17 16l4-4-4-4zM5 5h7V3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h7v-2H5V5z" />
            </svg>
            <span>No data retention</span>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
