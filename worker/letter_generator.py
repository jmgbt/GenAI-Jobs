import os
from datetime import date
from dotenv import load_dotenv
from openai import OpenAI


def generate_cover_letter(custom_cv_text, job_context):
    """
    Generate a complete, professional and dynamic cover letter
    with a fixed location and the current date (French month).
    """

    # Load environment variables at call time (robust)
    load_dotenv(dotenv_path="worker/.env")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set or not loaded.")

    client = OpenAI(api_key=api_key)

    # Fixed metadata (product decision)
    location = "Saint-Maur-des-Fossés"

    # --- Force French date ---
    months_fr = {
        1: "janvier",
        2: "février",
        3: "mars",
        4: "avril",
        5: "mai",
        6: "juin",
        7: "juillet",
        8: "août",
        9: "septembre",
        10: "octobre",
        11: "novembre",
        12: "décembre",
    }

    today = date.today()
    today_str = f"{today.day} {months_fr[today.month]} {today.year}"
    # -------------------------

    prompt = f"""
You are a professional career advisor.

You are given:
1) A TAILORED CV (already adapted to the job)
2) A JOB CONTEXT

The cover letter MUST:
- Be written in French
- Be complete (header + body + closing)
- Start EXACTLY with this first line (no variation allowed):
  "{location}, le {today_str}"
- Then include:
  - a professional recipient block (generic if needed)
  - a clear subject line related to the job
  - the body of the cover letter
- Tone: professional and dynamic
- Avoid clichés and generic phrasing
- Stay factual and consistent with the CV
- Do NOT invent experiences, skills, dates, or locations
- Length: approximately one page maximum

JOB CONTEXT:
{job_context}

TAILORED CV:
{custom_cv_text}

OUTPUT:
A complete French cover letter starting exactly with:
"{location}, le {today_str}"
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You write professional, factual and tailored cover letters."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()
