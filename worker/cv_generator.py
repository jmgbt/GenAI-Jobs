import os
from dotenv import load_dotenv
from openai import OpenAI

def generate_custom_cv(cv_default_text, job_context):
    """
    Generate a tailored CV based on a default CV and a job context.
    The default CV is the ONLY source of truth for personal information.
    """

    # Load env
    #load_dotenv(dotenv_path="worker/.env")
    load_dotenv(dotenv_path=".env")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set or not loaded.")

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a professional career advisor.

You are given:
1) A DEFAULT CV (this is the ONLY source of truth)
2) A JOB CONTEXT (job offer details)

STRICT RULES (must be followed):
- Do NOT invent or add any personal information
- Keep the full header block with phone, email, linkedin, age and availability
- Never repeat the candidate's name inside the CV body
- The candidate's name will appear only once, as the main header
- Add the job title after the candidate's name with a "-" inbetween
- If job title include "(H/F)" then REMOVE IT (super important from the indicated title
- Adapt the introduction paragraph in relation to the job description
- Do NOT add any location, city, mobility, or geographic preference
- Do NOT add lines such as "Localisation souhaitée", "Lieu", "Mobilité"
- Do NOT add new experiences, degrees, skills, or certifications
- You may reorder, prioritize, and slightly reformulate existing content only
- Keep the CV professional, concise, and factual
- Output ONLY the CV content, in clean Markdown
- Do NOT add comments, explanations, or metadata
- Do not forget the diploma along with specializatoin

JOB CONTEXT:
{job_context}

DEFAULT CV:
{cv_default_text}

OUTPUT:
Tailored CV in Markdown.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You generate professional CVs. "
                    "You strictly follow instructions and never add inferred or missing information."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()
