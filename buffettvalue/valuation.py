"""Transparent DCF calculation; research only, not an execution signal."""
from math import isfinite


def dcf(free_cash_flow: float, growth: float, discount: float,
        terminal_growth: float, years: int, net_debt: float,
        shares: float, price: float) -> dict:
    values = (free_cash_flow, growth, discount, terminal_growth, net_debt, shares, price)
    if not all(not isinstance(x, bool) and isfinite(x) for x in values) or type(years) is not int or years < 1 or years > 15:
        raise ValueError('invalid inputs')
    if discount <= terminal_growth or discount <= -1 or growth <= -1 or terminal_growth <= -1 or shares <= 0 or price <= 0:
        raise ValueError('invalid DCF assumptions')
    fcf = free_cash_flow
    present_value = 0.0
    for year in range(1, years + 1):
        fcf *= 1 + growth
        present_value += fcf / (1 + discount) ** year
    terminal_value = fcf * (1 + terminal_growth) / (discount - terminal_growth)
    equity_value = present_value + terminal_value / (1 + discount) ** years - net_debt
    intrinsic = equity_value / shares
    return {'intrinsic_per_share': intrinsic, 'margin_of_safety': 1 - price / intrinsic if intrinsic > 0 else None,
            'paper_eligible': False, 'reason': 'FINANCIALS_PUBLICATION_DATES_NOT_VERIFIED'}
