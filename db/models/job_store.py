from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Session, mapped_column
from sqlalchemy.orm.attributes import flag_modified
from .base import Base


# TODO: Change this to QueueStore, since this is basically tracking queues and not individual jobs.

class JobStore(Base):
    __tablename__ = "job"
    id = mapped_column(Integer, primary_key=True)
    job_id = mapped_column(String, nullable=False)
    name = mapped_column(String)
    status = mapped_column(String, default="in_progress")
    properties = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())


    def to_dict(self):
        return {
            "id": self.id,
            "pid": self.job_id,
            "name": self.name,
            "status": self.status,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    def get_properties(self, key=None):
        properties = self.properties or {}
        if key: return properties.get(key, None)

        return properties


    def set_complete(self, db: Session):
        self.status = "completed"
        db.commit()

        return self


    def update_properties(self, db: Session, properties: dict):
        self.properties = self.get_properties()
        self.properties.update(properties)
        flag_modified(self, 'properties')
        db.commit()

        return self


    @staticmethod
    def first_or_create(db: Session, job):
        existing_job = db.query(JobStore).filter(
            JobStore.job_id == job.id
        ).first()

        if existing_job:
            return existing_job

        job_name = job.data.get("eventName", "Unknown")

        jobstore = JobStore(
            name=job_name,
            job_id=job.id,
            properties=job.data
        )

        db.add(jobstore)
        db.commit()

        return jobstore
