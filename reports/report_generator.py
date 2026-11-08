
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)


def generate_marketing_report(
    user_name,
    campaigns,
    total_campaigns=0,
    total_budget=0,
    total_revenue=0
):
    """
    Generate a professional MarketMind marketing report.

    Returns:
        BytesIO: Generated PDF file in memory.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=42,
        bottomMargin=42
    )

    # Premium report colors
    navy = colors.HexColor("#25283B")
    purple = colors.HexColor("#7770A8")
    light_purple = colors.HexColor("#EEECF7")
    light_gray = colors.HexColor("#F6F7FA")
    text_gray = colors.HexColor("#737789")
    green = colors.HexColor("#648B78")

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=31,
        textColor=navy,
        alignment=TA_LEFT,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        textColor=text_gray,
        spaceAfter=15
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=19,
        textColor=navy,
        spaceBefore=15,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        name="SmallText",
        parent=styles["Normal"],
        fontSize=8,
        leading=12,
        textColor=text_gray
    ))

    styles.add(ParagraphStyle(
        name="MetricValue",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=navy,
        alignment=TA_CENTER
    ))

    story = []

    # Header
    story.append(Paragraph("MARKETMIND", ParagraphStyle(
        name="Brand",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=purple,
        spaceAfter=12
    )))

    story.append(Paragraph(
        "Marketing Performance Report",
        styles["ReportTitle"]
    ))

    story.append(Paragraph(
        f"Prepared for: {user_name} | "
        f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
        styles["ReportSubtitle"]
    ))

    story.append(HRFlowable(
        width="100%",
        thickness=1,
        color=light_purple,
        spaceAfter=18
    ))

    # Summary metrics
    story.append(Paragraph(
        "Executive Summary",
        styles["SectionHeading"]
    ))

    metrics = [
        [
            Paragraph("TOTAL CAMPAIGNS", styles["SmallText"]),
            Paragraph("TOTAL BUDGET", styles["SmallText"]),
            Paragraph("TOTAL REVENUE", styles["SmallText"])
        ],
        [
            Paragraph(str(total_campaigns), styles["MetricValue"]),
            Paragraph(f"Rs. {total_budget:,.2f}", styles["MetricValue"]),
            Paragraph(f"Rs. {total_revenue:,.2f}", styles["MetricValue"])
        ]
    ]

    summary_table = Table(
        metrics,
        colWidths=[2.15 * inch] * 3,
        rowHeights=[25, 42]
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light_gray),
        ("BOX", (0, 0), (-1, -1), 0.7, light_purple),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 18))

    # Campaign details
    story.append(Paragraph(
        "Campaign Performance Details",
        styles["SectionHeading"]
    ))

    table_data = [[
        "Campaign",
        "Platform",
        "Impressions",
        "Clicks",
        "Conversions",
        "Revenue"
    ]]

    for campaign in campaigns:
        table_data.append([
            str(campaign["campaign_name"]),
            str(campaign["platform"]),
            f'{campaign["impressions"]:,}',
            f'{campaign["clicks"]:,}',
            f'{campaign["conversions"]:,}',
            f'Rs. {campaign["revenue"]:,.2f}'
        ])

    if len(table_data) == 1:
        table_data.append([
            "No campaigns",
            "-",
            "0",
            "0",
            "0",
            "Rs. 0.00"
        ])

    campaign_table = Table(
        table_data,
        colWidths=[
            1.25 * inch,
            0.85 * inch,
            0.85 * inch,
            0.65 * inch,
            0.85 * inch,
            1.0 * inch
        ],
        repeatRows=1
    )

    campaign_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.4, light_purple),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            light_gray
        ]),
        ("TEXTCOLOR", (0, 1), (-1, -1), navy),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(campaign_table)
    story.append(Spacer(1, 18))

    # Performance insights
    story.append(Paragraph(
        "Marketing Insights",
        styles["SectionHeading"]
    ))

    if campaigns:
        total_impressions = sum(
            int(c["impressions"] or 0) for c in campaigns
        )
        total_clicks = sum(
            int(c["clicks"] or 0) for c in campaigns
        )
        total_conversions = sum(
            int(c["conversions"] or 0) for c in campaigns
        )

        ctr = (
            total_clicks / total_impressions * 100
            if total_impressions else 0
        )

        conversion_rate = (
            total_conversions / total_clicks * 100
            if total_clicks else 0
        )

        insights = [
            f"Total impressions: {total_impressions:,}",
            f"Total clicks: {total_clicks:,}",
            f"Total conversions: {total_conversions:,}",
            f"Overall click-through rate (CTR): {ctr:.2f}%",
            f"Overall conversion rate: {conversion_rate:.2f}%"
        ]
    else:
        insights = [
            "No campaign data is available yet.",
            "Add campaigns to generate performance insights."
        ]

    for insight in insights:
        story.append(Paragraph(
            f"&bull; {insight}",
            styles["Normal"]
        ))
        story.append(Spacer(1, 5))

    # Closing note
    story.append(Spacer(1, 18))

    story.append(HRFlowable(
        width="100%",
        thickness=0.7,
        color=light_purple,
        spaceAfter=10
    ))

    story.append(Paragraph(
        "This report is generated by MarketMind Digital Marketing "
        "Intelligence Platform. The metrics are based on the campaign "
        "data available in the system at the time of generation.",
        styles["SmallText"]
    ))

    # Footer
    def add_footer(canvas, doc):
        canvas.saveState()

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(text_gray)

        canvas.drawString(
            42,
            25,
            "MarketMind | Marketing Intelligence"
        )

        canvas.drawRightString(
            A4[0] - 42,
            25,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    document.build(
        story,
        onFirstPage=add_footer,
        onLaterPages=add_footer
    )

    buffer.seek(0)

    return buffer
