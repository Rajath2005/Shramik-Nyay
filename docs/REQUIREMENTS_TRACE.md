# Blueprint requirements trace

The source blueprint PDF is expected at `docs/reference/blueprint.pdf`. It is
not present in this checkout yet, so exact requirement wording and page
references remain **unmet / pending reference upload**.

| Blueprint requirement | Implementation | Test / evidence | Status |
|---|---|---|---|
| Problem statement and acceptance criteria | Pending blueprint PDF | Pending reference upload | Unmet |
| Voice-led claim intake | `backend/main.py`, `backend/audio_pacer.py`, `frontend/src/hooks/useMicrophone.ts` | `backend/test_audio_pacer.py`, WebSocket workflow | Partially verified |
| Gnani Prisma STT | `backend/audio_pacer.py` | `backend/test_audio_pacer.py`, `backend/diagnose_prisma.py` | Verified for protocol; live matrix requires authorized key |
| Gnani Evon extraction and audit | `backend/evon_legal_engine.py` | `backend/test_evon_legal_engine.py`, `verify_live_apis.py --evon` | Live Evon check returned 401 |
| Gnani Timbre read-back | `backend/timbre_tts_client.py` | `backend/test_timbre_tts_client.py`, one live diagnostic run | Live check passed |
| Wage arithmetic and checks | `backend/legal_rules.py` | `backend/test_legal_rules.py` | Verified by tests; legal constants require professional review |
| Form A PDF draft | `backend/form_a_pdf_generator.py` | `backend/test_form_a_pdf_generator.py` | Verified as draft output |
| Official filing/submission | No filing client exists | Generated payload declares `not_filed` | Unmet |
| Synthetic/demo data disclosure | `backend/samadhan_payload.py`, PDF watermark, UI sample labels | `backend/test_demo.py` | Verified |
| Data retention and deletion | `backend/main.py`, `PRIVACY.md` | Local DELETE workflow | Verified locally |
