from collections.abc import Callable

import pytest

from app.modules.league.domain.duels import Starter, Team
from app.modules.players.domain.enums import PhysicalCondition, Position


@pytest.fixture
def make_starter() -> Callable[..., Starter]:
    def make(
        player_id: int,
        name: str,
        position: Position,
        condition: PhysicalCondition = PhysicalCondition.APTO,
        shooting: int = 1,
        passing: int = 1,
        dribbling: int = 1,
        defending: int = 1,
    ) -> Starter:
        return Starter(
            player_id=player_id,
            name=name,
            position=position,
            condition=condition,
            shooting=shooting,
            passing=passing,
            dribbling=dribbling,
            defending=defending,
        )

    return make


@pytest.fixture
def eagles(make_starter) -> Team:
    """Águias FC, o mandante do exemplo da RN20 (o lateral está MAL_CONDICIONADO)."""
    return Team.from_starters(
        club_id=1,
        formation="2-1-1",
        starters=[
            make_starter(30, "Rui Prado", Position.GOL, defending=77),
            make_starter(32, "Téo Brandão", Position.ZAG, defending=84),
            make_starter(
                31,
                "Davi Lins",
                Position.LAT,
                PhysicalCondition.MAL_CONDICIONADO,
                dribbling=74,
                defending=66,
            ),
            make_starter(33, "Lauro Neves", Position.MEI, passing=82),
            make_starter(34, "Otto Rangel", Position.ATA, shooting=75),
        ],
    )


@pytest.fixture
def delta(make_starter) -> Team:
    """Delta FC, o visitante do exemplo da RN20."""
    return Team.from_starters(
        club_id=2,
        formation="2-1-1",
        starters=[
            make_starter(40, "Ivo Teles", Position.GOL, defending=72),
            make_starter(41, "Hugo Vaz", Position.ZAG, defending=84),
            make_starter(42, "Lino Matos", Position.LAT, dribbling=79, defending=63),
            make_starter(43, "Nei Soares", Position.MEI, passing=70),
            make_starter(44, "Ugo Falcão", Position.ATA, shooting=81),
        ],
    )
