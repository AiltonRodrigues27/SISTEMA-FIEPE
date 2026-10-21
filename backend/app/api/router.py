from fastapi import APIRouter

from app.modules.clubs.adapters.inbound.http.routes import router as clubs_router
from app.modules.league.adapters.inbound.http.routes import router as league_router
from app.modules.market.adapters.inbound.http.routes import router as market_router
from app.modules.players.adapters.inbound.http.routes import router as players_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(players_router)
api_router.include_router(clubs_router)
api_router.include_router(market_router)
api_router.include_router(league_router)
