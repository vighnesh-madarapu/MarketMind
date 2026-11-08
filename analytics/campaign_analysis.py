
def analyze_campaign_performance(campaigns):
    """
    Analyze marketing campaign performance.

    Returns campaign-wise metrics and overall summary.
    """

    results = []

    total_impressions = 0
    total_clicks = 0
    total_conversions = 0
    total_revenue = 0
    total_budget = 0

    for campaign in campaigns:

        impressions = int(campaign["impressions"] or 0)
        clicks = int(campaign["clicks"] or 0)
        conversions = int(campaign["conversions"] or 0)
        revenue = float(campaign["revenue"] or 0)
        budget = float(campaign["budget"] or 0)

        ctr = (
            (clicks / impressions) * 100
            if impressions > 0 else 0
        )

        conversion_rate = (
            (conversions / clicks) * 100
            if clicks > 0 else 0
        )

        roi = (
            ((revenue - budget) / budget) * 100
            if budget > 0 else 0
        )

        result = {
            "campaign_name": campaign["campaign_name"],
            "platform": campaign["platform"],
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "budget": round(budget, 2),
            "revenue": round(revenue, 2),
            "ctr": round(ctr, 2),
            "conversion_rate": round(conversion_rate, 2),
            "roi": round(roi, 2)
        }

        results.append(result)

        total_impressions += impressions
        total_clicks += clicks
        total_conversions += conversions
        total_revenue += revenue
        total_budget += budget

    # Overall performance
    overall_ctr = (
        (total_clicks / total_impressions) * 100
        if total_impressions > 0 else 0
    )

    overall_conversion_rate = (
        (total_conversions / total_clicks) * 100
        if total_clicks > 0 else 0
    )

    overall_roi = (
        ((total_revenue - total_budget) / total_budget) * 100
        if total_budget > 0 else 0
    )

    summary = {
        "total_campaigns": len(results),
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "total_budget": round(total_budget, 2),
        "total_revenue": round(total_revenue, 2),
        "ctr": round(overall_ctr, 2),
        "conversion_rate": round(overall_conversion_rate, 2),
        "roi": round(overall_roi, 2)
    }

    return {
        "campaigns": results,
        "summary": summary
    }


def get_best_campaign(campaigns):
    """Return the campaign with the highest revenue."""

    if not campaigns:
        return None

    return max(
        campaigns,
        key=lambda campaign: float(campaign["revenue"] or 0)
    )


def get_campaign_insights(analysis):
    """Generate simple insights from campaign performance."""

    summary = analysis["summary"]
    insights = []

    if summary["total_campaigns"] == 0:
        return ["Add campaigns to view marketing performance insights."]

    if summary["ctr"] >= 3:
        insights.append(
            "Your overall click-through rate is performing well."
        )
    else:
        insights.append(
            "Consider improving your campaign content and audience targeting."
        )

    if summary["conversion_rate"] >= 2:
        insights.append(
            "Your campaigns are converting clicks into customers effectively."
        )
    else:
        insights.append(
            "Review your landing pages and campaign calls-to-action."
        )

    if summary["roi"] > 0:
        insights.append(
            "Your campaigns are generating revenue above the recorded budget."
        )
    elif summary["total_budget"] > 0:
        insights.append(
            "Review campaign spending and performance to improve ROI."
        )

    return insights
