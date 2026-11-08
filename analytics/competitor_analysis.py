
def analyze_competitors(competitors):
    """
    Analyze competitor social media performance.
    """

    results = []
    total_followers = 0
    total_engagement = 0

    for competitor in competitors:

        name = competitor["competitor_name"]
        platform = competitor["platform"] or "Other"
        followers = int(competitor["followers"] or 0)
        engagement = float(
            competitor["engagement_rate"] or 0
        )

        results.append({
            "competitor_name": name,
            "platform": platform,
            "followers": followers,
            "engagement_rate": round(engagement, 2)
        })

        total_followers += followers
        total_engagement += engagement

    count = len(results)

    average_engagement = (
        total_engagement / count if count else 0
    )

    platform_summary = {}

    for item in results:
        platform = item["platform"]

        if platform not in platform_summary:
            platform_summary[platform] = {
                "competitor_count": 0,
                "total_followers": 0,
                "total_engagement": 0
            }

        platform_summary[platform]["competitor_count"] += 1
        platform_summary[platform]["total_followers"] += item["followers"]
        platform_summary[platform]["total_engagement"] += item["engagement_rate"]

    for platform, data in platform_summary.items():
        platform_count = data["competitor_count"]

        data["average_engagement"] = round(
            data["total_engagement"] / platform_count,
            2
        )

        del data["total_engagement"]

    return {
        "competitors": results,
        "summary": {
            "total_competitors": count,
            "total_followers": total_followers,
            "average_engagement": round(
                average_engagement, 2
            )
        },
        "platform_summary": platform_summary
    }


def get_top_competitor(competitors):
    """
    Identify competitor with highest follower count.
    """

    if not competitors:
        return None

    return max(
        competitors,
        key=lambda item: int(item["followers"] or 0)
    )


def get_top_engagement_competitor(competitors):
    """
    Identify competitor with highest engagement rate.
    """

    if not competitors:
        return None

    return max(
        competitors,
        key=lambda item: float(
            item["engagement_rate"] or 0
        )
    )


def compare_competitors(competitors):
    """
    Rank competitors by engagement rate.
    """

    ranked = sorted(
        competitors,
        key=lambda item: float(
            item["engagement_rate"] or 0
        ),
        reverse=True
    )

    comparison = []

    for index, competitor in enumerate(ranked, start=1):

        comparison.append({
            "rank": index,
            "competitor_name": competitor["competitor_name"],
            "platform": competitor["platform"] or "Other",
            "followers": int(competitor["followers"] or 0),
            "engagement_rate": round(
                float(competitor["engagement_rate"] or 0),
                2
            )
        })

    return comparison


def generate_competitor_insights(competitors):
    """
    Generate rule-based competitor marketing insights.
    """

    if not competitors:
        return [
            "Add competitor details to start competitor analysis."
        ]

    insights = []

    top_followers = get_top_competitor(competitors)
    top_engagement = get_top_engagement_competitor(competitors)

    if top_followers:
        insights.append(
            f'{top_followers["competitor_name"]} has the highest '
            f'follower count with '
            f'{int(top_followers["followers"] or 0):,} followers.'
        )

    if top_engagement:
        insights.append(
            f'{top_engagement["competitor_name"]} has the highest '
            f'engagement rate of '
            f'{float(top_engagement["engagement_rate"] or 0):.2f}%.'
        )

    average_engagement = sum(
        float(item["engagement_rate"] or 0)
        for item in competitors
    ) / len(competitors)

    insights.append(
        f"Average competitor engagement rate is "
        f"{average_engagement:.2f}%."
    )

    if average_engagement >= 5:
        insights.append(
            "Competitors show strong recorded engagement. "
            "Study their content themes and audience interactions."
        )
    else:
        insights.append(
            "There may be opportunities to improve content quality "
            "and audience engagement."
        )

    return insights
