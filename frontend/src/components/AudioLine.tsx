import type { AudioTelemetry, PipelineLatencyStage } from '../hooks/useSession'
import Oscilloscope from './Oscilloscope'
import type { AppCopy } from './types'
import styles from './AudioLine.module.css'

const STAGES: readonly PipelineLatencyStage[] = [
  'prisma_segment',
  'evon_stage_a',
  'evon_stage_b',
  'timbre_first_audio_chunk',
]

type Props = {
  copy: AppCopy
  theme: 'light' | 'dark'
  levels: number[]
  micLive: boolean
  micError: string
  sample: boolean
  online: boolean
  serviceMode: string
  telemetry: AudioTelemetry | null
  latency: number | null
  pipelineLatencies: Partial<Record<PipelineLatencyStage, number>>
  biasWords: string[]
  biasSettingsUpdated: boolean
  biasBoostFailed: boolean
  noiseLevel: number
  onNoiseLevelChange: (value: number) => void
  onToggleMicrophone: () => void
  onPlaySample: () => void
  onReplayRecordedCall: () => void
  replayActive: boolean
  className?: string
}

export function MicIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" focusable="false">
      <rect x="9" y="2.75" width="6" height="12" rx="3" />
      <path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3.25m-4 0h8" />
    </svg>
  )
}

export default function AudioLine({
  copy,
  theme,
  levels,
  micLive,
  micError,
  sample,
  online,
  serviceMode,
  telemetry,
  latency,
  pipelineLatencies,
  biasWords,
  biasSettingsUpdated,
  biasBoostFailed,
  noiseLevel,
  onNoiseLevelChange,
  onToggleMicrophone,
  onPlaySample,
  onReplayRecordedCall,
  replayActive,
  className,
}: Props) {
  const stageLabels = [copy.prismaStage, copy.extractionStage, copy.auditStage, copy.readbackStage]

  return (
    <article className={`${styles.zone}${className ? ` ${className}` : ''}`} aria-labelledby="audio-heading">
      <div className={styles.heading}>
        <h2 id="audio-heading">{copy.audioLine}</h2>
        <span className={sample ? styles.sampleSource : undefined}>
          {sample ? copy.sample : micLive ? copy.microphoneOn : copy.waitingForSpeech}
        </span>
      </div>
      <div className={styles.scopeFrame}>
        <Oscilloscope
          levels={levels}
          threshold={0.72}
          theme={theme}
          label={`${micLive ? copy.liveWaveform : sample ? copy.sampleWaveform : copy.waitingForSpeech}; ${copy.vadThreshold}`}
        />
        <span className={styles.thresholdLabel}>{copy.vadThreshold}</span>
      </div>
      <div className={styles.signalCaption}>
        <span>{telemetry?.sampleRateHz ?? 8000} Hz</span>
        <span>{micLive ? copy.inputActive : sample ? copy.sampleComplete : copy.noAudio}</span>
      </div>
      <div className={styles.telemetryLine} aria-label={copy.audioMeasurements}>
        <div><span>{copy.frameSize}</span><strong>{telemetry?.frameBytes ?? 1024} B</strong></div>
        <div><span>{copy.frameCadence}</span><strong>{telemetry?.cadenceMs ?? 64} ms</strong></div>
        <div><span>{copy.transcriptLatency}</span><strong>{latency ?? 0} ms</strong></div>
      </div>
      <div className={styles.pipelineLine}>
        {STAGES.map((stage, index) => (
          <div key={stage}>
            <span>{stageLabels[index]}</span>
            <strong>{pipelineLatencies[stage] === undefined ? '—' : `${pipelineLatencies[stage]} ms`}</strong>
          </div>
        ))}
      </div>
      <div className={styles.actions}>
        <button
          type="button"
          className={`${styles.microphone}${micLive ? ` ${styles.recording}` : ''}`}
          disabled={(!online || serviceMode !== 'LIVE') && !micLive}
          onClick={onToggleMicrophone}
        >
          <MicIcon />
          {micLive ? copy.stopRecording : copy.speakAnswer}
        </button>
        {sample && (
          <button type="button" className={styles.sampleAction} disabled={!online} onClick={onPlaySample}>
            {copy.playSample}
          </button>
        )}
        {serviceMode === 'LIVE' && (
          <button type="button" className={styles.sampleAction} disabled={!online || replayActive} onClick={onReplayRecordedCall}>
            {replayActive ? copy.replayActive : copy.replayRecordedCall}
          </button>
        )}
      </div>
      {serviceMode === 'LIVE' && (
        <details className={styles.noiseTest}>
          <summary>{copy.noiseTest}</summary>
          <label htmlFor="noise-level">{copy.noiseLevel}</label>
          <input
            id="noise-level"
            type="range"
            min="0"
            max="100"
            step="1"
            value={noiseLevel}
            aria-valuetext={`${noiseLevel}%`}
            onChange={(event) => onNoiseLevelChange(Number(event.target.value))}
          />
          <output htmlFor="noise-level">{noiseLevel}%</output>
        </details>
      )}
      <p className={styles.boostLabel}>{copy.vocabularyHints}</p>
      <div className={styles.boostList} role="status">
        {biasWords.length
          ? biasWords.map((word) => <span className={styles.word} key={word}>{word}</span>)
          : <span>{copy.noVocabularyHints}</span>}
        {biasWords.length > 0 && (
          <span className={`${styles.boostState}${biasSettingsUpdated ? ` ${styles.confirmed}` : ''}`}>
            {biasSettingsUpdated
              ? copy.vocabularyReady
              : biasBoostFailed ? copy.vocabularyFailed : copy.vocabularyUpdating}
          </span>
        )}
      </div>
      {micError && <p className={styles.error} role="alert">{copy.microphoneError}</p>}
    </article>
  )
}
