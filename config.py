import os
from dotenv import load_dotenv

# Only load .env for local development. Inside Databricks Apps, configuration
# comes from app.yaml (env / valueFrom) and a stray .env would override it.
if not os.getenv("DATABRICKS_APP_NAME"):
    load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

    DATABASE_URL = os.getenv("DATABASE_URL")

    ENABLE_JS_ENHANCEMENTS = os.getenv("ENABLE_JS_ENHANCEMENTS", "true").lower() == "true"

    GENIE_SPACE_URL = os.getenv("GENIE_SPACE_URL", "")

    STATUSES = ["Backlog", "Refinement", "Under Review", "Approved"]

    AI_CAPABILITIES = [
        "Forecasting",
        "Anomaly Detection",
        "Optimization",
        "Computer Vision",
        "Generative AI / Agents",
        "Predictive Maintenance",
        "Recommendation",
        "Other",
    ]

    VALUE_STREAMS = [
        "Distribution",
        "Transmission",
        "Generation",
        "Customer",
        "Regulatory",
        "Corporate Services",
    ]

    FUNDING_OPTIONS = ["Funded", "Partially Funded", "Unfunded", "TBD"]
