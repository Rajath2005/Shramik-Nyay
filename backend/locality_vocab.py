from __future__ import annotations

import re

LOCALITY_VOCAB: dict[str, tuple[str, ...]] = {
    "peenya": ("Peenya",),
    "whitefield": ("Whitefield",),
    "yeshwanthpur": ("Yeshwanthpur",),
    "bommanahalli": ("Bommanahalli",),
    "dasarahalli": ("Dasarahalli",),
}

_LOCALITY_PATTERNS = tuple(
    (re.compile(rf"(?<!\w){re.escape(name)}(?!\w)", re.IGNORECASE), terms)
    for name, terms in LOCALITY_VOCAB.items()
)


def locality_terms_in(text: str) -> list[str]:
    """Return canonical bias terms for known localities mentioned in text."""
    return [
        term
        for pattern, terms in _LOCALITY_PATTERNS
        if pattern.search(text)
        for term in terms
    ]
