from sqlalchemy.orm import Session
import models, schemas

def create_job(db: Session, recipients: list[schemas.RecipientBase]):
    db_job = models.Job(status="pending")
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    for recipient in recipients:
        db_cert = models.Certificate(
            job_id=db_job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            status="pending"
        )
        db.add(db_cert)
    
    db.commit()
    return db_job

def get_job(db: Session, job_id: int):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def get_job_stats(db: Session, job_id: int):
    job = get_job(db, job_id)
    if not job:
        return None
    
    certs = db.query(models.Certificate).filter(models.Certificate.job_id == job_id).all()
    total = len(certs)
    completed = sum(1 for c in certs if c.status == "generated")
    failed = sum(1 for c in certs if c.status == "failed")
    pending = sum(1 for c in certs if c.status == "pending")

    return schemas.JobStatusResponse(
        id=job.id,
        status=job.status,
        created_at=job.created_at,
        total_certificates=total,
        completed_certificates=completed,
        failed_certificates=failed,
        pending_certificates=pending
    )

def get_job_certificates(db: Session, job_id: int):
    return db.query(models.Certificate).filter(models.Certificate.job_id == job_id).all()

def get_jobs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Job).order_by(models.Job.created_at.desc()).offset(skip).limit(limit).all()

def get_certificate(db: Session, cert_id: int):
    return db.query(models.Certificate).filter(models.Certificate.id == cert_id).first()
