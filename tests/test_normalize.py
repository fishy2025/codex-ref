from src.normalize import build_alias_map, canonicalize_venue, normalize_text, normalize_title


def test_normalize_text_basic():
    assert normalize_text(" Environ. Sci. & Technol. ") == "environ sci and technol"


def test_canonicalize_with_aliases():
    aliases = build_alias_map({"Environ. Sci. Technol.": "Environmental Science & Technology"})
    assert canonicalize_venue("Environ. Sci. Technol.", aliases) == "environmental science and technology"


def test_normalize_title():
    assert normalize_title("Microalgae-based nitrogen removal!") == "microalgae based nitrogen removal"
