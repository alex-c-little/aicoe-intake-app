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

    # Board columns — the 8 stages of PPL's "Use Case Intake and Delivery Process".
    STATUSES = [
        "Demand",
        "Discovery",
        "Qualify",
        "Prioritize & Plan",
        "Value Capture & Reviews/Approvals",
        "Develop",
        "Final Review",
        "Deployment",
    ]

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
