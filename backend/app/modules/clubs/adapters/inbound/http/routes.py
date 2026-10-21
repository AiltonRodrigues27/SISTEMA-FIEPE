from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from app.api.dependencies import build_get_club, build_list_clubs, parse_resource_id
from app.api.error_docs import error_responses
from app.modules.clubs.adapters.inbound.http.dependencies import build_create_club
from app.modules.clubs.adapters.inbound.http.list_query import get_club_sort
from app.modules.clubs.adapters.inbound.http.schemas import (
    ClubDetailResponse,
    ClubResponse,
    CreateClubRequest,
)
from app.modules.clubs.application.create_club import CreateClub
from app.modules.clubs.application.get_club import GetClub
from app.modules.clubs.application.list_clubs import ListClubs
from app.modules.clubs.domain.listing import ClubSortKey

router = APIRouter(prefix="/clubs", tags=["Clubes"])


@router.get(
    "",
    summary="Lista os clubes",
    responses=error_responses(400),
)
def list_clubs(
    sort: Annotated[ClubSortKey, Depends(get_club_sort)],
    use_case: Annotated[ListClubs, Depends(build_list_clubs)],
) -> list[ClubResponse]:
    """
    Lista todos os clubes, com o caixa, o valor do elenco e o patrimônio calculados agora.

    Parâmetro de consulta opcional:

    - `sort`: um só valor: `name` (padrão, ordem alfabética), `net_worth_asc` ou
      `net_worth_desc`. Empates: nome e depois id.

    Erros: `400` (`sort` vazio ou fora da lista, inclusive com maiúsculas trocadas).
    """
    return [ClubResponse.from_view(view) for view in use_case.execute(sort)]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Cria um clube",
    responses=error_responses(400, 409),
)
def create_club(
    body: CreateClubRequest,
    request: Request,
    response: Response,
    use_case: Annotated[CreateClub, Depends(build_create_club)],
) -> ClubResponse:
    """
    Cria um clube com **300,00** em caixa e sem jogadores.

    - `name`: 3 a 60 caracteres, de 2 a 5 palavras; só letras, espaços, hífen e ponto. É único,
      sem diferenciar maiúsculas e minúsculas, mas diferenciando acentos.
    - `acronym`: 3 letras de A a Z, maiúsculas, que aparecem no nome nessa ordem (a primeira é
      a inicial do nome) e não são todas iguais. É única.
    - `cash` não é enviado; se vier, é ignorado.

    A liga aceita no máximo 20 clubes. Responde `201` com o cabeçalho `Location`.

    Erros: `400` (campo ausente ou fora do formato) e `409` (nome ou sigla já cadastrados, ou
    limite de 20 clubes).
    """
    view = use_case.execute(body.name, body.acronym)
    response.headers["Location"] = request.url_for("get_club", club_id=view.club.id).path
    return ClubResponse.from_view(view)


@router.get(
    "/{club_id}",
    summary="Consulta um clube com o elenco",
    responses=error_responses(404),
)
def get_club(
    club_id: str,
    use_case: Annotated[GetClub, Depends(build_get_club)],
) -> ClubDetailResponse:
    """
    Consulta o clube com o elenco, o valor do elenco e o patrimônio.

    - O elenco vem na ordem das posições (GOL, ZAG, LAT, MEI, ATA), depois pelo nome e pelo id.
    - Cada jogador traz o contrato: valor de compra, fim da fidelidade, dias restantes e o
      percentual de multa se fosse vendido agora.
    - Valor do elenco = soma dos valores de mercado; patrimônio = caixa + valor do elenco.
      Tudo é calculado a cada consulta.

    Erros: `404` (clube inexistente ou id mal formado).
    """
    return ClubDetailResponse.from_details(use_case.execute(parse_resource_id(club_id)))
