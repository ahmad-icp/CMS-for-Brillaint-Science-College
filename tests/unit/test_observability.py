import json
import logging


def test_request_id_and_structured_log(client, caplog) -> None:
    with caplog.at_level(logging.INFO, logger="college_erp.requests"):
        response = client.get("/health?do_not_log=this", headers={"X-Request-ID": "demo-request-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "demo-request-123"
    event = json.loads(next(record.message for record in caplog.records if "request_completed" in record.message))
    assert event["event"] == "request_completed"
    assert event["path"] == "/health"
    assert event["status"] == 200
    assert "do_not_log" not in event


def test_unsafe_request_id_is_replaced(client) -> None:
    response = client.get("/health", headers={"X-Request-ID": "unsafe\nlog-entry"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "unsafe\nlog-entry"
    assert "\n" not in response.headers["X-Request-ID"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
