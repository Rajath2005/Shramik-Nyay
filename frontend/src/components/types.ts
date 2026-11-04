import { COPY, FIELD_LABELS, type SupportedLanguage } from '../language'

export type ViewMode = 'worker' | 'studio'
export type AppCopy = (typeof COPY)[SupportedLanguage]
export type ClaimFields = (typeof FIELD_LABELS)[SupportedLanguage]
