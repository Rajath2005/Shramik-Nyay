# Privacy posture

- **Audio:** Microphone PCM and read-back audio are processed in memory for the active session. Consent audio is not retained or included in claim files by default (`SHRAMIK_STORE_CONSENT_AUDIO=false`). The browser may keep a temporary playback object URL until the page closes or the claim is deleted.
- **Claim files:** After the worker confirms the read-back, the backend writes a PDF draft, a Form A JSON draft, and a SAMADHAN-mapped JSON draft under `backend/claims/<claim-id>/`. These files contain the claim fields and legal-draft output needed to review or download the draft; they are not filed.
- **Retention:** A backend cleanup task deletes claim directories when their directory modification time reaches `SHRAMIK_CLAIM_TTL_SECONDS` (default: 86,400 seconds / 24 hours); downloads and new claims also trigger cleanup. Set the value to `0` to disable automatic deletion.
- **Deletion:** The visible **Delete this claim** action calls `DELETE /api/claims/<claim-id>` and removes the entire claim directory immediately.
- **Logs:** The application does not log transcripts, claim fields, audio, UANs, or provider payloads. Keep deployment and reverse-proxy access logs configured without request bodies and redact identifiers if request logging is enabled.
- **Synthetic data:** The sample replay, synthetic badge, and synthetic watermark remain clearly marked and are not real worker records.
