from decimal import Decimal

import pytest

from app.modules.clubs.domain.entities import Club, ClubView
from app.modules.clubs.domain.errors import InvalidClubData


@pytest.mark.parametrize(
    ("name", "acronym"),
    [
        pytest.param("Águias FC", "AGU", id="letters_in_order_ignoring_accent"),
        pytest.param("Águias FC", "AFC", id="initial_of_each_word"),
        pytest.param("Delta FC", "DFC", id="delta"),
        pytest.param("Real Madrid", "RMA", id="skipping_letters"),
        pytest.param("sport club recife", "SCR", id="lowercase_name"),
        pytest.param("Atlético Mineiro", "AMI", id="accent_in_the_name"),
    ],
)
def test_register_accepts_an_acronym_that_matches_the_name(name, acronym) -> None:
    club = Club.register(name, acronym)

    assert (club.name, club.acronym) == (name, acronym)


@pytest.mark.parametrize(
    ("name", "acronym"),
    [
        pytest.param("Águias FC", "XYZ", id="first_letter_is_not_the_initial"),
        pytest.param("Águias FC", "FCA", id="first_letter_is_not_the_first_of_the_name"),
        pytest.param("Águias FC", "AXC", id="letter_that_is_not_in_the_name"),
        pytest.param("Águias FC", "AUG", id="letters_out_of_order"),
        pytest.param("Alfa Atletico", "AAA", id="three_equal_letters"),
    ],
)
def test_register_rejects_an_acronym_that_does_not_match_the_name(name, acronym) -> None:
    with pytest.raises(InvalidClubData):
        Club.register(name, acronym)


def test_register_creates_the_club_with_initial_cash_and_no_lineup() -> None:
    club = Club.register("Águias FC", "AGU")

    assert club.id is None
    assert club.cash == Decimal("300.00")
    assert club.formation is None


def test_net_worth_is_cash_plus_squad_value() -> None:
    club = Club(id=1, name="Águias FC", acronym="AGU", cash=Decimal("261.15"), formation=None)

    view = ClubView(club, Decimal("37.00"))

    assert view.net_worth == Decimal("298.15")
