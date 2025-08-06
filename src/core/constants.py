"""Project constants"""

from enum import Enum

class QuestionType(Enum):
    """Types of questions in RD Sharma"""
    ILLUSTRATION = "illustration"
    EXERCISE = "exercise"
    EXAMPLE = "example"
    PRACTICE = "practice"
    OBJECTIVE = "objective"
    SUBJECTIVE = "subjective"

class ExportFormat(Enum):
    """Supported export formats"""
    LATEX = "latex"
    MARKDOWN = "markdown"
    JSON = "json"
    PDF = "pdf"

# Chapter mappings for RD Sharma Class 12
CHAPTER_TOPICS = {
    30: {
        "name": "Probability",
        "topics": {
            "30.1": "Introduction",
            "30.2": "Recapitulation",
            "30.3": "Conditional Probability",
            "30.4": "Multiplication Theorem on Probability",
            "30.5": "Independent Events",
            "30.6": "Partition of a Sample Space",
            "30.7": "Theorem of Total Probability",
            "30.8": "Bayes' Theorem",
            "30.9": "Random Variables and its Probability Distributions",
        }
    },
    # Add more chapters as needed
}

# LaTeX math delimiters
LATEX_DELIMITERS = {
    "inline": ("$", "$"),
    "display": ("$$", "$$"),
    "equation": (r"\begin{equation}", r"\end{equation}"),
    "align": (r"\begin{align}", r"\end{align}"),
}

# Question patterns
QUESTION_PATTERNS = [
    r"^\d+\.",  # Numbered questions
    r"^Q\d+",   # Q1, Q2, etc.
    r"^Example \d+",  # Examples
    r"^Illustration \d+",  # Illustrations
    r"^Exercise",  # Exercise sections
    r"^Problem",  # Problem statements
]

# Mathematical symbols mapping
MATH_SYMBOLS = {
    "α": r"\alpha",
    "β": r"\beta",
    "γ": r"\gamma",
    "δ": r"\delta",
    "θ": r"\theta",
    "λ": r"\lambda",
    "μ": r"\mu",
    "σ": r"\sigma",
    "φ": r"\phi",
    "ω": r"\omega",
    "Σ": r"\sum",
    "∫": r"\int",
    "∞": r"\infty",
    "√": r"\sqrt",
    "≤": r"\leq",
    "≥": r"\geq",
    "≠": r"\neq",
    "≈": r"\approx",
    "∈": r"\in",
    "∉": r"\notin",
    "⊂": r"\subset",
    "⊃": r"\supset",
    "∪": r"\cup",
    "∩": r"\cap",
    "∀": r"\forall",
    "∃": r"\exists",
}