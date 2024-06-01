from sqlmodel import Session
from fastapi.testclient import TestClient

from app.core.config import settings
from app.tests.utils.loan import create_loan


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


def test_fetch_loan_schedule(client: TestClient, superuser_token_headers: dict[str, str], db: Session):
    data = {"amount": "500000.00", "annual_interest_rate": "0.07", "loan_term": 30*12}
    loan = create_loan(db, **data)
    response = client.get(
        f"{settings.API_V1_STR}/loans/{loan.id}/schedule",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert type(content) is list
    assert len(content) == data['loan_term']
    expected_keys = ['month', 'remaining_balance', 'monthly_payment']
    assert all(set(r.keys()) == set(expected_keys) for r in content)


# def test_read_item_not_found(
#     client: TestClient, superuser_token_headers: dict[str, str]
# ) -> None:
#     response = client.get(
#         f"{settings.API_V1_STR}/items/999",
#         headers=superuser_token_headers,
#     )
#     assert response.status_code == 404
#     content = response.json()
#     assert content["detail"] == "Item not found"
#
#
# def test_read_item_not_enough_permissions(
#     client: TestClient, normal_user_token_headers: dict[str, str], db: Session
# ) -> None:
#     item = create_random_item(db)
#     response = client.get(
#         f"{settings.API_V1_STR}/items/{item.id}",
#         headers=normal_user_token_headers,
#     )
#     assert response.status_code == 400
#     content = response.json()
#     assert content["detail"] == "Not enough permissions"
