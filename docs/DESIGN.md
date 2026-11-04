# Shramik-Nyay design system

## Product and visual direction

**The claim writes itself.** A worker speaks one fact at a time; the Form A
document quietly takes shape beside the conversation. The paper is the
evidence, not a decorative preview. A dark, precise audio instrument makes
the live process legible without competing with the claim.

The product serves two very different viewers:

- **Worker:** a person on a low-cost phone who may prefer to speak, may have
  limited literacy, and may switch between Hindi, Kannada, and English.
- **Studio viewer:** a judge, engineer, or reviewer watching one 60-second
  recording and needing to understand what was heard, what was extracted, and
  what the worker is being asked to approve.

Keep the worker experience plain and reassuring, with the directness of a
civic service. Make Studio feel like a calibrated audio instrument beside an
official paper record. The signature is the material contrast between the
dark console and warm Form A paper.

Do not use a landing-page hero, uniform card grid, decorative icons, emoji,
gradient, glow, glass effect, stock illustration, or filler welcome. Align
content to the left. Use rules, labels, and state changes only when they help
someone understand a claim or act safely. Do not imply that a draft has been
filed, legally approved, or submitted to an authority.

## Color tokens

The console has complete dark and light palettes. Form A remains warm paper in
both themes so its purpose is recognizable. Ratios below are WCAG contrast
ratios, calculated for the named text/accent color against both console
surfaces. All text combinations exceed 4.5:1. Borders are non-text graphics;
keep them distinct from their adjacent surface.

| Token | Use | Dark | Light | Dark contrast (surface / raised) | Light contrast (surface / raised) |
|---|---|---:|---:|---:|---:|
| `surface` | Main console canvas | `#101820` | `#F0F3F5` | — | — |
| `raised` | Console controls and inset regions | `#17232D` | `#FFFFFF` | — | — |
| `line` | Hairline dividers, input and zone boundaries | `#687A8A` | `#697985` | 4.04 / 3.60 | 4.03 / 4.49 |
| `ink` | Primary text | `#F3F5F7` | `#14212B` | 16.37 / 14.62 | 14.70 / 16.38 |
| `mute` | Secondary text, never the only status cue | `#BAC4CE` | `#52616D` | 10.12 / 9.03 | 5.73 / 6.38 |
| `amber` | Missing information, attention, warning | `#FFD166` | `#764B00` | 12.41 / 11.08 | 6.79 / 7.56 |
| `emerald` | Verified fact, successful check | `#80DDA8` | `#176940` | 10.93 / 9.76 | 6.02 / 6.71 |
| `blue` | Active system, selected control, focus | `#8CC8FF` | `#1B5F9E` | 10.07 / 8.99 | 5.93 / 6.61 |
| `paper` | Form A document in either theme | `#FFF9EA` | `#FFF9EA` | — | — |
| `paper-ink` | Main paper text | `#1D2A2D` | `#1D2A2D` | 14.06 on paper | 14.06 on paper |
| `paper-mute` | Paper labels and supporting text | `#536168` | `#536168` | 6.10 on paper | 6.10 on paper |
| `paper-verified` | Verified amount or fact on paper | `#176940` | `#176940` | 6.38 on paper | 6.38 on paper |

Use the same status meaning in both themes. Pair each color with a word, icon,
or structural marker; color alone never communicates verification or error.
Do not add red, pink, or purple as status accents. An error uses the `amber`
attention treatment plus a specific message and recovery action. Focus uses a
visible 3px `blue` outline with offset; where blue does not contrast against
the current control, place the outline against a contrasting outer ring.

The contrast values are for these exact tokens. Recalculate if a value or its
background changes; do not lower text opacity or blend a text token with a
surface. Avoid placing console `mute` text on paper: use `paper-mute`.

## Type

| Role | Family | Use |
|---|---|---|
| Interface | Atkinson Hyperlegible | Questions, controls, transcript, claim details, and all UI labels |
| Devanagari | Noto Sans Devanagari | Hindi UI and worker speech |
| Kannada | Noto Sans Kannada | Kannada UI and worker speech |
| Form heading | Source Serif 4 | Form A title and paper section headings only |
| Instrument data | IBM Plex Mono | Latency, sample rate, frame size, and other measured values |

Use the script-specific Noto Sans face before the generic sans fallback. Keep
the serif to paper headings; long-form paper content and all controls remain
in the accessible sans face. Prefer self-hosted font assets so a weak or
offline connection does not remove script support. The UI must remain usable
if a non-script display family fails to load.

| Level | Worker | Studio |
|---|---:|---:|
| Main question / transcript | 28–40px, 1.35 line height | 20–28px, 1.45 line height |
| Zone / paper heading | 22–28px | 16–22px |
| Body / claim values | 18–20px | 14–16px |
| Supporting labels | 14–16px | 12–13px |
| Dense telemetry only | Not shown | 11px minimum |

No Worker-mode text may fall below 13px; no Studio text may fall below 11px.
Do not use tiny grey captions as a substitute for hierarchy. Use sentence
case, normal letter spacing, and readable line lengths. Enable tabular
numerals for every count, amount, date, and latency value; keep currency and
date formatting consistent within a claim.

## Shape, spacing, and elevation

- Use a **4px spacing grid**. Common gaps are 8, 12, 16, 24, and 32px.
- Use only two radii: **4px** for controls and document details; **8px** for
  instrument zones and larger interactive surfaces. Do not make every region
  a rounded card.
- Separate console zones with 1px hairline borders and deliberate spacing.
  Avoid drop-shadow stacks and floating-card treatments.
- The paper is the only elevated surface: one quiet, hard 2px offset in the
  surrounding surface color, plus its own hairline edge. It should read as a
  physical sheet, not a floating modal.
- Preserve generous space around the active question and paper. Keep
  telemetry compact and aligned in rows, not a grid of identical cards.

## Modes and layout

The header contains the Shramik-Nyay identity, a persistent **Worker / Studio**
mode switch, language selection, and theme control. Remember mode and theme
locally. Language remains visible and changeable without burying it in
settings. Do not use a text-only “engineer view” toggle as a substitute for
the two explicit modes.

### Worker mode

One question at a time; the next question follows the current answer. The
question is the visual anchor, followed by plain progress, one large
microphone control, and a quiet paper preview. No telemetry, technical
vocabulary, legal reasoning trace, or raw event log appears here. A
keyboard-first “Type an answer” alternative is available without competing
with the main microphone action. Keep the 9-field count and progress clear.

```text
┌─────────────────────────────────────┐
│ श्रमिक-न्याय     Worker  Studio  हिन्दी │
├─────────────────────────────────────┤
│                                     │
│  How much pay are you owed?         │
│  5 of 9 answers recorded            │
│                                     │
│             ┌─────────┐             │
│             │  Speak  │             │
│             └─────────┘             │
│        Type an answer instead       │
│                                     │
├─────────────────────────────────────┤
│ Form A preview                      │
│ Name · Worksite · Unpaid wages      │
│ Draft only — not filed               │
└─────────────────────────────────────┘
               360px wide
```

At 360px, use one column, no horizontal scrolling, comfortable text wrapping,
and a mic target at least 64px square. Every interactive target is at least
44×44px. Keep the paper preview quiet and short; opening it must not lose the
current question or progress. Do not make the worker scan several questions
or nine fields at once.

In MOCK_REPLAY, label the experience as a sample and clearly say that sample
speech and claim details are synthetic. Disable live microphone capture and
offer the sample replay or typed answer. Never represent sample data as a
worker’s real claim.

### Studio mode

Design for a fixed 1920×1080 recording frame with no page scroll. Use the
following positions and reading order: audio line (top-left), live transcript
(bottom-left), claim slots and reasoning (top-right), Form A and consent
(bottom-right). The Form A zone is visually largest and remains the focal
surface. Keep the header short; fit the four zones into the remaining
viewport. Do not add a separate raw-event list to the main composition.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Shramik-Nyay        Worker / Studio       Theme       Language   LIVE     │
├───────────────────────────────┬──────────────────────────────────────────┤
│ 1  AUDIO LINE                 │ 3  CLAIM SLOTS + REASONING               │
│    waveform / signal state    │    nine facts; checks; expandable trace  │
│    frame + latency readouts   │                                          │
├───────────────────────────────┼──────────────────────────────────────────┤
│ 2  LIVE TRANSCRIPT            │ 4  FORM A + CONSENT                      │
│    worker’s words             │    ┌──────────────────────────────────┐  │
│    boosted vocabulary marks   │    │                                  │  │
│                               │    │       FORM A PAPER               │  │
│                               │    │       largest surface            │  │
│                               │    │                                  │  │
│                               │    └──────────────────────────────────┘  │
│                               │    consent state / read-back / action    │
└───────────────────────────────┴──────────────────────────────────────────┘
                                1920 × 1080; no page scroll
```

Keep the left column instrument-like and dense but legible. Allocate more
width and height to the right column; the lower-right paper zone should be
the largest single zone. Give the document enough room for names, dates,
amounts, and consent copy without truncation. Put detailed reasoning behind
an explicit disclosure; it must not displace the paper.

At a viewport smaller than the Studio canvas, do not silently crop or create
page scrolling: offer a direct switch to Worker mode or a clear
“Studio requires a 1920×1080 display” message. The Studio canvas is not a
mobile layout.

## Component inventory

All components expose the same six state names. The state description is
specific to each component; do not render six generic colored cards.

| Component | Empty | Active | Success | Warning | Error | Disabled | MOCK / LIVE distinction |
|---|---|---|---|---|---|---|---|
| **Mic control** | Ready, with a clear speak action | Listening; show stop action and local input state | Speech stopped and a transcript was received | Still listening or waiting for speech; explain what to do | Permission or service failure with a recovery step | Offline, or MOCK_REPLAY capture unavailable | MOCK offers sample replay or typing and states the mic is not live. LIVE captures real microphone audio; no fake active state. |
| **Oscilloscope** | Quiet baseline marked “Waiting for speech” | Bars reflect actual input signal; show the agreed noise-floor indicator only when available | Hold the last measured trace briefly and label it as captured | Synthetic trace, high ambient noise, or no recent frames is explicitly labeled | Telemetry is malformed or unavailable; show “Signal unavailable,” not invented data | No stream/session; neutral baseline | MOCK shows only the prerecorded `waveform` and “Sample audio.” LIVE shows microphone-derived local levels or actual server telemetry. Never animate a fabricated waveform. |
| **Slot row** | “Not yet answered” in amber; retain its field name | Only the field asked for next is marked active in blue | Captured value in ink with a non-color verified marker | Partial or uncertain value asks for a repeat; do not imply backend confidence not present in the event | Invalid data only if a real validation result exists; otherwise show a general service error outside the row | No active claim/session | MOCK values carry a visible synthetic label. LIVE values come from the claim session. |
| **Transcript line + boosted words** | Explain that the worker’s words will appear here | Listening status while awaiting a transcript; do not invent partial text | Show the exact received transcript; distinct boosted-term treatment | Mark sample transcript or a boost request awaiting confirmation | Show transcript/service error and a recovery path | No audio session | MOCK is marked as a sample transcript. LIVE shows received speech. Boosted words are vocabulary hints, not proof of recognition or legal fact. |
| **Paper document** | Form A skeleton with clear “Not yet answered” values | Newly received facts ink into their matching fields | Filled fact or calculated amount is legible and source-appropriate | Missing fields, estimated amount, unconfirmed consent, or sample data are explicitly identified | A failed draft action explains that no file was created | No claim session; paper skeleton remains a quiet preview | MOCK has a persistent “SAMPLE — synthetic details” mark. LIVE reads only current session data. Both show “Draft only — not filed” until another filing contract exists. |
| **Statutory check row** | “Checks appear after claim details are complete” | “Checking these details” only while the audit is actually running | Name the passed check; use a word/icon plus emerald | A failed/warn result uses its supplied label/detail and amber; do not call it legal advice | Missing or malformed audit response is a service error, distinct from a failed check | No completed Stage B audit | MOCK checks are identified as sample results. LIVE displays the returned audit without changing its legal meaning. |
| **Latency readout** | Em dash plus “No measurement yet” | Show only a measured, in-flight stage if one is exposed | Show measured milliseconds with tabular numerals and stage label | Distinguish stale, missing, or sample latency; never imply a zero | Invalid/unavailable measurement is named; do not substitute a success-shaped value | Telemetry disabled or not available | MOCK labels values “Sample”; LIVE uses received measurements. No fabricated interpolation. |
| **Status chip** | “Connecting” with neutral marker | “Listening” or “Connected” with current mode stated | “Connected · LIVE” or “Sample ready” | “Sample mode” or “Waiting for transcript” | “Connection lost” / service message with reconnect guidance | Relevant action unavailable | The chip distinguishes MOCK_REPLAY from LIVE in text, not color alone. |
| **Consent bar** | Hidden until read-back is ready; before that, no consent prompt | Read-back is ready; ask for an explicit yes or no | “You agreed to prepare this draft” and enable preparation | “I didn’t catch that” or “No draft will be prepared”; explain the next step | Consent/audio service error; do not interpret silence as yes | Preparation disabled until affirmative consent and audit exist | MOCK says the read-back and response are sample-only. LIVE makes clear consent prepares a draft; it does not file a claim. |

### State and data rules

- A slot is verified only when its value is present; do not label it
  “verified by law” or infer confidence from a populated string.
- Keep “missing,” “not provided,” “uncertain,” and “failed check” distinct.
- Do not use a positive green status for a sample, a pending check, or a
  merely generated value.
- The paper remains readable during partial entry. Use a short ink-in
  transition only when a new fact arrives; do not animate the entire page.
- In the right-hand paper zone, consent remains separate from the legal
  check result and from the document’s draft status.

## Motion

- Filling one claim slot uses a 150–250ms ink-in reveal; reduce it to no
  animation when `prefers-reduced-motion: reduce` is enabled.
- A slot moves from amber to emerald only when its value becomes present.
  The transition is brief and does not pulse or glow.
- The oscilloscope reflects actual input or sample waveform data. No
  decorative oscillation, looping progress, or generated “voice” animation.
- Do not animate page entry, cards, labels, or background surfaces.
- Keep focus movement and status updates immediate. Motion never delays an
  action, reading, or confirmation.

## Copy and localization

Use short, specific, active sentences. Ask about wages, not “your issue.”
Avoid technical terms in Worker mode, double labels, “Welcome to…,” vague
success messages, and claims that imply a draft has been filed. Keep backend
follow-up questions and statutory check details grounded in their returned
meaning. Localize the displayed wording without changing their event payload
or legal meaning. Map known `notice` and `error` conditions to the recovery
copy in this catalog instead of showing raw exception text or internal event
names.

The table gives proposed shared and Worker-mode strings. **† means a native
Hindi or Kannada speaker must review the wording in the context of a real
worker conversation before release.** Consent, wage, and statutory terms
require a labor-rights/domain reviewer as well as a language reviewer.

| Purpose | English | Hindi | Kannada |
|---|---|---|---|
| First question | How much pay are you owed? | आपकी कितनी मज़दूरी बाकी है? † | ನಿಮಗೆ ಬರಬೇಕಿರುವ ಕೂಲಿ ಎಷ್ಟು? † |
| Progress example | 5 of 9 answers recorded | 9 में से 5 जवाब दर्ज हुए † | 9ರಲ್ಲಿ 5 ಉತ್ತರಗಳು ದಾಖಲಾಗಿವೆ † |
| Start speaking | Speak your answer | अपना जवाब बोलें † | ನಿಮ್ಮ ಉತ್ತರವನ್ನು ಹೇಳಿ † |
| Stop speaking | Stop recording | रिकॉर्डिंग रोकें † | ಧ್ವನಿಮುದ್ರಣ ನಿಲ್ಲಿಸಿ † |
| Text alternative | Type an answer instead | जवाब लिखें † | ಉತ್ತರವನ್ನು ಟೈಪ್ ಮಾಡಿ † |
| Submit typed answer | Send answer | जवाब भेजें † | ಉತ್ತರ ಕಳುಹಿಸಿ † |
| Language control | Language | भाषा | ಭಾಷೆ |
| Automatic language | Detect automatically | भाषा अपने आप पहचानें † | ಭಾಷೆಯನ್ನು ಸ್ವಯಂ ಗುರುತಿಸಿ † |
| Worker paper preview | Form A preview | फ़ॉर्म A की झलक † | ಫಾರ್ಮ್ A ಮುನ್ನೋಟ † |
| Missing field | Not answered yet | अभी जवाब नहीं मिला † | ಇನ್ನೂ ಉತ್ತರ ಸಿಕ್ಕಿಲ್ಲ † |
| Claim status | Draft only — not filed | यह सिर्फ़ मसौदा है। दावा दाखिल नहीं हुआ है। † | ಇದು ಕರಡು ಮಾತ್ರ. ಅರ್ಜಿ ಸಲ್ಲಿಕೆಯಾಗಿಲ್ಲ. † |
| Consent prompt | Listen to the draft. Say yes to prepare it, or no to stop. | मसौदा सुनें। इसे तैयार करने के लिए हाँ कहें, रोकने के लिए ना। † | ಕರಡನ್ನು ಕೇಳಿ. ಸಿದ್ಧಪಡಿಸಲು ಹೌದು, ನಿಲ್ಲಿಸಲು ಇಲ್ಲ ಎಂದು ಹೇಳಿ. † |
| Consent yes | You agreed to prepare this draft. | आपने यह मसौदा तैयार करने की सहमति दी है। † | ಈ ಕರಡನ್ನು ಸಿದ್ಧಪಡಿಸಲು ನೀವು ಒಪ್ಪಿದ್ದೀರಿ. † |
| Consent no | No draft will be prepared. | मसौदा तैयार नहीं होगा। † | ಕರಡು ಸಿದ್ಧಪಡಿಸುವುದಿಲ್ಲ. † |
| Consent not understood | I didn’t catch that. Say yes or no. | जवाब समझ नहीं आया। हाँ या ना कहें। † | ಉತ್ತರ ಅರ್ಥವಾಗಲಿಲ್ಲ. ಹೌದು ಅಥವಾ ಇಲ್ಲ ಎಂದು ಹೇಳಿ. † |
| Mic permission error | Microphone access is off. Allow it in your browser, or type your answer. | माइक्रोफ़ोन की अनुमति नहीं है। ब्राउज़र में अनुमति दें या जवाब लिखें। † | ಮೈಕ್ರೊಫೋನ್ ಅನುಮತಿ ಇಲ್ಲ. ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಅನುಮತಿಸಿ ಅಥವಾ ಉತ್ತರ ಟೈಪ್ ಮಾಡಿ. † |
| Sample mode | Sample recording — not a live worker call. | यह नमूना रिकॉर्डिंग है, किसी असली मज़दूर की बातचीत नहीं। † | ಇದು ಮಾದರಿ ಧ್ವನಿಮುದ್ರಣ; ನೈಜ ಕಾರ್ಮಿಕರ ಕರೆ ಅಲ್ಲ. † |
| Connection error | Connection lost. Reconnecting… | सेवा से संपर्क टूट गया है। फिर से जुड़ रहे हैं… † | ಸಂಪರ್ಕ ಕಡಿತವಾಗಿದೆ. ಮತ್ತೆ ಸಂಪರ್ಕಿಸುತ್ತಿದ್ದೇವೆ… † |
| UAN lookup (Studio / MOCK only) | Sample registry lookup | नमूना रजिस्टर में जाँच † | ಮಾದರಿ ನೋಂದಣಿಯಲ್ಲಿ ಪರಿಶೀಲಿಸಿ † |
| UAN not found (Studio / MOCK only) | UAN not found in the sample registry. Check the number and try again. | नमूना रजिस्टर में यह UAN नहीं मिला। नंबर जाँचकर फिर कोशिश करें। † | ಮಾದರಿ ನೋಂದಣಿಯಲ್ಲಿ ಈ UAN ಸಿಗಲಿಲ್ಲ. ಸಂಖ್ಯೆಯನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ. † |
| Read-back audio unavailable | Draft audio could not be prepared. Read the draft, then ask for a clear yes or no. | मसौदे की आवाज़ तैयार नहीं हुई। मसौदा पढ़ें, फिर साफ़ हाँ या ना पूछें। † | ಕರಡಿನ ಧ್ವನಿ ಸಿದ್ಧವಾಗಲಿಲ್ಲ. ಕರಡನ್ನು ಓದಿ, ನಂತರ ಸ್ಪಷ್ಟ ಹೌದು ಅಥವಾ ಇಲ್ಲ ಎಂದು ಕೇಳಿ. † |
| Draft review details unavailable | Review details are unavailable. The draft is not verified. | जाँच की जानकारी नहीं मिली। मसौदे की पुष्टि नहीं हुई है। † | ಪರಿಶೀಲನೆಯ ವಿವರಗಳು ಲಭ್ಯವಿಲ್ಲ. ಕರಡು ದೃಢಪಟ್ಟಿಲ್ಲ. † |
| Microphone service error | The microphone could not connect. Try again or type your answer. | माइक्रोफ़ोन नहीं जुड़ सका। फिर कोशिश करें या जवाब लिखें। † | ಮೈಕ್ರೊಫೋನ್ ಸಂಪರ್ಕವಾಗಲಿಲ್ಲ. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ ಅಥವಾ ಉತ್ತರ ಟೈಪ್ ಮಾಡಿ. † |
| Draft preparation blocked | Listen to the draft and say yes before preparing the files. | फ़ाइलें बनाने से पहले मसौदा सुनें और हाँ कहें। † | ಫೈಲ್‌ಗಳನ್ನು ಸಿದ್ಧಪಡಿಸುವ ಮೊದಲು ಕರಡನ್ನು ಕೇಳಿ ಹೌದು ಎಂದು ಹೇಳಿ. † |

Studio-only labels should be terse but human-readable: **Audio line**, **Live
transcript**, **Claim details**, **Statutory checks**, **Form A**, **Consent**,
**Sample**, and **LIVE**. Put technical units beside values (“64 ms,”
“8 kHz”), not in explanatory prose for workers. Replace raw event names and
internal model terminology with a human label in the presentation layer.

### Remaining existing interface copy

This catalog covers the remaining static strings currently owned by the
frontend. It replaces the existing generic/demo-oriented labels; it is not
an additional set of captions to show together. **† still requires native
review.** Technical diagnostic text is Studio-only.

| Purpose | English | Hindi | Kannada |
|---|---|---|---|
| Worker mode | Worker | श्रमिक † | ಕಾರ್ಮಿಕ † |
| Studio mode | Studio | स्टूडियो † | ಸ್ಟುಡಿಯೋ † |
| Hear prompts | Hear questions and the draft | सवाल और मसौदा सुनें † | ಪ್ರಶ್ನೆ ಮತ್ತು ಕರಡನ್ನು ಕೇಳಿ † |
| Read-aloud enabled | Read aloud: on | आवाज़ में सुनना: चालू † | ಧ್ವನಿಯಲ್ಲಿ ಕೇಳುವುದು: ಆನ್ † |
| Read-aloud disabled | Read aloud: off | आवाज़ में सुनना: बंद † | ಧ್ವನಿಯಲ್ಲಿ ಕೇಳುವುದು: ಆಫ್ † |
| Switch to light theme | Use light theme | हल्की थीम अपनाएँ † | ಬೆಳಕಿನ ಥೀಮ್ ಬಳಸಿ † |
| Switch to dark theme | Use dark theme | गहरी थीम अपनाएँ † | ಗಾಢ ಥೀಮ್ ಬಳಸಿ † |
| All details collected | That’s all the details. Review the draft. | सारी जानकारी मिल गई। मसौदा देखें। † | ಎಲ್ಲ ವಿವರಗಳು ಸಿಕ್ಕಿವೆ. ಕರಡನ್ನು ಪರಿಶೀಲಿಸಿ. † |
| Auto-language hint | Speak or type. We’ll detect the language. | बोलें या लिखें। हम भाषा पहचानेंगे। † | ಮಾತನಾಡಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ. ಭಾಷೆಯನ್ನು ಗುರುತಿಸುತ್ತೇವೆ. † |
| Sample UAN field (Studio only) | Sample UAN (optional) | नमूना UAN (ज़रूरी नहीं) † | ಮಾದರಿ UAN (ಐಚ್ಛಿಕ) † |
| Sample UAN action | Check sample registry | नमूना रजिस्टर में जाँचें † | ಮಾದರಿ ನೋಂದಣಿಯಲ್ಲಿ ಪರಿಶೀಲಿಸಿ † |
| Sample replay action | Play sample conversation | नमूना बातचीत चलाएँ † | ಮಾದರಿ ಸಂಭಾಷಣೆ ಪ್ಲೇ ಮಾಡಿ † |
| Replay unavailable | Sample replay is unavailable in LIVE mode. | LIVE मोड में नमूना नहीं चल सकता। † | LIVE ಮೋಡ್‌ನಲ್ಲಿ ಮಾದರಿ ಪ್ಲೇ ಆಗುವುದಿಲ್ಲ. † |
| MOCK guidance | This is a sample. Use the replay or type an answer. | यह नमूना है। बातचीत सुनें या जवाब लिखें। † | ಇದು ಮಾದರಿ. ಸಂಭಾಷಣೆ ಪ್ಲೇ ಮಾಡಿ ಅಥವಾ ಉತ್ತರ ಟೈಪ್ ಮಾಡಿ. † |
| Studio noise test | Test background noise | काम की जगह का शोर जाँचें † | ಕೆಲಸದ ಸ್ಥಳದ ಶಬ್ದವನ್ನು ಪರೀಕ್ಷಿಸಿ † |
| Noise level | Background noise level | आसपास के शोर का स्तर † | ಸುತ್ತಲಿನ ಶಬ್ದದ ಮಟ್ಟ † |
| Audio zone | Audio line | आवाज़ की लाइन † | ಧ್ವನಿ ರೇಖೆ † |
| Sample audio | Sample audio | नमूना आवाज़ † | ಮಾದರಿ ಧ್ವನಿ † |
| Microphone live | Microphone is on | माइक्रोफ़ोन चालू है † | ಮೈಕ್ರೊಫೋನ್ ಆನ್ ಆಗಿದೆ † |
| Waiting for speech | Waiting for speech | आपकी बात सुन रहे हैं † | ನಿಮ್ಮ ಮಾತಿಗಾಗಿ ಕಾಯುತ್ತಿದ್ದೇವೆ † |
| Audio active | Speech received | आवाज़ मिल रही है † | ಧ್ವನಿ ಸಿಗುತ್ತಿದೆ † |
| Replay complete | Sample finished | नमूना पूरा हुआ † | ಮಾದರಿ ಮುಗಿದಿದೆ † |
| No audio | No audio yet | अभी आवाज़ नहीं मिली † | ಇನ್ನೂ ಧ್ವನಿ ಸಿಕ್ಕಿಲ್ಲ † |
| Frame size | Audio frame size | ऑडियो फ़्रेम का आकार † | ಆಡಿಯೊ ಫ್ರೇಮ್ ಗಾತ್ರ † |
| Frame interval | Audio frame interval | ऑडियो फ़्रेम का अंतर † | ಆಡಿಯೊ ಫ್ರೇಮ್ ಅವಧಿ † |
| Speech threshold | Speech detection threshold | आवाज़ पहचानने की सीमा † | ಧ್ವನಿ ಗುರುತಿಸುವ ಮಿತಿ † |
| Transcript latency | Time to transcript | लिखित रूप मिलने में समय † | ಲಿಪ್ಯಂತರ ಬರಲು ಬೇಕಾದ ಸಮಯ † |
| Vocabulary status | Place and work words to listen for | जगह और काम के पहचानने वाले शब्द † | ಸ್ಥಳ ಮತ್ತು ಕೆಲಸದ ಗುರುತು ಪದಗಳು † |
| No vocabulary hints | No extra words yet | अभी कोई खास शब्द नहीं † | ಇನ್ನೂ ವಿಶೇಷ ಪದಗಳಿಲ್ಲ † |
| Transcript heading | Worker’s words | मज़दूर की बात † | ಕಾರ್ಮಿಕರ ಮಾತು † |
| Transcript empty | The worker’s words will appear here. | मज़दूर की बात यहाँ दिखेगी। † | ಕಾರ್ಮಿಕರ ಮಾತು ಇಲ್ಲಿ ಕಾಣಿಸುತ್ತದೆ. † |
| Transcript received | Words captured for this draft | मसौदे के लिए बात दर्ज हुई † | ಕರಡಿಗಾಗಿ ಮಾತು ದಾಖಲಿಸಲಾಗಿದೆ † |
| Waiting for transcript | Waiting for the worker’s words | मज़दूर की बात सुनने की प्रतीक्षा † | ಕಾರ್ಮಿಕರ ಮಾತಿಗಾಗಿ ಕಾಯುತ್ತಿದೆ † |
| Claim information | Claim details | दावे की जानकारी † | ಅರ್ಜಿಯ ವಿವರಗಳು † |
| Field not answered | Not answered yet | अभी जवाब नहीं मिला † | ಇನ್ನೂ ಉತ್ತರ ಸಿಕ್ಕಿಲ್ಲ † |
| Statutory checks | Legal checks for this draft | मसौदे की कानूनी जाँच † | ಈ ಕರಡಿನ ಕಾನೂನು ಪರಿಶೀಲನೆ † |
| Paper heading | Form A · draft | फ़ॉर्म A · मसौदा † | ಫಾರ್ಮ್ A · ಕರಡು † |
| Paper status | Details ready for review | जानकारी देखने के लिए तैयार † | ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸಲು ಸಿದ್ಧ † |
| Files ready | Draft files are ready to download | मसौदे की फ़ाइलें डाउनलोड के लिए तैयार हैं † | ಕರಡಿನ ಫೈಲ್‌ಗಳು ಡೌನ್‌ಲೋಡ್‌ಗೆ ಸಿದ್ಧವಾಗಿವೆ † |
| Paper not filed | Not filed | दाखिल नहीं हुआ † | ಸಲ್ಲಿಕೆಯಾಗಿಲ್ಲ † |
| Paper title | Application for unpaid wages | बकाया मज़दूरी का आवेदन † | ಬಾಕಿ ಕೂಲಿಗಾಗಿ ಅರ್ಜಿ † |
| Worker field | Worker | मज़दूर † | ಕಾರ್ಮಿಕ † |
| Missing worker name | Waiting for the worker’s name | मज़दूर के नाम की प्रतीक्षा † | ಕಾರ್ಮಿಕರ ಹೆಸರಿಗಾಗಿ ಕಾಯುತ್ತಿದೆ † |
| Missing worksite | Worksite not provided | काम की जगह नहीं बताई † | ಕೆಲಸದ ಸ್ಥಳ ತಿಳಿಸಿಲ್ಲ † |
| Amount | Estimated unpaid wages | अनुमानित बकाया मज़दूरी † | ಅಂದಾಜು ಬಾಕಿ ಕೂಲಿ † |
| Missing employer | Employer details not provided | मालिक या कंपनी की जानकारी नहीं मिली † | ಮಾಲೀಕ ಅಥವಾ ಕಂಪನಿಯ ವಿವರ ಸಿಕ್ಕಿಲ್ಲ † |
| Listen to draft | Listen to the draft | मसौदा सुनें † | ಕರಡನ್ನು ಕೇಳಿ † |
| Audio unavailable | Audio playback is not available in this browser. | इस ब्राउज़र में आवाज़ नहीं चल सकती। † | ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ಪ್ಲೇ ಆಗುವುದಿಲ್ಲ. † |
| Audio ready | Draft audio is ready. Press play to listen. | मसौदे की आवाज़ तैयार है। सुनने के लिए चलाएँ दबाएँ। † | ಕರಡಿನ ಧ್ವನಿ ಸಿದ್ಧವಾಗಿದೆ. ಕೇಳಲು ಪ್ಲೇ ಒತ್ತಿ. † |
| Prepare action | Prepare the draft PDF and data file | मसौदे की PDF और डेटा फ़ाइल बनाएँ † | ಕರಡಿನ PDF ಮತ್ತು ಡೇಟಾ ಫೈಲ್ ಸಿದ್ಧಪಡಿಸಿ † |
| PDF download | Download Form A PDF | फ़ॉर्म A PDF डाउनलोड करें † | ಫಾರ್ಮ್ A PDF ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ † |
| Data download | Download draft data (JSON) | मसौदे का डेटा (JSON) डाउनलोड करें † | ಕರಡಿನ ಡೇಟಾ (JSON) ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ † |
| Sample disclaimer | Sample data. Draft only. Not filed with an authority. | नमूना जानकारी। सिर्फ़ मसौदा। किसी विभाग में दाखिल नहीं। † | ಮಾದರಿ ಮಾಹಿತಿ. ಕರಡು ಮಾತ್ರ. ಯಾವುದೇ ಇಲಾಖೆಗೆ ಸಲ್ಲಿಸಿಲ್ಲ. † |
| Voice confirmation recorded | Voice confirmation recorded for this draft | इस मसौदे के लिए आवाज़ में पुष्टि दर्ज हुई † | ಈ ಕರಡಿಗಾಗಿ ಧ್ವನಿ ದೃಢೀಕರಣ ದಾಖಲಾಗಿದೆ † |
| No voice confirmation | No voice confirmation was recorded. | आवाज़ में पुष्टि दर्ज नहीं हुई। † | ಧ್ವನಿ ದೃಢೀಕರಣ ದಾಖಲಾಗಿಲ್ಲ. † |
| Connected status | Connected · LIVE | LIVE से जुड़ा है † | LIVE ಸಂಪರ್ಕವಾಗಿದೆ † |
| Connecting status | Connecting to the claim service | दावे की सेवा से जुड़ रहे हैं † | ಅರ್ಜಿ ಸೇವೆಗೆ ಸಂಪರ್ಕಿಸುತ್ತಿದ್ದೇವೆ † |
| Signal format | 8 kHz audio | 8 kHz ऑडियो † | 8 kHz ಆಡಿಯೊ † |
| Slot recorded state | Recorded | दर्ज हुआ † | ದಾಖಲಾಗಿದೆ † |
| Reasoning disclosure | How this draft was checked | इस मसौदे की जाँच कैसे हुई † | ಈ ಕರಡನ್ನು ಹೇಗೆ ಪರಿಶೀಲಿಸಲಾಗಿದೆ † |
| Prisma latency | Speech recognition | आवाज़ पहचान † | ಧ್ವನಿ ಗುರುತಿಸುವಿಕೆ † |
| Evon Stage A latency | Collecting claim details | दावे की जानकारी जुटाना † | ಅರ್ಜಿಯ ವಿವರಗಳನ್ನು ಸಂಗ್ರಹಿಸುವುದು † |
| Evon Stage B latency | Checking the draft | मसौदे की जाँच † | ಕರಡನ್ನು ಪರಿಶೀಲಿಸುವುದು † |
| Timbre latency | Preparing read-aloud audio | मसौदे की आवाज़ तैयार करना † | ಕರಡಿನ ಧ್ವನಿ ಸಿದ್ಧಪಡಿಸುವುದು † |

Use the following claim field labels consistently. Do not duplicate a field
name as a second tiny caption. “Principal employer” is a legal term; the
translations below are working copy pending domain and native-speaker review.

| Claim field | English | Hindi | Kannada |
|---|---|---|---|
| Worker | Worker’s name | मज़दूर का नाम † | ಕಾರ್ಮಿಕರ ಹೆಸರು † |
| Worksite | Worksite and area | काम की जगह और इलाका † | ಕೆಲಸದ ಸ್ಥಳ ಮತ್ತು ಪ್ರದೇಶ † |
| Contractor | Contractor’s name and phone | ठेकेदार का नाम और फ़ोन † | ಗುತ್ತಿಗೆದಾರರ ಹೆಸರು ಮತ್ತು ಫೋನ್ † |
| Principal employer | Main employer or company | मुख्य नियोक्ता या कंपनी † | ಮುಖ್ಯ ಉದ್ಯೋಗದಾತ ಅಥವಾ ಕಂಪನಿ † |
| Wage period start | First day of the unpaid period | बकाया अवधि का पहला दिन † | ಬಾಕಿ ಅವಧಿಯ ಮೊದಲ ದಿನ † |
| Wage period end | Last day of the unpaid period | बकाया अवधि का आख़िरी दिन † | ಬಾಕಿ ಅವಧಿಯ ಕೊನೆಯ ದಿನ † |
| Days worked | Number of days worked | काम किए दिनों की संख्या † | ಕೆಲಸ ಮಾಡಿದ ದಿನಗಳ ಸಂಖ್ಯೆ † |
| Daily wage | Agreed pay per day | तय रोज़ की मज़दूरी † | ಒಪ್ಪಿದ ದಿನದ ಕೂಲಿ † |
| Advance | Amount already paid | पहले से मिली रकम † | ಈಗಾಗಲೇ ಪಡೆದ ಮೊತ್ತ † |

Do not expose the current raw-event inspector, `enable_thinking` field, model
names, or JSON snippets in the product-facing Studio composition. Keep
diagnostic data available to engineers through development tooling, not as a
fifth zone or a scrollable event feed.

### Content requiring review

- Have Hindi and Kannada speakers from the intended worker communities
  validate every marked string, including whether “मज़दूरी / ಕೂಲಿ” is the
  clearest local term for unpaid wages.
- Have a labor-rights reviewer approve translated terms for arrears,
  statutory checks, consent, and Form A. Do not translate a legal conclusion
  into a stronger claim than the returned check supports.
- Verify the final consent copy with a native speaker using read-aloud and
  speech recognition. The spoken “yes/no” vocabulary must match the backend’s
  existing consent-intent handling.
- Have a Kannada reader check script rendering, punctuation, and the difference
  between a typed response and a spoken one on the actual device font.

## Accessibility and interaction

### Keyboard and focus order

- **Worker:** mode/language/theme controls → current question → microphone
  button → “Type an answer instead” and its input/send action → paper preview
  disclosure. Keep the primary action reachable without tabbing through
  decorative content.
- **Studio:** header controls → audio line controls → transcript/read-back
  controls → claim slots and reasoning disclosure → paper/consent actions.
  This follows the specified zone reading order, not an arbitrary card order.
- Provide a visible, high-contrast focus ring for every button, link, input,
  disclosure, mode switch, and language control. Never remove the browser
  focus indicator without an equally visible replacement.
- Use native buttons, labels, inputs, and disclosures. Give the microphone
  an accessible name that changes between “Speak your answer” and “Stop
  recording.” Do not expose decorative waveform bars one by one to screen
  readers.

### Announcements and touch

- Announce the next follow-up question in a polite `aria-live` region after a
  completed answer; do not announce every render or repeat unchanged copy.
- Give the live transcript a separate polite `aria-live` region. Announce a
  completed transcript as one update, not character-by-character.
- Announce consent state changes and actionable errors once. Do not move
  focus automatically when a question or transcript changes.
- Maintain 44×44px minimum interactive targets in Worker mode, including
  language, mode, mic, typed-answer, and paper-preview controls. The main mic
  target should be substantially larger.
- Support zoom, dynamic text, keyboard-only use, and 360px-wide layouts.
  Preserve script shaping and line wrapping for Hindi and Kannada. Do not
  communicate status by color alone.

## WebSocket event contract

This section documents the existing contract; it does not define a new one.
The frontend’s `useSession` hook receives the following JSON event types.
Components consume the listed state; if an event is currently unhandled, that
is called out rather than silently assigning it a new meaning.

| Existing server event | Existing data used by the UI | Component(s) |
|---|---|---|
| `session_started` | `mode`; clears the current session’s claim, transcript, consent, and telemetry state | Status chip, slot rows, transcript, paper, consent, latency |
| `language_status` | `language_preference`, `effective_language` | Header language control, transcript language |
| `prisma_telemetry` | `frame_bytes`, `cadence_ms`, `sample_rate_hz`, `vad_threshold`, optional `latency_ms`, `source`, MOCK `waveform` | Oscilloscope, audio-line readouts, latency, status/source label |
| `prisma_transcript` | `text`, `detected_language_code`, `effective_language`, `latency`, optional `source` | Transcript line, language label, latency |
| `pipeline_latency` | `stage`, `latency_ms`, `source` | Latency readout for Prisma segment, Stage A, Stage B, and first Timbre audio chunk |
| `bias_boost_triggered` | `request_id` when available; `words` | Audio-line vocabulary status; transcript highlight vocabulary |
| `bias_boost_failed` | `request_id` | Audio-line vocabulary status |
| `prisma_settings_updated` | `request_id`, `config.bias_word_count`, `config.bias_score`, `confirmed_words` | Audio-line vocabulary confirmation; transcript highlight vocabulary |
| `evon_stage_a` | `slots`, `missing_fields`, `followup` | Slot rows, paper fields, Worker follow-up question |
| `evon_stage_b_complete` | audit result, `checks`, arrears, read-back script, `stage`, `thinking_trace`, `enable_thinking` | Statutory checks, paper amount/summary, reasoning disclosure, consent/read-back |
| `timbre_audio` | `script` | Consent/read-back bar |
| `timbre_audio_ready` | Event marker after LIVE binary audio is sent | No current `useSession` handler; do not imply the current UI consumes it |
| `timbre_audio_unavailable` | `message` | Consent/read-back bar and service error |
| Binary audio frame | Audio bytes; the browser treats the received frame as playable audio | Consent/read-back player. This is not a JSON event. |
| `consent_status` | `state`, `voice_consent_recorded` | Consent bar and draft action |
| `claim_ready` | `claim_id`, `pdf_url`, `json_url` | Paper/document actions and download links |
| `uan_result` | `found`, optional `worker_name` | Studio / MOCK UAN lookup status and slot flow |
| `notice` | `message` | Status chip or relevant action’s inline status |
| `error` | `message` | Relevant component’s inline error/status |

### Component event and command boundary

| Component | Existing inbound event(s) | Existing client command(s) / transport |
|---|---|---|
| Mic control | `notice`, `error`; no dedicated mic-start acknowledgement | JSON `start_mic`, `stop_mic`; outgoing binary PCM frames |
| Oscilloscope | `prisma_telemetry` | No component-specific command |
| Slot row | `session_started`, `evon_stage_a`, `uan_result` | JSON `utterance`, `uan`, and `demo` (sample flow) |
| Transcript + boosted words | `session_started`, `language_status`, `prisma_transcript`, `bias_boost_triggered`, `bias_boost_failed`, `prisma_settings_updated` | JSON `utterance`; audio via mic control |
| Paper document | `session_started`, `evon_stage_a`, `evon_stage_b_complete`, `consent_status`, `claim_ready` | JSON `confirm` after affirmative consent |
| Statutory check row | `evon_stage_b_complete` | No component-specific command |
| Latency readout | `prisma_telemetry`, `prisma_transcript`, `pipeline_latency` | No component-specific command |
| Status chip | `session_started`, `prisma_telemetry`, `notice`, `error`; local WebSocket open/close state | JSON `set_language` is sent on connection and language change |
| Consent bar | `evon_stage_b_complete`, `timbre_audio`, `timbre_audio_unavailable`, `consent_status`, binary audio frame | JSON `utterance` or microphone audio for the answer; `confirm` prepares files after a yes |

Other existing client commands are `set_language` (`language`), `start_mic`,
`stop_mic`, `utterance` (`text`), `uan` (`value`), `demo`, and `confirm`.
The legacy `transcript:<text>` text fallback is also accepted by the backend,
but is not used by the current UI. Preserve existing command names and
payload meanings. Outgoing audio is raw mono `pcm_s16le`, exactly 1024 bytes
per frame, paced one frame every 64ms at 8000Hz; never send WAV/MP3 container
headers mid-stream. The MOCK replay emits the same claim/transcript event
types with `source: "mock"` where supplied; display that source as sample
data, not as live worker input.

The backend forwards Prisma event names with a `prisma_` prefix. The frontend
currently handles `prisma_transcript` and `prisma_settings_updated`; do not
invent partial-transcript, word-timing, or confidence events. In particular,
the existing protocol does not provide token-level boost alignment. Any
highlight must be presented as a vocabulary hint, never as proof that a
particular word was recognized accurately. Do not alter the backend event
contract to support the design.
