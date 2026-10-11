
import os
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from llm_analyzer import create_incident_report

app = FastAPI(
    title="AI Incident Resolution Agent",
    description=(
        "Analyze application logs and generate "
        "AI-assisted incident reports."
    ),
    version="1.0.0",
)

ALLOWED_EXTENSIONS = {".log", ".txt"}
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB


@app.get("/")
def home():
    return {
        "message": "AI Incident Resolution Agent API is running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/analyze")
async def analyze_uploaded_log(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Please upload a log file.",
        )

    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .log and .txt files are supported.",
        )

    temp_path = None

    try:
        # Save the uploaded file temporarily.
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=Path(filename).suffix.lower(),
            delete=False,
        ) as temp_file:
            temp_path = temp_file.name
            size = 0

            while True:
                chunk = await file.read(64 * 1024)

                if not chunk:
                    break

                size += len(chunk)

                if size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the 1 MB limit.",
                    )

                temp_file.write(chunk)

        # Run the existing log analysis and AI workflow.
        report = create_incident_report(temp_path)

        if isinstance(report, dict):
            raise HTTPException(
                status_code=422,
                detail=report,
            )

        if not isinstance(report, str) or not report.strip():
            raise HTTPException(
                status_code=502,
                detail="The incident report could not be generated.",
            )

        if "temporarily unavailable (503)" in report:
            raise HTTPException(
                status_code=503,
                detail=report,
            )

        return {
            "filename": filename,
            "status": "success",
            "incident_report": report,
        }

    except HTTPException:
        raise

    except Exception:
        # Avoid returning internal exception details to API clients.
        raise HTTPException(
            status_code=500,
            detail="Incident analysis failed. Check the server logs.",
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        await file.close()
