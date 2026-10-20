import pytest

CLUBS_URL = "/api/v1/clubs"

ACRONYM_SUFFIXES = "ABCDEFGHIJKLMNOPQRST"

INVALID_BODIES = [
    pytest.param({"name": "Águias", "acronym": "AGU"}, id="name_with_one_word"),
    pytest.param({"name": "Águias FC 1", "acronym": "AGU"}, id="name_with_digit"),
    pytest.param({"name": "Águias_FC", "acronym": "AGU"}, id="name_with_underscore"),
    pytest.param({"name": "A B C D E F", "acronym": "ABC"}, id="name_with_six_words"),
    pytest.param({"name": "A " + "b" * 59, "acronym": "ABB"}, id="name_with_sixty_one_characters"),
    pytest.param({"name": "Águias\tFC", "acronym": "AGU"}, id="name_with_tab"),
    pytest.param({"name": None, "acronym": "AGU"}, id="null_name"),
    pytest.param({"name": "Águias FC", "acronym": "agu"}, id="acronym_in_lowercase"),
    pytest.param({"name": "Águias FC", "acronym": "AG"}, id="acronym_with_two_letters"),
    pytest.param({"name": "Águias FC", "acronym": "AGUI"}, id="acronym_with_four_letters"),
    pytest.param({"name": "Águias FC", "acronym": "ÁGU"}, id="acronym_with_accent"),
    pytest.param({"name": "Águias FC", "acronym": None}, id="null_acronym"),
    pytest.param({"name": "Águias FC", "acronym": "XYZ"}, id="acronym_that_does_not_match"),
    pytest.param({"name": "Águias FC", "acronym": "AUG"}, id="acronym_letters_out_of_order"),
    pytest.param({"name": "Alfa Atletico", "acronym": "AAA"}, id="acronym_with_equal_letters"),
    pytest.param({"acronym": "AGU"}, id="missing_name"),
    pytest.param({"name": "Águias FC"}, id="missing_acronym"),
]


def create_club(client, name="Águias FC", acronym="AGU"):
    response = client.post(CLUBS_URL, json={"name": name, "acronym": acronym})
    assert response.status_code == 201
    return response.json()


def test_create_club_returns_201_with_location_and_initial_values(client):
    response = client.post(CLUBS_URL, json={"name": "Águias FC", "acronym": "AGU"})

    body = response.json()
    assert response.status_code == 201
    assert response.headers["location"] == f"{CLUBS_URL}/{body['id']}"
    assert body == {
        "id": body["id"],
        "name": "Águias FC",
        "acronym": "AGU",
        "cash": 300.0,
        "squad_value": 0.0,
        "net_worth": 300.0,
    }


def test_create_club_cleans_the_name(client):
    body = create_club(client, name="  Águias   FC ", acronym="AGU")

    assert body["name"] == "Águias FC"


def test_create_club_ignores_fields_controlled_by_the_system(client):
    response = client.post(
        CLUBS_URL,
        json={"name": "Águias FC", "acronym": "AGU", "id": 5, "cash": 999, "net_worth": 1},
    )

    assert response.status_code == 201
    assert response.json()["cash"] == 300.0
    assert response.json()["id"] != 5


@pytest.mark.parametrize("body", INVALID_BODIES)
def test_create_club_rejects_an_invalid_body_with_400_and_message(client, body):
    response = client.post(CLUBS_URL, json=body)

    assert response.status_code == 400
    assert response.json()["message"]


def test_create_club_rejects_a_body_that_is_not_an_object(client):
    response = client.post(CLUBS_URL, json=[])

    assert response.status_code == 400
    assert response.json()["message"]


@pytest.mark.parametrize("name", ["águias fc", "  ÁGUIAS   FC "])
def test_create_club_rejects_a_name_that_differs_only_by_case_or_spaces_with_409(client, name):
    create_club(client)

    response = client.post(CLUBS_URL, json={"name": name, "acronym": "AFC"})

    assert response.status_code == 409
    assert response.json() == {"message": "Já existe um clube com esse nome."}


def test_create_club_accepts_a_name_that_differs_by_accent(client):
    create_club(client, "Águias FC", "AGU")

    response = client.post(CLUBS_URL, json={"name": "Aguias FC", "acronym": "AFC"})

    assert response.status_code == 201


def test_create_club_rejects_a_repeated_acronym_with_409(client):
    create_club(client, "Águias FC", "AGU")

    response = client.post(CLUBS_URL, json={"name": "Aguias Futebol", "acronym": "AGU"})

    assert response.status_code == 409
    assert response.json() == {"message": "Já existe um clube com essa sigla."}


def test_create_club_rejects_the_twenty_first_club_with_409(client):
    for suffix in ACRONYM_SUFFIXES:
        create_club(client, f"Clube {suffix}", f"CL{suffix}")

    response = client.post(CLUBS_URL, json={"name": "Clube U", "acronym": "CLU"})

    assert response.status_code == 409
    assert response.json() == {"message": "A liga aceita no máximo 20 clubes."}


def test_list_clubs_without_clubs_is_an_empty_array(client):
    response = client.get(CLUBS_URL)

    assert response.status_code == 200
    assert response.json() == []


def test_list_clubs_returns_an_array_ordered_by_name_ignoring_accents(client):
    zebras = create_club(client, "Zebras FC", "ZFC")
    eagles = create_club(client, "Águias FC", "AGU")
    beta = create_club(client, "beta FC", "BFC")

    response = client.get(CLUBS_URL)

    assert response.status_code == 200
    assert response.json() == [eagles, beta, zebras]


@pytest.mark.parametrize("sort", ["name", "net_worth_asc", "net_worth_desc"])
def test_list_clubs_accepts_every_sort_value_and_breaks_ties_by_name(client, sort):
    create_club(client, "Zebras FC", "ZFC")
    create_club(client, "Águias FC", "AGU")

    response = client.get(f"{CLUBS_URL}?sort={sort}")

    assert response.status_code == 200
    assert [club["name"] for club in response.json()] == ["Águias FC", "Zebras FC"]


@pytest.mark.parametrize("query", ["sort=", "sort=NAME", "sort=price", "sort=name,net_worth_asc"])
def test_list_clubs_rejects_an_invalid_sort_with_400(client, query):
    response = client.get(f"{CLUBS_URL}?{query}")

    assert response.status_code == 400
    assert response.json()["message"]


def test_list_clubs_ignores_unknown_parameters(client):
    create_club(client)

    response = client.get(f"{CLUBS_URL}?foo=bar")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_club_returns_the_club_with_an_empty_squad(client):
    created = create_club(client)

    response = client.get(f"{CLUBS_URL}/{created['id']}")

    assert response.status_code == 200
    assert response.json() == {**created, "players": []}


def test_get_club_returns_404_with_message_for_unknown_id(client):
    response = client.get(f"{CLUBS_URL}/999999")

    assert response.status_code == 404
    assert response.json() == {"message": "Clube não encontrado."}


@pytest.mark.parametrize("club_id", ["01", "0", "abc", "-1", "1.5", "2147483648"])
def test_get_club_treats_a_malformed_id_as_not_found(client, club_id):
    create_club(client)

    response = client.get(f"{CLUBS_URL}/{club_id}")

    assert response.status_code == 404
    assert response.json()["message"]
