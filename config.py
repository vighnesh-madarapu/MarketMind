
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:

    # Application security
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "marketmind-development-key-change-before-deployment"
    )

    # Database configuration
    DATABASE_PATH = BASE_DIR / "database" / "marketmind.db"

    # Upload configuration
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (
        os.environ.get("SESSION_COOKIE_SECURE", "False").lower()
        == "true"
    )

    # Application settings
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
