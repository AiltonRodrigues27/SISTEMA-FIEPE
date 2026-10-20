import string
from dataclasses import replace

import pytest

from app.modules.players.application.list_players import ListPlayers, ListPlayersQuery
from app.modules.players.domain.entities import Player
from app.modules.players.domain.enums import Position
from app.modules.players.domain.listing import PlayerFilters, SortKey

DEFAULT_QUERY = ListPlayersQuery(filters=PlayerFilters(), sort=(SortKey.NAME,), page=1, limit=10)


def add_player(player_repository, registration, name, **changes) -> Player:
    return player_repository.add(Player.register(replace(registration, name=name, **changes)))


def add_23_players(player_repository, registration) -> None:
    letters = string.ascii_uppercase[:23]
    for letter in reversed(letters):
        add_player(player_repository, registration, f"Jogador {letter}")


@pytest.mark.parametrize(
    ("limit", "page", "expected_items", "expected_pages"),
    [
        pytest.param(10, 1, 10, 3, id="first_page"),
        pytest.param(10, 3, 3, 3, id="last_page_is_partial"),
        pytest.param(10, 4, 0, 3, id="page_after_the_last"),
        pytest.param(50, 1, 23, 1, id="everything_in_one_page"),
    ],
)
def test_list_players_paginates_after_searching(
    player_repository, registration, limit, page, expected_items, expected_pages
) -> None:
    add_23_players(player_repository, registration)

    result = ListPlayers(player_repository).execute(replace(DEFAULT_QUERY, page=page, limit=limit))

    assert len(result.players) == expected_items
    assert result.total_items == 23
    assert result.total_pages == expected_pages
    assert (result.page, result.limit) == (page, limit)


def test_list_players_without_players_has_zero_pages(player_repository) -> None:
    result = ListPlayers(player_repository).execute(DEFAULT_QUERY)

    assert result.players == []
    assert result.total_items == 0
    assert result.total_pages == 0


def test_list_players_counts_all_matches_not_only_the_page(player_repository, registration) -> None:
    add_23_players(player_repository, registration)
    for letter in "XYZUV":
        add_player(player_repository, registration, f"Atacante {letter}", position=Position.ATA)
    query = replace(DEFAULT_QUERY, filters=PlayerFilters(position=Position.ATA), page=3, limit=2)

    result = ListPlayers(player_repository).execute(query)

    assert len(result.players) == 1
    assert result.total_items == 5
    assert result.total_pages == 3


def test_list_players_orders_before_paginating(player_repository, registration) -> None:
    add_23_players(player_repository, registration)

    result = ListPlayers(player_repository).execute(replace(DEFAULT_QUERY, page=2, limit=10))

    expected = [f"Jogador {letter}" for letter in string.ascii_uppercase[10:20]]
    assert [player.name for player in result.players] == expected
