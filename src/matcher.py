"""Local CV-to-job-description matching utilities.

The matcher intentionally avoids external AI APIs. It combines semantic-ish text
similarity (TF-IDF + cosine similarity) with deterministic skill overlap so the
result is explainable and reproducible.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "Python": ("python",),
    "JavaScript": ("javascript", "java script", "js"),
    "TypeScript": ("typescript", "type script", "ts"),
    "Java": ("java",),
    "C++": ("c++", "cpp"),
    "C#": ("c#", "c sharp"),
    "SQL": ("sql", "mysql", "postgresql", "postgres", "sqlite"),
    "HTML": ("html", "html5"),
    "CSS": ("css", "css3", "tailwind", "bootstrap"),
    "React": ("react", "reactjs", "react.js"),
    "Next.js": ("next.js", "nextjs"),
    "Node.js": ("node.js", "nodejs", "express"),
    "Django": ("django",),
    "Flask": ("flask",),
    "FastAPI": ("fastapi", "fast api"),
    "Streamlit": ("streamlit",),
    "Git": ("git", "github", "gitlab"),
    "Docker": ("docker", "containerization", "containers"),
    "Kubernetes": ("kubernetes", "k8s"),
    "AWS": ("aws", "amazon web services"),
    "Azure": ("azure",),
    "GCP": ("gcp", "google cloud"),
    "Linux": ("linux", "ubuntu"),
    "REST APIs": ("rest api", "rest apis", "restful", "api development"),
    "Machine Learning": ("machine learning", "ml"),
    "Deep Learning": ("deep learning", "neural network", "neural networks"),
    "NLP": ("natural language processing", "nlp"),
    "Computer Vision": ("computer vision", "opencv"),
    "Pandas": ("pandas",),
    "NumPy": ("numpy",),
    "scikit-learn": ("scikit-learn", "sklearn"),
    "PyTorch": ("pytorch", "torch"),
    "TensorFlow": ("tensorflow", "keras"),
    "Data Analysis": ("data analysis", "data analytics"),
    "Data Visualization": ("data visualization", "matplotlib", "plotly", "power bi", "tableau"),
    "Testing": ("pytest", "unit testing", "automated testing", "test automation"),
    "CI/CD": ("ci/cd", "continuous integration", "github actions"),
    "Agile": ("agile", "scrum", "kanban"),
    "WordPress": ("wordpress",),
    "SEO": ("seo", "search engine optimization"),
    "Firebase": ("firebase", "firestore"),
}


@dataclass(frozen=True)
class MatchResult:
    overall_score: int
    text_similarity: int
    skill_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    cv_skills: list[str]
    job_skills: list[str]
    recommendations: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def _normalize(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z0-9+#.\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _contains_alias(text: str, alias: str) -> bool:
    """Return True when alias appears as a phrase/token, avoiding most false hits."""
    escaped = re.escape(alias.lower())
    pattern = rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"
    return bool(re.search(pattern, text))


def extract_skills(text: str, skills: dict[str, Iterable[str]] | None = None) -> list[str]:
    normalized = _normalize(text)
    catalog = skills or SKILL_ALIASES
    found = [name for name, aliases in catalog.items() if any(_contains_alias(normalized, a) for a in aliases)]
    return sorted(found)


def _text_similarity(cv_text: str, job_text: str) -> float:
    cv = _normalize(cv_text)
    job = _normalize(job_text)
    if not cv or not job:
        return 0.0

    try:
        matrix = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True,
        ).fit_transform([cv, job])
    except ValueError:
        return 0.0
    return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])


def analyze_match(cv_text: str, job_text: str) -> MatchResult:
    """Analyze a CV against a job description and return an explainable score."""
    cv_skills = extract_skills(cv_text)
    job_skills = extract_skills(job_text)

    matched = sorted(set(cv_skills) & set(job_skills))
    missing = sorted(set(job_skills) - set(cv_skills))

    if job_skills:
        skill_ratio = len(matched) / len(job_skills)
    else:
        # Do not punish a description that contains no recognized catalog skills.
        skill_ratio = 0.5 if _normalize(job_text) else 0.0

    text_ratio = _text_similarity(cv_text, job_text)
    # Text gives broad contextual similarity; skills keep the score explainable.
    overall = round((text_ratio * 0.65 + skill_ratio * 0.35) * 100)

    recommendations: list[str] = []
    if missing:
        recommendations.append(
            "Show evidence for the most important missing skills: " + ", ".join(missing[:5]) + "."
        )
    if text_ratio < 0.35:
        recommendations.append(
            "Rewrite the summary and project bullets using the job description's exact terminology where truthful."
        )
    if len(cv_skills) < 5:
        recommendations.append(
            "Add a focused technical-skills section and connect each skill to a project or measurable result."
        )
    if overall >= 75:
        recommendations.append("Strong fit. Apply with a tailored opening paragraph and a role-specific project link.")
    elif overall >= 50:
        recommendations.append("Moderate fit. Tailor the CV before applying; do not send the generic version.")
    else:
        recommendations.append("Weak fit today. Close one or two critical gaps or prioritize a better-matched role.")

    return MatchResult(
        overall_score=max(0, min(100, overall)),
        text_similarity=round(text_ratio * 100),
        skill_score=round(skill_ratio * 100),
        matched_skills=matched,
        missing_skills=missing,
        cv_skills=cv_skills,
        job_skills=job_skills,
        recommendations=recommendations,
    )
