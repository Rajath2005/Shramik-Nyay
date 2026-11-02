import { describe, expect, it } from 'vitest'
import { FIELD_KEYS, isSlotVerified } from './claimSlots'

describe('claim slot state', () => {
  it('defines all nine claim slots', () => {
    expect(FIELD_KEYS).toHaveLength(9)
  })

  it.each([null, undefined, '', '  '])('treats %s as missing', (value) => {
    expect(isSlotVerified(value)).toBe(false)
  })

  it.each(['Ramesh Kumar', 0, 1200])('treats %s as verified', (value) => {
    expect(isSlotVerified(value)).toBe(true)
  })
})
