"""
Study Resource Recommendation engine.

This module keeps the original project logic from rs.py:
- Pandas DataFrame for the resource dataset
- One-hot encoding with pandas.get_dummies
- Cosine similarity from scikit-learn
- Top 3 ranked recommendations

Fixes applied:
- Subject is now part of the feature vector (the original code collected it
  but did not use it, which caused mixed-subject results)
- Matching is case-insensitive
- Low-similarity rows are filtered out so weak matches are not shown
"""

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------
# 1. Create the study resource dataset
#    (same resources as the original rs.py)
# ---------------------------------------

data = {
    "Resource": [
        "Python Basics Tutorial",
        "Python Practice Problems",
        "Java Programming Course",
        "Java DSA Tutorial",
        "Data Structures Video",
        "DBMS Complete Notes",
        "SQL Practice Questions",
        "Computer Networks Notes",
        "Operating Systems Video",
        "Machine Learning Basics",
        "Machine Learning Practice",
        "HTML CSS Tutorial",
        "Web Development Course",
        "Cybersecurity Fundamentals",
    ],
    "Subject": [
        "Python",
        "Python",
        "Java",
        "Java",
        "DSA",
        "DBMS",
        "DBMS",
        "Computer Networks",
        "Operating Systems",
        "Machine Learning",
        "Machine Learning",
        "Web Development",
        "Web Development",
        "Cybersecurity",
    ],
    "Topic": [
        "Programming",
        "Programming",
        "Programming",
        "Data Structures",
        "Data Structures",
        "Database",
        "SQL",
        "Networking",
        "Operating System",
        "Machine Learning",
        "Machine Learning",
        "Web Development",
        "Web Development",
        "Security",
    ],
    "Level": [
        "Beginner",
        "Beginner",
        "Beginner",
        "Intermediate",
        "Intermediate",
        "Beginner",
        "Intermediate",
        "Beginner",
        "Beginner",
        "Beginner",
        "Intermediate",
        "Beginner",
        "Intermediate",
        "Beginner",
    ],
    "Type": [
        "Video",
        "Practice",
        "Video",
        "Video",
        "Video",
        "Notes",
        "Practice",
        "Notes",
        "Video",
        "Video",
        "Practice",
        "Video",
        "Video",
        "Video",
    ],
    # Original project had no URLs. Do not invent links.
    "URL": [""] * 14,
}

df = pd.DataFrame(data)

VALID_SUBJECTS = [
    "Python",
    "Java",
    "DSA",
    "DBMS",
    "Computer Networks",
    "Operating Systems",
    "Machine Learning",
    "Web Development",
    "Cybersecurity",
]
VALID_LEVELS = ["Beginner", "Intermediate"]
VALID_TYPES = ["Video", "Notes", "Practice"]

# Weak matches below this score are treated as "not suitable".
MIN_SIMILARITY = 0.25


def get_topics():
    """Return unique topics from the dataset for the form dropdown."""
    return sorted(df["Topic"].dropna().unique().tolist())


def _canonical(value, allowed):
    """Map user text to a known category, ignoring extra spaces and case."""
    if value is None:
        return ""
    cleaned = " ".join(str(value).split())
    lookup = {item.lower(): item for item in allowed}
    return lookup.get(cleaned.lower(), cleaned)


def recommend(subject, topic, level, resource_type, top_n=3):
    """
    Rank resources using one-hot encoding + cosine similarity.

    Returns a DataFrame with columns:
    Resource, Subject, Topic, Level, Type, URL, Similarity
    """
    subject = _canonical(subject, VALID_SUBJECTS)
    level = _canonical(level, VALID_LEVELS)
    resource_type = _canonical(resource_type, VALID_TYPES)
    topic = _canonical(topic, get_topics())

    if subject not in VALID_SUBJECTS:
        return df.iloc[0:0].copy()
    if level not in VALID_LEVELS:
        return df.iloc[0:0].copy()
    if resource_type not in VALID_TYPES:
        return df.iloc[0:0].copy()
    if not topic:
        return df.iloc[0:0].copy()

    # Limit to the chosen subject first so Java resources are not
    # recommended for a Python student just because the topic matches.
    candidates = df[df["Subject"] == subject].copy()
    if candidates.empty:
        return candidates

    user = pd.DataFrame(
        {
            "Subject": [subject],
            "Topic": [topic],
            "Level": [level],
            "Type": [resource_type],
        }
    )

    # If the typed topic is unknown, drop Topic from encoding so a unique
    # dummy column does not unfairly lower every score.
    feature_cols = ["Subject", "Level", "Type"]
    if topic in set(candidates["Topic"]):
        feature_cols = ["Subject", "Topic", "Level", "Type"]

    combined = pd.concat(
        [candidates[feature_cols], user[feature_cols]],
        ignore_index=True,
    )

    encoded = pd.get_dummies(combined)
    resource_features = encoded.iloc[:-1]
    user_features = encoded.iloc[-1:]

    similarity = cosine_similarity(user_features, resource_features)
    candidates["Similarity"] = similarity[0]

    ranked = candidates.sort_values(by="Similarity", ascending=False)
    ranked = ranked[ranked["Similarity"] >= MIN_SIMILARITY]
    return ranked.head(top_n).reset_index(drop=True)
