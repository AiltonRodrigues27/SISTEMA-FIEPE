from enum import StrEnum


class Position(StrEnum):
    GOL = "GOL"
    ZAG = "ZAG"
    LAT = "LAT"
    MEI = "MEI"
    ATA = "ATA"


class PhysicalCondition(StrEnum):
    APTO = "APTO"
    MAL_CONDICIONADO = "MAL_CONDICIONADO"
    DOENTE = "DOENTE"

    @property
    def can_play(self) -> bool:
        return self is not PhysicalCondition.DOENTE
