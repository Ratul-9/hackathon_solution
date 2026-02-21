import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_build_transactions_success():
    payload = [
        {"date": "2026-02-20", "amount": 250},
        {"date": "2026-02-21", "amount": 90}
    ]

    response = client.post(
        "/blackrock/challenge/v1/transactions:parse",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2

    # First transaction
    assert data[0]["id"] == "txn_0"
    assert data[0]["ceiling"] == 300
    assert data[0]["remanent"] == 50
    assert data[0]["status"] == "valid"

    # Second transaction
    assert data[1]["ceiling"] == 100
    assert data[1]["remanent"] == 10


def test_build_transactions_invalid_amount():
    payload = [
        {"date": "2026-02-20", "amount": -10}
    ]

    response = client.post(
        "/blackrock/challenge/v1/transactions:parse",
        json=payload
    )

    # Pydantic validation should fail
    assert response.status_code == 422