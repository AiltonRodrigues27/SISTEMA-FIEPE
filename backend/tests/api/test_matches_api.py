from datetime import timedelta

import pytest

PLAYERS_URL = "/api/v1/players"
CLUBS_URL = "/api/v1/clubs"
MATCHES_URL = "/api/v1/matches"
ATTRIBUTES = ("pace", "shooting", "passing", "dribbling", "defending", "physical")
STRONG, MIDDLE, WEAK = 60, 30, 1

EAGLES = (
    ("Rui Prado", "GOL", {"defending": 77}),
    ("Téo Brandão", "ZAG", {"defending": 84}),
    ("Davi Lins", "LAT", {"dribbling": 74, "defending": 66}),
    ("Lauro Neves", "MEI", {"passing": 82}),
    ("Otto Rangel", "ATA", {"shooting": 75}),
)
DELTA = (
    ("Ivo Teles", "GOL", {"defending": 72}),
    ("Hugo Vaz", "ZAG", {"defending": 84}),
    ("Lino Matos", "LAT", {"dribbling": 79, "defending": 63}),
    ("Nei Soares", "MEI", {"passing": 70}),
    ("Ugo Falcão", "ATA", {"shooting": 81}),
)
POWER_POSITIONS = (
    ("Goleiro", "GOL"),
    ("Zagueiro", "ZAG"),
    ("Lateral", "LAT"),
    ("Meia", "MEI"),
    ("Atacante", "ATA"),
)


def create_player(client, name, position, **attributes):
    body = {
        "name": name,
        "position": position,
        "agility": 50,
        "age": 25,
        **dict.fromkeys(ATTRIBUTES, 1),
        "potential": 99,
        **attributes,
    }
    response = client.post(PLAYERS_URL, json=body)
    assert response.status_code == 201
    return response.json()


def create_club(client, name, acronym):
    response = client.post(CLUBS_URL, json={"name": name, "acronym": acronym})
    assert response.status_code == 201
    return response.json()


def loyalty_in(clock, days=120):
    return (clock.moment + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M-03:00")


def buy_ok(client, player, club, clock):
    response = client.post(
        f"{PLAYERS_URL}/{player['id']}/buy",
        json={"club_id": club["id"], "loyalty_until": loyalty_in(clock)},
    )
    assert response.status_code == 200


def change_condition(client, player, condition):
    response = client.patch(
        f"{PLAYERS_URL}/{player['id']}/condition", json={"condition": condition}
    )
    assert response.status_code == 200


def sell_ok(client, player):
    assert client.post(f"{PLAYERS_URL}/{player['id']}/sell").status_code == 200


def set_lineup_ok(client, club, players):
    response = client.put(
        f"{CLUBS_URL}/{club['id']}/lineup",
        json={"formation": "2-1-1", "player_ids": [player["id"] for player in players]},
    )
    assert response.status_code == 200


def build_club(client, clock, name, acronym, members):
    club = create_club(client, name, acronym)
    players = {}
    for player_name, position, attributes in members:
        player = create_player(client, player_name, position, **attributes)
        buy_ok(client, player, club, clock)
        players[player_name] = player
    set_lineup_ok(client, club, players.values())
    return club, players


def build_power_club(client, clock, name, acronym, tag, power):
    members = [
        (f"{label} {tag}", position, dict.fromkeys(ATTRIBUTES, power))
        for label, position in POWER_POSITIONS
    ]
    return build_club(client, clock, name, acronym, members)


def play(client, home, away):
    return client.post(MATCHES_URL, json={"home_club_id": home["id"], "away_club_id": away["id"]})


def play_ok(client, home, away):
    response = play(client, home, away)
    assert response.status_code == 201
    return response.json()


def duel_json(
    order,
    club,
    attacker,
    attribute,
    value,
    defender,
    defender_value,
    goal,
    attacker_condition="APTO",
    defender_condition="APTO",
):
    return {
        "order": order,
        "attacking_club_id": club["id"],
        "attacker": {
            "player_id": attacker["id"],
            "player_name": attacker["name"],
            "position": attacker["position"],
            "condition": attacker_condition,
            "attribute": attribute,
            "value": value,
        },
        "defender": {
            "player_id": defender["id"],
            "player_name": defender["name"],
            "position": defender["position"],
            "condition": defender_condition,
            "attribute": "defending",
            "value": defender_value,
        },
        "goal": goal,
    }


@pytest.fixture
def statement_clubs(client, clock):
    eagles, eagles_players = build_club(client, clock, "Águias FC", "AGU", EAGLES)
    change_condition(client, eagles_players["Davi Lins"], "MAL_CONDICIONADO")
    delta, delta_players = build_club(client, clock, "Delta FC", "DFC", DELTA)
    return eagles, eagles_players, delta, delta_players


def test_play_match_follows_the_example_of_the_statement(client, statement_clubs):
    eagles, e, delta, d = statement_clubs

    response = play(client, eagles, delta)

    assert response.status_code == 201
    body = response.json()
    mal = "MAL_CONDICIONADO"
    assert body == {
        "id": body["id"],
        "played_at": "2026-11-02T10:15:00-03:00",
        "home": {
            "club_id": eagles["id"],
            "club_name": "Águias FC",
            "formation": "2-1-1",
            "goals": 1,
        },
        "away": {"club_id": delta["id"], "club_name": "Delta FC", "formation": "2-1-1", "goals": 2},
        "result": "VISITANTE",
        "duels": [
            duel_json(1, eagles, e["Otto Rangel"], "shooting", 75, d["Ivo Teles"], 72, True),
            duel_json(2, eagles, e["Lauro Neves"], "passing", 82, d["Hugo Vaz"], 84, False),
            duel_json(
                3,
                eagles,
                e["Davi Lins"],
                "dribbling",
                63,
                d["Lino Matos"],
                63,
                False,
                attacker_condition=mal,
            ),
            duel_json(4, delta, d["Ugo Falcão"], "shooting", 81, e["Rui Prado"], 77, True),
            duel_json(5, delta, d["Nei Soares"], "passing", 70, e["Téo Brandão"], 84, False),
            duel_json(
                6,
                delta,
                d["Lino Matos"],
                "dribbling",
                79,
                e["Davi Lins"],
                56,
                True,
                defender_condition=mal,
            ),
        ],
    }


def test_play_match_answers_with_the_location_of_the_new_match(client, statement_clubs):
    eagles, _, delta, _ = statement_clubs

    response = play(client, eagles, delta)

    assert response.headers["location"] == f"{MATCHES_URL}/{response.json()['id']}"


def test_get_match_returns_the_same_match_with_the_six_duels(client, statement_clubs):
    eagles, _, delta, _ = statement_clubs
    played = play_ok(client, eagles, delta)

    response = client.get(f"{MATCHES_URL}/{played['id']}")

    assert response.status_code == 200
    assert response.json() == played
    assert [duel["order"] for duel in response.json()["duels"]] == [1, 2, 3, 4, 5, 6]


def test_the_same_confrontation_can_be_played_again_with_the_same_score(client, statement_clubs):
    eagles, _, delta, _ = statement_clubs

    first = play_ok(client, eagles, delta)
    second = play_ok(client, eagles, delta)

    assert second["id"] > first["id"]
    assert second["duels"] == first["duels"]
    assert (second["home"]["goals"], second["away"]["goals"]) == (1, 2)


def test_the_result_is_home_away_or_draw_by_the_goals(client, clock):
    alpha, _ = build_power_club(client, clock, "Alfa FC", "AFC", "Alfa", STRONG)
    gama, _ = build_power_club(client, clock, "Gama FC", "GFC", "Gama", WEAK)
    delta, _ = build_power_club(client, clock, "Delta FC", "DFC", "Delta", WEAK)

    home_wins = play_ok(client, alpha, gama)
    away_wins = play_ok(client, gama, alpha)
    draw = play_ok(client, gama, delta)

    assert (home_wins["result"], home_wins["home"]["goals"], home_wins["away"]["goals"]) == (
        "MANDANTE",
        3,
        0,
    )
    assert (away_wins["result"], away_wins["home"]["goals"], away_wins["away"]["goals"]) == (
        "VISITANTE",
        0,
        3,
    )
    assert (draw["result"], draw["home"]["goals"], draw["away"]["goals"]) == ("EMPATE", 0, 0)


def test_play_match_does_not_change_the_cash_the_lineups_or_the_players(client, statement_clubs):
    eagles, e, delta, _ = statement_clubs

    def snapshot():
        return (
            client.get(f"{CLUBS_URL}/{eagles['id']}").json(),
            client.get(f"{CLUBS_URL}/{delta['id']}").json(),
            client.get(f"{CLUBS_URL}/{eagles['id']}/lineup").json(),
            client.get(f"{PLAYERS_URL}/{e['Davi Lins']['id']}").json(),
        )

    before = snapshot()
    play_ok(client, eagles, delta)

    assert snapshot() == before


def test_a_played_match_keeps_the_names_and_values_of_the_moment(client, statement_clubs):
    eagles, e, delta, _ = statement_clubs
    played = play_ok(client, eagles, delta)
    renamed = {"name": "Otto Rangel Jr", "position": "ATA", "agility": 50, "age": 26}
    assert client.put(f"{PLAYERS_URL}/{e['Otto Rangel']['id']}", json=renamed).status_code == 200
    change_condition(client, e["Davi Lins"], "APTO")
    sell_ok(client, e["Lauro Neves"])

    assert client.get(f"{MATCHES_URL}/{played['id']}").json() == played


def test_list_matches_returns_the_most_recent_first_without_the_duels(client, clock):
    alpha, _ = build_power_club(client, clock, "Alfa FC", "AFC", "Alfa", STRONG)
    beta, _ = build_power_club(client, clock, "Beta FC", "BFC", "Beta", MIDDLE)
    gama, _ = build_power_club(client, clock, "Gama FC", "GFC", "Gama", WEAK)
    first = play_ok(client, alpha, beta)
    clock.moment += timedelta(days=1)
    second = play_ok(client, beta, gama)
    third = play_ok(client, gama, alpha)

    response = client.get(MATCHES_URL)

    assert response.status_code == 200
    body = response.json()
    assert [match["id"] for match in body] == [third["id"], second["id"], first["id"]]
    assert all("duels" not in match for match in body)
    assert body[0] == {key: value for key, value in third.items() if key != "duels"}


def test_list_matches_filters_by_a_club_that_was_home_or_away(client, clock):
    alpha, _ = build_power_club(client, clock, "Alfa FC", "AFC", "Alfa", STRONG)
    beta, _ = build_power_club(client, clock, "Beta FC", "BFC", "Beta", MIDDLE)
    gama, _ = build_power_club(client, clock, "Gama FC", "GFC", "Gama", WEAK)
    first = play_ok(client, alpha, beta)
    clock.moment += timedelta(days=1)
    second = play_ok(client, beta, gama)

    def ids_for(club):
        return [match["id"] for match in client.get(f"{MATCHES_URL}?club_id={club['id']}").json()]

    assert ids_for(alpha) == [first["id"]]
    assert ids_for(beta) == [second["id"], first["id"]]
    assert ids_for(gama) == [second["id"]]


def test_list_matches_is_empty_without_matches_and_for_a_club_that_never_played(client, clock):
    alpha, _ = build_power_club(client, clock, "Alfa FC", "AFC", "Alfa", STRONG)

    assert client.get(MATCHES_URL).json() == []
    assert client.get(f"{MATCHES_URL}?club_id={alpha['id']}").json() == []


@pytest.mark.parametrize(
    "query",
    ["club_id=", "club_id=0", "club_id=01", "club_id=-1", "club_id=+1", "club_id=1.5"]
    + ["club_id=1e2", "club_id=abc", "club_id=%201", "club_id=2147483648"],
)
def test_list_matches_rejects_an_invalid_club_id_with_400(client, query):
    response = client.get(f"{MATCHES_URL}?{query}")

    assert response.status_code == 400
    assert response.json()["message"]
    assert response.headers["content-type"].startswith("application/json")


def test_list_matches_returns_404_for_an_unknown_club(client):
    response = client.get(f"{MATCHES_URL}?club_id=999999")

    assert response.status_code == 404
    assert response.json()["message"]


def test_list_matches_ignores_unknown_parameters(client):
    assert client.get(f"{MATCHES_URL}?foo=bar").status_code == 200


@pytest.mark.parametrize("match_id", ["999999", "01", "0", "abc", "-1", "1.5", "2147483648"])
def test_get_match_returns_404_for_an_unknown_or_malformed_id(client, match_id):
    response = client.get(f"{MATCHES_URL}/{match_id}")

    assert response.status_code == 404
    assert response.json()["message"]


BAD_BODIES = {
    "home_missing": lambda home, away: {"away_club_id": away},
    "away_missing": lambda home, away: {"home_club_id": home},
    "home_null": lambda home, away: {"home_club_id": None, "away_club_id": away},
    "away_null": lambda home, away: {"home_club_id": home, "away_club_id": None},
    "home_zero": lambda home, away: {"home_club_id": 0, "away_club_id": away},
    "away_negative": lambda home, away: {"home_club_id": home, "away_club_id": -1},
    "home_text": lambda home, away: {"home_club_id": str(home), "away_club_id": away},
    "away_fraction": lambda home, away: {"home_club_id": home, "away_club_id": 1.5},
    "home_boolean": lambda home, away: {"home_club_id": True, "away_club_id": away},
    "away_above_int32": lambda home, away: {"home_club_id": home, "away_club_id": 2147483648},
    "home_list": lambda home, away: {"home_club_id": [home], "away_club_id": away},
    "same_club": lambda home, away: {"home_club_id": home, "away_club_id": home},
    "empty_object": lambda home, away: {},
}


@pytest.mark.parametrize("make_body", BAD_BODIES.values(), ids=BAD_BODIES.keys())
def test_play_match_rejects_a_bad_body_with_400_and_saves_nothing(client, clock, make_body):
    alpha, _ = build_power_club(client, clock, "Alfa FC", "AFC", "Alfa", STRONG)
    beta, _ = build_power_club(client, clock, "Beta FC", "BFC", "Beta", MIDDLE)

    response = client.post(MATCHES_URL, json=make_body(alpha["id"], beta["id"]))

    assert response.status_code == 400
    assert response.json()["message"]
    assert response.headers["content-type"].startswith("application/json")
    assert client.get(MATCHES_URL).json() == []


@pytest.mark.parametrize("raw_body", [b"[]", b'"text"', b"null", b"not json", b""])
def test_play_match_rejects_a_body_that_is_not_an_object_with_400(client, raw_body):
    response = client.post(
        MATCHES_URL, content=raw_body, headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400
    assert response.json()["message"]


@pytest.mark.parametrize("unknown_side", ["home", "away"])
def test_play_match_returns_404_for_an_unknown_club_and_saves_nothing(client, clock, unknown_side):
    alpha, _ = build_power_club(client, clock, "Alfa FC", "AFC", "Alfa", STRONG)
    known, unknown = alpha["id"], 999999
    body = {
        "home_club_id": unknown if unknown_side == "home" else known,
        "away_club_id": unknown if unknown_side == "away" else known,
    }

    response = client.post(MATCHES_URL, json=body)

    assert response.status_code == 404
    assert response.json()["message"]
    assert client.get(MATCHES_URL).json() == []


@pytest.mark.parametrize("home_first", [True, False])
def test_play_match_returns_409_for_a_club_that_never_made_a_lineup(client, clock, home_first):
    alpha, _ = build_power_club(client, clock, "Alfa FC", "AFC", "Alfa", STRONG)
    empty = create_club(client, "Vazio FC", "VFC")
    home, away = (alpha, empty) if home_first else (empty, alpha)

    response = play(client, home, away)

    assert response.status_code == 409
    assert response.json()["message"]
    assert client.get(MATCHES_URL).json() == []


@pytest.mark.parametrize("home_first", [True, False])
def test_play_match_returns_409_for_a_club_that_sold_a_starter(client, clock, home_first):
    alpha, alpha_players = build_power_club(client, clock, "Alfa FC", "AFC", "Alfa", STRONG)
    beta, _ = build_power_club(client, clock, "Beta FC", "BFC", "Beta", MIDDLE)
    sell_ok(client, alpha_players["Atacante Alfa"])
    home, away = (alpha, beta) if home_first else (beta, alpha)

    response = play(client, home, away)

    assert response.status_code == 409
    assert client.get(MATCHES_URL).json() == []


@pytest.mark.parametrize("home_first", [True, False])
def test_play_match_returns_409_for_a_club_with_a_sick_starter(client, clock, home_first):
    alpha, alpha_players = build_power_club(client, clock, "Alfa FC", "AFC", "Alfa", STRONG)
    beta, _ = build_power_club(client, clock, "Beta FC", "BFC", "Beta", MIDDLE)
    change_condition(client, alpha_players["Meia Alfa"], "DOENTE")
    home, away = (alpha, beta) if home_first else (beta, alpha)

    response = play(client, home, away)

    assert response.status_code == 409
    assert client.get(MATCHES_URL).json() == []


def test_a_club_can_play_again_after_completing_the_lineup(client, clock):
    alpha, alpha_players = build_power_club(client, clock, "Alfa FC", "AFC", "Alfa", STRONG)
    beta, _ = build_power_club(client, clock, "Beta FC", "BFC", "Beta", MIDDLE)
    sell_ok(client, alpha_players["Atacante Alfa"])
    assert play(client, alpha, beta).status_code == 409
    replacement = create_player(client, "Reserva Alfa", "ATA", **dict.fromkeys(ATTRIBUTES, STRONG))
    buy_ok(client, replacement, alpha, clock)
    starters = [alpha_players[name] for name in alpha_players if name != "Atacante Alfa"]
    set_lineup_ok(client, alpha, [*starters, replacement])

    response = play(client, alpha, beta)

    assert response.status_code == 201
