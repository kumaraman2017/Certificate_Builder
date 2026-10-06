from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

from database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending") # pending, processing, completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    certificates = relationship("Certificate", back_populates="job")

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    recipient_name = Column(String, index=True)
    recipient_email = Column(String, index=True, nullable=True)
    status = Column(String, default="pending") # pending, generated, failed
    file_path = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("Job", back_populates="certificates")
