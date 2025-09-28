from flask import Flask, jsonify, request, render_template
import json
import os

app = Flask(__name__)

# Load dataset
with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

# Short notes per topic
NOTES = {
    "Vectors": [
        "Vectors have both magnitude and direction.",
        "They can be added using head-to-tail or components.",
        "Examples: velocity, acceleration, force."
    ],
    "Projectile Motion": [
        "Horizontal and vertical motions are independent.",
        "Range R = (v^2 * sin(2θ)) / g on level ground.",
        "Time of flight T = (2v * sinθ) / g."
    ],
    "Kinematics": [
        "Displacement vs distance: displacement is vector.",
        "Equations: v = u + at, s = ut + ½at², v² = u² + 2as.",
        "Acceleration is change of velocity per unit time."
    ]
}

# Progress file
PROGRESS_FILE = "progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)


# ---------- ROUTES ----------



@app.route("/questions")
def get_questions():
    return jsonify(QUESTIONS)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    student = data.get("student", "guest")
    answers = data.get("answers", [])
    total = len(answers)
    correct = 0
    feedback = {}

    for ans in answers:
        qid = ans["question_id"]
        choice = ans["choice"]
        q = next((q for q in QUESTIONS if q["id"] == qid), None)
        if q:
            is_correct = (choice == q["answer"])
            if is_correct:
                correct += 1
            topic = q["topic"]
            if topic not in feedback:
                feedback[topic] = {"correct": 0, "total": 0}
            feedback[topic]["total"] += 1
            if is_correct:
                feedback[topic]["correct"] += 1

    accuracy = (correct / total * 100) if total > 0 else 0

    progress = load_progress()
    if student not in progress:
        progress[student] = {}

    recommendations = {}
    for topic, stats in feedback.items():
        score = stats["correct"] / stats["total"] * 100
        old_score = progress[student].get(topic, 50)
        new_score = round(0.4 * old_score + 0.6 * score, 2)
        progress[student][topic] = new_score

        if new_score < 50:
            rec = [
                "Start with concept map",
                "Read the short notes",
                "Solve 3 practice problems",
                "Take a mini-test"
            ]
        elif new_score < 80:
            rec = [
                "Review key formulas",
                "Do 5 mixed practice problems"
            ]
        else:
            rec = ["Great job! Move to the next topic."]

        recommendations[topic] = {
            "score": score,
            "updated_mastery": new_score,
            "recommendation": rec
        }

    save_progress(progress)

    return jsonify({
        "student": student,
        "total_questions": total,
        "correct": correct,
        "accuracy": round(accuracy, 2),
        "recommendations": recommendations
    })

@app.route("/progress/<student>", methods=["GET"])
def get_progress(student):
    progress = load_progress()
    return jsonify(progress.get(student, {}))

@app.route("/notes", methods=["GET"])
def get_notes():
    topic = request.args.get("topic")
    notes = NOTES.get(topic, ["No notes found for this topic."])
    return jsonify({"topic": topic, "notes": notes})


if __name__ == "__main__":
    app.run(debug=True, port=5000)

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def signup():
    return render_template("signup.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/results")
def results():
    return render_template("results.html")

@app.route("/notes")
def notes():
    return render_template("notes.html")

if __name__ == "__main__":
    app.run(debug=True)
@app.route("/")
def home():
    return render_template("index.html")

