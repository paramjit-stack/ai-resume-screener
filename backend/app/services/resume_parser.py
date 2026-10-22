
import re


KNOWN_SKILLS = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C++",
    "SQL",
    "FastAPI",
    "Flask",
    "Django",
    "React",
    "Node.js",
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
    "Docker",
    "Git",
    "AWS",
    "Azure",
    "MongoDB",
    "PostgreSQL",
]


INVALID_NAME_PATTERNS = re.compile(
    r"\b("
    r"full[- ]stack developer|"
    r"software developer|"
    r"senior developer|"
    r"junior developer|"
    r"python developer|"
    r"frontend developer|"
    r"front[- ]end developer|"
    r"backend developer|"
    r"back[- ]end developer|"
    r"software engineer|"
    r"data scientist|"
    r"web developer|"
    r"AI engineer|"
    r"machine learning engineer|"
    r"job description|"
    r"job summary|"
    r"about the role|"
    r"required skills|"
    r"responsibilities|"
    r"qualifications|"
    r"career objective|"
    r"professional summary|"
    r"technical skills|"
    r"work experience|"
    r"education|"
    r"experience|"
    r"curriculum vitae|"
    r"resume"
    r")\b",
    re.IGNORECASE,
)


def extract_resume_details(text: str) -> dict:
    """Extract basic candidate details and skills from resume text."""

    text = text or ""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Find email address
    email_match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text,
    )
    email = email_match.group(0) if email_match else None

    # Find possible phone number
    phone_match = re.search(
        r"(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)",
        text,
    )
    phone = phone_match.group(0).strip() if phone_match else None

    # Find skills mentioned in the resume
    skills = []

    for skill in KNOWN_SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            skills.append(skill)

    # Find education-related lines
    education_keywords = [
        "Bachelor",
        "Master",
        "B.Tech",
        "M.Tech",
        "B.E.",
        "M.E.",
        "BCA",
        "MCA",
        "B.Sc",
        "M.Sc",
        "Ph.D",
        "Diploma",
        "University",
        "College",
    ]

    education = [
        line
        for line in lines
        if any(
            keyword.lower() in line.lower()
            for keyword in education_keywords
        )
    ]

    # Identify a possible candidate name from the first five lines.
    # Do not accept job titles, headings, emails, or phone numbers.
    candidate_name = None

    for line in lines[:5]:
        if len(line.split()) > 4:
            continue

        if re.search(r"[@\d]", line):
            continue

        if INVALID_NAME_PATTERNS.search(line):
            continue

        if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", line):
            continue

        # Avoid accepting generic single-word headings.
        if len(line.split()) == 1 and line.lower() in {
            "developer",
            "engineer",
            "consultant",
            "manager",
            "analyst",
            "designer",
            "recruiter",
        }:
            continue

        candidate_name = line
        break

    return {
        "candidate_name": candidate_name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": education,
    }

def validate_resume_text(text: str) -> tuple[bool, str]:
    """Check whether extracted PDF text looks like a candidate resume."""

    if not text or len(text.strip()) < 100:
        return False, (
            "Invalid Resume: The PDF contains insufficient text. "
            "Please upload a readable candidate resume."
        )

    text_lower = text.lower()

    # Common job-description phrases
    job_description_patterns = [
        r"\bjob description\b",
        r"\bjob responsibilities\b",
        r"\bkey responsibilities\b",
        r"\bwhat you will do\b",
        r"\bqualifications required\b",
        r"\bapply now\b",
        r"\bwe are hiring\b",
    ]

    # Common resume sections
    resume_patterns = [
        r"\bwork experience\b",
        r"\bprofessional experience\b",
        r"\beducation\b",
        r"\bemployment history\b",
        r"\bcareer summary\b",
        r"\bprofessional summary\b",
        r"\bprojects\b",
        r"\bcontact\b",
        r"\bemail\b",
        r"\bphone\b",
    ]

    jd_matches = sum(
        bool(re.search(pattern, text_lower))
        for pattern in job_description_patterns
    )

    resume_matches = sum(
        bool(re.search(pattern, text_lower))
        for pattern in resume_patterns
    )

    if jd_matches >= 2 and resume_matches == 0:
        return False, (
            "Invalid Resume: This document appears to be a job "
            "description, not a candidate resume. "
            "Please upload a valid resume PDF."
        )

    if resume_matches == 0:
        return False, (
            "Unable to verify this document as a resume. "
            "Please upload a candidate resume containing "
            "contact details, experience, or education."
        )

    return True, "Resume validation successful."
