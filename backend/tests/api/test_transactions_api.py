from datetime import datetime, timedelta

import pytest

from app.shared.domain.brasilia_time import BRASILIA

PLAYERS_URL = "/api/v1/players"
CLUBS_URL = "/api/v1/clubs"

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
HEADER = "data_hora;tipo;jogador;valor;taxa_ou_comissao;multa;lucro;variacao_caixa\n"
SALE_LINE = "2026-11-05T16:40:00-03:00;VENDA;Meia Lua;40,00;0,30;4,00;3,00;35,70\n"
PURCHASE_LINE = "2026-11-02T10:15:00-03:00;COMPRA;Meia Lua;37,00;1,85;0,00;;-38,85\n"
ZERO_SUMMARY = {
    "total_spent": 0.0,
    "total_received": 0.0,
    "total_fees": 0.0,
    "total_penalties": 0.0,
    "total_profit": 0.0,
}


def create_player(client, body=None, **changes):
    response = client.post(PLAYERS_URL, json={**(body or MEIA_LUA), **changes})
    assert response.status_code == 201
    return response.json()


def create_cheap_player(client, name):
    return create_player(client, {**CHEAP, "name": name})


def create_club(client, name="Águias FC", acronym="AGU"):
    response = client.post(CLUBS_URL, json={"name": name, "acronym": acronym})
    assert response.status_code == 201
    return response.json()


def change_condition(client, player, condition):
    response = client.patch(
        f"{PLAYERS_URL}/{player['id']}/condition", json={"condition": condition}
    )
    assert response.status_code == 200


def loyalty_in(clock, days=120):
    return (clock.moment + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M-03:00")


def buy_ok(client, player, club, loyalty_until):
    response = client.post(
        f"{PLAYERS_URL}/{player['id']}/buy",
        json={"club_id": club["id"], "loyalty_until": loyalty_until},
    )
    assert response.status_code == 200
    return response.json()


def sell_ok(client, player):
    response = client.post(f"{PLAYERS_URL}/{player['id']}/sell")
    assert response.status_code == 200
    return response.json()


def transactions_url(club, query=""):
    return f"{CLUBS_URL}/{club['id']}/transactions{query}"


def play_the_example(client, clock):
    player = create_player(client)
    change_condition(client, player, "MAL_CONDICIONADO")
    club = create_club(client)
    buy_ok(client, player, club, "2027-03-02T10:15-03:00")
    change_condition(client, player, "APTO")
    clock.moment = datetime(2026, 11, 5, 16, 40, tzinfo=BRASILIA)
    sell_ok(client, player)
    return player, club


def test_history_follows_the_example_of_the_statement(client, clock):
    player, club = play_the_example(client, clock)

    response = client.get(transactions_url(club))

    assert response.status_code == 200
    body = response.json()
    sale, purchase = body["data"]
    assert sale == {
        "id": sale["id"],
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
    }
    assert purchase == {
        "id": purchase["id"],
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
    }
    assert sale["id"] > purchase["id"]
    assert body["summary"] == {
        "total_spent": 38.85,
        "total_received": 35.7,
        "total_fees": 2.15,
        "total_penalties": 4.0,
        "total_profit": 3.0,
    }


@pytest.mark.parametrize(
    ("query", "expected_types", "summary"),
    [
        pytest.param(
            "?type=VENDA",
            ["VENDA"],
            {
                "total_spent": 0.0,
                "total_received": 35.7,
                "total_fees": 0.3,
                "total_penalties": 4.0,
                "total_profit": 3.0,
            },
            id="sales_only",
        ),
        pytest.param(
            "?type=COMPRA",
            ["COMPRA"],
            {
                "total_spent": 38.85,
                "total_received": 0.0,
                "total_fees": 1.85,
                "total_penalties": 0.0,
                "total_profit": 0.0,
            },
            id="purchases_only",
        ),
        pytest.param(
            "?type=COMPRA,VENDA",
            ["VENDA", "COMPRA"],
            {
                "total_spent": 38.85,
                "total_received": 35.7,
                "total_fees": 2.15,
                "total_penalties": 4.0,
                "total_profit": 3.0,
            },
            id="both_types",
        ),
        pytest.param(
            "?type=VENDA,COMPRA",
            ["VENDA", "COMPRA"],
            {
                "total_spent": 38.85,
                "total_received": 35.7,
                "total_fees": 2.15,
                "total_penalties": 4.0,
                "total_profit": 3.0,
            },
            id="both_types_reversed",
        ),
    ],
)
def test_history_filters_by_type_and_the_summary_follows_the_filter(
    client, clock, query, expected_types, summary
):
    _, club = play_the_example(client, clock)

    body = client.get(transactions_url(club, query)).json()

    assert [item["type"] for item in body["data"]] == expected_types
    assert body["summary"] == summary


def test_history_filters_by_player(client, clock):
    club = create_club(client)
    first = create_cheap_player(client, "Reserva Um")
    second = create_cheap_player(client, "Reserva Dois")
    free = create_cheap_player(client, "Reserva Tres")
    buy_ok(client, first, club, loyalty_in(clock))
    buy_ok(client, second, club, loyalty_in(clock))

    only_second = client.get(transactions_url(club, f"?player_id={second['id']}")).json()
    nothing = client.get(transactions_url(club, f"?player_id={free['id']}")).json()

    assert [item["player_id"] for item in only_second["data"]] == [second["id"]]
    assert only_second["summary"]["total_spent"] == 1.0
    assert nothing == {"data": [], "summary": ZERO_SUMMARY}


def test_history_of_a_club_without_transactions_is_empty_with_a_zero_summary(client):
    club = create_club(client)

    response = client.get(transactions_url(club))

    assert response.status_code == 200
    assert response.json() == {"data": [], "summary": ZERO_SUMMARY}


def test_history_breaks_a_tie_of_date_and_time_by_the_decreasing_id(client, clock):
    club = create_club(client)
    first = create_cheap_player(client, "Reserva Um")
    second = create_cheap_player(client, "Reserva Dois")
    buy_ok(client, first, club, loyalty_in(clock))
    buy_ok(client, second, club, loyalty_in(clock))

    data = client.get(transactions_url(club)).json()["data"]

    assert [item["player_id"] for item in data] == [second["id"], first["id"]]
    assert data[0]["created_at"] == data[1]["created_at"]


def test_history_cash_reconciles_with_the_club_cash(client, clock):
    _, club = play_the_example(client, clock)

    data = client.get(transactions_url(club)).json()["data"]
    club_cash = client.get(f"{CLUBS_URL}/{club['id']}").json()["cash"]

    assert round(300 + sum(item["cash_change"] for item in data), 2) == club_cash == 296.85


def test_history_keeps_the_name_and_the_values_of_the_moment(client, clock):
    player = create_player(client)
    change_condition(client, player, "MAL_CONDICIONADO")
    club = create_club(client)
    buy_ok(client, player, club, "2027-03-02T10:15-03:00")
    renamed = {"name": "Meia Lua Jr", "position": "MEI", "agility": 85, "age": 25}
    assert client.put(f"{PLAYERS_URL}/{player['id']}", json=renamed).status_code == 200
    change_condition(client, player, "DOENTE")

    data = client.get(transactions_url(club)).json()["data"]

    assert data[0]["player_name"] == "Meia Lua"
    assert (data[0]["value"], data[0]["fee"]) == (37.0, 1.85)


def test_history_keeps_the_transactions_of_a_deleted_player_but_refuses_the_filter(client, clock):
    player, club = play_the_example(client, clock)
    assert client.delete(f"{PLAYERS_URL}/{player['id']}").status_code == 204

    everything = client.get(transactions_url(club))
    filtered = client.get(transactions_url(club, f"?player_id={player['id']}"))

    assert [item["player_name"] for item in everything.json()["data"]] == ["Meia Lua", "Meia Lua"]
    assert filtered.status_code == 404
    assert filtered.json()["message"]


@pytest.mark.parametrize(
    "query",
    [
        "type=",
        "type=compra",
        "type=COMPRA,compra",
        "type=COMPRA,COMPRA",
        "type=COMPRA,%20VENDA",
        "type=COMPRA,",
        "type=TROCA",
        "player_id=",
        "player_id=0",
        "player_id=01",
        "player_id=-1",
        "player_id=1.5",
        "player_id=abc",
        "player_id=2147483648",
    ],
)
def test_history_and_export_reject_invalid_filters_with_400_in_json(client, query):
    club = create_club(client)

    history = client.get(transactions_url(club, f"?{query}"))
    export = client.get(f"{transactions_url(club)}/export?{query}")

    for response in (history, export):
        assert response.status_code == 400
        assert response.json()["message"]
        assert response.headers["content-type"].startswith("application/json")


def test_history_and_export_return_404_for_an_unknown_club_or_player(client):
    club = create_club(client)

    unknown_club = client.get(f"{CLUBS_URL}/999999/transactions")
    unknown_club_export = client.get(f"{CLUBS_URL}/999999/transactions/export")
    unknown_player = client.get(transactions_url(club, "?player_id=999999"))
    unknown_player_export = client.get(f"{transactions_url(club)}/export?player_id=999999")

    for response in (unknown_club, unknown_club_export, unknown_player, unknown_player_export):
        assert response.status_code == 404
        assert response.json()["message"]


@pytest.mark.parametrize("club_id", ["01", "0", "abc", "-1", "1.5", "2147483648"])
def test_history_and_export_treat_a_malformed_club_id_as_not_found(client, club_id):
    assert client.get(f"{CLUBS_URL}/{club_id}/transactions").status_code == 404
    assert client.get(f"{CLUBS_URL}/{club_id}/transactions/export").status_code == 404


def test_export_follows_the_example_of_the_statement(client, clock):
    _, club = play_the_example(client, clock)

    response = client.get(f"{transactions_url(club)}/export")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.text == HEADER + SALE_LINE + PURCHASE_LINE


def test_export_applies_the_same_filters_as_the_history(client, clock):
    _, club = play_the_example(client, clock)

    sales = client.get(f"{transactions_url(club)}/export?type=VENDA")
    purchases = client.get(f"{transactions_url(club)}/export?type=COMPRA")

    assert sales.text == HEADER + SALE_LINE
    assert purchases.text == HEADER + PURCHASE_LINE


def test_export_of_a_club_without_transactions_has_only_the_header(client):
    club = create_club(client)

    response = client.get(f"{transactions_url(club)}/export")

    assert response.status_code == 200
    assert response.text == HEADER


def test_export_is_utf8_without_bom_and_every_line_ends_with_a_line_feed(client, clock):
    _, club = play_the_example(client, clock)

    content = client.get(f"{transactions_url(club)}/export").content

    assert not content.startswith(b"\xef\xbb\xbf")
    assert content.endswith(b"\n")
    assert b"\r" not in content
    assert content.decode("utf-8").count("\n") == 3


@pytest.mark.parametrize(
    ("player_name", "expected_field"),
    [
        pytest.param('Zé "Foguete" Lima', '"Zé ""Foguete"" Lima"', id="double_quotes"),
        pytest.param("Zé; Foguete", '"Zé; Foguete"', id="semicolon"),
        pytest.param("Zé Foguete", "Zé Foguete", id="plain_name"),
    ],
)
def test_export_quotes_the_name_only_when_needed(client, clock, player_name, expected_field):
    club = create_club(client)
    player = create_cheap_player(client, player_name)
    buy_ok(client, player, club, loyalty_in(clock))

    lines = client.get(f"{transactions_url(club)}/export").text.splitlines()

    assert lines[1] == f"2026-11-02T10:15:00-03:00;COMPRA;{expected_field};1,00;0,00;0,00;;-1,00"
