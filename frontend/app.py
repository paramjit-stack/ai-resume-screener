
import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide",
)

# =========================================================
# STYLING
# =========================================================

st.markdown(
    """
    <style>
    /* Main application */
    .stApp {
        background: linear-gradient(
            135deg, #0b1020 0%, #111a30 100%
        );
        color: #f1f5f9;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    h1, h2, h3, h4, p, label {
        color: #f1f5f9;
    }

    [data-testid="stCaptionContainer"] p {
        color: #aebdd5 !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: linear-gradient(
            145deg, #1b2942, #182035
        );
        border: 1px solid #334766;
        padding: 18px 20px;
        border-radius: 14px;
    }

    [data-testid="stMetricLabel"] {
        color: #b8c5de !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem;
        font-weight: 700;
    }

    /* =====================================================
       UPLOAD CARDS
       ===================================================== */

    /* Bordered Streamlit cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(
            145deg, #17243b, #131e33
        ) !important;
        border: 1px solid #394b68 !important;
        border-radius: 14px !important;
        padding: 4px;
    }

    /* Keep uploaders transparent inside their cards */
    [data-testid="stFileUploader"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-bottom: 8px !important;
        color: #f1f5f9 !important;
    }

    /* Dropzone */
    [data-testid="stFileUploaderDropzone"] {
        background: #0f192c !important;
        border: 1px dashed #7868ef !important;
        border-radius: 10px !important;
    }

    /* Dropzone instructions */
    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] * {
        color: #e2e8f0 !important;
        opacity: 1 !important;
    }

    /* Browse files button */
    [data-testid="stFileUploaderDropzone"] button {
        background: #6857e8 !important;
        color: #ffffff !important;
        border: 1px solid #7868ef !important;
        border-radius: 7px !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    [data-testid="stFileUploaderDropzone"] button * {
        color: #ffffff !important;
        fill: #ffffff !important;
        opacity: 1 !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {
        background: #5141cf !important;
        border-color: #a99cff !important;
    }

    /* Selected filenames and file details */
    [data-testid="stFileUploaderFileName"],
    [data-testid="stFileUploaderFileName"] * {
        color: #f1f5f9 !important;
        opacity: 1 !important;
    }

    [data-testid="stFileUploader"] small {
        color: #b8c5de !important;
    }

    /* =====================================================
       BUTTONS
       ===================================================== */

    div.stButton > button[kind="primary"] {
        width: 100%;
        min-height: 42px;
        background: linear-gradient(
            90deg, #6857e8, #477ff7
        ) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 0.55rem 1rem !important;
        opacity: 1 !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(
            90deg, #5745d8, #3569e5
        ) !important;
        color: #ffffff !important;
        border: 1px solid #a99cff !important;
    }

    div.stButton > button[kind="primary"]:disabled {
        background: #303b53 !important;
        color: #aab5ca !important;
        border: 1px solid #43516a !important;
        opacity: 1 !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(
            90deg, #6857e8, #477ff7
        ) !important;
        color: #ffffff !important;
        border: 1px solid #7c83ff !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        padding: 0.65rem 1.1rem !important;
    }

    .stDownloadButton > button:hover {
        color: #ffffff !important;
        border-color: #a99cff !important;
    }

    /* =====================================================
       TABLES
       ===================================================== */

    [data-testid="stDataFrame"] {
        border: 1px solid #334766;
        border-radius: 10px;
        overflow: hidden;
    }

    /* =====================================================
       EXPANDERS
       ===================================================== */

    div[data-testid="stExpander"] {
        background: #17233a !important;
        border: 1px solid #394b68 !important;
        border-radius: 10px !important;
    }

    div[data-testid="stExpander"] details summary {
        color: #ffffff !important;
        background: #1b2942 !important;
        border-radius: 10px !important;
    }

    div[data-testid="stExpander"] details summary p,
    div[data-testid="stExpander"] details summary span,
    div[data-testid="stExpander"] details summary svg {
        color: #ffffff !important;
        fill: #ffffff !important;
    }

    /* Select box text */
    [data-testid="stSelectbox"] label {
        color: #f1f5f9 !important;
    }

    /* Progress bar */
    [data-testid="stProgress"] > div {
        background: #273650 !important;
    }

    [data-testid="stProgress"] [data-testid="stProgressBar"] {
        background: linear-gradient(
            90deg, #6857e8, #477ff7
        ) !important;
    }
    
    /* Section headings with SVG icons */
    .section-heading {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 0 16px 0;
    padding: 0;
    color: #f1f5f9 !important;
    font-family: inherit;
    font-size: 1.25rem;
    font-weight: 650;
    line-height: 1.5;
}

.section-heading span {
    color: #f1f5f9 !important;
    background: transparent !important;
}

.section-heading svg {
    width: 28px;
    height: 28px;
    flex-shrink: 0;
}
    /* Responsive columns */
    @media (max-width: 700px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        [data-testid="stMetric"] {
            padding: 12px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# REUSABLE SVG ICONS
# =========================================================

JOB_ICON = """
<svg xmlns="http://www.w3.org/2000/svg"
     width="28" height="28" viewBox="0 0 24 24"
     fill="none" stroke="#a99cff" stroke-width="1.8"
     stroke-linecap="round" stroke-linejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <path d="M14 2v6h6"/>
    <path d="M8 13h8"/>
    <path d="M8 17h8"/>
    <path d="M8 9h2"/>
</svg>
"""

RESUME_ICON = """
<svg xmlns="http://www.w3.org/2000/svg"
     width="28" height="28" viewBox="0 0 24 24"
     fill="none" stroke="#7db7ff" stroke-width="1.8"
     stroke-linecap="round" stroke-linejoin="round">
    <path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
    <circle cx="10" cy="7" r="4"/>
    <path d="M20 8v6"/>
    <path d="M23 11h-6"/>
</svg>
"""

TROPHY_ICON = """
<svg xmlns="http://www.w3.org/2000/svg"
     width="30" height="30" viewBox="0 0 24 24"
     fill="none" stroke="#9585ff" stroke-width="1.8"
     stroke-linecap="round" stroke-linejoin="round">
    <path d="M8 21h8"/>
    <path d="M12 17v4"/>
    <path d="M7 4h10v5a5 5 0 0 1-10 0V4Z"/>
    <path d="M7 7H4v2a4 4 0 0 0 4 4"/>
    <path d="M17 7h3v2a4 4 0 0 1-4 4"/>
</svg>
"""


# HEADER

st.title("AI Resume Screener")

st.write(
    "Screen resumes against a job description, rank candidates "
    "by skill match, and review potential consistency issues."
)


# =========================================================
# UPLOAD UI — TWO CARDS
# =========================================================

st.divider()

st.subheader("Bulk Resume Screening")

st.caption(
    "Upload a job description and candidate resumes "
    "to identify and rank the best matches."
)

job_col, resume_col = st.columns(2, gap="large")

# ---------------------------------------------------------
# JOB DESCRIPTION CARD
# ---------------------------------------------------------

with job_col:
    with st.container(border=True):
        icon_col, title_col = st.columns([0.5, 9.5], gap="small")

    with icon_col:
        st.markdown(JOB_ICON, unsafe_allow_html=True)

    with title_col:
        st.markdown("#### Job Description")

        st.caption("Upload the role requirements.")

        job_pdf = st.file_uploader(
            "Choose job description PDF",
            type=["pdf"],
            accept_multiple_files=False,
            key="job_description_upload",
        )

        if job_pdf is not None:
            st.success(f"Ready: {job_pdf.name}")
            st.caption(
                f"File size: {len(job_pdf.getvalue()) / 1024:.1f} KB"
            )
        else:
            st.caption("PDF format · One file")


# ---------------------------------------------------------
# CANDIDATE RESUMES CARD
# ---------------------------------------------------------

with resume_col:
    with st.container(border=True):
          icon_col, title_col = st.columns([1, 9], gap="small")

    with icon_col:
        st.markdown(RESUME_ICON, unsafe_allow_html=True)

    with title_col:
        st.markdown("#### Candidate Resumes")

        st.caption("Upload multiple candidate resumes.")

        resume_pdfs = st.file_uploader(
            "Choose resume PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            key="resume_bulk_upload",
        )

        if resume_pdfs:
            total_size = sum(
                len(resume.getvalue())
                for resume in resume_pdfs
            )

            st.success(
                f"{len(resume_pdfs)} resume(s) selected"
            )

            with st.expander("View uploaded files"):
                for resume in resume_pdfs:
                    st.write(
                        f"{resume.name} · "
                        f"{len(resume.getvalue()) / 1024:.1f} KB"
                    )

            st.caption(
                f"Total size: "
                f"{total_size / (1024 * 1024):.2f} MB"
            )
        else:
            st.caption("PDF format · Multiple files supported")


# =========================================================
# COMPACT SCREENING BUTTON
# =========================================================

st.write("")

left_space, button_col, right_space = st.columns(
    [1.5, 1, 1.5]
)

with button_col:
    run_screening = st.button(
        "Run AI Screening →",
        type="primary",
        use_container_width=True,
        disabled=not (job_pdf is not None and resume_pdfs),
    )


# =========================================================
# SCREENING REQUEST
# =========================================================

if run_screening:
    if job_pdf is None:
        st.error("Please upload a job description PDF.")

    elif not resume_pdfs:
        st.error("Please upload at least one resume PDF.")

    else:
        files = [
            (
                "job_description",
                (
                    job_pdf.name,
                    job_pdf.getvalue(),
                    "application/pdf",
                ),
            )
        ]

        for resume in resume_pdfs:
            files.append(
                (
                    "resumes",
                    (
                        resume.name,
                        resume.getvalue(),
                        "application/pdf",
                    ),
                )
            )

        try:
            with st.spinner(
                "Screening resumes, matching skills, "
                "and checking consistency..."
            ):
                response = requests.post(
                    f"{API_URL}/screen-uploaded",
                    files=files,
                    timeout=300,
                )

                response.raise_for_status()
                result = response.json()

            if not isinstance(result, dict):
                st.error(
                    "The backend returned an unexpected response."
                )

            elif not isinstance(result.get("results"), list):
                st.error(
                    "The backend response does not contain a results "
                    "list. Check the /screen-uploaded endpoint."
                )

            else:
                candidates = []
                errors = []

                for item in result["results"]:
                    if not isinstance(item, dict):
                        errors.append({
                            "Resume": "Unknown",
                            "Error": (
                                "Invalid result returned by backend."
                            ),
                        })
                        continue

                    filename = item.get(
                        "filename",
                        "Unknown PDF",
                    )

                    if item.get("status") != "success":
                        errors.append({
                            "Resume": filename,
                            "Error": item.get(
                                "error",
                                "Screening failed.",
                            ),
                        })
                        continue

                    candidate = item.get("candidate") or {}
                    match = item.get("match") or {}
                    flags = item.get("flags") or []

                    if not isinstance(candidate, dict):
                        candidate = {}

                    if not isinstance(match, dict):
                        match = {}

                    if not isinstance(flags, list):
                        flags = [flags]

                    # Adapt common score field names.
                    score = match.get(
                        "match_score",
                        match.get("score"),
                    )

                    try:
                        score = (
                            float(score)
                            if score is not None
                            else None
                        )
                    except (TypeError, ValueError):
                        score = None

                    skills = candidate.get("skills", [])
                    matched = match.get("matched_skills", [])

                    missing_required = match.get(
                        "missing_required_skills",
                        [],
                    )

                    missing_preferred = match.get(
                        "missing_preferred_skills",
                        [],
                    )

                    reasons = match.get("reasons", [])

                    if not isinstance(skills, list):
                        skills = []

                    if not isinstance(matched, list):
                        matched = []

                    if not isinstance(missing_required, list):
                        missing_required = []

                    if not isinstance(missing_preferred, list):
                        missing_preferred = []

                    if not isinstance(reasons, list):
                        reasons = [str(reasons)]

                    candidates.append({
                        "rank": 0,
                        "candidate_name": (
                            candidate.get("candidate_name")
                            or candidate.get("name")
                            or candidate.get("full_name")
                            or "Unknown"
                        ),
                        "filename": filename,
                        "match_score": score,
                        "skills": skills,
                        "matched_skills": matched,
                        "missing_required_skills": missing_required,
                        "missing_preferred_skills": missing_preferred,
                        "reasons": reasons,
                        "consistency_flags": flags,
                        "flag_count": len(flags),
                    })

                # Rank scored candidates first.
                candidates.sort(
                    key=lambda c: (
                        c["match_score"] is not None,
                        c["match_score"]
                        if c["match_score"] is not None
                        else -1,
                    ),
                    reverse=True,
                )

                for rank, candidate in enumerate(
                    candidates,
                    start=1,
                ):
                    candidate["rank"] = rank

                st.session_state["batch_results"] = {
                    "resumes_found": result.get(
                        "total_resumes",
                        len(resume_pdfs),
                    ),
                    "resumes_screened": len(candidates),
                    "resumes_with_errors": len(errors),
                    "ranked_candidates": candidates,
                    "errors": errors,
                    "scoring_method": (
                        "Scores are returned by the backend "
                        "matching service."
                    ),
                }

               # st.success("Screening completed successfully.")

        except requests.Timeout:
            st.error(
                "The screening request timed out. Try screening "
                "fewer resumes at once or increase the API timeout."
            )

        except requests.RequestException as exc:
            st.error(
                "Could not connect to the FastAPI backend. Check "
                "that the backend is running and /screen-uploaded "
                "is available."
            )
            st.caption(str(exc))

        except ValueError as exc:
            st.error(
                f"The backend returned invalid JSON: {exc}"
            )

# =========================================================
# RANKED CANDIDATES
# =========================================================

batch_results = st.session_state.get("batch_results")

if not isinstance(batch_results, dict):
    st.info(
        "Your candidate results will appear here after you upload "
        "the files and run screening."
    )

else:
    st.divider()

    # Section heading with trophy icon
    icon_col, title_col = st.columns([1, 9], gap="small")

    with icon_col:
        st.markdown(TROPHY_ICON, unsafe_allow_html=True)

    with title_col:
        st.markdown("#### Ranked Candidates")

    total = batch_results.get("resumes_found", 0)
    screened = batch_results.get("resumes_screened", 0)
    errors_count = batch_results.get("resumes_with_errors", 0)

    candidates = batch_results.get("ranked_candidates", [])
    errors = batch_results.get("errors", [])

    # Summary metrics
    scores = [
        float(candidate["match_score"])
        for candidate in candidates
        if candidate.get("match_score") is not None
    ]

    top_score = max(scores, default=0)

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric("Resumes Uploaded", total)
    metric2.metric("Successfully Screened", screened)
    metric3.metric("Top Match Score", f"{top_score:.1f}%")
    metric4.metric("Screening Errors", errors_count)

    progress = min(screened / total, 1.0) if total else 0.0

    

    st.caption(batch_results.get("scoring_method", ""))

    if not candidates:
        st.warning("No ranked candidates were returned.")

    else:
        # Ranked candidates table
        table_rows = []

        for candidate in candidates:
            flags = candidate.get("consistency_flags", [])
            score = candidate.get("match_score")

            flag_messages = []

            for flag in flags:
                if isinstance(flag, dict):
                    flag_messages.append(str(flag.get("message", flag)))
                else:
                    flag_messages.append(str(flag))

            table_rows.append({
                "Rank": candidate.get("rank"),
                "Candidate": candidate.get("candidate_name", "Unknown"),
                "Resume": candidate.get("filename", ""),
                "Match": f"{score:.1f}%" if score is not None else "N/A",
                "Matched Skills": ", ".join(
                    str(skill)
                    for skill in candidate.get("matched_skills", [])
                ) or "—",
                "Missing Skills": ", ".join(
                    str(skill)
                    for skill in candidate.get("missing_required_skills", [])
                ) or "—",
                "Flags": len(flags),
                "Flag Summary": " | ".join(flag_messages) or "None",
            })

        df = pd.DataFrame(table_rows)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=min(420, 38 * (len(df) + 1)),
        )

        st.download_button(
            "Download Ranked Results (CSV)",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="ranked_resume_screening.csv",
            mime="text/csv",
        )

        # Candidate details
        st.subheader("Candidate Details")

        def candidate_label(candidate):
            score = candidate.get("match_score")
            score_text = f"{score:.1f}%" if score is not None else "N/A"

            return (
                f"#{candidate.get('rank', '-')} — "
                f"{candidate.get('candidate_name', 'Unknown')} "
                f"({score_text})"
            )

        selected_candidate = st.selectbox(
            "Select a candidate to inspect",
            candidates,
            format_func=candidate_label,
            key="candidate_details_select",
        )

        with st.expander("View selected candidate details", expanded=True):
            detail1, detail2, detail3 = st.columns(3)

            detail1.metric("Rank", selected_candidate.get("rank", "N/A"))

            score = selected_candidate.get("match_score")

            detail2.metric(
                "Match Score",
                f"{score:.1f}%" if score is not None else "N/A",
            )

            flags = selected_candidate.get("consistency_flags", [])

            detail3.metric(
                "Consistency Flags",
                selected_candidate.get("flag_count", len(flags)),
            )

            if score is not None:
                st.progress(
                    max(0.0, min(float(score) / 100, 1.0)),
                    text=f"{score:.1f}% match score",
                )

            st.write("**Resume**")
            st.write(selected_candidate.get("filename", "Not available"))

            st.write("**Detected Skills**")
            st.write(", ".join(map(str, selected_candidate.get("skills", []))) or "None detected")

            st.write("**Matched Skills**")
            st.write(", ".join(map(str, selected_candidate.get("matched_skills", []))) or "None detected")

            st.write("**Missing Required Skills**")
            st.write(", ".join(map(str, selected_candidate.get("missing_required_skills", []))) or "None detected")

            st.write("**Missing Preferred Skills**")
            st.write(", ".join(map(str, selected_candidate.get("missing_preferred_skills", []))) or "None detected")

            st.write("**Screening Reasons**")
            reasons = selected_candidate.get("reasons", [])

            if reasons:
                for reason in reasons:
                    st.write(f"- {reason}")
            else:
                st.write("No reasons supplied by the backend.")

            st.write("**Consistency Checks**")

            if flags:
                for flag in flags:
                    message = (
                        flag.get("message", str(flag))
                        if isinstance(flag, dict)
                        else str(flag)
                    )
                    st.warning(message)
            else:
                st.success("No consistency flags detected.")

            st.caption(
                "Missing skills mean they were not detected in "
                "the extracted resume text. Consistency flags "
                "are signals for review, not proof of "
                "misrepresentation."
            )

    # Screening errors
    if errors:
        with st.expander("View files that could not be screened"):
            st.dataframe(
                pd.DataFrame(errors),
                use_container_width=True,
                hide_index=True,
            )

