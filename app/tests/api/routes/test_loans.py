from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_loan(client: TestClient, superuser_token_headers: dict[str, str]):
    data = {"amount": "500000.00",
            "annual_interest_rate": "0.07",
            "loan_term": 30*12}
    response = client.post(
        f"{settings.API_V1_STR}/loans/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["amount"] == float(data['amount'])
    assert content["annual_interest_rate"] == float(data["annual_interest_rate"])
    assert content["loan_term"] == float(data["loan_term"])
    assert "id" in content
    assert "owner_id" in content
