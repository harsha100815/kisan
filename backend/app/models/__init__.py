"""Models package: importing modules registers tables on Base.metadata."""

from app.db.base import Base
from app.models import diagnosis, user  # noqa: F401

__all__ = ["Base"]
