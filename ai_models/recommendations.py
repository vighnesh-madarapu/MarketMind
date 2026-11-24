
def generate_recommendations(campaigns):
    """
    Generate rule-based marketing recommendations
    using campaign performance metrics.
    """

    recommendations = []

    if not campaigns:
        return [{
            "title": "Start Your First Campaign",
            "description": (
                "Create your first marketing campaign to "
                "start tracking business performance."
            ),
            "priority": "High"
        }]

    total_budget = 0
    total_revenue = 0
    total_impressions = 0
    total_clicks = 0
    total_conversions = 0

    for campaign in campaigns:

        name = campaign["campaign_name"]

        impressions = float(campaign["impressions"] or 0)
        clicks = float(campaign["clicks"] or 0)
        conversions = float(campaign["conversions"] or 0)
        budget = float(campaign["budget"] or 0)
        revenue = float(campaign["revenue"] or 0)

        total_budget += budget
        total_revenue += revenue
        total_impressions += impressions
        total_clicks += clicks
        total_conversions += conversions

        ctr = (
            clicks / impressions * 100
            if impressions else 0
        )

        conversion_rate = (
            conversions / clicks * 100
            if clicks else 0
        )

        roi = (
            (revenue - budget) / budget * 100
            if budget else 0
        )

        # Engagement analysis
        if impressions > 0 and ctr < 2:
            recommendations.append({
                "title": f"Improve {name} Engagement",
                "description": (
                    f"Current CTR is {ctr:.2f}%. "
                    "Improve ad creatives, headlines and "
                    "audience targeting."
                ),
                "priority": "High"
            })

        # Conversion analysis
        if clicks >= 10 and conversion_rate < 2:
            recommendations.append({
                "title": f"Increase {name} Conversions",
                "description": (
                    f"Conversion rate is {conversion_rate:.2f}%. "
                    "Review landing page content and call-to-action."
                ),
                "priority": "Medium"
            })

        # ROI analysis
        if budget > 0 and roi < 0:
            recommendations.append({
                "title": f"Review {name} Budget",
                "description": (
                    f"Campaign ROI is {roi:.2f}%. "
                    "Review spending and campaign targeting."
                ),
                "priority": "High"
            })

        # Good performance
        if ctr >= 5 and conversion_rate >= 5 and roi > 0:
            recommendations.append({
                "title": f"Strong Performance: {name}",
                "description": (
                    "This campaign has strong engagement, "
                    "conversions and positive ROI. "
                    "Consider maintaining its current strategy."
                ),
                "priority": "Low"
            })

        # No impressions
        if impressions == 0:
            recommendations.append({
                "title": f"Check {name} Campaign Activity",
                "description": (
                    "No impressions have been recorded. "
                    "Check campaign status and tracking data."
                ),
                "priority": "Medium"
            })

    # Overall campaign analysis
    overall_ctr = (
        total_clicks / total_impressions * 100
        if total_impressions else 0
    )

    overall_conversion = (
        total_conversions / total_clicks * 100
        if total_clicks else 0
    )

    overall_roi = (
        (total_revenue - total_budget) / total_budget * 100
        if total_budget else 0
    )

    if total_impressions > 0 and overall_ctr < 2:
        recommendations.append({
            "title": "Overall Engagement Needs Improvement",
            "description": (
                f"Overall CTR is {overall_ctr:.2f}%. "
                "Focus on improving marketing creatives "
                "and audience targeting."
            ),
            "priority": "High"
        })

    if total_clicks >= 10 and overall_conversion < 2:
        recommendations.append({
            "title": "Improve Overall Conversion Strategy",
            "description": (
                "Your overall conversion rate needs attention. "
                "Review landing pages and customer journeys."
            ),
            "priority": "Medium"
        })

    if total_budget > 0 and overall_roi < 0:
        recommendations.append({
            "title": "Optimize Overall Marketing Spending",
            "description": (
                "Total campaign spending is higher than "
                "total revenue. Review campaign budgets."
            ),
            "priority": "High"
        })

    # Remove duplicate recommendations
    unique_recommendations = []
    seen_titles = set()

    for item in recommendations:
        if item["title"] not in seen_titles:
            unique_recommendations.append(item)
            seen_titles.add(item["title"])

    if not unique_recommendations:
        unique_recommendations.append({
            "title": "Maintain Marketing Performance",
            "description": (
                "No major performance issues were identified. "
                "Continue monitoring your campaigns regularly."
            ),
            "priority": "Low"
        })

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    unique_recommendations.sort(
        key=lambda item: priority_order.get(
            item["priority"], 4
        )
    )

    return unique_recommendations
