
def calculate_roi(revenue, investment):
    """
    Calculate Return on Investment (ROI).

    ROI = ((Revenue - Investment) / Investment) * 100
    """

    revenue = float(revenue or 0)
    investment = float(investment or 0)

    if investment <= 0:
        return 0.0

    roi = ((revenue - investment) / investment) * 100

    return round(roi, 2)


def calculate_roas(revenue, advertising_cost):
    """
    Calculate Return on Ad Spend (ROAS).

    ROAS = Revenue / Advertising Cost
    """

    revenue = float(revenue or 0)
    advertising_cost = float(advertising_cost or 0)

    if advertising_cost <= 0:
        return 0.0

    return round(revenue / advertising_cost, 2)


def calculate_profit(revenue, investment):
    """Calculate profit or loss from campaign investment."""

    revenue = float(revenue or 0)
    investment = float(investment or 0)

    return round(revenue - investment, 2)


def calculate_campaign_metrics(campaign):
    """
    Calculate complete financial metrics for one campaign.
    """

    budget = float(campaign["budget"] or 0)
    revenue = float(campaign["revenue"] or 0)

    return {
        "campaign_name": campaign["campaign_name"],
        "budget": round(budget, 2),
        "revenue": round(revenue, 2),
        "profit": calculate_profit(revenue, budget),
        "roi": calculate_roi(revenue, budget),
        "roas": calculate_roas(revenue, budget)
    }


def calculate_total_metrics(campaigns):
    """Calculate combined financial performance."""

    total_budget = 0
    total_revenue = 0

    for campaign in campaigns:
        total_budget += float(campaign["budget"] or 0)
        total_revenue += float(campaign["revenue"] or 0)

    return {
        "total_budget": round(total_budget, 2),
        "total_revenue": round(total_revenue, 2),
        "total_profit": calculate_profit(
            total_revenue,
            total_budget
        ),
        "overall_roi": calculate_roi(
            total_revenue,
            total_budget
        ),
        "overall_roas": calculate_roas(
            total_revenue,
            total_budget
        )
    }
