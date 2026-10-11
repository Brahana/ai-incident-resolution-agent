
from fastapi.testclient import TestClient
from unittest.mock import patch

from app import app

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "AI Incident Resolution Agent API is running"
    )


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_reject_unsupported_file():
    response = client.post(
        "/analyze",
        files={
            "file": (
                "notes.csv",
                b"some,data",
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert "Only .log and .txt files" in response.json()["detail"]


def test_analyze_valid_log():
    fake_report = "Test incident report"

    with patch(
        "app.create_incident_report",
        return_value=fake_report,
    ):
        response = client.post(
            "/analyze",
            files={
                "file": (
                    "sample.log",
                    b"2026-10-11 ERROR Database connection timeout",
                    "text/plain",
                )
            },
        )

    assert response.status_code == 200

    result = response.json()
    assert result["filename"] == "sample.log"
    assert result["status"] == "success"
    assert result["incident_report"] == fake_report
