from sqlalchemy.sql import func
from sqlalchemy import Integer, String, JSON, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, relationship
from .base import Base


class PageInteractive(Base):
    __tablename__ = "page_interactive"
    interactive_id = mapped_column(ForeignKey("interactive.id"), primary_key=True)
    page_id = mapped_column(ForeignKey("page.id"), primary_key=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "interactive_id": self.interactive_id,
            "page_id": self.page_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
