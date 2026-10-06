from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import datetime

class RecipientBase(BaseModel):
    name: str
    email: Optional[str] = None

class CertificateCreate(BaseModel):
    recipients: List[RecipientBase]

class CertificateResponse(BaseModel):
    id: int
    recipient_name: str
    recipient_email: Optional[str]
    status: str
    file_path: Optional[str]
    error_message: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class JobResponse(BaseModel):
    id: int
    status: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class JobStatusResponse(BaseModel):
    id: int
    status: str
    created_at: datetime.datetime
    total_certificates: int
    completed_certificates: int
    failed_certificates: int
    pending_certificates: int

    model_config = ConfigDict(from_attributes=True)

class JobCreateResponse(BaseModel):
    job_id: int
    status: str
    message: str
