import { describe, expect, it } from 'vitest'
import { COPY, FIELD_LABELS, LANGUAGE_OPTIONS } from './language'

describe('multilingual worker experience', () => {
  it('offers automatic detection and Hindi, Kannada, and English', () => {
    expect(LANGUAGE_OPTIONS.map(({ value }) => value)).toEqual(['auto', 'hi-IN', 'kn-IN', 'en-IN'])
  })

  it('has localized interface copy and claim fields for every supported language', () => {
    for (const language of ['hi-IN', 'kn-IN', 'en-IN'] as const) {
      expect(COPY[language].welcome.length).toBeGreaterThan(0)
      expect(FIELD_LABELS[language]).toHaveLength(9)
      expect(COPY[language].progressValue(5, 9)).toContain('5')
      expect(COPY[language].consentAwaiting.length).toBeGreaterThan(0)
      expect(COPY[language].consentYes.length).toBeGreaterThan(0)
      expect(COPY[language].consentNo.length).toBeGreaterThan(0)
      expect(COPY[language].consentUnrecognized.length).toBeGreaterThan(0)
    }
  })

  it('keeps the document fields aligned to the same nine claim fields', () => {
    for (const language of ['hi-IN', 'kn-IN', 'en-IN'] as const) {
      expect(FIELD_LABELS[language].every(([label]) => label.length > 0)).toBe(true)
    }
  })
})
