import { FIELD_KEYS, isSlotVerified } from '../claimSlots'
import type { Audit, Slots } from '../hooks/useSession'
import type { AppCopy, ClaimFields } from './types'
import styles from './PaperForm.module.css'

type Props = {
  copy: AppCopy
  fields: ClaimFields
  slots: Slots
  audit: Audit | null
  sample: boolean
  compact?: boolean
  studio?: boolean
  arrearsDisplayValue: number | null
}

type FieldRow = { id: string; label: string; value: string | number | null }

const CLAUSE_FIELDS = [[0, 1], [2, 3], [4, 5, 6, 7, 8], [], []] as const
const inr = (amount: number) => `₹${amount.toLocaleString('en-IN')}`

function PaperField({ label, value, missingLabel }: FieldRow & { missingLabel: string }) {
  const answered = isSlotVerified(value)
  return (
    <div className={styles.field}>
      <dt>{label}</dt>
      <dd
        key={answered ? String(value) : 'empty'}
        className={answered ? styles.value : styles.empty}
        aria-label={answered ? String(value) : missingLabel}
      >
        {answered
          ? String(value)
          : <><span className={styles.blankLine} aria-hidden="true" /><span className="visually-hidden">{missingLabel}</span></>}
      </dd>
    </div>
  )
}

export default function PaperForm({
  copy,
  fields,
  slots,
  audit,
  sample,
  compact = false,
  studio = false,
  arrearsDisplayValue,
}: Props) {
  const fieldRows: FieldRow[] = FIELD_KEYS.map((key, index) => ({
    id: key,
    label: fields[index][0],
    value: slots[key] ?? null,
  }))
  const compactRows = [fieldRows[0], fieldRows[1], fieldRows[3]]

  return (
    <div className={`${styles.sheet}${compact ? ` ${styles.compact}` : ''}${studio ? ` ${styles.studio}` : ''}`}>
      <header className={styles.documentHeader}>
        <div className={styles.identity}>
          <span className={styles.wordmark}>श्रमिक-न्याय</span>
          <span className={styles.formNumber}>FORM A</span>
        </div>
        <span className={styles.draft}>{copy.draftOnly}</span>
      </header>
      <h2 className={styles.title} lang={copy.languageCode}>{copy.claimTitle}</h2>
      {sample && <p className={styles.sample}>{copy.sampleDetails}</p>}

      {compact && !studio ? (
        <>
          <dl className={styles.compactFields}>
            {compactRows.map((row) => (
              <PaperField key={row.id} {...row} missingLabel={copy.notAnswered} />
            ))}
          </dl>
          {audit && (
            <div className={styles.compactAmount}>
              <span>{copy.estimatedArrears}</span>
              <strong aria-label={inr(audit.principal_arrears_inr)}>{inr(arrearsDisplayValue ?? 0)}</strong>
            </div>
          )}
        </>
      ) : (
        <div className={styles.clauses}>
          {CLAUSE_FIELDS.map((indices, clauseIndex) => {
            const clauseText = audit?.form_a_clauses?.[clauseIndex]
            return (
              <section className={styles.clause} key={clauseIndex}>
                <h3 lang={copy.languageCode}>
                  <span>{clauseIndex + 1}.</span> {copy.formASections[clauseIndex]}
                </h3>
                {clauseText && <p className={styles.clauseText}>{clauseText}</p>}
                {clauseIndex === 3 ? (
                  <div className={styles.amount}>
                    <span>{copy.estimatedArrears}</span>
                    {audit && (
                      <strong aria-label={inr(audit.principal_arrears_inr)}>
                        {inr(arrearsDisplayValue ?? 0)}
                      </strong>
                    )}
                    {!audit && <span className={styles.blankLine} aria-label={copy.notAnswered} />}
                  </div>
                ) : indices.length > 0 ? (
                  <dl className={styles.fields}>
                    {indices.map((fieldIndex) => {
                      const row = fieldRows[fieldIndex]
                      return <PaperField key={row.id} {...row} missingLabel={copy.notAnswered} />
                    })}
                  </dl>
                ) : null}
              </section>
            )
          })}
        </div>
      )}
      {!compact && audit?.legal_audit_summary && <p className={styles.summary}>{audit.legal_audit_summary}</p>}
    </div>
  )
}
