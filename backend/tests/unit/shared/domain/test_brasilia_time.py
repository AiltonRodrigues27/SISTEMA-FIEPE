from datetime import UTC, datetime, timedelta, timezone

from app.shared.domain.brasilia_time import BRASILIA, format_api_datetime


def test_brasilia_is_three_hours_behind_utc() -> None:
    assert BRASILIA.utcoffset(None) == timedelta(hours=-3)


def test_format_keeps_a_datetime_already_in_brasilia_time() -> None:
    moment = datetime(2026, 11, 5, 16, 40, 5, tzinfo=BRASILIA)

    assert format_api_datetime(moment) == "2026-11-05T16:40:05-03:00"


def test_format_converts_other_time_zones_to_brasilia_time() -> None:
    from_utc = datetime(2027, 3, 2, 13, 15, tzinfo=UTC)
    from_tokyo = datetime(2027, 3, 2, 22, 15, tzinfo=timezone(timedelta(hours=9)))

    assert format_api_datetime(from_utc) == "2027-03-02T10:15:00-03:00"
    assert format_api_datetime(from_tokyo) == "2027-03-02T10:15:00-03:00"
