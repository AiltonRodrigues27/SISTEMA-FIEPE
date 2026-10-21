from datetime import timedelta

PLAYERS_URL = "/api/v1/players"
CLUBS_URL = "/api/v1/clubs"
MATCHES_URL = "/api/v1/matches"
STANDINGS_URL = "/api/v1/standings"
ATTRIBUTES = ("pace", "shooting", "passing", "dribbling", "defending", "physical")
STRONG, MIDDLE, WEAK = 60, 30, 1
POWER_POSITIONS = (
    ("Goleiro", "GOL"),
    ("Zagueiro", "ZAG"),
    ("Lateral", "LAT"),
    ("Meia", "MEI"),
    ("Atacante", "ATA"),
)


def create_club(client, name, acronym):
    response = client.post(CLUBS_URL, json={"name": name, "acronym": acronym})
    assert response.status_code == 201
    return response.json()


def build_power_club(client, clock, name, acronym, tag, power):
    club = create_club(client, name, acronym)
    player_ids = []
    for label, position in POWER_POSITIONS:
        body = {
            "name": f"{label} {tag}",
            "position": position,
            "agility": 50,
            "age": 25,
            **dict.fromkeys(ATTRIBUTES, power),
            "potential": 99,
        }
        player = client.post(PLAYERS_URL, json=body).json()
        loyalty = (clock.moment + timedelta(days=120)).strftime("%Y-%m-%dT%H:%M-03:00")
        bought = client.post(
            f"{PLAYERS_URL}/{player['id']}/buy",
            json={"club_id": club["id"], "loyalty_until": loyalty},
        )
        assert bought.status_code == 200
        player_ids.append(player["id"])
    lineup = client.put(
        f"{CLUBS_URL}/{club['id']}/lineup", json={"formation": "2-1-1", "player_ids": player_ids}
    )
    assert lineup.status_code == 200
    return club


def play_ok(client, home, away):
    body = {"home_club_id": home["id"], "away_club_id": away["id"]}
    response = client.post(MATCHES_URL, json=body)
    assert response.status_code == 201
    return response.json()


def row(position, club, name, played, wins, draws, losses, goals_for, goals_against):
    return {
        "position": position,
        "club_id": club["id"],
        "club_name": name,
        "played": played,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "goal_difference": goals_for - goals_against,
        "points": wins * 3 + draws,
    }


def test_standings_list_every_club_with_zeros_before_the_first_match(client):
    delta = create_club(client, "Delta FC", "DFC")
    aguias = create_club(client, "Águias FC", "AGU")
    epsilon = create_club(client, "Épsilon EC", "EEC")

    response = client.get(STANDINGS_URL)

    assert response.status_code == 200
    assert response.json() == [
        row(1, aguias, "Águias FC", 0, 0, 0, 0, 0, 0),
        row(2, delta, "Delta FC", 0, 0, 0, 0, 0, 0),
        row(3, epsilon, "Épsilon EC", 0, 0, 0, 0, 0, 0),
    ]


def test_standings_without_clubs_are_empty(client):
    response = client.get(STANDINGS_URL)

    assert response.status_code == 200
    assert response.json() == []


def test_standings_are_calculated_from_the_played_matches(client, clock):
    alpha = build_power_club(client, clock, "Alfa FC", "AFC", "Alfa", STRONG)
    beta = build_power_club(client, clock, "Beta FC", "BFC", "Beta", MIDDLE)
    gama = build_power_club(client, clock, "Gama FC", "GFC", "Gama", WEAK)
    delta = build_power_club(client, clock, "Delta FC", "DFC", "Delta", WEAK)
    play_ok(client, alpha, beta)
    play_ok(client, beta, gama)
    play_ok(client, gama, alpha)
    play_ok(client, gama, delta)

    response = client.get(STANDINGS_URL)

    assert response.status_code == 200
    assert response.json() == [
        row(1, alpha, "Alfa FC", 2, 2, 0, 0, 6, 0),
        row(2, beta, "Beta FC", 2, 1, 0, 1, 3, 3),
        row(3, delta, "Delta FC", 1, 0, 1, 0, 0, 0),
        row(4, gama, "Gama FC", 3, 0, 1, 2, 0, 6),
    ]


def test_a_new_match_changes_the_standings_on_the_next_query(client, clock):
    alpha = build_power_club(client, clock, "Alfa FC", "AFC", "Alfa", STRONG)
    gama = build_power_club(client, clock, "Gama FC", "GFC", "Gama", WEAK)
    before = client.get(STANDINGS_URL).json()
    play_ok(client, gama, alpha)

    after = client.get(STANDINGS_URL).json()

    assert [item["club_name"] for item in before] == ["Alfa FC", "Gama FC"]
    assert after == [
        row(1, alpha, "Alfa FC", 1, 1, 0, 0, 3, 0),
        row(2, gama, "Gama FC", 1, 0, 0, 1, 0, 3),
    ]
