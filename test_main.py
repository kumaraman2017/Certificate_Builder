import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from main import app, get_db
from database import Base, engine
import time





@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_create_generation_job_valid(client):
    response = client.post(
        "/api/jobs",
        json={"recipients": [{"name": "Alice"}, {"name": "Bob", "email": "bob@example.com"}]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    
def test_create_generation_job_invalid(client):
    response = client.post(
        "/api/jobs",
        json={"recipients": []}
    )
    assert response.status_code == 400

    response = client.post(
        "/api/jobs",
        json={"recipients": [{"name": ""}]}
    )
    assert response.status_code == 400

def test_job_status_and_progress(client):
    # Create job
    response = client.post(
        "/api/jobs",
        json={"recipients": [{"name": "Charlie"}]}
    )
    job_id = response.json()["job_id"]
    
    # Wait for background task to complete
    time.sleep(2)
    
    status_res = client.get(f"/api/jobs/{job_id}")
    assert status_res.status_code == 200
    stats = status_res.json()
    assert stats["id"] == job_id
    assert stats["total_certificates"] == 1
    # Depending on background execution it could be completed or pending, but with time.sleep it should be completed
    assert stats["completed_certificates"] == 1
    
    # We can retrieve the certificate using DB logic, but since we don't return cert IDs in job status, 
    # we need to either add it or infer it. Let's assume cert ID is the max ID or query directly.
    # We can add an endpoint to get all certs for a job to make testing easier, or just query DB.
    
    from database import SessionLocal
    db = SessionLocal()
    from models import Certificate
    cert = db.query(Certificate).filter(Certificate.job_id == job_id).first()
    db.close()
    
    assert cert is not None
    
    download_res = client.get(f"/api/certificates/{cert.id}/download")
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "image/png"

def test_retrieve_failed_certificate(client):
    # To test failed certificate download, request download for non-existent cert
    download_res = client.get("/api/certificates/999/download")
    assert download_res.status_code == 404
