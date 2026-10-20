from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.clubs.adapters.inbound.http.schemas import (
    ClubDetailResponse,
    ClubResponse,
    ContractResponse,
    CreateClubRequest,
)
from app.modules.clubs.application.get_club import ClubDetails, ContractView, SquadMember
from app.modules.clubs.domain.entities import Club, ClubView
from app.modules.players.application.public_operations import PlayerView
from app.modules.players.domain.entities import Attributes
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.shared.domain.brasilia_time import BRASILIA


@pytest.mark.parametrize(
    ("raw_name", "clean_name"),
    [
        pytest.param("  Águias   FC ", "Águias FC", id="trims_and_collapses_spaces"),
        pytest.param("Sport-Club Recife", "Sport-Club Recife", id="hyphen"),
        pytest.param("St. Pauli FC", "St. Pauli FC", id="dot"),
        pytest.param("A B", "A B", id="shortest_name"),
        pytest.param("A B C D E", "A B C D E", id="five_words"),
        pytest.param("A " + "b" * 58, "A " + "b" * 58, id="sixty_characters"),
    ],
)
def test_club_name_is_cleaned_and_accepted(raw_name, clean_name) -> None:
    request = CreateClubRequest.model_validate({"name": raw_name, "acronym": "AGU"})

    assert request.name == clean_name


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("Águias", id="one_word"),
        pytest.param("AB", id="two_characters"),
        pytest.param("Águias FC 1", id="digit"),
        pytest.param("Águias_FC", id="underscore"),
        pytest.param("Águias&FC", id="symbol"),
        pytest.param("Águias\tFC", id="tab"),
        pytest.param("A B C D E F", id="six_words"),
        pytest.param("A " + "b" * 59, id="sixty_one_characters"),
        pytest.param("- - -", id="only_symbols"),
        pytest.param("   ", id="blank"),
        pytest.param(None, id="null"),
        pytest.param(10, id="number"),
    ],
)
def test_club_name_is_rejected(name) -> None:
    with pytest.raises(ValidationError):
        CreateClubRequest.model_validate({"name": name, "acronym": "AGU"})


@pytest.mark.parametrize(
    "acronym",
    [
        pytest.param("agu", id="lowercase"),
        pytest.param("AG", id="two_letters"),
        pytest.param("AGUI", id="four_letters"),
        pytest.param("AG1", id="digit"),
        pytest.param("ÁGU", id="accent"),
        pytest.param("A U", id="space"),
        pytest.param("", id="empty"),
        pytest.param(None, id="null"),
        pytest.param(123, id="number"),
    ],
)
def test_acronym_is_rejected(acronym) -> None:
    with pytest.raises(ValidationError):
        CreateClubRequest.model_validate({"name": "Águias FC", "acronym": acronym})


@pytest.mark.parametrize("field", ["name", "acronym"])
def test_missing_field_is_rejected(field) -> None:
    body = {"name": "Águias FC", "acronym": "AGU"}
    del body[field]

    with pytest.raises(ValidationError):
        CreateClubRequest.model_validate(body)


def test_fields_controlled_by_the_system_are_ignored() -> None:
    request = CreateClubRequest.model_validate(
        {"name": "Águias FC", "acronym": "AGU", "cash": 999, "id": 5, "squad_value": 1}
    )

    assert not hasattr(request, "cash")
    assert not hasattr(request, "id")


def test_club_response_has_money_as_numbers() -> None:
    club = Club(id=1, name="Águias FC", acronym="AGU", cash=Decimal("261.15"), formation=None)

    response = ClubResponse.from_view(ClubView(club, Decimal("37.00")))

    assert response.model_dump() == {
        "id": 1,
        "name": "Águias FC",
        "acronym": "AGU",
        "cash": 261.15,
        "squad_value": 37.0,
        "net_worth": 298.15,
    }


def test_contract_response_formats_the_date_in_brasilia_time() -> None:
    view = ContractView(
        purchase_value=Decimal("37.00"),
        loyalty_until=datetime(2027, 3, 2, 13, 15, tzinfo=UTC),
        remaining_days=120,
        penalty_percent=10,
    )

    assert ContractResponse.from_view(view).model_dump() == {
        "purchase_value": 37.0,
        "loyalty_until": "2027-03-02T10:15:00-03:00",
        "remaining_days": 120,
        "penalty_rate": 10,
    }


def test_club_detail_response_has_the_squad_with_the_contract() -> None:
    club = Club(id=1, name="Águias FC", acronym="AGU", cash=Decimal("261.15"), formation=None)
    player = PlayerView(
        id=2,
        name="Meia Lua",
        position=Position.MEI,
        agility=85,
        age=25,
        condition=PhysicalCondition.MAL_CONDICIONADO,
        base_value=Decimal("40.00"),
        market_value=Decimal("37.00"),
        attributes=Attributes(70, 68, 82, 79, 55, 64),
        potential=86,
        overall=75,
        club_id=1,
    )
    contract = ContractView(
        Decimal("37.00"), datetime(2027, 3, 2, 10, 15, tzinfo=BRASILIA), 120, 10
    )
    details = ClubDetails(ClubView(club, Decimal("37.00")), [SquadMember(player, contract)])

    response = ClubDetailResponse.from_details(details)

    member = response.players[0]
    assert response.net_worth == 298.15
    assert member.name == "Meia Lua"
    assert member.market_value == 37.0
    assert member.club_id == 1
    assert member.contract.penalty_rate == 10
    assert member.contract.loyalty_until == "2027-03-02T10:15:00-03:00"
