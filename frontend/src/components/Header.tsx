import { isLanguagePreference, LANGUAGE_OPTIONS, type LanguagePreference, type SupportedLanguage } from '../language'
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
  worker?: boolean
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
  worker = false,
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
        {worker ? (
          <WorkerLanguageSwitch
            value={workerLanguage ?? 'hi-IN'}
            onChange={onLanguageChange}
            copy={copy}
          />
        ) : (
          <>
            <label className="visually-hidden" htmlFor="language-choice">{copy.language}</label>
            <select
              id="language-choice"
              value={language}
              onChange={(event) => {
                if (isLanguagePreference(event.target.value)) onLanguageChange(event.target.value)
              }}
            >
              {LANGUAGE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.value === 'auto' ? copy.autoDetect : option.label}
                </option>
              ))}
            </select>
          </>
        )}
        <button className={styles.themeToggle} type="button" onClick={onThemeChange}>
          {dark ? copy.lightTheme : copy.darkTheme}
        </button>
        {studio && liveUsage && (
          <div className={styles.creditCounter} role="status" aria-label="LIVE credit usage">
            LIVE credits: Evon {liveUsage.evon.used}/{liveUsage.evon.limit}
            {' · '}Timbre {liveUsage.timbre.used}/{liveUsage.timbre.limit}
            {' · '}Prisma {liveUsage.prisma.used}/{liveUsage.prisma.limit}
          </div>
        )}
        <StatusChip online={online} connectionState={connectionState} serviceMode={serviceMode} copy={copy} />
      </div>
    </header>
  )
}
