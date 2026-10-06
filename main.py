from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

import models, schemas, crud, worker
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bulk Certificate Generator")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/jobs", response_model=schemas.JobCreateResponse)
def create_generation_job(request: schemas.CertificateCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if not request.recipients:
        raise HTTPException(status_code=400, detail="Recipients list cannot be empty")
        
    # Validate emails if provided
    for rec in request.recipients:
        if rec.name.strip() == "":
            raise HTTPException(status_code=400, detail="Recipient name cannot be empty")
            
    job = crud.create_job(db, request.recipients)
    background_tasks.add_task(worker.process_job, job.id)
    return schemas.JobCreateResponse(job_id=job.id, status="pending", message="Job created successfully")

@app.get("/api/jobs/{job_id}", response_model=schemas.JobStatusResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    job_stats = crud.get_job_stats(db, job_id)
    if not job_stats:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_stats

@app.get("/api/jobs", response_model=list[schemas.JobResponse])
def list_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_jobs(db, skip=skip, limit=limit)

@app.get("/api/jobs/{job_id}/certificates", response_model=list[schemas.CertificateResponse])
def get_job_certificates(job_id: int, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return crud.get_job_certificates(db, job_id)

@app.get("/api/certificates/{cert_id}/download")
def download_certificate(cert_id: int, db: Session = Depends(get_db)):
    cert = crud.get_certificate(db, cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
        
    if cert.status != "generated":
        raise HTTPException(status_code=400, detail=f"Certificate is in '{cert.status}' state")
        
    if not cert.file_path or not os.path.exists(cert.file_path):
        raise HTTPException(status_code=404, detail="Certificate file not found on disk")
        
    return FileResponse(path=cert.file_path, filename=f"{cert.recipient_name}_certificate.png", media_type='image/png')
