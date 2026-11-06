import { motion } from 'motion/react';
import { springs } from '../../lib/springs';
import styles from './StudioHeader.module.css';

type ViewMode = 'worker' | 'studio';
type ConnectionState = 'connected' | 'connecting' | 'reconnecting' | 'disconnected';
type LanguagePreference = 'auto' | 'hi-IN' | 'kn-IN' | 'en-IN';

interface LiveUsage {
  evon: { used: number; limit: number };
  timbre: { used: number; limit: number };
  prisma: { used: number; limit: number };
}

interface StudioHeaderProps {
  mode: ViewMode;
  onModeChange: (mode: ViewMode) => void;
  dark: boolean;
  onThemeChange: () => void;
  language: LanguagePreference;
  onLanguageChange: (language: LanguagePreference) => void;
  online: boolean;
  connectionState: ConnectionState;
  serviceMode: string;
  liveUsage?: LiveUsage | null;
  copy: {
    workerMode: string;
    studioMode: string;
    lightTheme: string;
    darkTheme: string;
    connected: string;
    connecting: string;
    reconnecting: string;
  };
}

export function StudioHeader({
  mode,
  onModeChange,
  dark,
  onThemeChange,
  language,
  onLanguageChange,
  online,
  connectionState,
  serviceMode,
  liveUsage,
  copy,
}: StudioHeaderProps) {
  const getLanguageLabel = (lang: LanguagePreference) => {
    switch (lang) {
      case 'hi-IN': return 'हिंदी';
      case 'kn-IN': return 'ಕನ್ನಡ';
      case 'en-IN': return 'English';
      default: return 'Auto';
    }
  };

  const getStatusText = () => {
    if (!online) {
      if (connectionState === 'reconnecting') return copy.reconnecting;
      return copy.connecting;
    }
    return copy.connected;
  };

  const getStatusClass = () => {
    if (!online) {
      if (connectionState === 'reconnecting') return styles.reconnecting;
      return styles.offline;
    }
    return '';
  };

  return (
    <motion.header
      className={styles.header}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={springs.smooth}
    >
      <div className={styles.container}>
        {/* Brand */}
        <div className={styles.brand}>
          <div className={styles.logo}>
            <img src="/logo-icon.png" alt="Shramik Nyay Logo" />
          </div>
          <span className={styles.brandName}>श्रमिक-न्याय</span>
        </div>

        {/* Mode Toggle */}
        <div className={styles.modeToggle}>
          <button
            type="button"
            className={`${styles.modeButton} ${mode === 'worker' ? styles.active : ''}`}
            onClick={() => onModeChange('worker')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            </svg>
            {copy.workerMode}
          </button>
          <button
            type="button"
            className={`${styles.modeButton} ${mode === 'studio' ? styles.active : ''}`}
            onClick={() => onModeChange('studio')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path d="M9 3v18M3 9h18M3 15h6M15 15h6" />
            </svg>
            {copy.studioMode}
          </button>
        </div>

        {/* Controls */}
        <div className={styles.controls}>
          {/* Language Selector */}
          <div className={styles.languageSelector}>
            <button
              type="button"
              className={styles.languageButton}
              onClick={() => {
                const languages: LanguagePreference[] = ['auto', 'hi-IN', 'kn-IN', 'en-IN'];
                const currentIndex = languages.indexOf(language);
                const nextIndex = (currentIndex + 1) % languages.length;
                onLanguageChange(languages[nextIndex]);
              }}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
              </svg>
              {getLanguageLabel(language)}
            </button>
          </div>

          {/* Theme Toggle */}
          <motion.button
            type="button"
            className={styles.themeToggle}
            onClick={onThemeChange}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            transition={springs.snappy}
            aria-label={dark ? copy.lightTheme : copy.darkTheme}
          >
            {dark ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20.2 15.1A8.5 8.5 0 0 1 8.9 3.8 8.5 8.5 0 1 0 20.2 15.1Z" />
              </svg>
            )}
          </motion.button>

          {/* Status */}
          <div className={styles.status}>
            {liveUsage && serviceMode === 'LIVE' && (
              <div className={styles.liveUsage}>
                <span className={styles.liveDot} />
                <span>
                  LIVE · E {liveUsage.evon.used}/{liveUsage.evon.limit} · 
                  T {liveUsage.timbre.used}/{liveUsage.timbre.limit} · 
                  P {liveUsage.prisma.used}/{liveUsage.prisma.limit}
                </span>
              </div>
            )}

            <div className={`${styles.statusChip} ${getStatusClass()}`}>
              <span className={styles.statusDot} />
              {getStatusText()}
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
}
