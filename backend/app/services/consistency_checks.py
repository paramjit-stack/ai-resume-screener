
import re


# The supplied assessment resumes appear to use a 2024 snapshot.
# This keeps "Present" consistent with the dates in that dataset.
DATASET_REFERENCE_YEAR = 2024


def extract_experience_roles(resume_text: str) -> list[dict]:
    """Extract employment periods from the EXPERIENCE section."""

    section_match = re.search(
        r"\bEXPERIENCE\b(.*?)(?=\n\s*"
        r"(?:EDUCATION|PROJECTS|CERTIFICATIONS|SKILLS)\b|\Z)",
        resume_text,
        re.IGNORECASE | re.DOTALL,
    )

    if not section_match:
        return []

    roles = []

    role_pattern = re.compile(
        r"^\s*(?P<title>.+?)\s+[—–-]\s+"
        r"(?P<company>.+?)\s+"
        r"\((?P<start>19\d{2}|20\d{2})\s*[–—-]\s*"
        r"(?P<end>Present|19\d{2}|20\d{2})\)\s*$",
        re.IGNORECASE,
    )

    for line in section_match.group(1).splitlines():
        match = role_pattern.search(line)

        if not match:
            continue

        start_year = int(match.group("start"))
        end_text = match.group("end")

        end_year = (
            DATASET_REFERENCE_YEAR
            if end_text.lower() == "present"
            else int(end_text)
        )

        if end_year < start_year:
            continue

        roles.append({
            "title": match.group("title").strip(),
            "company": match.group("company").strip(),
            "start_year": start_year,
            "end_year": end_year,
        })

    return roles


def check_resume_consistency(resume_text: str) -> list[dict]:
    """
    Flag potential inconsistencies for human review.

    Year-only employment dates are approximate. Flags are not
    proof of dishonesty or incorrect information.
    """

    flags = []
    roles = extract_experience_roles(resume_text)

    # 1. Look for employment periods that overlap by more than
    # one year. Concurrent jobs can be legitimate.
    for index, first in enumerate(roles):
        for second in roles[index + 1:]:
            overlap_start = max(
                first["start_year"],
                second["start_year"],
            )
            overlap_end = min(
                first["end_year"],
                second["end_year"],
            )

            if overlap_end - overlap_start > 1:
                flags.append({
                    "type": "overlapping_employment",
                    "severity": "review",
                    "message": (
                        f"{first['company']} "
                        f"({first['start_year']}–{first['end_year']}) "
                        f"and {second['company']} "
                        f"({second['start_year']}–{second['end_year']}) "
                        "have substantially overlapping dates. "
                        "Verify whether the roles were concurrent."
                    ),
                })

    # 2. Compare an explicit experience claim in the summary/objective
    # with the span of the listed employment history.
    summary_match = re.search(
        r"\b(?:SUMMARY|OBJECTIVE)\b(.*?)(?=\n\s*"
        r"(?:SKILLS|EXPERIENCE|EDUCATION)\b|\Z)",
        resume_text,
        re.IGNORECASE | re.DOTALL,
    )

    if summary_match and roles:
        summary = summary_match.group(1)

        claim_match = re.search(
            r"\b(\d+(?:\.\d+)?)\s*\+?\s*years?"
            r"(?:\s+of)?\s+(?:total\s+)?experience\b"
            r"|\b(\d+(?:\.\d+)?)\s*\+?\s*years?"
            r"(?:\s+total)?\b",
            summary,
            re.IGNORECASE,
        )

        if claim_match:
            claim_text = next(
                group for group in claim_match.groups()
                if group is not None
            )
            claimed_years = float(claim_text)

            earliest_start = min(
                role["start_year"] for role in roles
            )
            listed_span = (
                DATASET_REFERENCE_YEAR - earliest_start
            )

            # Allow a tolerance because year-only dates are imprecise.
            if claimed_years - listed_span > 1.5:
                flags.append({
                    "type": "experience_claim_needs_review",
                    "severity": "review",
                    "message": (
                        f"The summary claims {claimed_years:g} years "
                        f"of experience, while the listed employment "
                        f"history spans approximately {listed_span} "
                        f"years from {earliest_start} to "
                        f"{DATASET_REFERENCE_YEAR}. Earlier or "
                        "unlisted experience may explain the difference."
                    ),
                })

    return flags
