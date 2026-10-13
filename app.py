"""
Flask website for the Study Resource Recommendation System.

How the pages connect to Python:
1. The browser shows HTML forms (templates/).
2. The student submits the form with POST to /results.
3. Flask reads the form values and calls recommend() in recommender.py.
4. Flask sends the ranked resources back into results.html.
"""

from flask import Flask, flash, redirect, render_template, request, url_for

from recommender import (
    VALID_LEVELS,
    VALID_SUBJECTS,
    VALID_TYPES,
    get_topics,
    recommend,
)

app = Flask(__name__)
app.secret_key = "study-resource-recommendation-system"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/recommend")
def recommend_form():
    return render_template(
        "recommend.html",
        subjects=VALID_SUBJECTS,
        topics=get_topics(),
        levels=VALID_LEVELS,
        types=VALID_TYPES,
        form_data={},
    )


@app.route("/results", methods=["POST"])
def results():
    subject = request.form.get("subject", "").strip()
    topic_choice = request.form.get("topic", "").strip()
    custom_topic = request.form.get("custom_topic", "").strip()
    level = request.form.get("level", "").strip()
    resource_type = request.form.get("resource_type", "").strip()

    topic = custom_topic if topic_choice == "Other" else topic_choice

    errors = []
    if subject not in VALID_SUBJECTS:
        errors.append("Please choose a valid subject.")
    if not topic:
        errors.append("Please choose a topic or enter your own topic.")
    if level not in VALID_LEVELS:
        errors.append("Please choose Beginner or Intermediate.")
    if resource_type not in VALID_TYPES:
        errors.append("Please choose Video, Notes, or Practice.")

    form_data = {
        "subject": subject,
        "topic": topic_choice,
        "custom_topic": custom_topic,
        "level": level,
        "resource_type": resource_type,
    }

    if errors:
        for message in errors:
            flash(message, "error")
        return render_template(
            "recommend.html",
            subjects=VALID_SUBJECTS,
            topics=get_topics(),
            levels=VALID_LEVELS,
            types=VALID_TYPES,
            form_data=form_data,
        ), 400

    recommendations = recommend(subject, topic, level, resource_type)
    cards = []
    for _, row in recommendations.iterrows():
        url = str(row.get("URL", "") or "").strip()
        cards.append(
            {
                "name": row["Resource"],
                "subject": row["Subject"],
                "topic": row["Topic"],
                "level": row["Level"],
                "type": row["Type"],
                "match": round(float(row["Similarity"]) * 100, 2),
                "url": url,
            }
        )

    return render_template(
        "results.html",
        cards=cards,
        query={
            "subject": subject,
            "topic": topic,
            "level": level,
            "resource_type": resource_type,
        },
    )


@app.route("/results")
def results_get():
    return redirect(url_for("recommend_form"))


if __name__ == "__main__":
    app.run(debug=True)
