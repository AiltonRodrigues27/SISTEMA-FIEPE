from datetime import datetime

from app.shared.application.clock import Clock
from app.shared.domain.brasilia_time import BRASILIA


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(BRASILIA)
