from pytest import approx

from app.amortization_calculator import calc_monthly_payment, calc_amortization_schedule


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
