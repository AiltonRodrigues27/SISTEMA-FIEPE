import pytest
from pydantic import ValidationError

from app.modules.players.adapters.inbound.http.schemas import (
    ChangeConditionRequest,
    CreatePlayerRequest,
    PlayerResponse,
    UpdatePlayerRequest,
)
from app.modules.players.application.update_player import PlayerProfileChanges
from app.modules.players.domain.entities import Attributes, Player, PlayerRegistration
from app.modules.players.domain.enums import PhysicalCondition, Position

VALID = {
    "name": "Vini Jr",
    "position": "MEI",
    "agility": 85,
    "age": 25,
    "pace": 70,
    "shooting": 68,
    "passing": 82,
    "dribbling": 79,
    "defending": 55,
    "physical": 64,
    "potential": 86,
}


def test_valid_body_converts_to_the_domain_registration() -> None:
    request = CreatePlayerRequest.model_validate(VALID)

    assert request.to_registration() == PlayerRegistration(
        name="Vini Jr",
        position=Position.MEI,
        agility=85,
        age=25,
        attributes=Attributes(70, 68, 82, 79, 55, 64),
        potential=86,
    )


@pytest.mark.parametrize(
    ("raw_name", "clean_name"),
    [
        pytest.param("  Meia   Zeta ", "Meia Zeta", id="trims_and_collapses_spaces"),
        pytest.param("Meia - Lua", "Meia - Lua", id="hyphen_is_not_a_word_but_is_allowed"),
        pytest.param("Zé  Foguete", "Zé Foguete", id="accented_letters"),
        pytest.param("A B", "A B", id="three_characters"),
        pytest.param("A " + "b" * 98, "A " + "b" * 98, id="one_hundred_characters"),
    ],
)
def test_name_is_cleaned_and_accepted(raw_name, clean_name) -> None:
    request = CreatePlayerRequest.model_validate({**VALID, "name": raw_name})

    assert request.name == clean_name


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("Pelé", id="one_word"),
        pytest.param("   ", id="blank"),
        pytest.param("", id="empty"),
        pytest.param("Ab", id="two_characters"),
        pytest.param("A " + "b" * 99, id="one_hundred_and_one_characters"),
        pytest.param("Jogador 2", id="digit"),
        pytest.param("Meia\tLua", id="tab"),
        pytest.param("Meia\nLua", id="line_break"),
        pytest.param("- -", id="only_symbols"),
        pytest.param(None, id="null"),
        pytest.param(10, id="number"),
    ],
)
def test_name_is_rejected(name) -> None:
    with pytest.raises(ValidationError):
        CreatePlayerRequest.model_validate({**VALID, "name": name})


def test_integer_sent_as_whole_decimal_is_accepted() -> None:
    request = CreatePlayerRequest.model_validate({**VALID, "agility": 50.0})

    assert request.agility == 50
    assert isinstance(request.agility, int)


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("85", id="text"),
        pytest.param(50.5, id="fraction"),
        pytest.param(True, id="boolean"),
        pytest.param(None, id="null"),
        pytest.param([85], id="list"),
    ],
)
def test_integer_is_rejected(value) -> None:
    with pytest.raises(ValidationError):
        CreatePlayerRequest.model_validate({**VALID, "agility": value})


@pytest.mark.parametrize("position", ["mei", "Mei", "XXX", "", None, 1])
def test_position_is_rejected(position) -> None:
    with pytest.raises(ValidationError):
        CreatePlayerRequest.model_validate({**VALID, "position": position})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("agility", 1),
        ("agility", 100),
        ("age", 16),
        ("age", 45),
        ("pace", 1),
        ("pace", 99),
        ("potential", 1),
        ("potential", 99),
    ],
)
def test_limits_are_inclusive(field, value) -> None:
    request = CreatePlayerRequest.model_validate({**VALID, field: value})

    assert getattr(request, field) == value


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("agility", 0),
        ("agility", 101),
        ("age", 15),
        ("age", 46),
        ("pace", 0),
        ("pace", 100),
        ("shooting", 0),
        ("passing", 100),
        ("dribbling", 0),
        ("defending", 100),
        ("physical", 0),
        ("potential", 0),
        ("potential", 100),
    ],
)
def test_values_outside_the_limits_are_rejected(field, value) -> None:
    with pytest.raises(ValidationError):
        CreatePlayerRequest.model_validate({**VALID, field: value})


@pytest.mark.parametrize("field", VALID)
def test_missing_field_is_rejected(field) -> None:
    body = {key: value for key, value in VALID.items() if key != field}

    with pytest.raises(ValidationError):
        CreatePlayerRequest.model_validate(body)


@pytest.mark.parametrize("field", VALID)
def test_null_field_is_rejected(field) -> None:
    with pytest.raises(ValidationError):
        CreatePlayerRequest.model_validate({**VALID, field: None})


def test_fields_controlled_by_the_system_are_ignored() -> None:
    request = CreatePlayerRequest.model_validate(
        {**VALID, "id": 9, "condition": "DOENTE", "club_id": 3, "base_value": 1, "overall": 1}
    )

    assert not hasattr(request, "id")
    assert not hasattr(request, "condition")
    assert not hasattr(request, "club_id")


def test_update_request_converts_to_profile_changes() -> None:
    request = UpdatePlayerRequest.model_validate(
        {"name": "  Davi   Melo ", "position": "ATA", "agility": 70, "age": 23, "potential": 1}
    )

    assert request.to_changes() == PlayerProfileChanges(
        name="Davi Melo", position=Position.ATA, agility=70, age=23
    )


@pytest.mark.parametrize("field", ["name", "position", "agility", "age"])
def test_update_request_requires_the_editable_fields(field) -> None:
    body = {"name": "Davi Melo", "position": "ATA", "agility": 70, "age": 23}
    del body[field]

    with pytest.raises(ValidationError):
        UpdatePlayerRequest.model_validate(body)


def test_change_condition_request_accepts_only_exact_values() -> None:
    assert (
        ChangeConditionRequest.model_validate({"condition": "DOENTE"}).condition
        is PhysicalCondition.DOENTE
    )
    for invalid in ({}, {"condition": None}, {"condition": "doente"}, {"condition": "XXX"}):
        with pytest.raises(ValidationError):
            ChangeConditionRequest.model_validate(invalid)


def test_response_carries_calculated_fields_as_numbers() -> None:
    player = Player.register(CreatePlayerRequest.model_validate(VALID).to_registration())
    player.id = 1

    response = PlayerResponse.from_entity(player)

    assert response.id == 1
    assert response.overall == 75
    assert response.base_value == 40.0
    assert response.market_value == 40.0
    assert response.condition is PhysicalCondition.APTO
    assert response.club_id is None
