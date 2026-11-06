import { type LanguagePreference, type SupportedLanguage } from '../language'
import ModeToggle from './ModeToggle'
import StatusChip from './StatusChip'
import WorkerLanguageSwitch from './WorkerLanguageSwitch'
import type { ConnectionState, LiveUsage } from '../hooks/useSession'
import type { AppCopy, ViewMode } from './types'
import styles from './Header.module.css'

function ThemeIcon({ dark }: { dark: boolean }) {
  return dark ? (
    <svg aria-hidden="true" viewBox="0 0 24 24" className={styles.themeIcon}><path d="M20.2 15.1A8.5 8.5 0 0 1 8.9 3.8 8.5 8.5 0 1 0 20.2 15.1Z" /></svg>
  ) : (
    <svg aria-hidden="true" viewBox="0 0 24 24" className={styles.themeIcon}><circle cx="12" cy="12" r="4" /><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" /></svg>
  )
}

type Props = {
  mode: ViewMode
  onModeChange: (mode: ViewMode) => void
  dark: boolean
  onThemeChange: () => void
  language: LanguagePreference
  workerLanguage?: SupportedLanguage
  onLanguageChange: (language: LanguagePreference) => void
  online: boolean
  connectionState: ConnectionState
  serviceMode: string
  copy: AppCopy
  studio?: boolean
  liveUsage?: LiveUsage | null
}

export default function Header({
  mode,
  onModeChange,
  dark,
  onThemeChange,
  language,
  workerLanguage,
  onLanguageChange,
  online,
  connectionState,
  serviceMode,
  copy,
  studio = false,
  liveUsage = null,
}: Props) {
  return (
    <header className={`${styles.header}${studio ? ` ${styles.studio}` : ''}`}>
      <div className={styles.brand} aria-label="Shramik-Nyay">
        <span className="brand-logo-mark" aria-hidden="true">
          <img src="/logo-icon.png" alt="" />
        </span>
        <span className={styles.name}>श्रमिक-न्याय</span>
      </div>
      <ModeToggle mode={mode} onChange={onModeChange} copy={copy} />
      <div className={styles.controls}>
        <WorkerLanguageSwitch
          value={workerLanguage ?? (language === 'auto' ? 'hi-IN' : language)}
          onChange={onLanguageChange}
          copy={copy}
        />
        <button className={styles.themeToggle} type="button" onClick={onThemeChange} aria-label={dark ? copy.lightTheme : copy.darkTheme}>
          <ThemeIcon dark={dark} />
          {dark ? copy.lightTheme : copy.darkTheme}
        </button>
        <div className={styles.statusCluster}>
          {studio && liveUsage && (
            <span className={styles.creditCounter} role="status" aria-label="LIVE credit usage">
              LIVE · E {liveUsage.evon.used}/{liveUsage.evon.limit}
              {' · '}T {liveUsage.timbre.used}/{liveUsage.timbre.limit}
              {' · '}P {liveUsage.prisma.used}/{liveUsage.prisma.limit}
            </span>
          )}
          <StatusChip online={online} connectionState={connectionState} serviceMode={serviceMode} copy={copy} />
        </div>
      </div>
    </header>
  )
}
