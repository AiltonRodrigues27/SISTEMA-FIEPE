from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from app.api.dependencies import build_list_players, parse_resource_id
from app.modules.players.adapters.inbound.http.dependencies import (
    build_change_player_condition,
    build_create_player,
    build_delete_player,
    build_get_player,
    build_update_player,
)
from app.modules.players.adapters.inbound.http.list_query import get_list_players_query
from app.modules.players.adapters.inbound.http.schemas import (
    ChangeConditionRequest,
    CreatePlayerRequest,
    PlayerResponse,
    PlayersPageResponse,
    UpdatePlayerRequest,
)
from app.modules.players.application.change_player_condition import ChangePlayerCondition
from app.modules.players.application.create_player import CreatePlayer
from app.modules.players.application.delete_player import DeletePlayer
from app.modules.players.application.get_player import GetPlayer
from app.modules.players.application.list_players import ListPlayers, ListPlayersQuery
from app.modules.players.application.update_player import UpdatePlayer

router = APIRouter(prefix="/players", tags=["Jogadores"])


@router.get("")
def list_players(
    query: Annotated[ListPlayersQuery, Depends(get_list_players_query)],
    use_case: Annotated[ListPlayers, Depends(build_list_players)],
) -> PlayersPageResponse:
    return PlayersPageResponse.from_page(use_case.execute(query))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_player(
    body: CreatePlayerRequest,
    request: Request,
    response: Response,
    use_case: Annotated[CreatePlayer, Depends(build_create_player)],
) -> PlayerResponse:
    player = use_case.execute(body.to_registration())
    response.headers["Location"] = request.url_for("get_player", player_id=player.id).path
    return PlayerResponse.from_entity(player)


@router.get("/{player_id}")
def get_player(
    player_id: str,
    use_case: Annotated[GetPlayer, Depends(build_get_player)],
) -> PlayerResponse:
    return PlayerResponse.from_entity(use_case.execute(parse_resource_id(player_id)))


@router.put("/{player_id}")
def update_player(
    player_id: str,
    body: UpdatePlayerRequest,
    use_case: Annotated[UpdatePlayer, Depends(build_update_player)],
) -> PlayerResponse:
    player = use_case.execute(parse_resource_id(player_id), body.to_changes())
    return PlayerResponse.from_entity(player)


@router.patch("/{player_id}/condition")
def change_player_condition(
    player_id: str,
    body: ChangeConditionRequest,
    use_case: Annotated[ChangePlayerCondition, Depends(build_change_player_condition)],
) -> PlayerResponse:
    player = use_case.execute(parse_resource_id(player_id), body.condition)
    return PlayerResponse.from_entity(player)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(
    player_id: str,
    use_case: Annotated[DeletePlayer, Depends(build_delete_player)],
) -> None:
    use_case.execute(parse_resource_id(player_id))
