from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship



class OutlineEntity(Base):
    __tablename__ = "outline_entity"
    id: Mapped[int] = mapped_column(primary_key=True)
    outline_id: Mapped[int] = mapped_column(ForeignKey("outline.id"))
    entity_id: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    outline = relationship("Outline", back_populates="entities")
