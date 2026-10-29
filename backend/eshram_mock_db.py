from __future__ import annotations

SYNTHETIC_ESHRAM_DB: dict[str, dict[str, object]] = {
    "100492837465": {
        "worker_name": "Ramesh Kumar Verma",
        "occupation": "Construction Mason (Mistry)",
        "permanent_address": "House No. 42, Ward 4, Phulwari Sharif, Patna, Bihar - 801505",
        "current_service_address": "Labour Shed 3, Near Peenya 2nd Stage Metro, Bengaluru - 560058",
        "bank_ifsc": "SBIN0004123 (Aadhaar Seeded)",
        "local_bias_words": ["Peenya", "Yeshwanthpur", "Dasarahalli", "Whitefield", "Ramesh", "Thekedar", "Dihadi"],
    },
    "100837465912": {
        "worker_name": "Lakshmi Devi",
        "occupation": "Garment & Construction Helper",
        "permanent_address": "18, Main Road, Raichur District, Karnataka - 584101",
        "current_service_address": "Bommanahalli Industrial Area, Bengaluru - 560068",
        "bank_ifsc": "CNRB0001892 (Aadhaar Seeded)",
        "local_bias_words": ["Bommanahalli", "Hosur", "Electronic", "Peenya", "Kaveri", "Mistry", "Hazari"],
    },
}


def lookup_eshram_uan(uan_digits: str) -> dict[str, object] | None:
    clean_uan = "".join(character for character in str(uan_digits) if character.isdigit())
    profile = SYNTHETIC_ESHRAM_DB.get(clean_uan)
    return dict(profile) if profile else None
