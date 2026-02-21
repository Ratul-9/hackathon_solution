import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from api.main import app  

client = TestClient(app)


# ----------------------------
# Helper Payload Builder
# ----------------------------
def build_payload():
    return {
        "age": 30,
        "wage": 100000,
        "inflation": 0.05,
        "q_periods": [],
        "p_periods": [],
        "k_periods": [],
        "transactions": [
            {
                "id": 1,
                "date": "2024-01-01 10:00:00",
                "remanent": 5000,
                "status": "valid"
            },
            {
                "id": 2,
                "date": "2024-01-02 10:00:00",
                "remanent": 3000,
                "status": "invalid"
            }
        ]
    }


# -------------------------------------------------
# Test 1 — Successful C++ Engine Execution
# -------------------------------------------------
@patch("subprocess.Popen")
def test_returns_success(mock_popen):
    mock_process = MagicMock()
    mock_process.communicate.return_value = (
        json.dumps({"final_amount": 15000}),
        ""
    )
    mock_process.returncode = 0
    mock_popen.return_value = mock_process

    response = client.post(
        "/blackrock/challenge/v1/returns:calculate",
        json=build_payload()
    )

    assert response.status_code == 200
    assert response.json() == {"final_amount": 15000}


# -------------------------------------------------
# Test 2 — Engine Returns Error
# -------------------------------------------------
@patch("subprocess.Popen")
def test_engine_failure(mock_popen):
    mock_process = MagicMock()
    mock_process.communicate.return_value = ("", "Engine crashed")
    mock_process.returncode = 1
    mock_popen.return_value = mock_process

    response = client.post(
        "/blackrock/challenge/v1/returns:calculate",
        json=build_payload()
    )

    assert response.status_code == 500
    assert "C++ Engine Error" in response.json()["detail"]


# -------------------------------------------------
# Test 3 — Engine Binary Not Found
# -------------------------------------------------
@patch("subprocess.Popen", side_effect=FileNotFoundError)
def test_engine_not_found(mock_popen):
    response = client.post(
        "/blackrock/challenge/v1/returns:calculate",
        json=build_payload()
    )

    assert response.status_code == 500
    assert "not found" in response.json()["detail"]


# -------------------------------------------------
# Test 4 — Ensure Only Valid Transactions Sent
# -------------------------------------------------
@patch("subprocess.Popen")
def test_only_valid_transactions_sent(mock_popen):
    mock_process = MagicMock()
    mock_process.communicate.return_value = (
        json.dumps({"ok": True}),
        ""
    )
    mock_process.returncode = 0
    mock_popen.return_value = mock_process

    client.post(
        "/blackrock/challenge/v1/returns:calculate",
        json=build_payload()
    )

    # Extract the payload sent to C++ engine
    args, kwargs = mock_process.communicate.call_args
    sent_payload = json.loads(kwargs["input"])

    # Only 1 transaction should be sent (status == "valid")
    assert len(sent_payload["transactions"]) == 1
    assert sent_payload["transactions"][0]["status"] == "valid"