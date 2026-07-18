import os
import re
from dotenv import load_dotenv

load_dotenv()


class Settings:
    _raw_db_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5433/zenthweb_leads",
    )
    DATABASE_URL: str = re.sub(r"^postgres://", "postgresql+psycopg2://", _raw_db_url)

    APP_NAME: str = "Lead Capture Service"
    ENV: str = os.getenv("ENV", "development")

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8001/auth/google/callback")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-to-a-random-secret")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7

    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://zenthweb.dev")

    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.zoho.in")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "contact@zenthweb.dev")
    FROM_NAME: str = os.getenv("FROM_NAME", "Zenthweb")

    ADMIN_EMAILS: set[str] = set(
        email.strip().lower()
        for email in os.getenv("ADMIN_EMAILS", "").split(",")
        if email.strip()
    )


settings = Settings()