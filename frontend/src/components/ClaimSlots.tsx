import type { Audit, EvonReasoning, Slots } from '../hooks/useSession'
import { FIELD_KEYS, isSlotVerified } from '../claimSlots'
import type { AppCopy, ClaimFields } from './types'
import styles from './ClaimSlots.module.css'

const ICON: Record<string, string> = { pass: '✓', fail: '!', warn: '!', unknown: '—' }
type AuditStatus = 'pass' | 'fail' | 'warn' | 'unknown'

type Props = {
  copy: AppCopy
  fields: ClaimFields
  slots: Slots
  done: number
  firstMissing: number
  audit: Audit | null
  reasoning: EvonReasoning | null
  sample: boolean
  uan: string
  onUanChange: (value: string) => void
  onSubmitUan: () => void
  online: boolean
  uanMessage: string
  className?: string
}

export default function ClaimSlots({
  copy,
  fields,
  slots,
  done,
  firstMissing,
  audit,
  reasoning,
  sample,
  uan,
  onUanChange,
  onSubmitUan,
  online,
  uanMessage,
  className,
}: Props) {
  return (
    <article className={`${styles.zone}${className ? ` ${className}` : ''}`} aria-labelledby="slots-heading">
      <div className={styles.heading}>
        <h2 id="slots-heading">{copy.claimDetails}</h2>
        <span className={styles.count}>{copy.progressValue(done, FIELD_KEYS.length)}</span>
      </div>
      {sample && <p className={styles.sampleNotice}>{copy.sampleDetails}</p>}
      <ul className={styles.ledger}>
        {FIELD_KEYS.map((key, index) => {
          const value = slots[key]
          const verified = isSlotVerified(value)
          const active = !verified && index === firstMissing
          return (
            <li
              key={key}
              className={`${verified ? styles.verified : ''}${active ? ` ${styles.active}` : ''}`}
            >
              <span className={styles.marker} aria-hidden="true">{verified ? '✓' : active ? '›' : '—'}</span>
              <span className={styles.name} lang={copy.languageCode}>{fields[index][0]}</span>
              <span className={`${styles.value}${verified ? ` ${styles.hasValue}` : ''}`}>
                {verified ? String(value) : copy.notAnswered}
              </span>
            </li>
          )
        })}
      </ul>
      {audit && (
        <section className={styles.audit} aria-label={copy.statutoryChecks}>
          <h3>{copy.statutoryChecks}</h3>
          <ul>
            {audit.checks.map((check) => {
              const status: AuditStatus = check.status === 'pass' || check.status === 'fail' || check.status === 'warn'
                ? check.status
                : 'unknown'
              return (
                <li key={check.id} className={styles[status]}>
                  <span className={styles.auditMarker} aria-hidden="true">{ICON[status]}</span>
                  <span><b>{check.label}</b><small>{check.detail}</small></span>
                </li>
              )
            })}
          </ul>
        </section>
      )}
      {reasoning && (
        <details className={styles.reasoning}>
          <summary>{copy.reasoningDisclosure}</summary>
          <pre>{reasoning.thinkingTrace || copy.reasoningUnavailable}</pre>
        </details>
      )}
      {sample && (
        <form className={styles.uanForm} onSubmit={(event) => {
          event.preventDefault()
          onSubmitUan()
        }}>
          <label htmlFor="sample-uan">{copy.sampleUan}</label>
          <input id="sample-uan" value={uan} onChange={(event) => onUanChange(event.target.value)} inputMode="numeric" />
          <button type="submit" disabled={!online}>{copy.checkSample}</button>
        </form>
      )}
      {uanMessage && <p className={styles.message} role="status">{uanMessage}</p>}
    </article>
  )
}
