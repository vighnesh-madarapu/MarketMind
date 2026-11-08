
def segment_customers(customers):
    """
    Group customers based on their purchase amount.

    This is a rule-based customer segmentation module.
    """

    segments = {
        "High Value": [],
        "Regular": [],
        "Potential": []
    }

    total_purchase = 0

    for customer in customers:

        amount = float(customer["purchase_amount"] or 0)
        total_purchase += amount

        if amount >= 10000:
            category = "High Value"

        elif amount >= 3000:
            category = "Regular"

        else:
            category = "Potential"

        # Keep the original customer record unchanged.
        customer_details = dict(customer)
        customer_details["segment"] = category

        segments[category].append(customer_details)

    total_customers = len(customers)

    high_value_count = len(segments["High Value"])
    regular_count = len(segments["Regular"])
    potential_count = len(segments["Potential"])

    average_purchase = (
        total_purchase / total_customers
        if total_customers else 0
    )

    segment_summary = {}

    for name, customer_list in segments.items():

        segment_total = sum(
            float(customer["purchase_amount"] or 0)
            for customer in customer_list
        )

        count = len(customer_list)

        segment_summary[name] = {
            "count": count,
            "total_purchase": round(segment_total, 2),
            "average_purchase": round(
                segment_total / count if count else 0,
                2
            )
        }

    return {
        "segments": segments,
        "total_customers": total_customers,
        "high_value_count": high_value_count,
        "regular_count": regular_count,
        "potential_count": potential_count,
        "total_purchase": round(total_purchase, 2),
        "average_purchase": round(average_purchase, 2),
        "segment_summary": segment_summary
    }


def get_customer_segment(purchase_amount):
    """
    Identify the segment of an individual customer.
    """

    amount = float(purchase_amount or 0)

    if amount >= 10000:
        return "High Value"

    elif amount >= 3000:
        return "Regular"

    return "Potential"


def get_segment_recommendations():
    """
    Generate basic marketing recommendations for each segment.
    """

    return {
        "High Value": (
            "Offer loyalty rewards and personalized product suggestions."
        ),
        "Regular": (
            "Encourage repeat purchases through relevant offers."
        ),
        "Potential": (
            "Share introductory offers and useful product information."
        )
    }
