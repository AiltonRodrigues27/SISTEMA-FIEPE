import unicodedata


def clean_text(value: str) -> str:
    if any(unicodedata.category(char) == "Cc" for char in value):
        raise ValueError("não pode ter caracteres de controle")
    return " ".join(part for part in value.split(" ") if part)


def has_letter(word: str) -> bool:
    return any(unicodedata.category(char).startswith("L") for char in word)


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.lower())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
