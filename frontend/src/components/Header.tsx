import { type LanguagePreference, type SupportedLanguage } from '../language'
import ModeToggle from './ModeToggle'
import StatusChip from './StatusChip'
import WorkerLanguageSwitch from './WorkerLanguageSwitch'
import type { ConnectionState, LiveUsage } from '../hooks/useSession'
import type { AppCopy, ViewMode } from './types'
import styles from './Header.module.css'

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
        <span className={styles.mark} aria-hidden="true">श्रम</span>
        <span className={styles.name}>श्रमिक-न्याय</span>
      </div>
      <ModeToggle mode={mode} onChange={onModeChange} copy={copy} />
      <div className={styles.controls}>
        <WorkerLanguageSwitch
          value={workerLanguage ?? (language === 'auto' ? 'hi-IN' : language)}
          onChange={onLanguageChange}
          copy={copy}
        />
        <button className={styles.themeToggle} type="button" onClick={onThemeChange}>
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
