# Bulk Certificate Generator

A backend API for generating certificates in bulk for a list of recipients. The certificates are generated asynchronously in the background.

## Technology Stack

- **Python 3**
- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy & SQLite**: Relational database for storing jobs and certificates.
- **Pillow (PIL)**: For image/certificate generation.
- **Pytest**: For testing.
- **uv**: Fast Python package manager (used for setup).

## How to Set Up the Project

1. Ensure you have Python installed. The project uses `uv` for environment management.
2. Open a terminal in the root directory of the project.
3. Install dependencies by running:
   ```bash
   uv pip install fastapi uvicorn sqlalchemy pydantic pillow pytest httpx
   ```

## How to Run the Application

Start the FastAPI server using `uvicorn`:

```bash
uv run uvicorn main:app --reload
```

The server will be available at `http://127.0.0.1:8000`. You can also access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## How to Run Tests

Run the test suite using `pytest`:

```bash
uv run pytest test_main.py
```

## How to Submit a Certificate Generation Request

Send a POST request to `/api/jobs` with a JSON body containing a list of recipients.

**Example Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/jobs" -H "Content-Type: application/json" -d '{
  "recipients": [
    {"name": "Alice"},
    {"name": "Bob", "email": "bob@example.com"}
  ]
}'
```

**Example Response:**
```json
{
  "job_id": 1,
  "status": "pending",
  "message": "Job created successfully"
}
```

## How to Check Job Status

Send a GET request to `/api/jobs/{job_id}` to check the progress of your generation job.

**Example Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/jobs/1"
```

**Example Response:**
```json
{
  "id": 1,
  "status": "completed",
  "created_at": "2026-10-06T19:00:00.000000",
  "total_certificates": 2,
  "completed_certificates": 2,
  "failed_certificates": 0,
  "pending_certificates": 0
}
```

## How to Retrieve Generated Certificates

Once the job is processing or completed, the certificates can be downloaded by their ID. Note: You would normally add an endpoint to list the certificate IDs for a job. For simplicity, assuming the certificate ID is known (e.g., sequentially from 1).

**Example Request to Download Certificate #1:**
```bash
curl -X GET "http://127.0.0.1:8000/api/certificates/1/download" --output certificate.png
```

## Important Implementation/Design Decisions

- **Background Processing:** The certificate generation is handled in the background using FastAPI's built-in `BackgroundTasks`. This allows the API to return immediately after accepting the request. Since generation can be I/O heavy (especially with images/PDFs in large quantities), background processing prevents the API from blocking.
- **Failure Isolation:** Each certificate is generated in a separate `try/except` block inside the background task loop. If one fails, its status is updated to `failed`, the error message is recorded, and the worker moves on to the next one. This prevents one bad data entry from halting the entire batch.
- **Relational DB / Status Tracking:** Using a database to track individual certificate records linked to a job ID provides granular insight into what succeeded, what is pending, and what failed.
- **Image Generation Template:** Used the Python Imaging Library (Pillow) to generate a base template (if one doesn't exist) and then draw text dynamically onto it. This avoids needing a separate complex HTML-to-PDF pipeline for a simple certificate task.
