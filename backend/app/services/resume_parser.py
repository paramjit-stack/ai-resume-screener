
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


def extract_resume_details(text: str) -> dict:
    """Extract basic information from resume text."""

    # Find email address
    email_match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text,
    )
    email = email_match.group(0) if email_match else None

    # Find possible phone number
    phone_match = re.search(
        r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)",
        text,
    )
    phone = phone_match.group(0).strip() if phone_match else None

    # Find skills from our known skills list
    skills = []
    for skill in KNOWN_SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text, re.IGNORECASE):
            skills.append(skill)

    # Look for education-related keywords
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
        line.strip()
        for line in text.splitlines()
        if any(
            keyword.lower() in line.lower()
            for keyword in education_keywords
        )
    ]

    # Use the first non-empty line as a possible name
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidate_name = None

    if lines:
        first_line = lines[0]
        if (
            len(first_line.split()) <= 5
            and not re.search(r"[@\d]", first_line)
        ):
            candidate_name = first_line

    return {
        "candidate_name": candidate_name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": education,
    }
