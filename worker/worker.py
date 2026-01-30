import os
import requests
import re
from dotenv import load_dotenv
from cv_generator import generate_custom_cv
from letter_generator import generate_cover_letter
from pdf_exporter import export_markdown_to_pdf
from pdf_exporter_letter import export_letter_to_pdf


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv(dotenv_path="worker/.env")

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

CANDIDATE_NAME = os.getenv("CANDIDATE_NAME", "Candidat")

AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json",
}


# --------------------------------------------------
# Utility functions
# --------------------------------------------------



def strip_citations(text: str) -> str:
    text = re.sub(r"\[cite_start\]", "", text)
    text = re.sub(r"\[cite:[^\]]+\]", "", text)
    return text


def clean_cv_artifacts(text: str) -> str:
    return text.split("## AGENT INSTRUCTIONS")[0].strip()


def clean_job_title(title: str) -> str:
    """Remove (H/F), (F/H), etc. from job titles."""
    if not title:
        return ""
    return (
        title
        .replace("(H/F)", "")
        .replace("(F/H)", "")
        .replace ("H/F", "")
        .replace ("F/H", "")
        .replace ("/", " ")
        .strip()
    )

def remove_trailing_ai_sentence(cv_text: str) -> str:
    """
    Remove generic trailing AI sentence like:
    'CV adapté pour le poste de ...'
    """
    lines = cv_text.split("\n")
    cleaned = []
    for line in lines:
        l = line.lower().strip()
        if l.startswith("cv adapté pour") or l.startswith("cv adapte pour"):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).rstrip()


def extract_cv_title(markdown_text: str) -> str:
    for line in markdown_text.split("\n"):
        clean = line.strip()
        if clean:
            return clean
    return "Candidat"

# --------------------------------------------------
# Airtable helpers
# --------------------------------------------------

def fetch_waiting_jobs():
    """Fetch jobs with Status = 'waiting'."""
    params = {"filterByFormula": "{Status}='waiting'"}
    response = requests.get(AIRTABLE_URL, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json().get("records", [])


def update_job_fields(record_id: str, fields: dict):
    """Generic Airtable PATCH helper."""
    url = f"{AIRTABLE_URL}/{record_id}"
    payload = {"fields": fields}
    response = requests.patch(url, headers=HEADERS, json=payload)
    response.raise_for_status()


def strip_markdown_fences(text: str) -> str:
    lines = text.strip().splitlines()

    # Remove opening ``` or ```markdown
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]

    # Remove closing ```
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()

# --------------------------------------------------
# Main worker logic
# --------------------------------------------------

def main():
    jobs = fetch_waiting_jobs()

    if not jobs:
        print("No jobs with status = waiting.")
        return

    print(f"{len(jobs)} job(s) found.\n")

    # Load default CV once
    with open("worker/cv_default.md", "r", encoding="utf-8") as f:
        cv_default_text = f.read()

    for job in jobs:
        record_id = job["id"]
        fields = job.get("fields", {})

        title = fields.get("title", "")
        company = fields.get("company", "Non indiqué")
        contract_type = fields.get("contract_type", "")
        city = fields.get("City", "")
        department = fields.get("Department", "")
        source = fields.get("Source", "")
        url = fields.get("URL", "")

        print("---- JOB ----")
        print(f"Title        : {title}")
        print(f"Company      : {company}")
        print(f"Contract     : {contract_type}")
        print(f"City         : {city}")
        print(f"Department  : {department}")
        print(f"Source       : {source}")
        print(f"URL          : {url}")
        print("-------------")

        try:
            # Mark job as processing
            update_job_fields(record_id, {"Status": "processing"})
            print("→ Status set to 'processing'")

            clean_title = clean_job_title(title)

            # Build job context (for LLM only)
            job_context = f"""
                Job title: {clean_title}
                Company: {company}
                Contract type: {contract_type}
                City: {city}
                Department: {department}
                Source: {source}
                Job URL: {url}
            """

            # -----------------------------
            # Generate tailored CV
            # -----------------------------
            custom_cv = generate_custom_cv(cv_default_text, job_context)
            cv_generated_clean = strip_markdown_fences(custom_cv)

            # Retrieve cv title
            cv_title= extract_cv_title(cv_generated_clean)

            update_job_fields(record_id, {"cv_custom":  cv_generated_clean})
            print("→ Custom CV generated and saved")

            # Export CV PDF
            cv_pdf_path = f"exports/CV - {cv_title}.pdf"

            tmp_cv_path = cv_pdf_path.replace(".pdf", "_NEW.pdf")

            export_markdown_to_pdf(
                markdown_text= cv_generated_clean,
                output_path=tmp_cv_path
            )


            # Try to replace existing file
            try:
                if os.path.exists(cv_pdf_path):
                    os.replace(tmp_cv_path, cv_pdf_path)
                else:
                    os.rename(tmp_cv_path, cv_pdf_path)
            except PermissionError:
                raise RuntimeError(
                    f"Le fichier PDF est ouvert. "
                    f"Fermez-le puis relancez le worker : {cv_pdf_path}"
                )
            
            print(f"→ CV PDF exported: {cv_pdf_path}")

            # -----------------------------
            # Generate cover letter
            # -----------------------------
            cover_letter = generate_cover_letter(cv_generated_clean, job_context)

            update_job_fields(record_id, {"cover_letter": cover_letter})
            print("→ Cover letter generated and saved")

            # Export cover letter PDF
            letter_pdf_path = f"exports/Lettre - {cv_title}.pdf"

            if os.path.exists(letter_pdf_path):
                os.remove(letter_pdf_path)


            export_letter_to_pdf(
                cover_letter,
                letter_pdf_path
            )

            print(f"→ Cover letter PDF exported: {letter_pdf_path}")

            # Final status
            update_job_fields(record_id, {"Status": "done"})
            print("→ Status set to 'done'\n")

        except Exception as e:
            print(f"❌ Error while processing job {record_id}: {e}")
            # IMPORTANT: ensure this value exists in Airtable Status options
            update_job_fields(record_id, {"Status": "error"})


if __name__ == "__main__":
    main()
