import type { AppCopy, ViewMode } from './types'
import styles from './ModeToggle.module.css'

type Props = {
  mode: ViewMode
  onChange: (mode: ViewMode) => void
  copy: AppCopy
}

export default function ModeToggle({ mode, onChange, copy }: Props) {
  return (
    <nav className={styles.toggle} aria-label={copy.viewMode}>
      <button type="button" aria-pressed={mode === 'worker'} onClick={() => onChange('worker')}>
        {copy.workerMode}
      </button>
      <button type="button" aria-pressed={mode === 'studio'} onClick={() => onChange('studio')}>
        {copy.studioMode}
      </button>
    </nav>
  )
}
