import { LANGUAGE_LABELS, type SupportedLanguage } from '../language'
import type { AppCopy } from './types'
import styles from './WorkerLanguageSwitch.module.css'

const LANGUAGES: SupportedLanguage[] = ['hi-IN', 'kn-IN', 'en-IN']

type Props = {
  value: SupportedLanguage
  onChange: (language: SupportedLanguage) => void
  copy: AppCopy
}

export default function WorkerLanguageSwitch({ value, onChange, copy }: Props) {
  return (
    <div className={styles.switch} role="group" aria-label={copy.language}>
      {LANGUAGES.map((language) => (
        <button
          type="button"
          key={language}
          aria-pressed={value === language}
          lang={language}
          onClick={() => onChange(language)}
        >
          {LANGUAGE_LABELS[language]}
        </button>
      ))}
    </div>
  )
}
