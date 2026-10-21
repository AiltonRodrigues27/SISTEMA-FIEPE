import logging
import re
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.request_logging import (
    LOGGER_NAME,
    RequestLoggingMiddleware,
    configure_request_logging,
    logger,
)
from app.main import app as real_app
from app.shared.domain.brasilia_time import BRASILIA


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 11, 2, 10, 15, tzinfo=BRASILIA)


@pytest.fixture
def small_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware, clock=FixedClock())

    @app.get("/ok")
    def ok() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/created", status_code=201)
    def created() -> dict[str, str]:
        return {"status": "created"}

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("falha inesperada")

    return app


def request_lines(caplog) -> list[str]:
    return [record.getMessage() for record in caplog.records if record.name == LOGGER_NAME]


def test_a_request_writes_one_line_with_date_time_method_path_and_status(small_app, caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    TestClient(small_app).get("/ok")

    lines = request_lines(caplog)
    assert len(lines) == 1
    assert re.fullmatch(r"2026-11-02T10:15:00-03:00 GET /ok 200 \d+ms", lines[0])


def test_the_line_shows_the_method_and_the_status_of_a_creation(small_app, caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    TestClient(small_app).post("/created")

    assert re.fullmatch(r"\S+ POST /created 201 \d+ms", request_lines(caplog)[0])


def test_the_line_has_the_path_without_the_query_string(small_app, caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    TestClient(small_app).get("/ok?secret=1&page=2")

    assert re.fullmatch(r"\S+ GET /ok 200 \d+ms", request_lines(caplog)[0])


def test_an_unknown_path_is_logged_with_the_404_status(small_app, caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    TestClient(small_app).get("/does-not-exist")

    assert re.fullmatch(r"\S+ GET /does-not-exist 404 \d+ms", request_lines(caplog)[0])


def test_an_unexpected_error_is_logged_with_the_500_status(small_app, caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    response = TestClient(small_app, raise_server_exceptions=False).get("/boom")

    assert response.status_code == 500
    assert re.fullmatch(r"\S+ GET /boom 500 \d+ms", request_lines(caplog)[0])


def test_each_request_writes_its_own_line(small_app, caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)
    client = TestClient(small_app)

    client.get("/ok")
    client.get("/ok")

    assert len(request_lines(caplog)) == 2


def test_the_real_application_logs_a_line_per_request(caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    TestClient(real_app).get("/health")

    lines = request_lines(caplog)
    assert len(lines) == 1
    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-03:00 GET /health 200 \d+ms", lines[0]
    )


def test_configuring_twice_does_not_duplicate_the_handler() -> None:
    configure_request_logging()
    handlers_after_first_call = len(logger.handlers)

    configure_request_logging()

    assert len(logger.handlers) == handlers_after_first_call == 1
