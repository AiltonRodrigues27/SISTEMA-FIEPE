import string

import pytest

PLAYERS_URL = "/api/v1/players"

BASE_BODY = {
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

INVALID_QUERIES = [
    "search=",
    "search=a",
    "search=Meia%09Lua",
    "position=mei",
    "position=",
    "condition=doente",
    "free=TRUE",
    "free=1",
    "club_id=0",
    "club_id=01",
    "min_age=15",
    "max_age=46",
    "min_age=30&max_age=20",
    "min_value=1e2",
    "min_value=551",
    "min_value=60&max_value=50",
    "sort=POSITION",
    "sort=value_asc,value_desc",
    "sort=name,age_asc,position",
    "page=0",
    "page=01",
    "limit=51",
    "limit=0",
    "limit=abc",
    "free=true&club_id=1",
]


def create(client, name, **changes):
    response = client.post(PLAYERS_URL, json={**BASE_BODY, "name": name, **changes})
    assert response.status_code == 201
    return response.json()


def list_players(client, query=""):
    response = client.get(f"{PLAYERS_URL}{query}")
    assert response.status_code == 200
    return response.json()


def names_of(client, query=""):
    return [player["name"] for player in list_players(client, query)["data"]]


def change_condition(client, player, condition):
    response = client.patch(
        f"{PLAYERS_URL}/{player['id']}/condition", json={"condition": condition}
    )
    assert response.status_code == 200


def test_list_returns_the_players_with_the_same_fields_as_get_and_the_meta(client):
    ana = create(client, "Ana Lima")
    beto = create(client, "Beto Souza")

    body = list_players(client)

    assert body["data"] == [ana, beto]
    assert body["meta"] == {"page": 1, "limit": 10, "total_items": 2, "total_pages": 1}


def test_list_without_players_is_empty_with_zero_pages(client):
    body = list_players(client)

    assert body == {
        "data": [],
        "meta": {"page": 1, "limit": 10, "total_items": 0, "total_pages": 0},
    }


def test_list_orders_by_name_ignoring_case_and_accents_by_default(client):
    for name in ["Zé Foguete", "Ana Lima", "Éder Gama", "beto Souza"]:
        create(client, name)

    assert names_of(client) == ["Ana Lima", "beto Souza", "Éder Gama", "Zé Foguete"]


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        pytest.param("?search=joao", ["João Silva"], id="accent_and_case"),
        pytest.param("?search=LUA", ["Meia Lua"], id="uppercase"),
        pytest.param("?search=ima", ["Ana Lima"], id="inside_the_name"),
        pytest.param("?search=%20%20ana%20%20lima", ["Ana Lima"], id="spaces_are_collapsed"),
        pytest.param("?search=zzz", [], id="nothing_found"),
    ],
)
def test_list_search_ignores_case_and_accents(client, query, expected):
    for name in ["João Silva", "Meia Lua", "Ana Lima"]:
        create(client, name)

    assert names_of(client, query) == expected


def test_list_search_with_no_match_has_zero_pages(client):
    create(client, "Ana Lima")

    body = list_players(client, "?search=zzz")

    assert body["meta"] == {"page": 1, "limit": 10, "total_items": 0, "total_pages": 0}


def test_list_filters_by_position_and_condition(client):
    create(client, "Ana Lima", position="ATA")
    beto = create(client, "Beto Souza", position="MEI")
    change_condition(client, beto, "DOENTE")

    assert names_of(client, "?position=ATA") == ["Ana Lima"]
    assert names_of(client, "?condition=DOENTE") == ["Beto Souza"]
    assert names_of(client, "?position=ATA&condition=DOENTE") == []


def test_list_filters_by_age_range_inclusive(client):
    create(client, "Ana Lima", age=30)
    create(client, "Beto Souza", age=20)
    create(client, "Caio Dias", age=25)

    assert names_of(client, "?min_age=25") == ["Ana Lima", "Caio Dias"]
    assert names_of(client, "?max_age=25") == ["Beto Souza", "Caio Dias"]
    assert names_of(client, "?min_age=25&max_age=25") == ["Caio Dias"]


def test_list_filters_free_and_club(client):
    create(client, "Ana Lima")
    club = client.post("/api/v1/clubs", json={"name": "Águias FC", "acronym": "AGU"}).json()

    assert names_of(client, "?free=true") == ["Ana Lima"]
    assert names_of(client, "?free=false") == []
    assert names_of(client, f"?club_id={club['id']}") == []
    assert names_of(client, f"?free=false&club_id={club['id']}") == []


def test_list_returns_404_for_a_club_that_does_not_exist(client):
    response = client.get(f"{PLAYERS_URL}?club_id=999")

    assert response.status_code == 404
    assert response.json() == {"message": "Clube não encontrado."}


def test_list_filters_and_sorts_by_market_value_not_base_value(client):
    create(client, "Ana Lima")
    beto = create(client, "Beto Souza")
    caio = create(client, "Caio Dias")
    change_condition(client, beto, "MAL_CONDICIONADO")
    change_condition(client, caio, "DOENTE")

    assert names_of(client, "?min_value=37") == ["Ana Lima", "Beto Souza"]
    assert names_of(client, "?max_value=37") == ["Beto Souza", "Caio Dias"]
    assert names_of(client, "?min_value=34&max_value=37") == ["Beto Souza", "Caio Dias"]
    assert names_of(client, "?min_value=40.01") == []
    assert names_of(client, "?sort=value_asc") == ["Caio Dias", "Beto Souza", "Ana Lima"]
    assert names_of(client, "?sort=value_desc") == ["Ana Lima", "Beto Souza", "Caio Dias"]


def test_list_sorts_by_age_and_by_position(client):
    create(client, "Ata Lima", position="ATA", age=30)
    create(client, "Mei Lima", position="MEI", age=20)
    create(client, "Gol Lima", position="GOL", age=25)
    create(client, "Zag Lima", position="ZAG", age=35, potential=82)
    create(client, "Lat Lima", position="LAT", age=22)

    assert names_of(client, "?sort=position") == [
        "Gol Lima",
        "Zag Lima",
        "Lat Lima",
        "Mei Lima",
        "Ata Lima",
    ]
    assert names_of(client, "?sort=age_asc")[0] == "Mei Lima"
    assert names_of(client, "?sort=age_desc")[0] == "Zag Lima"


def test_list_second_sort_criterion_breaks_ties_of_the_first(client):
    create(client, "Ana Lima", position="MEI")
    beto = create(client, "Beto Souza", position="MEI")
    create(client, "Caio Dias", position="GOL")
    change_condition(client, beto, "MAL_CONDICIONADO")

    assert names_of(client, "?sort=position,value_desc") == ["Caio Dias", "Ana Lima", "Beto Souza"]
    assert names_of(client, "?sort=position,value_asc") == ["Caio Dias", "Beto Souza", "Ana Lima"]


@pytest.mark.parametrize(
    ("query", "expected_items", "expected_pages"),
    [
        pytest.param("?limit=10&page=1", 10, 3, id="first_page"),
        pytest.param("?limit=10&page=3", 3, 3, id="last_page_is_partial"),
        pytest.param("?limit=10&page=4", 0, 3, id="page_after_the_last"),
        pytest.param("?limit=50", 23, 1, id="everything_in_one_page"),
        pytest.param("", 10, 3, id="defaults"),
    ],
)
def test_list_paginates_after_searching_with_the_meta_of_the_whole_search(
    client, query, expected_items, expected_pages
):
    for letter in string.ascii_uppercase[:23]:
        create(client, f"Jogador {letter}")

    body = list_players(client, query)

    assert len(body["data"]) == expected_items
    assert body["meta"]["total_items"] == 23
    assert body["meta"]["total_pages"] == expected_pages


def test_list_page_is_cut_after_ordering(client):
    for letter in reversed(string.ascii_uppercase[:23]):
        create(client, f"Jogador {letter}")

    body = list_players(client, "?limit=5&page=2")

    assert [player["name"] for player in body["data"]] == [
        "Jogador F",
        "Jogador G",
        "Jogador H",
        "Jogador I",
        "Jogador J",
    ]
    assert body["meta"] == {"page": 2, "limit": 5, "total_items": 23, "total_pages": 5}


def test_list_does_not_show_deleted_players(client):
    create(client, "Ana Lima")
    beto = create(client, "Beto Souza")
    client.delete(f"{PLAYERS_URL}/{beto['id']}")

    body = list_players(client)

    assert [player["name"] for player in body["data"]] == ["Ana Lima"]
    assert body["meta"]["total_items"] == 1


def test_list_ignores_unknown_parameters(client):
    create(client, "Ana Lima")

    assert names_of(client, "?foo=bar&Page=2") == ["Ana Lima"]


@pytest.mark.parametrize("query", INVALID_QUERIES)
def test_list_rejects_invalid_parameters_with_400_and_message(client, query):
    response = client.get(f"{PLAYERS_URL}?{query}")

    assert response.status_code == 400
    assert response.json()["message"]
