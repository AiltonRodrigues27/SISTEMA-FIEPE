from datetime import timedelta

import pytest

PLAYERS_URL = "/api/v1/players"
CLUBS_URL = "/api/v1/clubs"

CHEAP = {
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
SQUAD = (
    ("Rui Prado", "GOL"),
    ("Teo Brandao", "ZAG"),
    ("Davi Lins", "LAT"),
    ("Lauro Neves", "MEI"),
    ("Otto Rangel", "ATA"),
    ("Ugo Falcao", "ATA"),
    ("Ivo Teles", "GOL"),
)
STARTERS_2_1_1 = ("Otto Rangel", "Davi Lins", "Rui Prado", "Lauro Neves", "Teo Brandao")
STARTERS_IN_SQUAD_ORDER = ["Rui Prado", "Teo Brandao", "Davi Lins", "Lauro Neves", "Otto Rangel"]
STARTERS_2_2 = ("Rui Prado", "Teo Brandao", "Davi Lins", "Otto Rangel", "Ugo Falcao")
EMPTY_LINEUP = {"formation": None, "complete": False, "players": []}


def create_cheap_player(client, name, position):
    response = client.post(PLAYERS_URL, json={**CHEAP, "name": name, "position": position})
    assert response.status_code == 201
    return response.json()


def create_club(client, name="Águias FC", acronym="AGU"):
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


def sell_ok(client, player):
    response = client.post(f"{PLAYERS_URL}/{player['id']}/sell")
    assert response.status_code == 200


def change_condition(client, player, condition):
    response = client.patch(
        f"{PLAYERS_URL}/{player['id']}/condition", json={"condition": condition}
    )
    assert response.status_code == 200


def build_squad(client, clock, club, members=SQUAD):
    squad = {}
    for name, position in members:
        player = create_cheap_player(client, name, position)
        buy_ok(client, player, club, clock)
        squad[name] = player
    return squad


def ids_of(squad, names):
    return [squad[name]["id"] for name in names]


def lineup_url(club):
    return f"{CLUBS_URL}/{club['id']}/lineup"


def put_lineup(client, club, formation, player_ids):
    return client.put(lineup_url(club), json={"formation": formation, "player_ids": player_ids})


def put_lineup_ok(client, club, formation, player_ids):
    response = put_lineup(client, club, formation, player_ids)
    assert response.status_code == 200
    return response.json()


def get_lineup(client, club):
    return client.get(lineup_url(club)).json()


def names_of(lineup):
    return [player["name"] for player in lineup["players"]]


def test_put_lineup_follows_the_example_of_the_statement(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    change_condition(client, squad["Davi Lins"], "MAL_CONDICIONADO")

    response = put_lineup(client, club, "2-1-1", ids_of(squad, STARTERS_2_1_1))

    assert response.status_code == 200
    body = response.json()
    assert (body["club_id"], body["formation"], body["complete"]) == (club["id"], "2-1-1", True)
    assert names_of(body) == STARTERS_IN_SQUAD_ORDER
    assert [player["position"] for player in body["players"]] == ["GOL", "ZAG", "LAT", "MEI", "ATA"]
    davi = body["players"][2]
    assert (davi["condition"], davi["club_id"]) == ("MAL_CONDICIONADO", club["id"])
    assert {"id", "base_value", "market_value", "overall", "dribbling", "defending"} <= set(davi)


def test_get_lineup_returns_what_was_saved(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    saved = put_lineup_ok(client, club, "2-1-1", ids_of(squad, STARTERS_2_1_1))

    response = client.get(lineup_url(club))

    assert response.status_code == 200
    assert response.json() == saved


def test_get_lineup_of_a_club_without_lineup_is_empty(client):
    club = create_club(client)

    response = client.get(lineup_url(club))

    assert response.status_code == 200
    assert response.json() == {"club_id": club["id"], **EMPTY_LINEUP}


def test_put_lineup_replaces_the_whole_lineup(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    put_lineup_ok(client, club, "2-1-1", ids_of(squad, STARTERS_2_1_1))

    body = put_lineup_ok(client, club, "2-2", ids_of(squad, STARTERS_2_2))

    assert body["formation"] == "2-2"
    assert names_of(body) == list(STARTERS_2_2)
    assert get_lineup(client, club) == body


def test_put_lineup_accepts_the_same_players_again(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    first = put_lineup_ok(client, club, "2-1-1", ids_of(squad, STARTERS_2_1_1))

    second = put_lineup_ok(client, club, "2-1-1", list(reversed(ids_of(squad, STARTERS_2_1_1))))

    assert second == first


@pytest.mark.parametrize(
    ("formation", "starters"),
    [
        pytest.param("2-2", STARTERS_2_2, id="2-2"),
        pytest.param("2-1-1", STARTERS_2_1_1, id="2-1-1"),
    ],
)
def test_put_lineup_accepts_the_formations_that_the_positions_fill(
    client, clock, formation, starters
):
    club = create_club(client)
    squad = build_squad(client, clock, club)

    body = put_lineup_ok(client, club, formation, ids_of(squad, starters))

    assert (body["formation"], body["complete"]) == (formation, True)


def test_put_lineup_does_not_change_the_cash_and_ignores_unknown_fields(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    cash_before = client.get(f"{CLUBS_URL}/{club['id']}").json()["cash"]

    response = client.put(
        lineup_url(club),
        json={
            "formation": "2-1-1",
            "player_ids": ids_of(squad, STARTERS_2_1_1),
            "cash": 999,
            "complete": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["complete"] is True
    assert client.get(f"{CLUBS_URL}/{club['id']}").json()["cash"] == cash_before == 293.0


BAD_BODIES = {
    "formation_missing": lambda ids: {"player_ids": ids},
    "formation_null": lambda ids: {"formation": None, "player_ids": ids},
    "formation_unknown": lambda ids: {"formation": "4-4-2", "player_ids": ids},
    "formation_with_space": lambda ids: {"formation": "2-1-1 ", "player_ids": ids},
    "formation_text": lambda ids: {"formation": "dois-um-um", "player_ids": ids},
    "formation_number": lambda ids: {"formation": 211, "player_ids": ids},
    "formation_empty": lambda ids: {"formation": "", "player_ids": ids},
    "player_ids_missing": lambda ids: {"formation": "2-1-1"},
    "player_ids_null": lambda ids: {"formation": "2-1-1", "player_ids": None},
    "player_ids_text": lambda ids: {"formation": "2-1-1", "player_ids": "abc"},
    "player_ids_object": lambda ids: {"formation": "2-1-1", "player_ids": {"0": ids[0]}},
    "player_ids_empty": lambda ids: {"formation": "2-1-1", "player_ids": []},
    "four_ids": lambda ids: {"formation": "2-1-1", "player_ids": ids[:4]},
    "six_ids": lambda ids: {"formation": "2-1-1", "player_ids": ids + [ids[0] + 100]},
    "repeated_ids": lambda ids: {"formation": "2-1-1", "player_ids": [ids[0]] * 5},
    "zero_id": lambda ids: {"formation": "2-1-1", "player_ids": ids[:4] + [0]},
    "negative_id": lambda ids: {"formation": "2-1-1", "player_ids": ids[:4] + [-1]},
    "text_id": lambda ids: {"formation": "2-1-1", "player_ids": ids[:4] + ["1"]},
    "fractional_id": lambda ids: {"formation": "2-1-1", "player_ids": ids[:4] + [1.5]},
    "boolean_id": lambda ids: {"formation": "2-1-1", "player_ids": ids[:4] + [True]},
    "null_id": lambda ids: {"formation": "2-1-1", "player_ids": ids[:4] + [None]},
    "id_above_int32": lambda ids: {"formation": "2-1-1", "player_ids": ids[:4] + [2147483648]},
}


@pytest.mark.parametrize("make_body", BAD_BODIES.values(), ids=BAD_BODIES.keys())
def test_put_lineup_rejects_a_malformed_body_with_400_and_saves_nothing(client, clock, make_body):
    club = create_club(client)
    squad = build_squad(client, clock, club)

    response = client.put(lineup_url(club), json=make_body(ids_of(squad, STARTERS_2_1_1)))

    assert response.status_code == 400
    assert response.json()["message"]
    assert response.headers["content-type"].startswith("application/json")
    assert get_lineup(client, club) == {"club_id": club["id"], **EMPTY_LINEUP}


@pytest.mark.parametrize("raw_body", [b"[]", b'"text"', b"null", b"not json", b""])
def test_put_lineup_rejects_a_body_that_is_not_an_object_with_400(client, raw_body):
    club = create_club(client)

    response = client.put(
        lineup_url(club), content=raw_body, headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400
    assert response.json()["message"]


def test_put_lineup_returns_404_for_an_unknown_club(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)

    response = client.put(
        f"{CLUBS_URL}/999999/lineup",
        json={"formation": "2-1-1", "player_ids": ids_of(squad, STARTERS_2_1_1)},
    )

    assert response.status_code == 404
    assert response.json()["message"]


def test_put_lineup_returns_404_for_an_unknown_player_and_saves_nothing(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    player_ids = ids_of(squad, STARTERS_2_1_1)[:4] + [999999]

    response = put_lineup(client, club, "2-1-1", player_ids)

    assert response.status_code == 404
    assert get_lineup(client, club) == {"club_id": club["id"], **EMPTY_LINEUP}


def test_put_lineup_returns_404_for_a_deleted_player(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    deleted = create_cheap_player(client, "Zeca Lima", "ATA")
    assert client.delete(f"{PLAYERS_URL}/{deleted['id']}").status_code == 204

    response = put_lineup(
        client, club, "2-1-1", ids_of(squad, STARTERS_2_1_1)[:4] + [deleted["id"]]
    )

    assert response.status_code == 404


@pytest.mark.parametrize("club_id", ["01", "0", "abc", "-1", "1.5", "2147483648"])
def test_lineup_routes_treat_a_malformed_club_id_as_not_found(client, club_id):
    body = {"formation": "2-1-1", "player_ids": [1, 2, 3, 4, 5]}

    assert client.put(f"{CLUBS_URL}/{club_id}/lineup", json=body).status_code == 404
    assert client.get(f"{CLUBS_URL}/{club_id}/lineup").status_code == 404


def test_get_lineup_returns_404_for_an_unknown_club(client):
    response = client.get(f"{CLUBS_URL}/999999/lineup")

    assert response.status_code == 404
    assert response.json()["message"]


def refused_lineups(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    delta = create_club(client, "Delta FC", "DFC")
    foreigner = build_squad(client, clock, delta, (("Hugo Vaz", "ATA"),))["Hugo Vaz"]
    free_player = create_cheap_player(client, "Nei Soares", "ATA")
    change_condition(client, squad["Ugo Falcao"], "DOENTE")
    starters = ids_of(squad, STARTERS_2_1_1)
    four = starters[:4]
    return (
        club,
        squad,
        {
            "player_from_another_club": ("2-1-1", four + [foreigner["id"]]),
            "free_player": ("2-1-1", four + [free_player["id"]]),
            "sick_player": ("2-1-1", four + [squad["Ugo Falcao"]["id"]]),
            "positions_for_another_formation": ("3-1", starters),
            "midfielder_in_2_2": ("2-2", starters),
            "two_goalkeepers": (
                "2-2",
                ids_of(
                    squad, ("Rui Prado", "Ivo Teles", "Teo Brandao", "Davi Lins", "Otto Rangel")
                ),
            ),
        },
    )


REFUSED_CASES = [
    "player_from_another_club",
    "free_player",
    "sick_player",
    "positions_for_another_formation",
    "midfielder_in_2_2",
    "two_goalkeepers",
]


@pytest.mark.parametrize("case", REFUSED_CASES)
def test_put_lineup_rejects_a_rule_violation_with_409_and_keeps_the_lineup(client, clock, case):
    club, squad, refused = refused_lineups(client, clock)
    saved = put_lineup_ok(client, club, "2-1-1", ids_of(squad, STARTERS_2_1_1))
    formation, player_ids = refused[case]

    response = put_lineup(client, club, formation, player_ids)

    assert response.status_code == 409
    assert response.json()["message"]
    assert get_lineup(client, club) == saved


def test_put_lineup_rejects_a_rule_violation_without_a_previous_lineup(client, clock):
    club, _, refused = refused_lineups(client, clock)
    formation, player_ids = refused["positions_for_another_formation"]

    response = put_lineup(client, club, formation, player_ids)

    assert response.status_code == 409
    assert get_lineup(client, club) == {"club_id": club["id"], **EMPTY_LINEUP}


def test_selling_a_starter_takes_him_out_and_keeps_the_formation(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    put_lineup_ok(client, club, "2-1-1", ids_of(squad, STARTERS_2_1_1))

    sell_ok(client, squad["Otto Rangel"])

    body = get_lineup(client, club)
    assert (body["formation"], body["complete"]) == ("2-1-1", False)
    assert names_of(body) == ["Rui Prado", "Teo Brandao", "Davi Lins", "Lauro Neves"]


def test_selling_a_player_on_the_bench_keeps_the_lineup_complete(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    put_lineup_ok(client, club, "2-1-1", ids_of(squad, STARTERS_2_1_1))

    sell_ok(client, squad["Ugo Falcao"])

    body = get_lineup(client, club)
    assert body["complete"] is True
    assert names_of(body) == STARTERS_IN_SQUAD_ORDER


def test_a_starter_who_becomes_sick_leaves_the_lineup(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    put_lineup_ok(client, club, "2-1-1", ids_of(squad, STARTERS_2_1_1))

    change_condition(client, squad["Lauro Neves"], "DOENTE")

    body = get_lineup(client, club)
    assert (body["formation"], body["complete"]) == ("2-1-1", False)
    assert names_of(body) == ["Rui Prado", "Teo Brandao", "Davi Lins", "Otto Rangel"]


def test_a_starter_who_recovers_does_not_come_back_by_himself(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    put_lineup_ok(client, club, "2-1-1", ids_of(squad, STARTERS_2_1_1))
    change_condition(client, squad["Lauro Neves"], "DOENTE")

    change_condition(client, squad["Lauro Neves"], "MAL_CONDICIONADO")

    body = get_lineup(client, club)
    assert body["complete"] is False
    assert "Lauro Neves" not in names_of(body)


def test_a_starter_who_gets_mal_condicionado_stays_in_the_lineup(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    put_lineup_ok(client, club, "2-1-1", ids_of(squad, STARTERS_2_1_1))

    change_condition(client, squad["Davi Lins"], "MAL_CONDICIONADO")

    body = get_lineup(client, club)
    assert body["complete"] is True
    assert body["players"][2]["condition"] == "MAL_CONDICIONADO"


def test_the_club_can_complete_the_lineup_again_after_losing_a_starter(client, clock):
    club = create_club(client)
    squad = build_squad(client, clock, club)
    put_lineup_ok(client, club, "2-1-1", ids_of(squad, STARTERS_2_1_1))
    sell_ok(client, squad["Otto Rangel"])
    replacement = ("Rui Prado", "Teo Brandao", "Davi Lins", "Lauro Neves", "Ugo Falcao")

    body = put_lineup_ok(client, club, "2-1-1", ids_of(squad, replacement))

    assert (body["formation"], body["complete"]) == ("2-1-1", True)
    assert "Ugo Falcao" in names_of(body)


def test_a_sold_starter_can_be_lined_up_by_the_club_that_buys_him(client, clock):
    eagles = create_club(client)
    squad = build_squad(client, clock, eagles)
    put_lineup_ok(client, eagles, "2-1-1", ids_of(squad, STARTERS_2_1_1))
    sell_ok(client, squad["Otto Rangel"])
    delta = create_club(client, "Delta FC", "DFC")
    delta_squad = build_squad(
        client,
        clock,
        delta,
        (("Hugo Vaz", "GOL"), ("Ivo Souza", "ZAG"), ("Lino Matos", "LAT"), ("Nei Soares", "MEI")),
    )
    buy_ok(client, squad["Otto Rangel"], delta, clock)
    delta_starters = [player["id"] for player in delta_squad.values()] + [
        squad["Otto Rangel"]["id"]
    ]

    body = put_lineup_ok(client, delta, "2-1-1", delta_starters)

    assert body["complete"] is True
    assert "Otto Rangel" in names_of(body)
    assert "Otto Rangel" not in names_of(get_lineup(client, eagles))
