import pytest

from app.shared.domain.text import clean_text, has_letter, normalize_text


@pytest.mark.parametrize(
    ("raw", "clean"),
    [
        pytest.param("  Meia   Zeta ", "Meia Zeta", id="trims_and_collapses_spaces"),
        pytest.param("Meia Zeta", "Meia Zeta", id="already_clean"),
        pytest.param("a  b   c", "a b c", id="several_runs_of_spaces"),
        pytest.param("   ", "", id="only_spaces"),
        pytest.param("", "", id="empty"),
        pytest.param("Meia Lua", "Meia Lua", id="non_breaking_space_is_not_a_space"),
    ],
)
def test_clean_text_trims_and_collapses_spaces(raw, clean) -> None:
    assert clean_text(raw) == clean


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param("Meia\tLua", id="tab"),
        pytest.param("Meia\nLua", id="line_break"),
        pytest.param("Meia\rLua", id="carriage_return"),
        pytest.param("Meia Lua\t", id="tab_at_the_end"),
        pytest.param("\x00", id="null_character"),
    ],
)
def test_clean_text_rejects_control_characters(raw) -> None:
    with pytest.raises(ValueError):
        clean_text(raw)


@pytest.mark.parametrize(
    ("raw", "normalized"),
    [
        pytest.param("João", "joao", id="tilde"),
        pytest.param("ÉPSILON", "epsilon", id="uppercase_and_acute"),
        pytest.param("Ça va", "ca va", id="cedilla"),
        pytest.param("Zé Foguete", "ze foguete", id="acute_in_a_phrase"),
        pytest.param("Águias FC", "aguias fc", id="acute_and_uppercase"),
        pytest.param("plain", "plain", id="nothing_to_change"),
    ],
)
def test_normalize_text_lowers_case_and_removes_accents(raw, normalized) -> None:
    assert normalize_text(raw) == normalized


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        pytest.param("Lua", True, id="plain_word"),
        pytest.param("Zé", True, id="accented_letter"),
        pytest.param("a1", True, id="letter_and_digit"),
        pytest.param("-", False, id="hyphen"),
        pytest.param("123", False, id="digits"),
        pytest.param("", False, id="empty"),
    ],
)
def test_has_letter_tells_if_a_word_has_a_unicode_letter(word, expected) -> None:
    assert has_letter(word) is expected


def test_normalize_text_makes_accented_and_plain_names_equal() -> None:
    assert normalize_text("Águias FC") == normalize_text("Aguias FC")


def test_alphabetical_order_follows_unicode_order_after_normalizing() -> None:
    names = ["Gama", "Épsilon", "Delta"]

    assert sorted(names, key=normalize_text) == ["Delta", "Épsilon", "Gama"]
    assert normalize_text("Ana Lima") < normalize_text("Ana-Maria")
    assert normalize_text("Ana-Maria") < normalize_text("Anaa")
