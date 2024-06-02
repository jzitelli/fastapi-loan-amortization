from decimal import Decimal

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
    assert Decimal(content["amount"]) == Decimal(data['amount'])
    assert Decimal(content["annual_interest_rate"]) == Decimal(data["annual_interest_rate"])
    assert content["loan_term"] == data["loan_term"]
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
    assert all(set(r.keys()) == {'month', 'remaining_balance', 'monthly_payment'}
               for r in content)


def test_fetch_loan_schedule_loan_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    non_existing_loan_id = 999999
    response = client.get(
        f"{settings.API_V1_STR}/loans/{non_existing_loan_id}/schedule",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Loan not found"


def test_fetch_loan_schedule_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    loan = create_loan(db, amount=10, annual_interest_rate=0, loan_term=12)
    response = client.get(
        f"{settings.API_V1_STR}/loans/{loan.id}/schedule",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Loan not found"


def test_fetch_loan_summary(client: TestClient, superuser_token_headers: dict[str, str], db: Session):
    # default/calculated values from https://www.zillow.com/mortgage-calculator/amortization-schedule-calculator
    data = {"amount": "200000.00", "annual_interest_rate": ".0657", "loan_term": 30*12}
    loan = create_loan(db, **data)
    response = client.get(
        f"{settings.API_V1_STR}/loans/{loan.id}/summary?month={data['loan_term']}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert set(content.keys()) == {'remaining_balance', 'aggregate_principal_paid', 'aggregate_interest_paid'}


def test_fetch_loan_summary_month_zero_is_invalid(client, superuser_token_headers, db):
    loan = create_loan(db, amount=10000.0, annual_interest_rate=0, loan_term=12)
    response = client.get(
        f"{settings.API_V1_STR}/loans/{loan.id}/summary?month=0",
        headers=superuser_token_headers,
    )
    assert response.status_code == 422


def test_fetch_loan_summary_negative_month_is_invalid(client, superuser_token_headers, db):
    loan = create_loan(db, amount=10000.0, annual_interest_rate=0, loan_term=12)
    response = client.get(
        f"{settings.API_V1_STR}/loans/{loan.id}/summary?month=-1",
        headers=superuser_token_headers,
    )
    assert response.status_code == 422


def test_fetch_loan_summary_month_gt_loan_term_is_invalid(client, superuser_token_headers, db):
    loan = create_loan(db, amount=10000.0, annual_interest_rate=0, loan_term=12)
    response = client.get(
        f"{settings.API_V1_STR}/loans/{loan.id}/summary?month=13",
        headers=superuser_token_headers,
    )
    assert response.status_code == 422
    content = response.json()
    assert content['detail'] == "month number exceeds loan term"
