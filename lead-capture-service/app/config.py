import os
import re
from dotenv import load_dotenv

load_dotenv()


class Settings:
    _raw_db_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5433/zenthweb_leads",
    )
    # Railway/Heroku "postgres://" dete hain, SQLAlchemy ko "postgresql+psycopg2://" chahiye
    DATABASE_URL: str = re.sub(r"^postgres://", "postgresql+psycopg2://", _raw_db_url)

    APP_NAME: str = "Lead Capture Service"
    ENV: str = os.getenv("ENV", "development")

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8001/auth/google/callback")

    # Our own JWT (issued after Google login succeeds)
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-to-a-random-secret")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours


settings = Settings()