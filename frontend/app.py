import os
import streamlit as st
import requests
import pandas as pd

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide",
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1020 0%, #111a30 100%);
    color: #f1f5f9;
}
.block-container {
    padding-top: 2rem;
    max-width: 1450px;
}
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1b2942, #182035);
    border: 1px solid #334766;
    padding: 20px 22px;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}
[data-testid="stMetricLabel"] {
    color: #b8c5de;
}
[data-testid="stMetricValue"] {
    color: #ffffff;
    font-size: 2rem;
    font-weight: 700;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #6857e8, #477ff7);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.65rem 1.2rem;
    font-weight: 600;
}
div.stButton > button[kind="primary"]:hover {
    border: 1px solid #a99cff;
    color: white;
}
[data-testid="stDataFrame"] {
    border: 1px solid #334766;
    border-radius: 12px;
    overflow: hidden;
}
div[data-testid="stExpander"] {
    border: 1px solid #334766;
    border-radius: 12px;
}
/* Download button: always visible */
.stDownloadButton > button {
    background: linear-gradient(90deg, #6857e8, #477ff7) !important;
    color: #ffffff !important;
    border: 1px solid #7c83ff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.2rem !important;
    opacity: 1 !important;
}

.stDownloadButton > button p,
.stDownloadButton > button span,
.stDownloadButton > button svg {
    color: #ffffff !important;
    fill: #ffffff !important;
}

.stDownloadButton > button:hover {
    background: linear-gradient(90deg, #5745d4, #3268df) !important;
    color: #ffffff !important;
}

/* Selected candidate expander: visible title */
div[data-testid="stExpander"] {
    background: #17233a !important;
    border: 1px solid #53698c !important;
    border-radius: 12px !important;
}

div[data-testid="stExpander"] details summary {
    color: #ffffff !important;
    background: #1b2942 !important;
    border-radius: 12px !important;
}

div[data-testid="stExpander"] details summary p,
div[data-testid="stExpander"] details summary span,
div[data-testid="stExpander"] details summary svg {
    color: #ffffff !important;
    fill: #ffffff !important;
    opacity: 1 !important;
}

div[data-testid="stExpander"] details summary:hover {
    background: #263957 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📄 AI Resume Screener")
st.write(
    "Screen resumes against the supplied job description, "
    "rank candidates by weighted skill overlap, and review "
    "potential consistency issues."
)

st.subheader("📊 Batch Screening")
st.write(
    "Screen all PDF resumes in the assessment dataset "
    "against the job description PDF."
)

if st.button("Screen All Resumes", type="primary"):
    with st.spinner("Screening resumes and ranking candidates..."):
        try:
            response = requests.post(
                f"{API_URL}/screen-all",
                timeout=300,
            )
            response.raise_for_status()

            result = response.json()

            if not isinstance(result, dict):
                st.error("The backend returned an unexpected response.")
            else:
                st.session_state["batch_results"] = result
                st.success("Screening completed.")

        except requests.RequestException as exc:
            st.error(
                "Batch screening failed. Check that the FastAPI "
                "backend is running and accessible."
            )
            st.caption(str(exc))

        except ValueError:
            st.error("The backend returned an invalid JSON response.")

batch_results = st.session_state.get("batch_results")

if not isinstance(batch_results, dict):
    st.info("Click **Screen All Resumes** to start screening and view results.")

else:
    st.divider()
    st.header("🏆 Ranked Candidates")

    total = batch_results.get("resumes_found", 0)
    screened = batch_results.get("resumes_screened", 0)
    errors_count = batch_results.get("resumes_with_errors", 0)
    candidates = batch_results.get("ranked_candidates", [])

    scores = [
        float(candidate["match_score"])
        for candidate in candidates
        if isinstance(candidate, dict)
        and candidate.get("match_score") is not None
    ]
    top_score = max(scores, default=0)

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("📄 Resumes Found", total)
    metric2.metric("✅ Successfully Screened", screened)
    metric3.metric("🏆 Top Match Score", f"{top_score:.1f}%")
    metric4.metric("⚠️ Screening Errors", errors_count)

    st.subheader("Screening Progress")
    progress = min(screened / total, 1.0) if total else 0.0
    st.progress(
        progress,
        text=f"{screened} of {total} resumes processed",
    )

    st.caption(batch_results.get("scoring_method", ""))

    if not candidates:
        st.warning("No ranked candidates were returned.")

    else:
        table_rows = []

        for candidate in candidates:
            flags = candidate.get("consistency_flags", [])
            score = candidate.get("match_score")

            table_rows.append({
                "Rank": candidate.get("rank"),
                "Candidate": candidate.get("candidate_name", "Unknown"),
                "Resume": candidate.get("filename", ""),
                "Score (%)": score,
                "Matched Skills": ", ".join(
                    candidate.get("matched_skills", [])
                ),
                "Missing Required Skills": ", ".join(
                    candidate.get("missing_required_skills", [])
                ),
                "Missing Preferred Skills": ", ".join(
                    candidate.get("missing_preferred_skills", [])
                ),
                "Reasons": " | ".join(candidate.get("reasons", [])),
                "Flag Count": candidate.get("flag_count", len(flags)),
                "Consistency Flags": " | ".join(
                    flag.get("message", str(flag))
                    if isinstance(flag, dict)
                    else str(flag)
                    for flag in flags
                ) or "No flags detected",
            })

        df = pd.DataFrame(table_rows)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "⬇️ Download Ranked Results (CSV)",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="ranked_resume_screening.csv",
            mime="text/csv",
        )

        def candidate_label(candidate):
            score = candidate.get("match_score")
            score_text = f"{score}%" if score is not None else "N/A"
            return (
                f"#{candidate.get('rank', '-')} — "
                f"{candidate.get('candidate_name', 'Unknown')} "
                f"({score_text})"
            )

        selected_candidate = st.selectbox(
            "Select a candidate to inspect",
            candidates,
            format_func=candidate_label,
        )

        with st.expander(
            "View selected candidate details",
            expanded=True,
        ):
            detail1, detail2, detail3 = st.columns(3)

            detail1.metric(
                "Rank",
                selected_candidate.get("rank", "N/A"),
            )

            score = selected_candidate.get("match_score")

            detail2.metric(
                "Match score",
                f"{score}%" if score is not None else "N/A",
            )

            detail3.metric(
                "Consistency flags",
                selected_candidate.get(
                    "flag_count",
                    len(selected_candidate.get("consistency_flags", [])),
                ),
            )

            if score is not None:
                st.progress(
                    max(0.0, min(float(score) / 100, 1.0)),
                    text=f"{float(score):.1f}% weighted skill overlap",
                )

            st.write("**Resume**")
            st.write(selected_candidate.get("filename", "Not available"))

            st.write("**Detected skills**")
            st.write(
                ", ".join(selected_candidate.get("skills", []))
                or "None detected"
            )

            st.write("**Matched skills**")
            st.write(
                ", ".join(selected_candidate.get("matched_skills", []))
                or "None detected"
            )

            st.write("**Missing required skills**")
            st.write(
                ", ".join(
                    selected_candidate.get("missing_required_skills", [])
                ) or "None detected"
            )

            st.write("**Missing preferred skills**")
            st.write(
                ", ".join(
                    selected_candidate.get("missing_preferred_skills", [])
                ) or "None detected"
            )

            st.write("**Screening reasons**")
            reasons = selected_candidate.get("reasons", [])

            if reasons:
                for reason in reasons:
                    st.write(f"- {reason}")
            else:
                st.write("No reasons supplied by the backend.")

            st.write("**Consistency checks**")
            flags = selected_candidate.get("consistency_flags", [])

            if flags:
                for flag in flags:
                    if isinstance(flag, dict):
                        st.warning(flag.get("message", str(flag)))
                    else:
                        st.warning(str(flag))
            else:
                st.success("No consistency flags detected.")

            st.caption(
                "A missing skill means it was not detected in the "
                "extracted resume text. A consistency flag is a signal "
                "for review, not proof of misrepresentation."
            )

    errors = batch_results.get("errors", [])

    if errors:
        with st.expander("View files that could not be screened"):
            st.json(errors)
