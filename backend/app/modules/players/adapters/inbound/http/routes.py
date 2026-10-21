from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from app.api.dependencies import (
    build_change_player_condition,
    build_list_players,
    parse_resource_id,
)
from app.api.error_docs import error_responses
from app.modules.players.adapters.inbound.http.dependencies import (
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


@router.get(
    "",
    summary="Lista os jogadores",
    responses=error_responses(400, 404),
)
def list_players(
    query: Annotated[ListPlayersQuery, Depends(get_list_players_query)],
    use_case: Annotated[ListPlayers, Depends(build_list_players)],
) -> PlayersPageResponse:
    """
    Lista os jogadores não excluídos, com busca, filtros, ordenação e paginação.

    Parâmetros de consulta, todos opcionais e combináveis:

    - `search`: texto de 2 a 100 caracteres, procurado dentro do nome, sem diferenciar
      maiúsculas, minúsculas nem acentos.
    - `position`: `GOL`, `ZAG`, `LAT`, `MEI` ou `ATA`.
    - `condition`: `APTO`, `MAL_CONDICIONADO` ou `DOENTE`.
    - `free`: `true` (só livres) ou `false` (só com clube).
    - `club_id`: só o elenco desse clube; não combina com `free=true`.
    - `min_age` e `max_age`: idade de 16 a 45, com o mínimo menor ou igual ao máximo.
    - `min_value` e `max_value`: **valor de mercado** de 0 a 550, com até 2 casas decimais.
    - `sort`: até dois critérios separados por vírgula, sem espaços e sem repetir o campo:
      `name` (padrão), `value_asc`, `value_desc`, `age_asc`, `age_desc` ou `position`
      (ordem GOL, ZAG, LAT, MEI, ATA). Empates: nome e depois id.
    - `page` (padrão 1) e `limit` (de 1 a 50, padrão 10).

    A resposta traz `data` e `meta` (`page`, `limit`, `total_items`, `total_pages`). Uma página
    além da última devolve `data` vazio.

    Erros: `400` (parâmetro inválido, vazio ou contraditório) e `404` (`club_id` inexistente).
    """
    return PlayersPageResponse.from_page(use_case.execute(query))


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um jogador",
    responses=error_responses(400),
)
def create_player(
    body: CreatePlayerRequest,
    request: Request,
    response: Response,
    use_case: Annotated[CreatePlayer, Depends(build_create_player)],
) -> PlayerResponse:
    """
    Cadastra um jogador livre, na condição `APTO`.

    - `name`: 3 a 100 caracteres, com pelo menos duas palavras e nenhum dígito.
    - `agility`: 1 a 100 (com 35 anos ou mais, no máximo 85). `age`: 16 a 45.
    - `pace`, `shooting`, `passing`, `dribbling`, `defending`, `physical` e `potential`: 1 a 99.
      A soma dos seis atributos não passa de 480, e o `potential` não é menor que o maior deles
      (com 33 anos ou mais, é igual a ele).
    - `club_id`, `condition`, `overall`, `base_value` e `market_value` não são enviados; se
      vierem, são ignorados.

    O **valor base** é calculado agora, uma única vez. O **overall** e o **valor de mercado** são
    calculados a cada consulta. Responde `201` com o cabeçalho `Location`.

    Erros: `400` (campo ausente, fora do limite ou fora do formato).
    """
    player = use_case.execute(body.to_registration())
    response.headers["Location"] = request.url_for("get_player", player_id=player.id).path
    return PlayerResponse.from_entity(player)


@router.get(
    "/{player_id}",
    summary="Consulta um jogador",
    responses=error_responses(404),
)
def get_player(
    player_id: str,
    use_case: Annotated[GetPlayer, Depends(build_get_player)],
) -> PlayerResponse:
    """
    Consulta um jogador pelo id, com o overall e o valor de mercado calculados agora.

    Erros: `404` (id inexistente, mal formado ou de jogador excluído).
    """
    return PlayerResponse.from_entity(use_case.execute(parse_resource_id(player_id)))


@router.put(
    "/{player_id}",
    summary="Edita um jogador",
    responses=error_responses(400, 404, 409),
)
def update_player(
    player_id: str,
    body: UpdatePlayerRequest,
    use_case: Annotated[UpdatePlayer, Depends(build_update_player)],
) -> PlayerResponse:
    """
    Edita só o nome, a posição, a agilidade e a idade do jogador.

    Os indicadores, o `potential` e o valor base continuam os do cadastro; os demais campos
    enviados são ignorados. As regras de limite são as do cadastro.

    Erros: `400` (campo ausente ou fora do limite), `404` (jogador inexistente ou excluído) e
    `409` (jogador com clube mudando de posição, ou idade menor que a atual).
    """
    player = use_case.execute(parse_resource_id(player_id), body.to_changes())
    return PlayerResponse.from_entity(player)


@router.patch(
    "/{player_id}/condition",
    summary="Altera a condição física de um jogador",
    responses=error_responses(400, 404, 409),
)
def change_player_condition(
    player_id: str,
    body: ChangeConditionRequest,
    use_case: Annotated[ChangePlayerCondition, Depends(build_change_player_condition)],
) -> PlayerResponse:
    """
    Altera a condição física: `APTO`, `MAL_CONDICIONADO` ou `DOENTE`.

    A condição muda o **valor de mercado** (descontos de 0%, 15% e 30%, ajustados pela
    agilidade). Enviar a condição atual é aceito, sem mudança.

    Erros: `400` (condição ausente ou fora da lista), `404` (jogador inexistente ou excluído) e
    `409` (de `DOENTE` não se passa direto para `APTO`).
    """
    player = use_case.execute(parse_resource_id(player_id), body.condition)
    return PlayerResponse.from_entity(player)


@router.delete(
    "/{player_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui um jogador livre",
    responses=error_responses(404, 409),
)
def delete_player(
    player_id: str,
    use_case: Annotated[DeletePlayer, Depends(build_delete_player)],
) -> None:
    """
    Exclui um jogador **livre** (exclusão lógica: nada é apagado do banco).

    Responde `204`, sem corpo. Depois disso o jogador conta como inexistente em todos os
    endpoints; as transações e as partidas antigas dele continuam como foram gravadas.

    Erros: `404` (jogador inexistente ou já excluído) e `409` (jogador no elenco de um clube).
    """
    use_case.execute(parse_resource_id(player_id))
