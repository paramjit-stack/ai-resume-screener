
import re


KNOWN_SKILLS = [
    "JavaScript",
    "TypeScript",
    "React Native",
    "Node.js",
    "React",
    "REST API",
    "PostgreSQL",
    "MySQL",
    "SQL",
    "Git",
    "CI/CD",
    "AWS",
    "Azure",
    "Docker",
    "Python",
    "Java",
    "C++",
    "FastAPI",
    "Flask",
    "Django",
    "HTML",
    "CSS",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "Natural Language Processing",
    "Generative AI",
    "RAG",
    "LangChain",
    "TensorFlow",
    "PyTorch",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "MongoDB",
]


def normalize_skill(skill: str) -> str:
    return re.sub(r"\s+", " ", skill.strip().lower())


def find_skills(text: str) -> list[str]:
    found = []

    for skill in KNOWN_SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)

    return found


def extract_sections(job_description: str) -> tuple[str, str]:
    """Extract required and preferred sections when headings exist."""

    required_match = re.search(
        r"^\s*Required\s*$\s*(.*?)(?=^\s*(?:Nice to have|Preferred Skills)\s*$|\Z)",
        job_description,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    preferred_match = re.search(
        r"^\s*(?:Nice to have|Preferred Skills)\s*$\s*(.*)",
        job_description,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    if required_match:
        return (
            required_match.group(1),
            preferred_match.group(1) if preferred_match else "",
        )

    # Also support headings such as "Required Skills:".
    required_match = re.search(
        r"required skills\s*:(.*?)(?:\n\s*(?:preferred skills|nice to have)\s*:|\Z)",
        job_description,
        re.IGNORECASE | re.DOTALL,
    )

    preferred_match = re.search(
        r"(?:preferred skills|nice to have)\s*:(.*)",
        job_description,
        re.IGNORECASE | re.DOTALL,
    )

    if required_match:
        return (
            required_match.group(1),
            preferred_match.group(1) if preferred_match else "",
        )

    # If there are no section headings, treat all detected skills
    # as required rather than guessing which ones are preferred.
    return job_description, ""


def match_resume_to_job(
    candidate_skills: list[str],
    job_description: str,
) -> dict:
    """
    Calculate transparent weighted skill overlap.

    Required criteria are worth 2 points each.
    Preferred criteria are worth 1 point each.
    Alternative technologies count as one criterion.
    """

    required_text, preferred_text = extract_sections(job_description)

    required_skills = find_skills(required_text)
    preferred_skills = find_skills(preferred_text)

    # A skill mentioned in both sections is counted only as required.
    required_set = {
        normalize_skill(skill) for skill in required_skills
    }

    preferred_skills = [
        skill for skill in preferred_skills
        if normalize_skill(skill) not in required_set
    ]

    candidate_set = {
        normalize_skill(skill) for skill in candidate_skills
    }

    # Handle JavaScript/TypeScript as one criterion when the JD
    # explicitly presents them as alternatives.
    js_ts_alternative = re.search(
        r"JavaScript\s*/\s*TypeScript|TypeScript\s*/\s*JavaScript",
        job_description,
        re.IGNORECASE,
    )

    if js_ts_alternative:
        has_javascript = "javascript" in candidate_set
        has_typescript = "typescript" in candidate_set

        required_skills = [
            skill for skill in required_skills
            if normalize_skill(skill) not in {"javascript", "typescript"}
        ]
        preferred_skills = [
            skill for skill in preferred_skills
            if normalize_skill(skill) not in {"javascript", "typescript"}
        ]

        if re.search(
            r"JavaScript\s*/\s*TypeScript|TypeScript\s*/\s*JavaScript",
            required_text,
            re.IGNORECASE,
        ):
            required_skills.append("JavaScript/TypeScript")
        elif re.search(
            r"JavaScript\s*/\s*TypeScript|TypeScript\s*/\s*JavaScript",
            preferred_text,
            re.IGNORECASE,
        ):
            preferred_skills.append("JavaScript/TypeScript")

    # PostgreSQL OR MySQL is one database requirement, not two.
    database_terms = {"sql", "postgresql", "mysql"}
    required_database_terms = [
        skill for skill in required_skills
        if normalize_skill(skill) in database_terms
    ]

    if len(required_database_terms) > 1:
        required_skills = [
            skill for skill in required_skills
            if normalize_skill(skill) not in database_terms
        ]
        required_skills.append("SQL database (SQL, PostgreSQL or MySQL)")

    preferred_database_terms = [
        skill for skill in preferred_skills
        if normalize_skill(skill) in database_terms
    ]

    if len(preferred_database_terms) > 1:
        preferred_skills = [
            skill for skill in preferred_skills
            if normalize_skill(skill) not in database_terms
        ]
        preferred_skills.append("SQL database (SQL, PostgreSQL or MySQL)")

    def criterion_is_matched(skill: str) -> bool:
        normalized = normalize_skill(skill)

        if normalized == "javascript/typescript":
            return bool(
                {"javascript", "typescript"} & candidate_set
            )

        if normalized == "sql database (sql, postgresql or mysql)":
            return bool(database_terms & candidate_set)

        return normalized in candidate_set

    matched_required = [
        skill for skill in required_skills
        if criterion_is_matched(skill)
    ]
    missing_required = [
        skill for skill in required_skills
        if not criterion_is_matched(skill)
    ]
    matched_preferred = [
        skill for skill in preferred_skills
        if criterion_is_matched(skill)
    ]
    missing_preferred = [
        skill for skill in preferred_skills
        if not criterion_is_matched(skill)
    ]

    total_weight = (
        2 * len(required_skills) + len(preferred_skills)
    )

    if total_weight:
        earned_weight = (
            2 * len(matched_required) + len(matched_preferred)
        )
        score = round(earned_weight / total_weight * 100)
    else:
        score = None

    return {
        "match_score": score,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "matched_skills": matched_required + matched_preferred,
        "missing_required_skills": missing_required,
        "missing_preferred_skills": missing_preferred,
        "matched_required_skills": matched_required,
        "matched_preferred_skills": matched_preferred,
        "scoring_method": (
            "Each detected required criterion is worth 2 points; "
            "each detected preferred criterion is worth 1 point. "
            "Alternative database technologies count as one criterion."
        ),
        "message": (
            "This score measures detected skill overlap only. "
            "It does not verify years of production experience, "
            "evidence quality, written English, or resume consistency. "
            "A skill not detected in the extracted text may still "
            "be present in the original resume."
        ),
    }
