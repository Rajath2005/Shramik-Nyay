import type { AppCopy } from './types'
import { splitTranscriptByBoostedWords } from './transcriptHighlight'
import styles from './Transcript.module.css'

type Props = {
  copy: AppCopy
  language: string
  detectedLanguage: string
  latency: number | null
  transcript: string
  boostedWords: string[]
  sample: boolean
  typedAnswer: string
  onTypedAnswerChange: (value: string) => void
  onSubmitAnswer: () => void
  online: boolean
  className?: string
}

export default function Transcript({
  copy,
  language,
  detectedLanguage,
  latency,
  transcript,
  boostedWords,
  sample,
  typedAnswer,
  onTypedAnswerChange,
  onSubmitAnswer,
  online,
  className,
}: Props) {
  return (
    <article className={`${styles.zone}${className ? ` ${className}` : ''}`} aria-labelledby="transcript-heading">
      <div className={styles.heading}>
        <h2 id="transcript-heading">{copy.workerWords}</h2>
        <div className={styles.metadata}>
          {sample && <span className={styles.sampleTag}>{copy.sample}</span>}
          <span className={styles.languageTag}>{detectedLanguage || copy.waitingForLanguage}</span>
          <span className={styles.latency} aria-label={`${copy.transcriptLatency}: ${latency === null ? '—' : `${latency} ms`}`}>
            {latency === null ? '—' : `${latency} ms`}
          </span>
        </div>
      </div>
      <p className={styles.text} lang={language} aria-live="polite" aria-atomic="true">
        {transcript
          ? splitTranscriptByBoostedWords(transcript, boostedWords).map(({ text, boosted }, index) =>
              boosted ? <mark key={`${text}-${index}`}>{text}</mark> : text,
            )
          : copy.transcriptEmpty}
      </p>
      <div className={styles.footer}>
        <span className={`${styles.stateMark}${transcript ? ` ${styles.ready}` : ''}`} aria-hidden="true" />
        {transcript ? copy.transcriptCaptured : copy.waitingTranscript}
      </div>
      <form className={styles.answerForm} onSubmit={(event) => {
        event.preventDefault()
        onSubmitAnswer()
      }}>
        <label className="visually-hidden" htmlFor="studio-answer">{copy.typeAnswer}</label>
        <input
          id="studio-answer"
          value={typedAnswer}
          onChange={(event) => onTypedAnswerChange(event.target.value)}
          placeholder={copy.typeAnswer}
        />
        <button type="submit" disabled={!online || !typedAnswer.trim()}>{copy.sendAnswer}</button>
      </form>
    </article>
  )
}
