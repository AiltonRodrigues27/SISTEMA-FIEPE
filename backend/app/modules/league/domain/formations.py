from dataclasses import dataclass

LINEUP_SIZE = 5


@dataclass(frozen=True)
class FormationShape:
    defense: int
    midfield: int
    attack: int


FORMATIONS = {
    "3-1": FormationShape(defense=3, midfield=0, attack=1),
    "2-2": FormationShape(defense=2, midfield=0, attack=2),
    "2-1-1": FormationShape(defense=2, midfield=1, attack=1),
    "1-2-1": FormationShape(defense=1, midfield=2, attack=1),
}
