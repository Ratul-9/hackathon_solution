import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

BASE_TXN = {
    "id": "txn_1",
    "amount": 100,
    "ceiling": 100,
    "remanent": 0,
    "status": "valid"
}


# ✅ 1. Fully Valid Payload
def test_filter_all_valid():
    payload = {
        "wage": 500000,
        "transactions": [
            {**BASE_TXN, "date": "2026-01-01 10:00:00"},
            {**BASE_TXN, "id": "txn_2", "date": "2026-01-02 10:00:00"},
        ],
        "q_periods": [{
            "start": "2026-01-01 10:00:00",
            "end": "2026-01-02 10:00:00",
            "fixed": 100
        }],
        "p_periods": [{
            "start": "2026-01-01 10:00:00",
            "end": "2026-01-02 10:00:00",
            "extra": 50
        }],
        "k_periods": [{
            "start": "2026-01-01 10:00:00",
            "end": "2026-01-30 00:00:00"
        }]
    }

    response = client.post(
        "/blackrock/challenge/v1/transactions:filter",
        json=payload
    )

    data = response.json()
    assert response.status_code == 200
    assert data["is_payload_safe_for_engine"] is True
    assert len(data["invalid_transactions"]) == 0


# ❌ 2. Invalid timestamp format
def test_invalid_timestamp_format():
    payload = {
        "wage": 500000,
        "transactions": [
            {**BASE_TXN, "date": "2026-01-01"}  # wrong format
        ],
        "q_periods": [],
        "p_periods": [],
        "k_periods": []
    }

    response = client.post(
        "/blackrock/challenge/v1/transactions:filter",
        json=payload
    )

    data = response.json()
    assert len(data["invalid_transactions"]) == 1


# ❌ 3. Duplicate timestamp
def test_duplicate_timestamp():
    payload = {
        "wage": 500000,
        "transactions": [
            {**BASE_TXN, "date": "2026-01-01 10:00:00"},
            {**BASE_TXN, "id": "txn_2", "date": "2026-01-01 10:00:00"},
        ],
        "q_periods": [],
        "p_periods": [],
        "k_periods": []
    }

    response = client.post(
        "/blackrock/challenge/v1/transactions:filter",
        json=payload
    )

    data = response.json()
    assert len(data["invalid_transactions"]) == 1


# ❌ 4. Period start after end
def test_period_start_after_end():
    payload = {
        "wage": 500000,
        "transactions": [
            {**BASE_TXN, "date": "2026-01-05 10:00:00"}
        ],
        "q_periods": [{
            "start": "2026-01-06 10:00:00",
            "end": "2026-01-05 10:00:00",
            "fixed": 10
        }],
        "p_periods": [],
        "k_periods": []
    }

    response = client.post(
        "/blackrock/challenge/v1/transactions:filter",
        json=payload
    )

    assert response.json()["is_payload_safe_for_engine"] is False


# ❌ 5. Out-of-bounds
def test_period_out_of_bounds():
    payload = {
        "wage": 500000,
        "transactions": [
            {**BASE_TXN, "date": "2026-01-05 10:00:00"},
            {**BASE_TXN, "id": "txn_2", "date": "2026-01-10 10:00:00"}
        ],
        "q_periods": [{
            "start": "2025-12-01 00:00:00",
            "end": "2026-01-10 10:00:00",
            "fixed": 10
        }],
        "p_periods": [],
        "k_periods": []
    }

    response = client.post(
        "/blackrock/challenge/v1/transactions:filter",
        json=payload
    )

    assert response.json()["is_payload_safe_for_engine"] is False


# ❌ 6. K-period multi-year
def test_k_period_multi_year():
    payload = {
        "wage": 500000,
        "transactions": [
            {**BASE_TXN, "date": "2026-01-05 10:00:00"}
        ],
        "q_periods": [],
        "p_periods": [],
        "k_periods": [{
            "start": "2025-12-31 00:00:00",
            "end": "2026-01-05 00:00:00"
        }]
    }

    response = client.post(
        "/blackrock/challenge/v1/transactions:filter",
        json=payload
    )

    assert response.json()["is_payload_safe_for_engine"] is False


# ❌ 7. Q-period missing fixed
def test_q_period_missing_fixed():
    payload = {
        "wage": 500000,
        "transactions": [
            {**BASE_TXN, "date": "2026-01-05 10:00:00"}
        ],
        "q_periods": [{
            "start": "2026-01-05 10:00:00",
            "end": "2026-01-05 12:00:00"
        }],
        "p_periods": [],
        "k_periods": []
    }

    response = client.post(
        "/blackrock/challenge/v1/transactions:filter",
        json=payload
    )

    assert response.json()["is_payload_safe_for_engine"] is False


# ❌ 8. P-period missing extra
def test_p_period_missing_extra():
    payload = {
        "wage": 500000,
        "transactions": [
            {**BASE_TXN, "date": "2026-01-05 10:00:00"}
        ],
        "q_periods": [],
        "p_periods": [{
            "start": "2026-01-05 10:00:00",
            "end": "2026-01-05 12:00:00"
        }],
        "k_periods": []
    }

    response = client.post(
        "/blackrock/challenge/v1/transactions:filter",
        json=payload
    )

    assert response.json()["is_payload_safe_for_engine"] is False


# ❌ 9. No valid transactions
def test_no_valid_transactions():
    payload = {
        "wage": 500000,
        "transactions": [],
        "q_periods": [],
        "p_periods": [],
        "k_periods": []
    }

    response = client.post(
        "/blackrock/challenge/v1/transactions:filter",
        json=payload
    )

    assert response.json()["is_payload_safe_for_engine"] is False