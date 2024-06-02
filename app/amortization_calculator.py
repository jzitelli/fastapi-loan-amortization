from decimal import Decimal, ROUND_HALF_UP


ONE_CENT = Decimal('0.01')


def round_to_nearest_cent(amount):
    return Decimal(amount).quantize(ONE_CENT, rounding=ROUND_HALF_UP)


def calc_monthly_payment(principal_amount, annual_interest_rate, number_of_months):
    # https://en.wikipedia.org/wiki/Amortization_calculator#The_formula
    P = principal_amount
    i = annual_interest_rate / 12
    n = number_of_months
    if i == 0:
        return P / n
    return P * (i + i / ((1 + i)**n - 1))


def calc_amortization_schedule(principal_amount, annual_interest_rate, number_of_months):
    A = calc_monthly_payment(principal_amount, annual_interest_rate, number_of_months)
    i = annual_interest_rate / 12
    balance = principal_amount
    result = []
    for n in range(1, number_of_months+1):
        monthly_accrued_interest = balance * i
        principal_payment = A - monthly_accrued_interest
        balance -= principal_payment
        result.append({
            'month': n,
            'monthly_payment': A,
            'monthly_accrued_interest': monthly_accrued_interest,
            'remaining_balance': balance
        })
    return result


def calc_monthly_summary(principal_amount, annual_interest_rate, number_of_months, month):
    schedule = calc_amortization_schedule(principal_amount, annual_interest_rate, number_of_months)
    return {
        'remaining_balance': schedule[month-1]['remaining_balance'],
        'aggregate_principal_paid': principal_amount - schedule[month-1]['remaining_balance'],
        'aggregate_interest_paid': sum(r['monthly_accrued_interest'] for r in schedule[:month])
    }


if __name__ == "__main__":
    import json

    # four-year, $30,000 auto loan at 3% interest
    print(calc_monthly_payment(30000.0, 0.03, 48))
    print(json.dumps(calc_amortization_schedule(30000.0, 0.03, 48), indent=2))
