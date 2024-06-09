from sqlalchemy.sql import func
from sqlalchemy import Integer, String, JSON, DateTime
from sqlalchemy.orm import Session, mapped_column, relationship
from sqlalchemy.orm.attributes import flag_modified
from .base import Base


class Interactive(Base):
    __tablename__ = "interactive"
    id = mapped_column(Integer, primary_key=True)
    page_source_id = mapped_column(Integer, nullable=False, comment="This is the page that the interactive is generated from.")
    type = mapped_column(String, nullable=False)
    difficulty = mapped_column(Integer)
    data = mapped_column(JSON, comment="Contains interactive fields and content which can vary widely between types.")
    meta = mapped_column(JSON, comment="Contains application information such as other relations.")
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    pages = relationship(
        "Page",
        secondary="page_interactive",
        back_populates="interactives",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "page_source_id": self.page_source_id,
            "type": self.type,
            "data": self.data,
            "meta": self.meta,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def get_data(self, key=None):
        data = self.data or {}
        if key: return data.get(key, None)

        return data

    def get_meta(self, key=None):
        meta = self.meta or {}
        if key: return meta.get(key, None)

        return meta


    def get_difficulty_enum(self):
        difficulties = {
            1: "easy",
            2: "intermediate",
            3: "advanced",
        }

        return difficulties.get(self.difficulty, None)


    def update_data(self, db: Session, data: dict):
        self.data = self.get_data()
        self.data.update(data)
        flag_modified(self, 'data')
        db.commit()

        return self


    def update_meta(self, db: Session, data: dict):
        self.meta = self.get_data()
        self.meta.update(data)
        flag_modified(self, 'meta')
        db.commit()

        return self
