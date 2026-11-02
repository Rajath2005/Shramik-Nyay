export const FIELD_KEYS = [
  'worker_name',
  'worksite_locality_and_sphere',
  'contractor_name_and_phone',
  'principal_employer_name',
  'wage_period_start',
  'wage_period_end',
  'days_worked',
  'agreed_daily_wage_inr',
  'advance_received_inr',
] as const

export function isSlotVerified(value: unknown): boolean {
  if (typeof value === 'string') return value.trim().length > 0
  return typeof value === 'number'
}
