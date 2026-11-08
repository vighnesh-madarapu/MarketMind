
import sqlite3
from functools import wraps
from io import BytesIO
from xml.sax.saxutils import escape

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, send_file
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from config import Config
from database.database import init_db, get_db_connection

from ai_models.sentiment import analyze_sentiment
from ai_models.segmentation import segment_customers
from ai_models.recommendations import generate_recommendations


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

init_db()


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

def login_required(route_function):

    @wraps(route_function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))

        return route_function(*args, **kwargs)

    return wrapper


def admin_required(route_function):

    @wraps(route_function)
    @login_required
    def wrapper(*args, **kwargs):

        connection = get_db_connection()

        try:
            user = connection.execute(
                "SELECT role FROM users WHERE id = ?",
                (session["user_id"],)
            ).fetchone()

        finally:
            connection.close()

        if not user or user["role"] != "admin":
            flash("Admin access is required.", "error")
            return redirect(url_for("dashboard"))

        return route_function(*args, **kwargs)

    return wrapper


def get_user_campaigns(connection):

    return connection.execute(
        """
        SELECT *
        FROM campaigns
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------------------------
# SIGNUP
# --------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("signup"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("signup"))

        connection = get_db_connection()

        try:

            connection.execute(
                """
                INSERT INTO users
                (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (
                    name,
                    email,
                    generate_password_hash(password)
                )
            )

            connection.commit()

            flash(
                "Account created successfully. Please log in.",
                "success"
            )

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            flash(
                "This email is already registered.",
                "error"
            )

            return redirect(url_for("signup"))

        finally:
            connection.close()

    return render_template("signup.html")


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = get_db_connection()

        try:

            user = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()

        finally:
            connection.close()

        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            session.clear()

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"] or "user"

            flash(
                "Welcome back, " + user["name"] + "!",
                "success"
            )

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    connection = get_db_connection()

    try:

        stats = connection.execute(
            """
            SELECT
                COUNT(*) AS total_campaigns,
                COALESCE(SUM(impressions), 0) AS impressions,
                COALESCE(SUM(clicks), 0) AS clicks,
                COALESCE(SUM(conversions), 0) AS conversions,
                COALESCE(SUM(revenue), 0) AS revenue,
                COALESCE(SUM(budget), 0) AS budget
            FROM campaigns
            WHERE user_id = ?
            """,
            (session["user_id"],)
        ).fetchone()

        recent = connection.execute(
            """
            SELECT campaign_name, platform, status, created_at
            FROM campaigns
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 5
            """,
            (session["user_id"],)
        ).fetchall()

    finally:
        connection.close()

    return render_template(
        "dashboard.html",
        stats=stats,
        recent=recent
    )


# --------------------------------------------------
# CAMPAIGNS
# --------------------------------------------------

@app.route("/campaigns", methods=["GET", "POST"])
@login_required
def campaigns():

    if request.method == "POST":

        name = request.form.get(
            "campaign_name", ""
        ).strip()

        platform = request.form.get(
            "platform", ""
        ).strip()

        status = request.form.get(
            "status", "Active"
        )

        try:

            budget = float(request.form.get("budget", 0))
            impressions = int(request.form.get("impressions", 0))
            clicks = int(request.form.get("clicks", 0))
            conversions = int(request.form.get("conversions", 0))
            revenue = float(request.form.get("revenue", 0))

        except ValueError:

            flash(
                "Please enter valid numeric campaign values.",
                "error"
            )

            return redirect(url_for("campaigns"))

        if not name or not platform:

            flash(
                "Campaign name and platform are required.",
                "error"
            )

            return redirect(url_for("campaigns"))

        if min(
            budget,
            impressions,
            clicks,
            conversions,
            revenue
        ) < 0:

            flash(
                "Campaign values cannot be negative.",
                "error"
            )

            return redirect(url_for("campaigns"))

        if clicks > impressions or conversions > clicks:

            flash(
                "Clicks cannot exceed impressions, and conversions cannot exceed clicks.",
                "error"
            )

            return redirect(url_for("campaigns"))

        if status not in ("Active", "Completed", "Paused"):

            flash(
                "Please select a valid campaign status.",
                "error"
            )

            return redirect(url_for("campaigns"))

        connection = get_db_connection()

        try:

            connection.execute(
                """
                INSERT INTO campaigns
                (
                    user_id,
                    campaign_name,
                    platform,
                    budget,
                    impressions,
                    clicks,
                    conversions,
                    revenue,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    name,
                    platform,
                    budget,
                    impressions,
                    clicks,
                    conversions,
                    revenue,
                    status
                )
            )

            connection.commit()

        finally:
            connection.close()

        flash("Campaign added successfully.", "success")

        return redirect(url_for("campaigns"))

    connection = get_db_connection()

    try:
        campaign_list = get_user_campaigns(connection)

    finally:
        connection.close()

    return render_template(
        "campaigns.html",
        campaigns=campaign_list
    )


@app.route(
    "/campaigns/delete/<int:campaign_id>",
    methods=["POST"]
)
@login_required
def delete_campaign(campaign_id):

    connection = get_db_connection()

    try:

        connection.execute(
            """
            DELETE FROM campaigns
            WHERE id = ? AND user_id = ?
            """,
            (campaign_id, session["user_id"])
        )

        connection.commit()

    finally:
        connection.close()

    flash(
        "Campaign deleted if it belonged to your account.",
        "success"
    )

    return redirect(url_for("campaigns"))


# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

@app.route("/analytics")
@login_required
def analytics():

    connection = get_db_connection()

    try:

        campaign_list = get_user_campaigns(connection)

        totals = connection.execute(
            """
            SELECT
                COALESCE(SUM(impressions), 0) AS impressions,
                COALESCE(SUM(clicks), 0) AS clicks,
                COALESCE(SUM(conversions), 0) AS conversions,
                COALESCE(SUM(revenue), 0) AS revenue,
                COALESCE(SUM(budget), 0) AS budget
            FROM campaigns
            WHERE user_id = ?
            """,
            (session["user_id"],)
        ).fetchone()

    finally:
        connection.close()

    impressions = totals["impressions"]
    clicks = totals["clicks"]
    conversions = totals["conversions"]
    budget = totals["budget"]
    revenue = totals["revenue"]

    ctr = clicks / impressions * 100 if impressions else 0

    conversion_rate = (
        conversions / clicks * 100 if clicks else 0
    )

    roi = (
        (revenue - budget) / budget * 100 if budget else 0
    )

    chart_data = {
        "labels": [
            c["campaign_name"] for c in campaign_list
        ],
        "impressions": [
            c["impressions"] for c in campaign_list
        ],
        "clicks": [
            c["clicks"] for c in campaign_list
        ],
        "conversions": [
            c["conversions"] for c in campaign_list
        ],
        "revenue": [
            c["revenue"] for c in campaign_list
        ]
    }

    return render_template(
        "analytics.html",
        totals=totals,
        ctr=ctr,
        conversion_rate=conversion_rate,
        roi=roi,
        chart_data=chart_data
    )


# --------------------------------------------------
# AI INSIGHTS
# --------------------------------------------------

@app.route("/ai-insights")
@login_required
def ai_insights():

    connection = get_db_connection()

    try:

        totals = connection.execute(
            """
            SELECT
                COUNT(*) AS total_campaigns,
                COALESCE(SUM(impressions), 0) AS impressions,
                COALESCE(SUM(clicks), 0) AS clicks,
                COALESCE(SUM(conversions), 0) AS conversions,
                COALESCE(SUM(revenue), 0) AS revenue,
                COALESCE(SUM(budget), 0) AS budget
            FROM campaigns
            WHERE user_id = ?
            """,
            (session["user_id"],)
        ).fetchone()

    finally:
        connection.close()

    insights = []

    impressions = totals["impressions"]
    clicks = totals["clicks"]
    conversions = totals["conversions"]
    budget = totals["budget"]
    revenue = totals["revenue"]

    if totals["total_campaigns"] == 0:

        insights.append({
            "title": "Start with campaign data",
            "description": (
                "Add a campaign to receive performance-based insights."
            ),
            "type": "info"
        })

    else:

        ctr = clicks / impressions * 100 if impressions else 0

        conversion_rate = (
            conversions / clicks * 100 if clicks else 0
        )

        roi = (
            (revenue - budget) / budget * 100
            if budget else None
        )

        if impressions == 0:

            insights.append({
                "title": "No recorded impressions",
                "description": (
                    "Enter impression data to evaluate audience reach."
                ),
                "type": "info"
            })

        elif ctr < 2:

            insights.append({
                "title": "Review audience engagement",
                "description": (
                    f"Your overall CTR is {ctr:.2f}%. "
                    "Review creative content and audience relevance."
                ),
                "type": "warning"
            })

        else:

            insights.append({
                "title": "Engagement is being recorded",
                "description": (
                    f"Your overall CTR is {ctr:.2f}%. "
                    "Compare individual campaigns."
                ),
                "type": "success"
            })

        if clicks and conversion_rate < 2:

            insights.append({
                "title": "Explore conversion improvements",
                "description": (
                    f"Your conversion rate is {conversion_rate:.2f}%. "
                    "Review your landing page and call to action."
                ),
                "type": "warning"
            })

        elif clicks:

            insights.append({
                "title": "Conversion activity",
                "description": (
                    f"Your recorded conversion rate is "
                    f"{conversion_rate:.2f}%."
                ),
                "type": "success"
            })

        if roi is None:

            insights.append({
                "title": "Add budget information",
                "description": (
                    "Enter campaign budget to calculate ROI."
                ),
                "type": "info"
            })

        elif roi >= 0:

            insights.append({
                "title": "Positive recorded ROI",
                "description": (
                    f"Your combined ROI is {roi:.2f}%."
                ),
                "type": "success"
            })

        else:

            insights.append({
                "title": "Review campaign spending",
                "description": (
                    f"Your combined ROI is {roi:.2f}%. "
                    "Examine campaign costs and revenue."
                ),
                "type": "warning"
            })

    return render_template(
        "ai_insights.html",
        insights=insights,
        totals=totals
    )



# --------------------------------------------------
# AUDIENCE SEGMENTATION
# --------------------------------------------------

@app.route("/audience")
@login_required
def audience():

    connection = get_db_connection()

    try:
        customers = connection.execute(
            """
            SELECT *
            FROM customers
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (session["user_id"],)
        ).fetchall()

    finally:
        connection.close()

    result = segment_customers(customers)

    return render_template(
        "audience.html",
        segments=result["segments"],
        total_customers=result["total_customers"],
        high_value_count=result["high_value_count"],
        regular_count=result["regular_count"],
        potential_count=result["potential_count"],
        total_purchase=result["total_purchase"],
        average_purchase=result["average_purchase"],
        segment_summary=result["segment_summary"]
    )


# --------------------------------------------------
# SENTIMENT ANALYSIS
# --------------------------------------------------

@app.route("/sentiment", methods=["GET", "POST"])
@login_required
def sentiment():

    result = None
    feedback = ""

    if request.method == "POST":

        feedback = request.form.get(
            "feedback", ""
        ).strip()

        if feedback:
            result = analyze_sentiment(feedback)

        else:
            flash(
                "Please enter customer feedback.",
                "warning"
            )

    return render_template(
        "sentiment.html",
        result=result,
        feedback=feedback
    )


# --------------------------------------------------
# AI RECOMMENDATIONS
# --------------------------------------------------

@app.route("/recommendations")
@login_required
def recommendations():

    connection = get_db_connection()

    try:
        campaigns_list = get_user_campaigns(connection)

    finally:
        connection.close()

    suggestions = generate_recommendations(campaigns_list)

    return render_template(
        "recommendations.html",
        recommendations=suggestions
    )


# --------------------------------------------------
# COMPETITOR ANALYSIS
# --------------------------------------------------

@app.route("/competitors", methods=["GET", "POST"])
@login_required
def competitors():

    connection = get_db_connection()

    if request.method == "POST":

        name = request.form.get(
            "competitor_name", ""
        ).strip()

        platform = request.form.get(
            "platform", ""
        ).strip()

        try:

            followers = int(
                request.form.get("followers", 0)
            )

            engagement = float(
                request.form.get("engagement_rate", 0)
            )

        except ValueError:

            connection.close()

            flash(
                "Enter valid competitor numbers.",
                "error"
            )

            return redirect(url_for("competitors"))

        if not name or not platform:

            connection.close()

            flash(
                "Competitor name and platform are required.",
                "error"
            )

            return redirect(url_for("competitors"))

        if (
            followers < 0
            or engagement < 0
            or engagement > 100
        ):

            connection.close()

            flash(
                "Enter valid follower and engagement values.",
                "error"
            )

            return redirect(url_for("competitors"))

        try:

            connection.execute(
                """
                INSERT INTO competitors
                (
                    user_id,
                    competitor_name,
                    platform,
                    followers,
                    engagement_rate
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    name,
                    platform,
                    followers,
                    engagement
                )
            )

            connection.commit()

        finally:
            connection.close()

        flash(
            "Competitor added successfully.",
            "success"
        )

        return redirect(url_for("competitors"))

    try:

        competitor_list = connection.execute(
            """
            SELECT *
            FROM competitors
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (session["user_id"],)
        ).fetchall()

    finally:
        connection.close()

    return render_template(
        "competitors.html",
        competitors=competitor_list
    )


@app.route(
    "/competitors/delete/<int:competitor_id>",
    methods=["POST"]
)
@login_required
def delete_competitor(competitor_id):

    connection = get_db_connection()

    try:

        connection.execute(
            """
            DELETE FROM competitors
            WHERE id = ? AND user_id = ?
            """,
            (competitor_id, session["user_id"])
        )

        connection.commit()

    finally:
        connection.close()

    flash("Competitor deleted.", "success")

    return redirect(url_for("competitors"))


# --------------------------------------------------
# CONTENT PLANNER
# --------------------------------------------------

@app.route("/content-planner", methods=["GET", "POST"])
@login_required
def content_planner():

    connection = get_db_connection()

    if request.method == "POST":

        title = request.form.get(
            "title", ""
        ).strip()

        platform = request.form.get(
            "platform", ""
        ).strip()

        post_date = request.form.get(
            "post_date", ""
        ).strip()

        status = request.form.get(
            "status", "Planned"
        )

        if not title or not platform or not post_date:

            connection.close()

            flash(
                "Please complete all content details.",
                "error"
            )

            return redirect(url_for("content_planner"))

        if status not in (
            "Planned",
            "Published",
            "Draft"
        ):

            connection.close()

            flash(
                "Select a valid content status.",
                "error"
            )

            return redirect(url_for("content_planner"))

        try:

            connection.execute(
                """
                INSERT INTO content_posts
                (
                    user_id,
                    title,
                    platform,
                    post_date,
                    status
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    title,
                    platform,
                    post_date,
                    status
                )
            )

            connection.commit()

        finally:
            connection.close()

        flash(
            "Content plan created successfully.",
            "success"
        )

        return redirect(url_for("content_planner"))

    try:

        posts = connection.execute(
            """
            SELECT *
            FROM content_posts
            WHERE user_id = ?
            ORDER BY post_date ASC, id DESC
            """,
            (session["user_id"],)
        ).fetchall()

    finally:
        connection.close()

    return render_template(
        "content_planner.html",
        posts=posts
    )


@app.route(
    "/content-planner/delete/<int:post_id>",
    methods=["POST"]
)
@login_required
def delete_content(post_id):

    connection = get_db_connection()

    try:

        connection.execute(
            """
            DELETE FROM content_posts
            WHERE id = ? AND user_id = ?
            """,
            (post_id, session["user_id"])
        )

        connection.commit()

    finally:
        connection.close()

    flash("Content plan deleted.", "success")

    return redirect(url_for("content_planner"))


# --------------------------------------------------
# BUDGET OPTIMIZER
# --------------------------------------------------

@app.route("/budget-optimizer")
@login_required
def budget_optimizer():

    connection = get_db_connection()

    try:
        campaign_list = get_user_campaigns(connection)

    finally:
        connection.close()

    total_budget = sum(
        float(c["budget"] or 0)
        for c in campaign_list
    )

    total_revenue = sum(
        float(c["revenue"] or 0)
        for c in campaign_list
    )

    allocations = []

    if campaign_list:

        positive_revenue = sum(
            max(float(c["revenue"] or 0), 0)
            for c in campaign_list
        )

        for campaign in campaign_list:

            current_budget = float(
                campaign["budget"] or 0
            )

            revenue = max(
                float(campaign["revenue"] or 0),
                0
            )

            if positive_revenue > 0:

                share = revenue / positive_revenue

            else:

                share = 1 / len(campaign_list)

            recommended_budget = total_budget * share

            allocations.append({
                "campaign_name": campaign["campaign_name"],
                "platform": campaign["platform"],
                "current_budget": current_budget,
                "recommended_budget": round(
                    recommended_budget, 2
                ),
                "revenue": revenue,
                "share": round(share * 100, 2)
            })

    return render_template(
        "budget_optimizer.html",
        allocations=allocations,
        total_budget=total_budget,
        total_revenue=total_revenue
    )


# --------------------------------------------------
# AI MARKETING ASSISTANT
# --------------------------------------------------

def get_marketing_answer(question):

    text = question.lower()

    if any(
        word in text
        for word in ["ctr", "click through"]
    ):

        return (
            "CTR (Click-Through Rate) measures the percentage "
            "of impressions that resulted in clicks. Formula: "
            "(Clicks / Impressions) × 100. Compare CTR across "
            "campaigns to understand engagement."
        )

    if "roi" in text or "return on investment" in text:

        return (
            "ROI measures the return compared with campaign spending. "
            "Formula: ((Revenue - Budget) / Budget) × 100. "
            "A positive ROI means recorded revenue is higher than budget."
        )

    if "conversion" in text:

        return (
            "Conversion rate measures how many clicks resulted "
            "in conversions. Formula: (Conversions / Clicks) × 100. "
            "A clear call to action and relevant landing page can help."
        )

    if "instagram" in text or "social media" in text:

        return (
            "Plan useful, audience-relevant posts, maintain a consistent "
            "publishing schedule, use clear captions, and review "
            "engagement metrics to understand what works."
        )

    if "budget" in text:

        return (
            "Start with a defined campaign objective. Compare campaign "
            "spending, revenue, and conversion performance before "
            "adjusting your budget. Avoid making decisions from "
            "a single metric."
        )

    if "content" in text:

        return (
            "Create content around your audience's needs. Use a mix "
            "of educational, informative, and product-focused posts. "
            "Track engagement to improve future content."
        )

    return (
        "I can help with marketing concepts such as CTR, ROI, "
        "conversions, social media strategy, content planning, "
        "and campaign budgets. Try asking a specific question "
        "about one of these topics."
    )


@app.route("/assistant", methods=["GET", "POST"])
@login_required
def assistant():

    answer = None
    question = ""

    if request.method == "POST":

        question = request.form.get(
            "question", ""
        ).strip()

        if question:

            answer = get_marketing_answer(question)

        else:

            flash(
                "Please enter a question.",
                "warning"
            )

    return render_template(
        "assistant.html",
        question=question,
        answer=answer
    )


# --------------------------------------------------
# PDF REPORTS
# --------------------------------------------------

@app.route("/reports")
@login_required
def reports():

    connection = get_db_connection()

    try:

        campaign_list = get_user_campaigns(connection)

        totals = connection.execute(
            """
            SELECT
                COUNT(*) AS total_campaigns,
                COALESCE(SUM(impressions), 0) AS impressions,
                COALESCE(SUM(clicks), 0) AS clicks,
                COALESCE(SUM(conversions), 0) AS conversions,
                COALESCE(SUM(revenue), 0) AS revenue,
                COALESCE(SUM(budget), 0) AS budget
            FROM campaigns
            WHERE user_id = ?
            """,
            (session["user_id"],)
        ).fetchone()

    finally:
        connection.close()

    return render_template(
        "reports.html",
        totals=totals,
        campaigns=campaign_list
    )


@app.route("/reports/download")
@login_required
def download_report():

    connection = get_db_connection()

    try:

        campaign_list = get_user_campaigns(connection)

        totals = connection.execute(
            """
            SELECT
                COUNT(*) AS total_campaigns,
                COALESCE(SUM(impressions), 0) AS impressions,
                COALESCE(SUM(clicks), 0) AS clicks,
                COALESCE(SUM(conversions), 0) AS conversions,
                COALESCE(SUM(revenue), 0) AS revenue,
                COALESCE(SUM(budget), 0) AS budget
            FROM campaigns
            WHERE user_id = ?
            """,
            (session["user_id"],)
        ).fetchone()

    finally:
        connection.close()

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=45,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "MarketMind Marketing Report",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "Prepared for: " + escape(
                str(session.get("user_name", "User"))
            ),
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 18))

    impressions = totals["impressions"]
    clicks = totals["clicks"]
    conversions = totals["conversions"]
    budget = totals["budget"]
    revenue = totals["revenue"]

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

    summary_data = [
        ["Metric", "Value"],
        ["Total Campaigns", str(totals["total_campaigns"])],
        ["Impressions", f"{impressions:,}"],
        ["Clicks", f"{clicks:,}"],
        ["Conversions", f"{conversions:,}"],
        ["Total Budget", f"Rs. {budget:,.2f}"],
        ["Total Revenue", f"Rs. {revenue:,.2f}"],
        ["CTR", f"{ctr:.2f}%"],
        ["Conversion Rate", f"{conversion_rate:.2f}%"],
        ["ROI", f"{roi:.2f}%"]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[240, 230]
    )

    summary_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#263451")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#dddddd")
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            )
        ])
    )

    story.append(
        Paragraph(
            "Performance Summary",
            styles["Heading2"]
        )
    )

    story.append(summary_table)
    story.append(Spacer(1, 22))

    story.append(
        Paragraph(
            "Campaign Details",
            styles["Heading2"]
        )
    )

    campaign_data = [[
        "Campaign",
        "Platform",
        "Budget",
        "Revenue",
        "Status"
    ]]

    for campaign in campaign_list:

        campaign_data.append([
            escape(str(campaign["campaign_name"]))[:35],
            escape(str(campaign["platform"]))[:20],
            f"Rs. {float(campaign['budget'] or 0):,.2f}",
            f"Rs. {float(campaign['revenue'] or 0):,.2f}",
            escape(str(campaign["status"]))
        ])

    campaign_table = Table(
        campaign_data,
        colWidths=[125, 85, 90, 90, 75],
        repeatRows=1
    )

    campaign_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#263451")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#dddddd")
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            )
        ])
    )

    story.append(campaign_table)
    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "Generated by MarketMind Digital Marketing "
            "Intelligence Platform.",
            styles["Italic"]
        )
    )

    document.build(story)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="MarketMind_Report.pdf",
        mimetype="application/pdf"
    )


# --------------------------------------------------
# PROFILE MANAGEMENT
# --------------------------------------------------

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    connection = get_db_connection()

    if request.method == "POST":

        name = request.form.get(
            "name", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        if not name or not email:

            connection.close()

            flash(
                "Name and email are required.",
                "error"
            )

            return redirect(url_for("profile"))

        try:

            connection.execute(
                """
                UPDATE users
                SET name = ?, email = ?
                WHERE id = ?
                """,
                (
                    name,
                    email,
                    session["user_id"]
                )
            )

            connection.commit()

            session["user_name"] = name
            session["user_email"] = email

            flash(
                "Profile updated successfully.",
                "success"
            )

        except sqlite3.IntegrityError:

            flash(
                "That email address is already registered.",
                "error"
            )

        finally:
            connection.close()

        return redirect(url_for("profile"))

    try:

        user = connection.execute(
            """
            SELECT id, name, email, role, created_at
            FROM users
            WHERE id = ?
            """,
            (session["user_id"],)
        ).fetchone()

    finally:
        connection.close()

    if not user:

        session.clear()

        flash(
            "Account not found. Please log in again.",
            "error"
        )

        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        user=user
    )


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

@app.route("/admin")
@admin_required
def admin():

    connection = get_db_connection()

    try:

        user_count = connection.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        campaign_count = connection.execute(
            "SELECT COUNT(*) FROM campaigns"
        ).fetchone()[0]

        total_revenue = connection.execute(
            """
            SELECT COALESCE(SUM(revenue), 0)
            FROM campaigns
            """
        ).fetchone()[0]

        users = connection.execute(
            """
            SELECT id, name, email, role, created_at
            FROM users
            ORDER BY id DESC
            """
        ).fetchall()

    finally:
        connection.close()

    return render_template(
        "admin.html",
        user_count=user_count,
        campaign_count=campaign_count,
        total_revenue=total_revenue,
        users=users
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("home"))


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.route("/health")
def health():

    return {
        "status": "success",
        "application": "MarketMind"
    }


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])