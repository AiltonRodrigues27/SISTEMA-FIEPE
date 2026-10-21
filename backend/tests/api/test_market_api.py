import string
from datetime import datetime, timedelta

import pytest

from app.shared.domain.brasilia_time import BRASILIA

PLAYERS_URL = "/api/v1/players"
CLUBS_URL = "/api/v1/clubs"
MISSING = object()

MEIA_LUA = {
    "name": "Meia Lua",
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
CHEAP = {
    "position": "MEI",
    "agility": 50,
    "age": 30,
    "pace": 1,
    "shooting": 1,
    "passing": 1,
    "dribbling": 1,
    "defending": 1,
    "physical": 1,
    "potential": 1,
}
EXPENSIVE_GOALKEEPER = {
    "name": "Goleiro Caro",
    "position": "GOL",
    "agility": 85,
    "age": 25,
    "pace": 99,
    "shooting": 1,
    "passing": 99,
    "dribbling": 1,
    "defending": 99,
    "physical": 99,
    "potential": 99,
}


def create_player(client, body=None, **changes):
    response = client.post(PLAYERS_URL, json={**(body or MEIA_LUA), **changes})
    assert response.status_code == 201
    return response.json()


def create_cheap_player(client, name, **changes):
    return create_player(client, {**CHEAP, "name": name}, **changes)


def create_club(client, name="Águias FC", acronym="AGU"):
    response = client.post(CLUBS_URL, json={"name": name, "acronym": acronym})
    assert response.status_code == 201
    return response.json()


def change_condition(client, player, condition):
    response = client.patch(
        f"{PLAYERS_URL}/{player['id']}/condition", json={"condition": condition}
    )
    assert response.status_code == 200


def loyalty_in(clock, days=120, minutes=0):
    moment = clock.moment + timedelta(days=days, minutes=minutes)
    return moment.strftime("%Y-%m-%dT%H:%M-03:00")


def buy(client, player, club, loyalty_until):
    return client.post(
        f"{PLAYERS_URL}/{player['id']}/buy",
        json={"club_id": club["id"], "loyalty_until": loyalty_until},
    )


def sell(client, player):
    return client.post(f"{PLAYERS_URL}/{player['id']}/sell")


def buy_ok(client, player, club, loyalty_until):
    response = buy(client, player, club, loyalty_until)
    assert response.status_code == 200
    return response.json()


def get_club(client, club):
    return client.get(f"{CLUBS_URL}/{club['id']}").json()


def get_player(client, player):
    return client.get(f"{PLAYERS_URL}/{player['id']}").json()


def build_body(club, clock, **changes):
    body = {"club_id": club["id"], "loyalty_until": loyalty_in(clock)}
    body.update(changes)
    return {key: value for key, value in body.items() if value is not MISSING}


def test_buy_follows_the_example_of_the_statement(client, clock):
    player = create_player(client)
    change_condition(client, player, "MAL_CONDICIONADO")
    club = create_club(client)

    response = buy(client, player, club, "2027-03-02T10:15-03:00")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "id": body["id"],
        "club_id": club["id"],
        "player_id": player["id"],
        "player_name": "Meia Lua",
        "type": "COMPRA",
        "value": 37.0,
        "fee": 1.85,
        "penalty": 0.0,
        "profit": None,
        "cash_change": -38.85,
        "created_at": "2026-11-02T10:15:00-03:00",
        "contract": {
            "purchase_value": 37.0,
            "loyalty_until": "2027-03-02T10:15:00-03:00",
            "status": "ATIVO",
        },
        "club_cash": 261.15,
    }


def test_after_a_purchase_the_club_page_the_player_and_the_filters_show_it(client, clock):
    player = create_player(client)
    change_condition(client, player, "MAL_CONDICIONADO")
    club = create_club(client)
    buy_ok(client, player, club, "2027-03-02T10:15-03:00")

    club_page = get_club(client, club)

    assert (club_page["cash"], club_page["squad_value"], club_page["net_worth"]) == (
        261.15,
        37.0,
        298.15,
    )
    member = club_page["players"][0]
    assert (member["id"], member["club_id"], member["market_value"]) == (
        player["id"],
        club["id"],
        37.0,
    )
    assert member["contract"] == {
        "purchase_value": 37.0,
        "loyalty_until": "2027-03-02T10:15:00-03:00",
        "remaining_days": 120,
        "penalty_rate": 10,
    }
    assert get_player(client, player)["club_id"] == club["id"]
    free_players = client.get(f"{PLAYERS_URL}?free=true").json()
    assert free_players["data"] == []
    in_club = client.get(f"{PLAYERS_URL}?club_id={club['id']}").json()
    assert [item["id"] for item in in_club["data"]] == [player["id"]]


def test_sell_follows_the_example_of_the_statement(client, clock):
    player = create_player(client)
    change_condition(client, player, "MAL_CONDICIONADO")
    club = create_club(client)
    buy_ok(client, player, club, "2027-03-02T10:15-03:00")
    change_condition(client, player, "APTO")
    clock.moment = datetime(2026, 11, 5, 16, 40, tzinfo=BRASILIA)

    response = sell(client, player)

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "id": body["id"],
        "club_id": club["id"],
        "player_id": player["id"],
        "player_name": "Meia Lua",
        "type": "VENDA",
        "value": 40.0,
        "fee": 0.3,
        "penalty": 4.0,
        "profit": 3.0,
        "cash_change": 35.7,
        "created_at": "2026-11-05T16:40:00-03:00",
        "purchase_value": 37.0,
        "remaining_days": 117,
        "penalty_rate": 10,
        "contract_status": "RESCINDIDO",
        "club_cash": 296.85,
    }
    assert get_player(client, player)["club_id"] is None
    club_page = get_club(client, club)
    assert club_page["cash"] == 296.85
    assert club_page["players"] == []


def test_sell_at_a_loss_has_no_commission_and_a_twenty_percent_penalty(client, clock):
    player = create_player(client)
    club = create_club(client)
    buy_ok(client, player, club, loyalty_in(clock, days=200))
    change_condition(client, player, "DOENTE")

    body = sell(client, player).json()

    assert body["value"] == 34.0
    assert body["fee"] == 0.0
    assert body["penalty"] == 6.8
    assert body["profit"] == -6.0
    assert body["cash_change"] == 27.2
    assert (body["remaining_days"], body["penalty_rate"]) == (200, 20)
    assert body["contract_status"] == "RESCINDIDO"
    assert body["club_cash"] == 285.2


def test_sell_after_the_loyalty_end_has_no_penalty_and_ends_the_contract(client, clock):
    player = create_player(client)
    club = create_club(client)
    buy_ok(client, player, club, loyalty_in(clock, days=1))
    clock.moment = clock.moment + timedelta(days=2)

    body = sell(client, player).json()

    assert (body["remaining_days"], body["penalty_rate"], body["penalty"]) == (0, 0, 0.0)
    assert body["contract_status"] == "ENCERRADO"
    assert (body["profit"], body["fee"], body["cash_change"]) == (0.0, 0.0, 40.0)
    assert body["club_cash"] == 298.0


def test_club_squad_is_in_goalkeeper_to_forward_order_with_summed_value(client, clock):
    club = create_club(client)
    for name, position in [("Ata Barata", "ATA"), ("Gol Barato", "GOL"), ("Mei Barato", "MEI")]:
        player = create_cheap_player(client, name, position=position)
        buy_ok(client, player, club, loyalty_in(clock))

    club_page = get_club(client, club)

    assert [member["name"] for member in club_page["players"]] == [
        "Gol Barato",
        "Mei Barato",
        "Ata Barata",
    ]
    assert (club_page["cash"], club_page["squad_value"], club_page["net_worth"]) == (
        297.0,
        3.0,
        300.0,
    )


@pytest.mark.parametrize(
    "changes",
    [
        pytest.param({"club_id": MISSING}, id="missing_club_id"),
        pytest.param({"club_id": 0}, id="club_id_zero"),
        pytest.param({"club_id": -1}, id="negative_club_id"),
        pytest.param({"club_id": "1"}, id="club_id_as_text"),
        pytest.param({"club_id": 1.5}, id="club_id_with_fraction"),
        pytest.param({"club_id": None}, id="null_club_id"),
        pytest.param({"loyalty_until": MISSING}, id="missing_loyalty_until"),
        pytest.param({"loyalty_until": None}, id="null_loyalty_until"),
        pytest.param({"loyalty_until": 20270302}, id="number_as_loyalty_until"),
        pytest.param({"loyalty_until": "2027-03-02T10:15"}, id="no_offset"),
        pytest.param({"loyalty_until": "2027-03-02T10:15:00-03:00"}, id="with_seconds"),
        pytest.param({"loyalty_until": "2027-03-02T10:15+00:00"}, id="other_offset"),
        pytest.param({"loyalty_until": "2027-02-30T10:15-03:00"}, id="day_that_does_not_exist"),
        pytest.param({"loyalty_until": "2027-03-02T24:00-03:00"}, id="hour_that_does_not_exist"),
    ],
)
def test_buy_rejects_an_invalid_body_with_400_and_buys_nothing(client, clock, changes):
    player = create_cheap_player(client, "Reserva Um")
    club = create_club(client)

    response = client.post(
        f"{PLAYERS_URL}/{player['id']}/buy", json=build_body(club, clock, **changes)
    )

    assert response.status_code == 400
    assert response.json()["message"]
    assert get_player(client, player)["club_id"] is None
    assert get_club(client, club)["cash"] == 300.0


def test_buy_rejects_a_body_that_is_not_an_object(client):
    player = create_cheap_player(client, "Reserva Um")

    response = client.post(f"{PLAYERS_URL}/{player['id']}/buy", json=[])

    assert response.status_code == 400
    assert response.json()["message"]


@pytest.mark.parametrize(
    ("days", "minutes"),
    [
        pytest.param(0, 0, id="exactly_now"),
        pytest.param(0, -1, id="one_minute_ago"),
        pytest.param(-10, 0, id="ten_days_ago"),
        pytest.param(1095, 1, id="a_minute_beyond_one_thousand_ninety_five_days"),
    ],
)
def test_buy_rejects_a_loyalty_end_out_of_the_window_without_charging(client, clock, days, minutes):
    player = create_cheap_player(client, "Reserva Um")
    club = create_club(client)

    response = buy(client, player, club, loyalty_in(clock, days, minutes))

    assert response.status_code == 400
    assert response.json()["message"]
    assert get_player(client, player)["club_id"] is None
    assert get_club(client, club)["cash"] == 300.0


@pytest.mark.parametrize(
    ("days", "minutes"),
    [
        pytest.param(0, 1, id="one_minute_ahead"),
        pytest.param(1095, 0, id="exactly_one_thousand_ninety_five_days"),
    ],
)
def test_buy_accepts_a_loyalty_end_at_the_edges_of_the_window(client, clock, days, minutes):
    player = create_cheap_player(client, "Reserva Um")
    club = create_club(client)

    response = buy(client, player, club, loyalty_in(clock, days, minutes))

    assert response.status_code == 200


def test_buy_returns_404_for_an_unknown_player(client, clock):
    club = create_club(client)

    response = client.post(f"{PLAYERS_URL}/999999/buy", json=build_body(club, clock))

    assert response.status_code == 404
    assert response.json() == {"message": "Jogador não encontrado."}


def test_buy_returns_404_for_an_unknown_club(client, clock):
    player = create_cheap_player(client, "Reserva Um")

    response = client.post(
        f"{PLAYERS_URL}/{player['id']}/buy",
        json={"club_id": 999999, "loyalty_until": loyalty_in(clock)},
    )

    assert response.status_code == 404
    assert response.json() == {"message": "Clube não encontrado."}


def test_buy_returns_404_for_a_deleted_player(client, clock):
    player = create_cheap_player(client, "Reserva Um")
    club = create_club(client)
    client.delete(f"{PLAYERS_URL}/{player['id']}")

    response = buy(client, player, club, loyalty_in(clock))

    assert response.status_code == 404


@pytest.mark.parametrize("player_id", ["01", "0", "abc", "-1", "1.5", "2147483648"])
def test_buy_and_sell_treat_a_malformed_id_as_not_found(client, clock, player_id):
    club = create_club(client)

    bought = client.post(f"{PLAYERS_URL}/{player_id}/buy", json=build_body(club, clock))
    sold = client.post(f"{PLAYERS_URL}/{player_id}/sell")

    assert bought.status_code == 404
    assert sold.status_code == 404
    assert bought.json()["message"] and sold.json()["message"]


def test_buy_rejects_a_player_that_already_has_a_club_with_409(client, clock):
    player = create_cheap_player(client, "Reserva Um")
    eagles = create_club(client)
    delta = create_club(client, "Delta FC", "DFC")
    buy_ok(client, player, eagles, loyalty_in(clock))

    by_the_owner = buy(client, player, eagles, loyalty_in(clock))
    by_another_club = buy(client, player, delta, loyalty_in(clock))

    assert by_the_owner.status_code == 409
    assert by_another_club.status_code == 409
    assert get_club(client, delta)["cash"] == 300.0
    assert get_player(client, player)["club_id"] == eagles["id"]


def test_buy_rejects_a_cost_above_half_of_the_cash_with_409_and_changes_nothing(client, clock):
    player = create_player(client, EXPENSIVE_GOALKEEPER)
    club = create_club(client)
    assert player["market_value"] == 184.0

    response = buy(client, player, club, loyalty_in(clock))

    assert response.status_code == 409
    assert response.json()["message"]
    assert get_player(client, player)["club_id"] is None
    club_page = get_club(client, club)
    assert club_page["cash"] == 300.0
    assert club_page["players"] == []


def test_buy_rejects_the_thirteenth_player_with_409(client, clock):
    club = create_club(client)
    players = [
        create_cheap_player(client, f"Reserva {letter}") for letter in string.ascii_uppercase[:13]
    ]
    for player in players[:12]:
        buy_ok(client, player, club, loyalty_in(clock))

    response = buy(client, players[12], club, loyalty_in(clock))

    assert response.status_code == 409
    club_page = get_club(client, club)
    assert len(club_page["players"]) == 12
    assert club_page["cash"] == 288.0
    assert get_player(client, players[12])["club_id"] is None


def test_the_club_that_sold_a_player_cannot_buy_him_back_but_another_club_can(client, clock):
    player = create_cheap_player(client, "Reserva Um")
    eagles = create_club(client)
    delta = create_club(client, "Delta FC", "DFC")
    buy_ok(client, player, eagles, loyalty_in(clock))
    assert sell(client, player).status_code == 200

    by_the_seller = buy(client, player, eagles, loyalty_in(clock))
    by_another_club = buy(client, player, delta, loyalty_in(clock))

    assert by_the_seller.status_code == 409
    assert by_another_club.status_code == 200
    assert get_player(client, player)["club_id"] == delta["id"]


def test_sell_rejects_a_free_player_with_409(client):
    player = create_cheap_player(client, "Reserva Um")

    response = sell(client, player)

    assert response.status_code == 409
    assert response.json()["message"]


def test_sell_returns_404_for_an_unknown_player(client):
    response = client.post(f"{PLAYERS_URL}/999999/sell")

    assert response.status_code == 404
    assert response.json() == {"message": "Jogador não encontrado."}


def test_sell_returns_404_for_a_deleted_player(client):
    player = create_cheap_player(client, "Reserva Um")
    client.delete(f"{PLAYERS_URL}/{player['id']}")

    response = sell(client, player)

    assert response.status_code == 404


def test_sell_ignores_a_body_sent_with_the_request(client, clock):
    player = create_cheap_player(client, "Reserva Um")
    club = create_club(client)
    buy_ok(client, player, club, loyalty_in(clock))

    response = client.post(f"{PLAYERS_URL}/{player['id']}/sell", json={"club_id": 99, "value": 1})

    assert response.status_code == 200
