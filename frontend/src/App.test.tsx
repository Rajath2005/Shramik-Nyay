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
    }
  })
})
