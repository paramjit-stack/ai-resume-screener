
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.services.resume_parser import extract_resume_details
from app.services.job_matcher import match_resume_to_job
from app.services.consistency_checks import check_resume_consistency
from app.services.pdf_utils import extract_pdf_text
from app.rag.chunker import chunk_text

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


router = APIRouter()

#Add Request Model
class ResumeTextRequest(BaseModel):
    text: str
#Add job Match Model    
class JobMatchRequest(BaseModel):
    resume_text: str
    job_description: str

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
# Batch-screen all resume PDFs against the project job description.
@router.post("/screen-uploaded")
async def screen_uploaded_resumes(
    job_description: UploadFile = File(...),
    resumes: List[UploadFile] = File(...),
):
    # Extract job description once
    jd_bytes = await job_description.read(MAX_FILE_SIZE + 1)
    job_text = extract_pdf_text(jd_bytes, "Job description")

    results = []

    # Process each uploaded resume
    for uploaded in resumes:
        filename = uploaded.filename or "unknown.pdf"

        try:
            content = await uploaded.read(MAX_FILE_SIZE + 1)
            resume_text = extract_pdf_text(
                content,
                f"Resume '{filename}'",
            )

            candidate = extract_resume_details(resume_text)

            match = match_resume_to_job(
                candidate_skills=candidate["skills"],
                job_description=job_text,
            )

            flags = check_resume_consistency(resume_text)

            results.append({
                "filename": filename,
                "candidate": candidate,
                "match": match,
                "flags": flags,
                "status": "success",
            })

        except HTTPException as exc:
            results.append({
                "filename": filename,
                "status": "failed",
                "error": exc.detail,
            })

        except Exception as exc:
            results.append({
                "filename": filename,
                "status": "failed",
                "error": str(exc),
            })

    return {
        "total_resumes": len(resumes),
        "successful": sum(
            1 for result in results
            if result["status"] == "success"
        ),
        "failed": sum(
            1 for result in results
            if result["status"] == "failed"
        ),
        "results": results,
    }






  
    