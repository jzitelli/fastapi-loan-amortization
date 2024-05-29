from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

def test_create_loan():
    response = client.post(
        "/loans",
        json={"amount": 100000.0, "annual_interest_rate": 0.03, "loan_term": 48},
    )
    assert response.status_code == 200
