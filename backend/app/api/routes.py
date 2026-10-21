
from pydantic import BaseModel
from app.services.resume_parser import extract_resume_details
from app.services.job_matcher import match_resume_to_job
from app.services.consistency_checks import check_resume_consistency
from app.rag.chunker import chunk_text
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import pymupdf


router = APIRouter()

#Add Request Model
class ResumeTextRequest(BaseModel):
    text: str
#Add job Match Model    
class JobMatchRequest(BaseModel):
    resume_text: str
    job_description: str

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

#Upload Resume
@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    #Check the file extension
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    #Read the file, limiting the amount of data read
    content = await file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 10 MB.",
        )

    #Check the PDF signature
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF.",
        )

    #Try opening the PDF to check that it is readable
    try:
        with pymupdf.open(stream=content, filetype="pdf") as pdf:
            page_count = pdf.page_count

            if page_count == 0:
                raise HTTPException(
                    status_code=400,
                    detail="The PDF contains no pages.",
                )
            #Extract text from every page
            extracted_text = "\n".join(
                page.get_text() for page in pdf
            ).strip()

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="The PDF is damaged or cannot be read.",
        )
    
    if not extracted_text:
        raise HTTPException(
            status_code= 422,
            detail= (
                "No text could be extracted. "
                "The PDF may contain scanned images and need OCR."
            ),

        )
    return {
        "message": "Resume uploaded and text extracted successfully.",
        "filename": file.filename,
        "size_bytes": len(content),
        "pages": page_count,
        "status": "text_extracted",
        "extracted_text": extracted_text,
    }
#Resume Parse
@router.post("/parse-resume")
def parse_resume(request: ResumeTextRequest):
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Resume text cannot be empty.",
        )

    return extract_resume_details(request.text)

#Resume analyze
@router.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    query: str = "React experience",
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    pdf_bytes = await file.read()

    if len(pdf_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 10 MB limit.",
        )

    if not pdf_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty.",
        )

    try:
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
            resume_text = "\n".join(
                page.get_text() for page in pdf
            ).strip()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF.",
        )

    if not resume_text:
        raise HTTPException(
            status_code=400,
            detail="No selectable text found in the PDF.",
        )

    candidate = extract_resume_details(resume_text)

    chunks = chunk_text(
        resume_text,
        chunk_size=100,
        overlap=20,
    )

    evidence = []

    if candidate["skills"]:
        from app.rag.semantic_retriever import retrieve_semantic_evidence

        evidence = retrieve_semantic_evidence(
            query=query,
            chunks=chunks,
            top_k=5,
        )

    return {
        "candidate": candidate,
        "resume_chunks": chunks,
        "evidence": evidence,
        "message": (
            "Evidence retrieved using semantic similarity. Review the original resume before drawing conclusions."
        ),
    }

#Job Matcher
@router.post("/match-job")
def match_job(request: JobMatchRequest):
    if not request.resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Resume text cannot be empty.",
        )

    if not request.job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty.",
        )

    candidate = extract_resume_details(request.resume_text)

    result = match_resume_to_job(
        candidate_skills=candidate["skills"],
        job_description=request.job_description,
    )

    return {
        "candidate": candidate,
        "job_match": result,
    }

#screen-all

# Batch-screen all resume PDFs against the project job description.
@router.post("/screen-all")
def screen_all_resumes():
    # routes.py is inside project_root/backend/app/api/
    project_root = Path(__file__).resolve().parents[3]
    assets_dir = project_root / "assets"
    resumes_dir = assets_dir / "resumes"
    job_description_path = assets_dir / "job-description.pdf"

    if not job_description_path.is_file():
        raise HTTPException(
            status_code=500,
            detail=f"Job description not found: {job_description_path}",
        )

    if not resumes_dir.is_dir():
        raise HTTPException(
            status_code=500,
            detail=f"Resume folder not found: {resumes_dir}",
        )

    # Extract the actual job description from its PDF.
    try:
        with pymupdf.open(str(job_description_path)) as pdf:
            job_description = "\n".join(
                page.get_text() for page in pdf
            ).strip()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read job description: {exc}",
        )

    if not job_description:
        raise HTTPException(
            status_code=422,
            detail="No selectable text found in the job description PDF.",
        )

    resume_files = sorted(
        resumes_dir.glob("*.pdf"),
        key=lambda path: path.name.lower(),
    )

    if not resume_files:
        raise HTTPException(
            status_code=404,
            detail="No PDF resumes found in assets/resumes.",
        )

    results = []
    errors = []

    for resume_path in resume_files:
        try:
            with pymupdf.open(str(resume_path)) as pdf:
                resume_text = "\n".join(
                    page.get_text() for page in pdf
                ).strip()

            if not resume_text:
                errors.append({
                    "filename": resume_path.name,
                    "error": "No selectable text; OCR may be needed.",
                })
                continue

            candidate = extract_resume_details(resume_text)
            

            match = match_resume_to_job(
                candidate_skills=candidate["skills"],
                job_description=job_description,
            )
            consistency_flags = check_resume_consistency(resume_text)

            matched = match["matched_skills"]
            missing = match["missing_required_skills"]

            reasons = []
            if matched:
                reasons.append(
                    "Matched skills: " + ", ".join(matched)
                )
            if missing:
                reasons.append(
                    "Required skills not detected: " + ", ".join(missing)
                )
            if not reasons:
                reasons.append(
                    "Insufficient recognized skill evidence for a detailed reason."
                )

            results.append({
                "filename": resume_path.name,
                "candidate_name": (
                    candidate["candidate_name"] or resume_path.stem
                ),
                "skills": candidate["skills"],
                "match_score": match["match_score"],
                "matched_skills": matched,
                "missing_required_skills": missing,
                "missing_preferred_skills": (
                    match["missing_preferred_skills"]
                ),
                "reasons": reasons,
                "consistency_flags": consistency_flags,
                "flag_count": len(consistency_flags),
                "scoring_note": match["message"],
                
            })

        except Exception as exc:
            errors.append({
                "filename": resume_path.name,
                "error": str(exc),
            })

    results.sort(
        key=lambda item: (
            item["match_score"] is not None,
            item["match_score"] if item["match_score"] is not None else -1,
        ),
        reverse=True,
    )

    for rank, result in enumerate(results, start=1):
        result["rank"] = rank

    return {
        "job_description_file": job_description_path.name,
        "resumes_found": len(resume_files),
        "resumes_screened": len(results),
        "resumes_with_errors": len(errors),
        "scoring_method": (
            "Weighted skill overlap: detected required skills count twice "
            "as much as detected preferred skills. This is not a hiring "
            "prediction and does not verify years of experience."
        ),
        "ranked_candidates": results,
        "errors": errors,
    }




  
    