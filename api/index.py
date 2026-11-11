"""Vercel entrypoint: serves the FastAPI backend as a serverless function.

vercel.json rewrites every /api/* request here; FastAPI still sees the original path
(for example /api/guilds), so the routers work unchanged.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import app  # noqa: E402,F401
