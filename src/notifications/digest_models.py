"""User notification digest preferences."""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.shared.database import Base


class DigestPreference(Base):
    """User-configured cadence for receiving notification digests.

    A user has at most one row. When ``enabled=False``, the digest
    cron skips the user entirely; when ``enabled=True``, the cadence
    column drives whether the digest dispatcher includes them in the
    daily or weekly batch.
    """

    __tablename__ = "notification_digest_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    cadence = Column(String(16), nullable=False, default="daily")  # "daily" | "weekly"
    enabled = Column(Boolean, nullable=False, default=True)
    delivery_hour_utc = Column(Integer, nullable=False, default=9)  # 0-23

    user = relationship("User")
