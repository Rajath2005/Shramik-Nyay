from __future__ import annotations

import re
from typing import Literal

from hindi_numbers import number_to_hindi_words

LanguagePreference = Literal["auto", "hi-IN", "kn-IN", "en-IN"]
SUPPORTED_LANGUAGES: tuple[str, ...] = ("hi-IN", "kn-IN", "en-IN")
DEFAULT_LANGUAGE = "hi-IN"
PRISMA_LANGUAGE_CODES = {
    "auto": "indic-auto",
    "hi-IN": "hi-IN,en-IN",
    "kn-IN": "kn-IN,en-IN",
    "en-IN": "en-IN",
}
LANGUAGE_NAMES = {
    "auto": "Auto-detect",
    "hi-IN": "हिन्दी",
    "kn-IN": "ಕನ್ನಡ",
    "en-IN": "English",
}

FOLLOWUPS = {
    "hi-IN": {
        "worker_name": "आपका पूरा नाम क्या है?",
        "worksite_locality_and_sphere": "आप किस जगह या साइट पर काम करते थे?",
        "contractor_name_and_phone": "ठेकेदार का नाम और फोन नंबर बताइए।",
        "principal_employer_name": "साइट किस कंपनी या मालिक की थी?",
        "wage_period_start": "आपने किस तारीख से काम शुरू किया था?",
        "wage_period_end": "आख़िरी काम का दिन कौन सा था?",
        "days_worked": "कुल कितने दिन काम किया?",
        "agreed_daily_wage_inr": "रोज़ की दिहाड़ी कितनी तय थी?",
        "advance_received_inr": "अब तक कुल कितने रुपये मिले हैं? कुछ नहीं मिला तो शून्य बोलिए।",
    },
    "kn-IN": {
        "worker_name": "ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರು ಏನು?",
        "worksite_locality_and_sphere": "ನೀವು ಯಾವ ಸ್ಥಳದಲ್ಲಿ ಅಥವಾ ಕೆಲಸದ ತಾಣದಲ್ಲಿ ಕೆಲಸ ಮಾಡಿದ್ದೀರಿ?",
        "contractor_name_and_phone": "ಗುತ್ತಿಗೆದಾರರ ಹೆಸರು ಮತ್ತು ಫೋನ್ ಸಂಖ್ಯೆ ತಿಳಿಸಿ.",
        "principal_employer_name": "ಕೆಲಸದ ತಾಣ ಯಾವ ಕಂಪನಿ ಅಥವಾ ಮಾಲೀಕರದ್ದು?",
        "wage_period_start": "ನೀವು ಯಾವ ದಿನದಿಂದ ಕೆಲಸ ಪ್ರಾರಂಭಿಸಿದ್ದೀರಿ?",
        "wage_period_end": "ನಿಮ್ಮ ಕೊನೆಯ ಕೆಲಸದ ದಿನ ಯಾವುದು?",
        "days_worked": "ಒಟ್ಟು ಎಷ್ಟು ದಿನ ಕೆಲಸ ಮಾಡಿದ್ದೀರಿ?",
        "agreed_daily_wage_inr": "ದಿನದ ಕೂಲಿ ಎಷ್ಟು ಎಂದು ನಿಗದಿಯಾಗಿತ್ತು?",
        "advance_received_inr": "ಈಗಾಗಲೇ ಒಟ್ಟು ಎಷ್ಟು ರೂಪಾಯಿ ಪಡೆದಿದ್ದೀರಿ? ಏನೂ ಸಿಗದಿದ್ದರೆ ಶೂನ್ಯ ಎಂದು ಹೇಳಿ.",
    },
    "en-IN": {
        "worker_name": "What is your full name?",
        "worksite_locality_and_sphere": "Where did you work?",
        "contractor_name_and_phone": "What is the contractor's name and phone number?",
        "principal_employer_name": "Which company or owner ran the worksite?",
        "wage_period_start": "On what date did you start work?",
        "wage_period_end": "What was your last day of work?",
        "days_worked": "How many days did you work in total?",
        "agreed_daily_wage_inr": "What daily wage did you agree on?",
        "advance_received_inr": "How much have you already received? Say zero if you received nothing.",
    },
}

MOCK_TRANSCRIPTS = {
    "hi-IN": "साहब, ठेकेदार मोहन ने पीन्या साइट पर अठारह दिन काम कराया, सात सौ रोज़ बोला था, दो हज़ार रुपये मिले।",
    "kn-IN": "ಸರ್, ಗುತ್ತಿಗೆದಾರ ಮೋಹನ್ ಪೀನ್ಯಾ ಸೈಟ್‌ನಲ್ಲಿ ಹದಿನೆಂಟು ದಿನ ಕೆಲಸ ಮಾಡಿಸಿದರು, ದಿನಕ್ಕೆ ಏಳು ನೂರು ಎಂದು ಹೇಳಿದರು, ಎರಡು ಸಾವಿರ ರೂಪಾಯಿ ಸಿಕ್ಕಿದೆ.",
    "en-IN": "Sir, contractor Mohan had me work at the Peenya site for eighteen days at seven hundred rupees a day. I received two thousand rupees.",
}

EN_ONES = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen",
)
EN_TENS = (
    "", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
)
KN_NUMBERS = (
    "ಸೊನ್ನೆ", "ಒಂದು", "ಎರಡು", "ಮೂರು", "ನಾಲ್ಕು", "ಐದು", "ಆರು", "ಏಳು", "ಎಂಟು", "ಒಂಬತ್ತು",
    "ಹತ್ತು", "ಹನ್ನೊಂದು", "ಹನ್ನೆರಡು", "ಹದಿಮೂರು", "ಹದಿನಾಲ್ಕು", "ಹದಿನೈದು", "ಹದಿನಾರು",
    "ಹದಿನೇಳು", "ಹದಿನೆಂಟು", "ಹತ್ತೊಂಬತ್ತು", "ಇಪ್ಪತ್ತು", "ಇಪ್ಪತ್ತೊಂದು", "ಇಪ್ಪತ್ತೆರಡು",
    "ಇಪ್ಪತ್ತಮೂರು", "ಇಪ್ಪತ್ತನಾಲ್ಕು", "ಇಪ್ಪತ್ತೈದು", "ಇಪ್ಪತ್ತಾರು", "ಇಪ್ಪತ್ತೇಳು",
    "ಇಪ್ಪತ್ತೆಂಟು", "ಇಪ್ಪತ್ತೊಂಬತ್ತು", "ಮೂವತ್ತು", "ಮೂವತ್ತೊಂದು", "ಮೂವತ್ತೆರಡು",
    "ಮೂವತ್ತಮೂರು", "ಮೂವತ್ತನಾಲ್ಕು", "ಮೂವತ್ತೈದು", "ಮೂವತ್ತಾರು", "ಮೂವತ್ತೇಳು",
    "ಮೂವತ್ತೆಂಟು", "ಮೂವತ್ತೊಂಬತ್ತು", "ನಲವತ್ತು", "ನಲವತ್ತೊಂದು", "ನಲವತ್ತೆರಡು",
    "ನಲವತ್ತಮೂರು", "ನಲವತ್ತನಾಲ್ಕು", "ನಲವತ್ತೈದು", "ನಲವತ್ತಾರು", "ನಲವತ್ತೇಳು",
    "ನಲವತ್ತೆಂಟು", "ನಲವತ್ತೊಂಬತ್ತು", "ಐವತ್ತು", "ಐವತ್ತೊಂದು", "ಐವತ್ತೆರಡು", "ಐವತ್ತಮೂರು",
    "ಐವತ್ತನಾಲ್ಕು", "ಐವತ್ತೈದು", "ಐವತ್ತಾರು", "ಐವತ್ತೇಳು", "ಐವತ್ತೆಂಟು", "ಐವತ್ತೊಂಬತ್ತು",
    "ಅರವತ್ತು", "ಅರವತ್ತೊಂದು", "ಅರವತ್ತೆರಡು", "ಅರವತ್ತಮೂರು", "ಅರವತ್ತನಾಲ್ಕು", "ಅರವತ್ತೈದು",
    "ಅರವತ್ತಾರು", "ಅರವತ್ತೇಳು", "ಅರವತ್ತೆಂಟು", "ಅರವತ್ತೊಂಬತ್ತು", "ಎಪ್ಪತ್ತು", "ಎಪ್ಪತ್ತೊಂದು",
    "ಎಪ್ಪತ್ತೆರಡು", "ಎಪ್ಪತ್ತಮೂರು", "ಎಪ್ಪತ್ತನಾಲ್ಕು", "ಎಪ್ಪತ್ತೈದು", "ಎಪ್ಪತ್ತಾರು",
    "ಎಪ್ಪತ್ತೇಳು", "ಎಪ್ಪತ್ತೆಂಟು", "ಎಪ್ಪತ್ತೊಂಬತ್ತು", "ಎಂಬತ್ತು", "ಎಂಬತ್ತೊಂದು", "ಎಂಬತ್ತೆರಡು",
    "ಎಂಬತ್ತಮೂರು", "ಎಂಬತ್ತನಾಲ್ಕು", "ಎಂಬತ್ತೈದು", "ಎಂಬತ್ತಾರು", "ಎಂಬತ್ತೇಳು",
    "ಎಂಬತ್ತೆಂಟು", "ಎಂಬತ್ತೊಂಬತ್ತು", "ತೊಂಬತ್ತು", "ತೊಂಬತ್ತೊಂದು", "ತೊಂಬತ್ತೆರಡು",
    "ತೊಂಬತ್ತಮೂರು", "ತೊಂಬತ್ತನಾಲ್ಕು", "ತೊಂಬತ್ತೈದು", "ತೊಂಬತ್ತಾರು", "ತೊಂಬತ್ತೇಳು",
    "ತೊಂಬತ್ತೆಂಟು", "ತೊಂಬತ್ತೊಂಬತ್ತು",
)


def validate_language(value: object) -> LanguagePreference:
    if value == "auto":
        return "auto"
    if value == "hi-IN":
        return "hi-IN"
    if value == "kn-IN":
        return "kn-IN"
    if value == "en-IN":
        return "en-IN"
    raise ValueError("language must be auto, hi-IN, kn-IN, or en-IN.")


def match_consent_intent(text: str) -> Literal["yes", "no"] | None:
    tokens = re.findall(r"[a-z]+|[\u0900-\u097f]+|[\u0c80-\u0cff]+", text.casefold())
    affirmative = {"yes", "haan", "हाँ", "हां", "ಹೌದು"}
    negative = {"no", "ना", "नहीं", "नही", "nahi", "nahin", "ಇಲ್ಲ"}
    has_affirmative = any(token in affirmative for token in tokens) or any(
        tokens[index:index + 2] == ["bhej", "dijiye"]
        for index in range(len(tokens) - 1)
    )
    has_negative = any(token in negative for token in tokens)
    if has_affirmative == has_negative:
        return None
    return "yes" if has_affirmative else "no"


def prisma_language_code(preference: str) -> str:
    return PRISMA_LANGUAGE_CODES[validate_language(preference)]


def resolve_language(preference: str, *, detected: str | None = None, text: str = "") -> str:
    selected = validate_language(preference)
    if selected != "auto":
        return selected
    if detected in SUPPORTED_LANGUAGES:
        return detected
    if re.search(r"[\u0c80-\u0cff]", text):
        return "kn-IN"
    if re.search(r"[\u0900-\u097f]", text):
        return "hi-IN"
    if re.search(r"[A-Za-z]", text):
        return "en-IN"
    return DEFAULT_LANGUAGE


def followup_for(field: str, language: str) -> str:
    locale = resolve_language(language)
    try:
        return FOLLOWUPS[locale][field]
    except KeyError as error:
        raise ValueError(f"No {locale} follow-up is defined for {field}.") from error


def _english_under_thousand(number: int) -> str:
    parts: list[str] = []
    if number >= 100:
        parts.extend((EN_ONES[number // 100], "hundred"))
        number %= 100
    if number >= 20:
        parts.append(EN_TENS[number // 10])
        number %= 10
    if number:
        parts.append(EN_ONES[number])
    return " ".join(parts)


def _kannada_under_thousand(number: int) -> str:
    parts: list[str] = []
    if number >= 100:
        parts.extend((KN_NUMBERS[number // 100], "ನೂರು"))
        number %= 100
    if number:
        parts.append(KN_NUMBERS[number])
    return " ".join(parts)


def _scale_words(number: int, language: str) -> str:
    if number == 0:
        return "zero" if language == "en-IN" else KN_NUMBERS[0]
    under_thousand = _english_under_thousand if language == "en-IN" else _kannada_under_thousand
    thousand, remainder = divmod(number, 1000)
    lakh, thousand = divmod(thousand, 100)
    crore, lakh = divmod(lakh, 100)
    parts: list[str] = []
    if crore:
        parts.extend((under_thousand(crore), "crore" if language == "en-IN" else "ಕೋಟಿ"))
    if lakh:
        parts.extend((under_thousand(lakh), "lakh" if language == "en-IN" else "ಲಕ್ಷ"))
    if thousand:
        parts.extend((under_thousand(thousand), "thousand" if language == "en-IN" else "ಸಾವಿರ"))
    if remainder:
        parts.append(under_thousand(remainder))
    return " ".join(parts)


def number_to_spoken_words(number: int, language: str) -> str:
    locale = resolve_language(language)
    if number < 0:
        minus = {"hi-IN": "माइनस", "kn-IN": "ಮೈನಸ್", "en-IN": "minus"}[locale]
        return f"{minus} {number_to_spoken_words(abs(number), locale)}"
    if locale == "hi-IN":
        return number_to_hindi_words(number)
    if number > 999_999_999:
        raise ValueError("Spoken number must be less than one billion.")
    return _scale_words(number, locale)


def readback_script(principal_arrears: int, language: str) -> str:
    locale = resolve_language(language)
    amount = number_to_spoken_words(principal_arrears, locale)
    if locale == "hi-IN":
        return (
            f"<slow>आपकी बकाया मज़दूरी {amount} रुपये है।</slow> <pauses> "
            "क्या मैं इस शिकायत का मसौदा तैयार करूँ? हाँ या ना बोलिए।"
        )
    if locale == "kn-IN":
        return (
            f"<slow>ನಿಮಗೆ ಬರಬೇಕಾದ ಬಾಕಿ ಕೂಲಿ {amount} ರೂಪಾಯಿ.</slow> <pauses> "
            "ಈ ದೂರು ಕರಡನ್ನು ಸಿದ್ಧಪಡಿಸಲೇ? ಹೌದು ಅಥವಾ ಇಲ್ಲ ಎಂದು ಹೇಳಿ."
        )
    return (
        f"<slow>Your unpaid wages are {amount} rupees.</slow> <pauses> "
        "Shall I prepare this claim draft? Please say yes or no."
    )
