
# MARKETMIND
### AI-Powered Digital Marketing Intelligence & Business Growth Platform

MarketMind is a web-based digital marketing intelligence platform designed to help businesses manage marketing campaigns, analyze performance, understand customer behavior, and make informed business decisions.

---

## Key Features

### 1. Dashboard
- Marketing performance overview
- Campaign statistics
- Revenue and budget summary
- Quick navigation to platform modules

### 2. Campaign Management
- Create and manage marketing campaigns
- Track impressions, clicks and conversions
- Monitor campaign budgets and revenue

### 3. Marketing Analytics
- Campaign performance analysis
- Click-through rate (CTR)
- Conversion rate
- Return on Investment (ROI)
- Interactive performance charts

### 4. AI-Based Insights
- Automated marketing suggestions
- Campaign performance classification
- Performance improvement recommendations

### 5. Customer Intelligence
- Customer segmentation
- Purchase behavior analysis
- Customer sentiment analysis
- Customer engagement insights

### 6. Competitor Analysis
- Competitor tracking
- Follower comparison
- Engagement rate analysis
- Competitor performance insights

### 7. Content Planner
- Plan social media posts
- Manage publishing schedules
- Track content status

### 8. Budget Optimizer
- Campaign budget analysis
- Revenue-based budget allocation
- Suggested budget distribution

### 9. Marketing Assistant
- Rule-based marketing guidance
- Answers to common marketing questions

### 10. Reports
- Generate marketing reports
- Download PDF reports
- View campaign performance summaries

### 11. User Management
- User registration and login
- Secure password hashing
- User profile management
- Admin dashboard with role-based access

---

## Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript
- Chart.js

### Backend
- Python
- Flask

### Database
- SQLite

### Data Analysis and AI Libraries
- Pandas
- NumPy
- Scikit-learn
- TextBlob
- Matplotlib
- Joblib

### Reporting
- ReportLab

---

## Project Structure

```text
MARKETMIND/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── ai_models/
│   ├── train_model.py
│   ├── prediction.py
│   ├── sentiment.py
│   ├── segmentation.py
│   └── recommendations.py
│
├── analytics/
│   ├── campaign_analysis.py
│   ├── roi_calculator.py
│   ├── performance.py
│   └── competitor_analysis.py
│
├── database/
│   ├── __init__.py
│   └── database.py
│
├── reports/
│   └── report_generator.py
│
├── templates/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── uploads/
```

---

## Installation and Setup

### Step 1: Download the Project

Clone or download the MarketMind project and open its folder in VS Code.

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate the Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
python app.py
```

### Step 6: Open in Browser

```text
http://127.0.0.1:5000
```

Register an account and log in to access the MarketMind dashboard.

---

## Database

MarketMind uses SQLite for storing:

- User accounts
- Marketing campaigns
- Customer information
- Competitor details
- Social media content schedules
- Activity records

The database tables are initialized automatically when the application starts.

---

## Project Purpose

The main objective of MarketMind is to provide a centralized digital marketing platform that combines campaign management, performance analytics, customer intelligence, and marketing recommendations.

It aims to simplify marketing analysis and support better business planning through data-driven insights.

---

## Important Notes

- Customer segmentation and marketing recommendations currently use rule-based logic.
- Budget optimization uses revenue-based allocation heuristics.
- Sentiment analysis uses TextBlob.
- The campaign classification model uses a small synthetic demonstration dataset and is not validated for real-world predictions.
- Competitor information depends on manually entered data.
- Analytical suggestions are informational and do not guarantee business results.

---

## Future Enhancements

- Live social media platform integrations
- Larger real-world marketing datasets
- Improved machine learning models
- Advanced customer behavior analytics
- Automated campaign performance monitoring

---

**Developed as an AI-powered Digital Marketing Intelligence and Business Growth Platform.**
