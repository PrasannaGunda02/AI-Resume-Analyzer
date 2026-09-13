import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI


# =========================
# Load environment variables
# =========================

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY is not set. "
        "Please add it to your .env file."
    )


# =========================
# OpenRouter Client
# =========================

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


# =========================
# Flask Application
# =========================

app = Flask(__name__)

CORS(app)


# =========================
# Resume Analyzer Prompt
# =========================

def resume_analyzer_prompt(text, role):

    return f"""
You are a professional ATS Resume Analyzer and HR Interview Evaluator.

Evaluate the following resume for the role of {role}.

Resume:
{text}

Provide output strictly in this format:

1. Resume Summary Quality (0-10)

2. Job Role Match Score (0-10)

3. Key Strengths Observed

4. Weak Areas and Points to Improve

5. Suggested Projects to Add

6. A Fully Improved Resume Version
Rewrite the resume professionally while preserving truthful information.
Do not invent education, experience, certifications, projects, or achievements.

7. Top 10 Interview Questions to Prepare for this role

Keep the analysis practical, specific to the target role,
and useful for improving the candidate's chances.
"""


# =========================
# Analyze Resume
# =========================

@app.route("/analyze", methods=["POST"])
def analyze_resume():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body is required."
            }), 400

        resume = data.get("resume", "").strip()
        role = data.get("role", "").strip()

        if not resume:
            return jsonify({
                "error": "Resume text is required."
            }), 400

        if not role:
            return jsonify({
                "error": "Job role is required."
            }), 400


        # =========================
        # Call OpenRouter
        # =========================

        response = client.chat.completions.create(

            model="openrouter/free",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional ATS Resume Analyzer "
                        "and HR Interview Evaluator."
                    )
                },
                {
                    "role": "user",
                    "content": resume_analyzer_prompt(
                        resume,
                        role
                    )
                }
            ],

            temperature=0.2
        )


        result = response.choices[0].message.content


        return jsonify({
            "result": result
        })


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================
# Run Application
# =========================

if __name__ == "__main__":

    app.run(
        port=8000,
        debug=True
    )