from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TenantSettings(Base):
    __tablename__ = "tenant_settings"

    college_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    institution_name: Mapped[str] = mapped_column(String(180), nullable=False)
    campus_name: Mapped[str] = mapped_column(String(180), default="", nullable=False)
    principal_name: Mapped[str] = mapped_column(String(180), default="", nullable=False)
    address: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    phone: Mapped[str] = mapped_column(String(40), default="", nullable=False)
    email: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    website: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    academic_year: Mapped[str] = mapped_column(String(40), default="", nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Karachi", nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="PKR", nullable=False)
    logo_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    primary_color: Mapped[str] = mapped_column(String(16), default="#1F4E79", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
