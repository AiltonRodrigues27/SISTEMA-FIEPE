import pytest

from app.modules.clubs.application.public_operations import ClubsPublicOperations
from app.modules.clubs.domain.errors import ClubNotFound


def build_operations(club_repository, contract_repository, players_operations):
    return ClubsPublicOperations(club_repository, contract_repository, players_operations)


def test_get_formation_of_a_new_club_is_none(
    club_repository, contract_repository, players_operations, add_club
) -> None:
    club = add_club("Águias FC", "AGU")
    operations = build_operations(club_repository, contract_repository, players_operations)

    assert operations.get_formation(club.id) is None


def test_set_formation_saves_it_and_get_formation_returns_it(
    club_repository, contract_repository, players_operations, add_club
) -> None:
    club = add_club("Águias FC", "AGU")
    operations = build_operations(club_repository, contract_repository, players_operations)

    operations.set_formation(club.id, "2-1-1")

    assert operations.get_formation(club.id) == "2-1-1"
    assert club_repository.get(club.id).formation == "2-1-1"


def test_set_formation_replaces_the_previous_one_and_keeps_the_cash(
    club_repository, contract_repository, players_operations, add_club
) -> None:
    club = add_club("Águias FC", "AGU", cash="261.15")
    operations = build_operations(club_repository, contract_repository, players_operations)
    operations.set_formation(club.id, "2-1-1")

    operations.set_formation(club.id, "3-1")

    assert operations.get_formation(club.id) == "3-1"
    assert str(club_repository.get(club.id).cash) == "261.15"


def test_get_formation_raises_not_found_for_unknown_club(
    club_repository, contract_repository, players_operations
) -> None:
    operations = build_operations(club_repository, contract_repository, players_operations)

    with pytest.raises(ClubNotFound):
        operations.get_formation(999)


def test_set_formation_raises_not_found_for_unknown_club(
    club_repository, contract_repository, players_operations
) -> None:
    operations = build_operations(club_repository, contract_repository, players_operations)

    with pytest.raises(ClubNotFound):
        operations.set_formation(999, "2-1-1")
