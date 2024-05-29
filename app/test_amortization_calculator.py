from .amortization_calculator import calc_monthly_payment
from pytest import approx

def test_calc_monthly_payment():
    "Example from https://www.investopedia.com/terms/a/amortization.asp#toc-example-of-amortization"
    A = calc_monthly_payment(30000.0, 0.03, 48)
    assert A == approx(664.03, abs=0.005)
