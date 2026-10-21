
import streamlit as st
import requests
from pathlib import Path
import pandas as pd

API_URL = "http://127.0.0.1:8000"

# Batch-screening controls
st.subheader("📊 Batch Screening")
st.write(
    "Screen all PDF resumes in resumes against the "
    "job description PDF stored in assets."
)

if st.button("Screen All 25 Resumes", type="primary"):
    with st.spinner("Screening all resumes and ranking candidates..."):
        try:
            response = requests.post(
                f"{API_URL}/screen-all",
                timeout=300,
            )
            response.raise_for_status()
            st.session_state["batch_results"] = response.json()
        except requests.RequestException as exc:
            st.error("Batch screening failed. Check that FastAPI is running.")
            st.caption(str(exc))

batch_results = st.session_state.get("batch_results")

if batch_results:
    st.divider()
    st.header("🏆 Ranked Candidates")

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("PDFs found", batch_results.get("resumes_found", 0))
    metric2.metric("Successfully screened", batch_results.get("resumes_screened", 0))
    metric3.metric("Errors", batch_results.get("resumes_with_errors", 0))

    st.caption(batch_results.get("scoring_method", ""))

    candidates = batch_results.get("ranked_candidates", [])

    if candidates:
        table_rows = []

        for candidate in candidates:
            score = candidate.get("match_score")
            table_rows.append({
                "Rank": candidate.get("rank"),
                "Candidate": candidate.get("candidate_name"),
                "Resume": candidate.get("filename"),
                "Score (%)": score,
                "Matched Skills": ", ".join(candidate.get("matched_skills", [])),
                "Missing Required Skills": ", ".join(
                    candidate.get("missing_required_skills", [])
                ),
                "Reason": " | ".join(candidate.get("reasons", [])),
                "Flag Count": candidate.get("flag_count", 0),
                "Consistency Flags": " | ".join(
                    flag.get("message", "")
                    for flag in candidate.get("consistency_flags", [])
                ) or "No flags detected",
            })

        df = pd.DataFrame(table_rows)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Ranked Results (CSV)",
            data=csv_data,
            file_name="ranked_resume_screening.csv",
            mime="text/csv",
        )

        selected_candidate = st.selectbox(
            "Inspect candidate details",
            candidates,
            format_func=lambda item: (
                f"#{item.get('rank')} — {item.get('candidate_name')} "
                f"({item.get('match_score')}%)"
            ),
        )

        with st.expander("View selected candidate details"):
            st.write("**Detected skills**")
            st.write(", ".join(selected_candidate.get("skills", [])) or "None")

            st.write("**Matched skills**")
            st.write(", ".join(selected_candidate.get("matched_skills", [])) or "None")

            st.write("**Missing required skills**")
            st.write(
                ", ".join(selected_candidate.get("missing_required_skills", []))
                or "None detected"
            )

            st.write("**Missing preferred skills**")
            st.write(
                ", ".join(selected_candidate.get("missing_preferred_skills", []))
                or "None detected"
            )

            st.write("**Reasons**")
            for reason in selected_candidate.get("reasons", []):
                st.write(f"- {reason}")

    if batch_results.get("errors"):
        with st.expander("View files that could not be screened"):
            st.json(batch_results["errors"])

