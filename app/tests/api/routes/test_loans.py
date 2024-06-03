from decimal import Decimal

from sqlmodel import Session
from fastapi.testclient import TestClient

from app.core.config import settings
from app.tests.utils.loan import create_loan
from app.tests.utils.user import create_random_user, authentication_token_from_email


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


def test_fetch_loans(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user = create_random_user(db)
    create_loan(db, user=user, amount=1, annual_interest_rate=0, loan_term=1)
    create_loan(db, user=user, amount=2, annual_interest_rate=0, loan_term=2)
    create_loan(db, user=user, amount=3, annual_interest_rate=0, loan_term=3)
    create_loan(db,            amount=4, annual_interest_rate=0, loan_term=4)
    response = client.get(
        f"{settings.API_V1_STR}/loans/",
        headers=authentication_token_from_email(client=client, email=user.email, db=db),
    )
    assert response.status_code == 200
    content = response.json()
    assert content['count'] == 3
    assert len(content["data"]) == 3
    assert {1,2,3} == set(r['loan_term'] for r in content['data'])


def test_fetch_loans_no_loans(client, db):
    user = create_random_user(db)
    response = client.get(
        f"{settings.API_V1_STR}/loans/",
        headers=authentication_token_from_email(client=client, email=user.email, db=db),
    )
    assert response.status_code == 200
    content = response.json()
    assert content['count'] == 0
    assert len(content["data"]) == 0


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


def test_fetch_loan_summary_loan_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    non_existing_loan_id = 999999
    response = client.get(
        f"{settings.API_V1_STR}/loans/{non_existing_loan_id}/summary?month=1",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Loan not found"


def test_fetch_loan_summary_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    loan = create_loan(db, amount=10, annual_interest_rate=0, loan_term=12)
    response = client.get(
        f"{settings.API_V1_STR}/loans/{loan.id}/summary?month=1",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Loan not found"


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


def test_share_loan(client, db):
    owner = create_random_user(db)
    loan = create_loan(db, user=owner, amount=1, annual_interest_rate=0, loan_term=1)
    user = create_random_user(db)
    response = client.put(
        f"{settings.API_V1_STR}/loans/{loan.id}/share?email={user.email}",
        headers=authentication_token_from_email(client=client, db=db, email=owner.email),
    )
    assert response.status_code == 200


def test_share_loan_does_not_leak_loan_existence(client, normal_user_token_headers, db):
    user = create_random_user(db)
    response = client.put(
        f"{settings.API_V1_STR}/loans/99999/share?email={user.email}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200


def test_share_loan_with_user_does_not_leak_user_existence(client, db):
    owner = create_random_user(db)
    loan = create_loan(db, user=owner, amount=1, annual_interest_rate=0, loan_term=1)
    response = client.put(
        f"{settings.API_V1_STR}/loans/{loan.id}/share?email=nonexistinguser@nonexisting.com",
        headers=authentication_token_from_email(client=client, db=db, email=owner.email),
    )
    assert response.status_code == 200


def test_share_loan_not_enough_permissions_does_not_leak_loan_existence(
            client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    owner = create_random_user(db)
    loan = create_loan(db, user=owner, amount=1, annual_interest_rate=0, loan_term=1)
    response = client.put(
        f"{settings.API_V1_STR}/loans/{loan.id}/share?email={settings.FIRST_SUPERUSER}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
