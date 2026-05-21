import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = os.getenv("API_KEY", "default-dev-key")
    DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()

    if DB_TYPE == "sqlite":
        SQLALCHEMY_DATABASE_URI = "sqlite:///monitoring.db"
    elif DB_TYPE == "sqlserver":
        SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
        if not SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URL is not set.")
    else:
        raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}")
