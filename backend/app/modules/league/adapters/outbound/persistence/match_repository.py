from dataclasses import replace

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.modules.league.adapters.outbound.persistence.models import MatchDuelModel, MatchModel
from app.modules.league.domain.duels import Duel, DuelPlayer
from app.modules.league.domain.match import Match
from app.modules.league.ports.repositories import MatchRepository
from app.modules.players.domain.enums import PhysicalCondition, Position


class SqlAlchemyMatchRepository(MatchRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, match: Match) -> Match:
        model = MatchModel(
            home_club_id=match.home_club_id,
            away_club_id=match.away_club_id,
            home_goals=match.home_goals,
            away_goals=match.away_goals,
            home_formation=match.home_formation,
            away_formation=match.away_formation,
            played_at=match.played_at,
        )
        self._session.add(model)
        self._session.flush()
        self._session.add_all(_to_duel_model(model.id, duel) for duel in match.duels)
        self._session.flush()
        return replace(match, id=model.id)

    def get(self, match_id: int) -> Match | None:
        model = self._session.get(MatchModel, match_id)
        if model is None:
            return None
        statement = (
            select(MatchDuelModel)
            .where(MatchDuelModel.match_id == match_id)
            .order_by(MatchDuelModel.order)
        )
        duels = tuple(_to_duel(duel_model) for duel_model in self._session.scalars(statement))
        return _to_match(model, duels)

    def list_matches(self, club_id: int | None) -> list[Match]:
        statement = select(MatchModel)
        if club_id is not None:
            statement = statement.where(
                or_(MatchModel.home_club_id == club_id, MatchModel.away_club_id == club_id)
            )
        statement = statement.order_by(MatchModel.played_at.desc(), MatchModel.id.desc())
        return [_to_match(model, ()) for model in self._session.scalars(statement)]


def _to_match(model: MatchModel, duels: tuple[Duel, ...]) -> Match:
    return Match(
        id=model.id,
        home_club_id=model.home_club_id,
        away_club_id=model.away_club_id,
        home_goals=model.home_goals,
        away_goals=model.away_goals,
        home_formation=model.home_formation,
        away_formation=model.away_formation,
        played_at=model.played_at,
        duels=duels,
    )


def _to_duel_model(match_id: int, duel: Duel) -> MatchDuelModel:
    return MatchDuelModel(
        match_id=match_id,
        order=duel.order,
        attacking_club_id=duel.attacking_club_id,
        attacker_id=duel.attacker.player_id,
        defender_id=duel.defender.player_id,
        attacker_name=duel.attacker.player_name,
        defender_name=duel.defender.player_name,
        attacker_position=duel.attacker.position.value,
        defender_position=duel.defender.position.value,
        attacker_condition=duel.attacker.condition.value,
        defender_condition=duel.defender.condition.value,
        attack_attribute=duel.attacker.attribute,
        defense_attribute=duel.defender.attribute,
        attack_value=duel.attacker.value,
        defense_value=duel.defender.value,
        goal=duel.goal,
    )


def _to_duel(model: MatchDuelModel) -> Duel:
    return Duel(
        order=model.order,
        attacking_club_id=model.attacking_club_id,
        attacker=DuelPlayer(
            player_id=model.attacker_id,
            player_name=model.attacker_name,
            position=Position(model.attacker_position),
            condition=PhysicalCondition(model.attacker_condition),
            attribute=model.attack_attribute,
            value=model.attack_value,
        ),
        defender=DuelPlayer(
            player_id=model.defender_id,
            player_name=model.defender_name,
            position=Position(model.defender_position),
            condition=PhysicalCondition(model.defender_condition),
            attribute=model.defense_attribute,
            value=model.defense_value,
        ),
        goal=model.goal,
    )
