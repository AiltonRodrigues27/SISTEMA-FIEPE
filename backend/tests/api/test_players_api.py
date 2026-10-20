import pytest

PLAYERS_URL = "/api/v1/players"

VALID_BODY = {
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

INVALID_CHANGES = [
    pytest.param({"agility": "85"}, id="agility_as_text"),
    pytest.param({"age": 25.5}, id="age_with_fraction"),
    pytest.param({"position": "mei"}, id="position_in_lowercase"),
    pytest.param({"position": "XXX"}, id="unknown_position"),
    pytest.param({"name": "Pelé"}, id="name_with_one_word"),
    pytest.param({"name": "   "}, id="blank_name"),
    pytest.param({"name": "Meia 10"}, id="name_with_digit"),
    pytest.param({"name": "Meia\tLua"}, id="name_with_control_character"),
    pytest.param({"name": None}, id="null_name"),
    pytest.param({"age": 15}, id="age_below_minimum"),
    pytest.param({"age": 46}, id="age_above_maximum"),
    pytest.param({"agility": 101}, id="agility_above_maximum"),
    pytest.param({"pace": 0}, id="attribute_below_minimum"),
    pytest.param({"pace": 100}, id="attribute_above_maximum"),
    pytest.param({"potential": 100}, id="potential_above_maximum"),
    pytest.param({"age": 35, "agility": 86, "potential": 82}, id="senior_with_agility_above_85"),
    pytest.param({"potential": 81}, id="potential_below_highest_attribute"),
    pytest.param({"age": 33}, id="age_33_with_potential_above_highest_attribute"),
    pytest.param(
        {
            "pace": 99,
            "shooting": 99,
            "passing": 99,
            "dribbling": 99,
            "defending": 99,
            "physical": 99,
            "potential": 99,
        },
        id="attributes_sum_above_480",
    ),
]

MALFORMED_IDS = ["01", "0", "abc", "-1", "1.5", "2147483648"]


def create_player(client, **changes):
    response = client.post(PLAYERS_URL, json={**VALID_BODY, **changes})
    assert response.status_code == 201
    return response.json()


def test_create_player_returns_201_with_location_and_calculated_fields(client):
    response = client.post(PLAYERS_URL, json=VALID_BODY)

    body = response.json()
    assert response.status_code == 201
    assert response.headers["location"] == f"{PLAYERS_URL}/{body['id']}"
    assert body == {
        "id": body["id"],
        "name": "Meia Lua",
        "position": "MEI",
        "agility": 85,
        "age": 25,
        "condition": "APTO",
        "base_value": 40.0,
        "market_value": 40.0,
        "pace": 70,
        "shooting": 68,
        "passing": 82,
        "dribbling": 79,
        "defending": 55,
        "physical": 64,
        "potential": 86,
        "overall": 75,
        "club_id": None,
    }


def test_create_player_ignores_fields_controlled_by_the_system(client):
    extra_fields = {
        "id": 99,
        "condition": "DOENTE",
        "club_id": 5,
        "base_value": 999,
        "market_value": 1,
        "overall": 1,
    }

    response = client.post(PLAYERS_URL, json={**VALID_BODY, **extra_fields})

    body = response.json()
    assert response.status_code == 201
    assert body["id"] != 99
    assert body["condition"] == "APTO"
    assert body["club_id"] is None
    assert body["base_value"] == 40.0
    assert body["overall"] == 75


def test_create_player_cleans_the_name(client):
    body = create_player(client, name="  Meia   Zeta ")

    assert body["name"] == "Meia Zeta"


def test_create_player_accepts_whole_number_sent_as_decimal(client):
    body = create_player(client, agility=85.0)

    assert body["agility"] == 85


@pytest.mark.parametrize("changes", INVALID_CHANGES)
def test_create_player_rejects_invalid_body_with_400_and_message(client, changes):
    response = client.post(PLAYERS_URL, json={**VALID_BODY, **changes})

    assert response.status_code == 400
    assert response.json()["message"]


@pytest.mark.parametrize("field", VALID_BODY)
def test_create_player_rejects_missing_field_with_400(client, field):
    body = {key: value for key, value in VALID_BODY.items() if key != field}

    response = client.post(PLAYERS_URL, json=body)

    assert response.status_code == 400
    assert response.json()["message"]


@pytest.mark.parametrize("body", [[], "texto", 10], ids=["array", "text", "number"])
def test_create_player_rejects_body_that_is_not_an_object(client, body):
    response = client.post(PLAYERS_URL, json=body)

    assert response.status_code == 400
    assert response.json()["message"]


def test_create_player_rejects_invalid_json_with_400(client):
    response = client.post(
        PLAYERS_URL, content="{nope", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400
    assert response.json()["message"]


def test_get_player_returns_the_created_player(client):
    created = create_player(client)

    response = client.get(f"{PLAYERS_URL}/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_player_returns_404_with_message_for_unknown_id(client):
    response = client.get(f"{PLAYERS_URL}/999999")

    assert response.status_code == 404
    assert response.json() == {"message": "Jogador não encontrado."}
    assert response.headers["content-type"].startswith("application/json")


@pytest.mark.parametrize("player_id", MALFORMED_IDS)
def test_get_player_treats_malformed_id_as_not_found(client, player_id):
    create_player(client)

    response = client.get(f"{PLAYERS_URL}/{player_id}")

    assert response.status_code == 404
    assert response.json()["message"]


def test_unknown_path_returns_404_with_message(client):
    response = client.get("/api/v1/inexistente")

    assert response.status_code == 404
    assert response.json()["message"]


def test_update_player_changes_only_the_profile(client):
    created = create_player(client)
    body = {"name": "Meia Lua Jr", "position": "MEI", "agility": 80, "age": 26}

    response = client.put(f"{PLAYERS_URL}/{created['id']}", json=body)

    assert response.status_code == 200
    assert response.json() == {**created, "name": "Meia Lua Jr", "agility": 80, "age": 26}
    assert client.get(f"{PLAYERS_URL}/{created['id']}").json() == response.json()


def test_update_player_allows_position_change_of_a_free_player(client):
    created = create_player(client)
    body = {"name": "Meia Lua", "position": "ATA", "agility": 85, "age": 25}

    response = client.put(f"{PLAYERS_URL}/{created['id']}", json=body)

    assert response.status_code == 200
    assert response.json()["position"] == "ATA"
    assert response.json()["base_value"] == created["base_value"]
    assert response.json()["potential"] == created["potential"]


def test_update_player_ignores_fields_that_are_not_editable(client):
    created = create_player(client)
    body = {
        "name": "Meia Lua",
        "position": "MEI",
        "agility": 85,
        "age": 25,
        "potential": 1,
        "pace": 1,
        "club_id": 3,
        "condition": "DOENTE",
        "base_value": 1,
    }

    response = client.put(f"{PLAYERS_URL}/{created['id']}", json=body)

    assert response.status_code == 200
    assert response.json() == created


def test_update_player_returns_404_for_unknown_id(client):
    body = {"name": "Meia Lua", "position": "MEI", "agility": 85, "age": 25}

    response = client.put(f"{PLAYERS_URL}/999999", json=body)

    assert response.status_code == 404
    assert response.json() == {"message": "Jogador não encontrado."}


@pytest.mark.parametrize(
    "changes",
    [
        pytest.param({"name": "Pelé"}, id="name_with_one_word"),
        pytest.param({"position": "mei"}, id="position_in_lowercase"),
        pytest.param({"agility": "85"}, id="agility_as_text"),
        pytest.param({"age": 46}, id="age_above_maximum"),
        pytest.param({"age": 35, "agility": 86}, id="senior_with_agility_above_85"),
    ],
)
def test_update_player_rejects_invalid_body_with_400(client, changes):
    created = create_player(client)
    body = {"name": "Meia Lua", "position": "MEI", "agility": 85, "age": 25, **changes}

    response = client.put(f"{PLAYERS_URL}/{created['id']}", json=body)

    assert response.status_code == 400
    assert response.json()["message"]
    assert client.get(f"{PLAYERS_URL}/{created['id']}").json() == created


def test_update_player_rejects_age_decrease_with_409(client):
    created = create_player(client)
    body = {"name": "Meia Lua", "position": "MEI", "agility": 85, "age": 24}

    response = client.put(f"{PLAYERS_URL}/{created['id']}", json=body)

    assert response.status_code == 409
    assert response.json() == {"message": "A idade do jogador não pode diminuir."}


def test_change_condition_updates_market_value(client):
    created = create_player(client)

    response = client.patch(
        f"{PLAYERS_URL}/{created['id']}/condition", json={"condition": "MAL_CONDICIONADO"}
    )

    assert response.status_code == 200
    assert response.json() == {**created, "condition": "MAL_CONDICIONADO", "market_value": 37.0}


def test_change_condition_to_the_current_one_is_accepted(client):
    created = create_player(client)

    response = client.patch(f"{PLAYERS_URL}/{created['id']}/condition", json={"condition": "APTO"})

    assert response.status_code == 200
    assert response.json() == created


def test_change_condition_ignores_fields_that_do_not_belong_to_the_endpoint(client):
    created = create_player(client)

    response = client.patch(
        f"{PLAYERS_URL}/{created['id']}/condition",
        json={"condition": "APTO", "name": "Outro Nome"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Meia Lua"


def test_change_condition_rejects_doente_straight_to_apto_with_409(client):
    created = create_player(client)
    url = f"{PLAYERS_URL}/{created['id']}/condition"
    client.patch(url, json={"condition": "DOENTE"})

    response = client.patch(url, json={"condition": "APTO"})

    assert response.status_code == 409
    assert response.json() == {"message": "Jogador DOENTE não pode passar direto para APTO."}


def test_change_condition_allows_doente_to_mal_condicionado(client):
    created = create_player(client)
    url = f"{PLAYERS_URL}/{created['id']}/condition"
    client.patch(url, json={"condition": "DOENTE"})

    response = client.patch(url, json={"condition": "MAL_CONDICIONADO"})

    assert response.status_code == 200
    assert response.json()["condition"] == "MAL_CONDICIONADO"


@pytest.mark.parametrize(
    "body",
    [
        pytest.param({}, id="missing"),
        pytest.param({"condition": None}, id="null"),
        pytest.param({"condition": "mal_condicionado"}, id="lowercase"),
        pytest.param({"condition": "XXX"}, id="unknown"),
        pytest.param({"condition": 1}, id="number"),
    ],
)
def test_change_condition_rejects_invalid_body_with_400(client, body):
    created = create_player(client)

    response = client.patch(f"{PLAYERS_URL}/{created['id']}/condition", json=body)

    assert response.status_code == 400
    assert response.json()["message"]


def test_change_condition_returns_404_for_unknown_id(client):
    response = client.patch(f"{PLAYERS_URL}/999999/condition", json={"condition": "DOENTE"})

    assert response.status_code == 404
    assert response.json() == {"message": "Jogador não encontrado."}


def test_delete_player_returns_204_and_the_player_becomes_not_found(client):
    created = create_player(client)

    response = client.delete(f"{PLAYERS_URL}/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"{PLAYERS_URL}/{created['id']}").status_code == 404


def test_delete_player_ignores_a_body_sent_with_the_request(client):
    created = create_player(client)

    response = client.request("DELETE", f"{PLAYERS_URL}/{created['id']}", json={"x": 1})

    assert response.status_code == 204


def test_delete_player_twice_returns_404_the_second_time(client):
    created = create_player(client)
    client.delete(f"{PLAYERS_URL}/{created['id']}")

    response = client.delete(f"{PLAYERS_URL}/{created['id']}")

    assert response.status_code == 404
    assert response.json() == {"message": "Jogador não encontrado."}


def test_delete_player_returns_404_for_unknown_id(client):
    response = client.delete(f"{PLAYERS_URL}/999999")

    assert response.status_code == 404


@pytest.mark.parametrize("player_id", MALFORMED_IDS)
def test_delete_player_treats_malformed_id_as_not_found(client, player_id):
    response = client.delete(f"{PLAYERS_URL}/{player_id}")

    assert response.status_code == 404
    assert response.json()["message"]
