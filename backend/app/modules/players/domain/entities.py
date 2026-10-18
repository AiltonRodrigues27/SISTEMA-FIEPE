# Conceitos e regras de negócio relacionados a entidade Player
from typing import NamedTuple


class Attributes(NamedTuple):
    pace: int
    shooting: int
    passing: int
    dribbling: int
    defending: int
    physical: int
