"""App settings, read from environment variables (or a .env file) with safe local defaults."""
import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./guild.db")

# Change SECRET_KEY in any real deployment. It signs the login tokens.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me-before-deploying-0123456789")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# The D&D 5e API (free, no key). Versioned by SRD year.
DND_API_BASE = os.getenv("DND_API_BASE", "https://www.dnd5eapi.co/api/2014")
DND_API_TIMEOUT = float(os.getenv("DND_API_TIMEOUT", "5"))

# Comma-separated list of frontend origins allowed to call the API.
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
