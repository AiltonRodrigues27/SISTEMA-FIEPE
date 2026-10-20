from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from app.api.dependencies import build_get_club, build_list_clubs, parse_resource_id
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


@router.get("")
def list_clubs(
    sort: Annotated[ClubSortKey, Depends(get_club_sort)],
    use_case: Annotated[ListClubs, Depends(build_list_clubs)],
) -> list[ClubResponse]:
    return [ClubResponse.from_view(view) for view in use_case.execute(sort)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_club(
    body: CreateClubRequest,
    request: Request,
    response: Response,
    use_case: Annotated[CreateClub, Depends(build_create_club)],
) -> ClubResponse:
    view = use_case.execute(body.name, body.acronym)
    response.headers["Location"] = request.url_for("get_club", club_id=view.club.id).path
    return ClubResponse.from_view(view)


@router.get("/{club_id}")
def get_club(
    club_id: str,
    use_case: Annotated[GetClub, Depends(build_get_club)],
) -> ClubDetailResponse:
    return ClubDetailResponse.from_details(use_case.execute(parse_resource_id(club_id)))
