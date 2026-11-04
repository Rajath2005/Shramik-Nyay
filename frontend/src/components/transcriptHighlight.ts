export type TranscriptPart = { text: string; boosted: boolean }

export function splitTranscriptByBoostedWords(text: string, words: string[]): TranscriptPart[] {
  const candidates = new Set(words.filter(Boolean).map((word) => word.toLocaleLowerCase()))
  if (!text) return []
  return text.split(/([\p{L}\p{N}_]+)/u).filter(Boolean).map((part) => ({
    text: part,
    boosted: candidates.has(part.toLocaleLowerCase()),
  }))
}
