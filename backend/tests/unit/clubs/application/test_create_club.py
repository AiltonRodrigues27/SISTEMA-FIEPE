import pytest

from app.modules.clubs.application.create_club import CreateClub
from app.modules.clubs.domain.entities import MAX_CLUBS
from app.modules.clubs.domain.errors import (
    AcronymAlreadyExists,
    ClubLimitReached,
    ClubNameAlreadyExists,
    InvalidClubData,
)

ACRONYM_SUFFIXES = "ABCDEFGHIJKLMNOPQRST"


def test_create_club_saves_it_with_initial_cash_and_commits(club_repository, unit_of_work) -> None:
    view = CreateClub(club_repository, unit_of_work).execute("Águias FC", "AGU")

    assert view.club.id == 1
    assert str(view.club.cash) == "300.00"
    assert str(view.squad_value) == "0.00"
    assert str(view.net_worth) == "300.00"
    assert club_repository.get(1) is view.club
    assert unit_of_work.commits == 1


def test_create_club_rejects_a_name_that_differs_only_by_case(
    club_repository, unit_of_work, add_club
) -> None:
    add_club("Águias FC", "AGU")

    with pytest.raises(ClubNameAlreadyExists):
        CreateClub(club_repository, unit_of_work).execute("águias fc", "AFC")

    assert club_repository.count() == 1
    assert unit_of_work.commits == 0


def test_create_club_accepts_a_name_that_differs_by_accent(
    club_repository, unit_of_work, add_club
) -> None:
    add_club("Águias FC", "AGU")

    view = CreateClub(club_repository, unit_of_work).execute("Aguias FC", "AFC")

    assert view.club.name == "Aguias FC"
    assert unit_of_work.commits == 1


def test_create_club_rejects_an_acronym_that_already_exists(
    club_repository, unit_of_work, add_club
) -> None:
    add_club("Águias FC", "AGU")

    with pytest.raises(AcronymAlreadyExists):
        CreateClub(club_repository, unit_of_work).execute("Aguias Futebol", "AGU")

    assert club_repository.count() == 1
    assert unit_of_work.commits == 0


def test_create_club_rejects_the_club_after_the_limit(
    club_repository, unit_of_work, add_club
) -> None:
    for suffix in ACRONYM_SUFFIXES:
        add_club(f"Clube {suffix}", f"CL{suffix}")
    assert club_repository.count() == MAX_CLUBS

    with pytest.raises(ClubLimitReached):
        CreateClub(club_repository, unit_of_work).execute("Clube U", "CLU")

    assert club_repository.count() == MAX_CLUBS
    assert unit_of_work.commits == 0


def test_create_club_rejects_an_acronym_that_does_not_match_the_name(
    club_repository, unit_of_work
) -> None:
    with pytest.raises(InvalidClubData):
        CreateClub(club_repository, unit_of_work).execute("Águias FC", "XYZ")

    assert club_repository.count() == 0
    assert unit_of_work.commits == 0
