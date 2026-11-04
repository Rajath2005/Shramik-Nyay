import type { RefObject } from 'react'
import type { ConsentState } from '../hooks/useSession'
import type { AppCopy } from './types'
import styles from './ConsentBar.module.css'

type Props = {
  copy: AppCopy
  state: ConsentState
  voiceConsentRecorded: boolean
  readback: string
  language: string
  audioUrl: string | null
  audioRef: RefObject<HTMLAudioElement | null>
  audioNotice: string
  pdfUrl: string | null
  jsonUrl: string | null
  onPrepare: () => void
  onConsentAnswer?: (accepted: boolean) => void
  isSpeaking?: boolean
  onSpeakingChange?: (speaking: boolean) => void
  onAudioNotice?: (message: string) => void
  worker?: boolean
}

function stripTags(text: string) {
  return text.replace(/<[^>]+>/g, ' ')
}

export default function ConsentBar({
  copy,
  state,
  voiceConsentRecorded,
  readback,
  language,
  audioUrl,
  audioRef,
  audioNotice,
  pdfUrl,
  jsonUrl,
  onPrepare,
  onConsentAnswer,
  isSpeaking = false,
  onSpeakingChange,
  onAudioNotice,
  worker = false,
}: Props) {
  const consentStatus = {
    not_requested: copy.consentNotRequested,
    awaiting: copy.consentAwaiting,
    yes: copy.consentYes,
    no: copy.consentNo,
    unrecognized: copy.consentUnrecognized,
  }[state]
  const instruction = state === 'awaiting' ? copy.consentPrompt : copy.consentInstruction
  const consentStyles: Record<ConsentState, string> = {
    not_requested: styles.notRequested,
    awaiting: styles.awaiting,
    yes: styles.yes,
    no: styles.no,
    unrecognized: styles.unrecognized,
  }
  const className = `${styles.bar} ${worker ? styles.worker : styles.studio} ${consentStyles[state]}`
  const consentStep = worker && state === 'awaiting'

  const toggleReadback = () => {
    if (worker && audioUrl && audioRef.current) {
      if (!audioRef.current.paused) {
        audioRef.current.pause()
        onSpeakingChange?.(false)
      } else {
        void audioRef.current.play().then(() => onAudioNotice?.('')).catch(() => {
          onAudioNotice?.(copy.readbackError)
        })
      }
      return
    }

    if ('speechSynthesis' in window && window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel()
      onSpeakingChange?.(false)
      return
    }
    if (!readback || !('speechSynthesis' in window)) {
      onAudioNotice?.(copy.readbackError)
      return
    }
    const utterance = new SpeechSynthesisUtterance(stripTags(readback))
    utterance.lang = language
    utterance.onstart = () => onSpeakingChange?.(true)
    utterance.onend = () => onSpeakingChange?.(false)
    utterance.onerror = () => {
      onSpeakingChange?.(false)
      onAudioNotice?.(copy.readbackError)
    }
    window.speechSynthesis.speak(utterance)
  }

  return (
    <section className={className} aria-label={copy.consentQuestionLabel} role="status" aria-live="polite">
      {!consentStep && (
        <div className={styles.copy}>
          <strong>{consentStatus}</strong>
          <span>{instruction}</span>
          {state === 'yes' && (
            <small>{voiceConsentRecorded ? copy.voiceConsentRecorded : copy.voiceConsentNotRecorded}</small>
          )}
        </div>
      )}
      {readback && !consentStep && (
        <details className={styles.readback}>
          <summary>{worker ? copy.readbackText : copy.listenToDraft}</summary>
          <p lang={language}>{stripTags(readback)}</p>
        </details>
      )}
      {audioUrl && (
        <audio
          ref={audioRef}
          className={worker ? styles.hiddenAudio : undefined}
          controls={!worker}
          src={audioUrl}
          onPlay={() => onSpeakingChange?.(true)}
          onPause={() => onSpeakingChange?.(false)}
          onEnded={() => onSpeakingChange?.(false)}
        >
          {copy.audioUnsupported}
        </audio>
      )}
      {audioNotice && <span className={styles.audioNotice}>{audioNotice}</span>}
      {worker && (
        <button
          type="button"
          className={styles.playControl}
          disabled={!readback && !audioUrl}
          aria-pressed={isSpeaking}
          onClick={toggleReadback}
        >
          <svg aria-hidden="true" viewBox="0 0 24 24" focusable="false">
            {isSpeaking
              ? <path d="M7 5h4v14H7zM15 5h4v14h-4z" />
              : <path d="M7 4.8v14.4L19 12 7 4.8z" />}
          </svg>
          <span>{isSpeaking ? copy.readbackPause : copy.readbackPlay}</span>
        </button>
      )}
      {worker && state === 'awaiting' && (
        <div className={styles.workerConsent}>
          <p>{copy.consentVoiceHint}</p>
          <div className={styles.consentChoices}>
            <button type="button" disabled={!onConsentAnswer} onClick={() => onConsentAnswer?.(true)}>
              {copy.consentYesButton}
            </button>
            <button type="button" disabled={!onConsentAnswer} onClick={() => onConsentAnswer?.(false)}>
              {copy.consentNoButton}
            </button>
          </div>
        </div>
      )}
      {(state === 'yes' || (pdfUrl && jsonUrl)) && (
        <div className={styles.actions}>
          {pdfUrl && jsonUrl ? (
            <>
              <a href={pdfUrl} download>{copy.downloadPdf}</a>
              <a className={styles.secondary} href={jsonUrl} download>{copy.downloadJson}</a>
            </>
          ) : (
            <button type="button" disabled={state !== 'yes'} onClick={onPrepare}>
              {copy.prepareDraft}
            </button>
          )}
        </div>
      )}
    </section>
  )
}
