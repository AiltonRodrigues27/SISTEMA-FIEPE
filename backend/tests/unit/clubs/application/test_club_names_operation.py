from app.modules.clubs.application.public_operations import ClubsPublicOperations


def build_operations(club_repository, contract_repository, players_operations):
    return ClubsPublicOperations(club_repository, contract_repository, players_operations)


def test_list_club_names_returns_every_club_by_id(
    club_repository, contract_repository, players_operations, add_club
) -> None:
    eagles = add_club("Águias FC", "AGU")
    delta = add_club("Delta FC", "DFC")
    operations = build_operations(club_repository, contract_repository, players_operations)

    assert operations.list_club_names() == {eagles.id: "Águias FC", delta.id: "Delta FC"}


def test_list_club_names_without_clubs_is_empty(
    club_repository, contract_repository, players_operations
) -> None:
    operations = build_operations(club_repository, contract_repository, players_operations)

    assert operations.list_club_names() == {}
