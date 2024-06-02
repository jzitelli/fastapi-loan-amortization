from decimal import Decimal
from pytest import approx

from app.amortization_calculator import calc_monthly_payment, calc_amortization_schedule, round_to_nearest_cent, calc_monthly_summary


def test_round_to_nearest_cent():
    assert Decimal('0.01') == round_to_nearest_cent('0.005')
    assert Decimal('-0.01') == round_to_nearest_cent('-0.005')
    assert 0 == round_to_nearest_cent('0.0049')
    assert 0 == round_to_nearest_cent('-0.0049')


def test_calc_monthly_payment():
    "Example from https://www.investopedia.com/terms/a/amortization.asp#toc-example-of-amortization"
    A = calc_monthly_payment(30000.0, 0.03, 48)
    assert A == approx(664.03, abs=0.005)


def test_calc_monthly_payment_zero_interest():
    A = calc_monthly_payment(30000.0, 0.0, 48)
    assert A == approx(30000.0 / 48, abs=0.005)


def test_calc_amortization_schedule():
    schedule = calc_amortization_schedule(30000.0, 0.03, 48)
    assert 48 == len(schedule)
    assert abs(schedule[-1]['remaining_balance']) < 1e-9


def test_calc_monthly_summary_last_month_principal_fully_paid():
    principal_amount = 200000
    summary = calc_monthly_summary(principal_amount, 0.03, 48, 48)
    assert summary['aggregate_principal_paid'] == principal_amount
