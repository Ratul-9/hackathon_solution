import pytest
from fastapi.testclient import TestClient
from api.main import app   # keep absolute import

client = TestClient(app)


def test_validator_all_valid():
    payload = {
        "wage": 5000000,   # 10% = 500000 (limit capped at 200000)
        "transactions": [
            {
                "id": "txn_1",
                "date": "2026-02-20",
                "amount": 250,
                "ceiling": 300,
                "remanent": 50,
                "status": "valid"
            },
            {
                "id": "txn_2",
                "date": "2026-02-21",
                "amount": 90,
                "ceiling": 100,
                "remanent": 10,
                "status": "valid"
            }
        ]
    }

    response = client.post(
        "/blackrock/challenge/v1/transactions:validator",
        json=payload
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data["valid"]) == 2
    assert len(data["invalid"]) == 0
    assert len(data["duplicates"]) == 0


def test_validator_exceeds_limit():
    payload = {
        "wage": 100000,  # 10% = 10,000 limit
        "transactions": [
            {
                "id": "txn_1",
                "date": "2026-02-20",
                "amount": 1000,
                "ceiling": 1100,
                "remanent": 10000,   # hits limit
                "status": "valid"
            },
            {
                "id": "txn_2",
                "date": "2026-02-21",
                "amount": 1000,
                "ceiling": 1100,
                "remanent": 5000,  # exceeds remaining capacity
                "status": "valid"
            }
        ]
    }

    response = client.post(
        "/blackrock/challenge/v1/transactions:validator",
        json=payload
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data["valid"]) == 1
    assert len(data["invalid"]) == 1
    assert data["invalid"][0]["status"] == "invalid_exceeds_limit"


def test_validator_duplicates():
    payload = {
        "wage": 500000,
        "transactions": [
            {
                "id": "txn_1",
                "date": "2026-02-20",
                "amount": 250,
                "ceiling": 300,
                "remanent": 50,
                "status": "valid"
            },
            {
                "id": "txn_1",   # duplicate id
                "date": "2026-02-21",
                "amount": 90,
                "ceiling": 100,
                "remanent": 10,
                "status": "valid"
            }
        ]
    }

    response = client.post(
        "/blackrock/challenge/v1/transactions:validator",
        json=payload
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data["duplicates"]) == 1
    assert data["duplicates"][0]["status"] == "duplicate"


def test_validator_invalid_wage():
    payload = {
        "wage": -1000,   # invalid
        "transactions": []
    }

    response = client.post(
        "/blackrock/challenge/v1/transactions:validator",
        json=payload
    )

    assert response.status_code == 422