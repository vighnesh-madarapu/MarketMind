
from analytics.campaign_analysis import analyze_campaign_performance


def get_performance_overview(campaigns):
    """
    Generate an overall marketing performance overview.
    """

    analysis = analyze_campaign_performance(campaigns)
    summary = analysis["summary"]

    return {
        "total_campaigns": summary["total_campaigns"],
        "total_impressions": summary["total_impressions"],
        "total_clicks": summary["total_clicks"],
        "total_conversions": summary["total_conversions"],
        "total_budget": summary["total_budget"],
        "total_revenue": summary["total_revenue"],
        "ctr": summary["ctr"],
        "conversion_rate": summary["conversion_rate"],
        "roi": summary["roi"]
    }


def get_platform_performance(campaigns):
    """
    Group campaign metrics by marketing platform.
    """

    platforms = {}

    for campaign in campaigns:

        platform = campaign["platform"] or "Other"

        if platform not in platforms:
            platforms[platform] = {
                "campaign_count": 0,
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "budget": 0.0,
                "revenue": 0.0
            }

        platforms[platform]["campaign_count"] += 1
        platforms[platform]["impressions"] += int(
            campaign["impressions"] or 0
        )
        platforms[platform]["clicks"] += int(
            campaign["clicks"] or 0
        )
        platforms[platform]["conversions"] += int(
            campaign["conversions"] or 0
        )
        platforms[platform]["budget"] += float(
            campaign["budget"] or 0
        )
        platforms[platform]["revenue"] += float(
            campaign["revenue"] or 0
        )

    for platform, metrics in platforms.items():

        impressions = metrics["impressions"]
        clicks = metrics["clicks"]
        conversions = metrics["conversions"]
        budget = metrics["budget"]
        revenue = metrics["revenue"]

        metrics["ctr"] = round(
            (clicks / impressions) * 100
            if impressions else 0,
            2
        )

        metrics["conversion_rate"] = round(
            (conversions / clicks) * 100
            if clicks else 0,
            2
        )

        metrics["roi"] = round(
            ((revenue - budget) / budget) * 100
            if budget else 0,
            2
        )

        metrics["budget"] = round(budget, 2)
        metrics["revenue"] = round(revenue, 2)

    return platforms


def get_top_campaigns(campaigns, limit=5):
    """
    Return top campaigns sorted by revenue.
    """

    return sorted(
        campaigns,
        key=lambda campaign: float(campaign["revenue"] or 0),
        reverse=True
    )[:limit]


def get_underperforming_campaigns(campaigns):
    """
    Identify campaigns with low CTR or no conversions.
    """

    underperforming = []

    for campaign in campaigns:

        impressions = int(campaign["impressions"] or 0)
        clicks = int(campaign["clicks"] or 0)
        conversions = int(campaign["conversions"] or 0)

        ctr = (
            (clicks / impressions) * 100
            if impressions else 0
        )

        if impressions > 0 and (ctr < 1 or conversions == 0):
            underperforming.append({
                "campaign_name": campaign["campaign_name"],
                "platform": campaign["platform"],
                "ctr": round(ctr, 2),
                "conversions": conversions,
                "reason": (
                    "Low click-through rate"
                    if ctr < 1
                    else "No recorded conversions"
                )
            })

    return underperforming
