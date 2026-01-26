from cv_generator import generate_custom_cv
from pdf_exporter import export_markdown_to_pdf

def strip_markdown_fences(text: str) -> str:
    lines = text.strip().splitlines()

    # Remove opening ``` or ```markdown
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]

    # Remove closing ```
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()

# 1️⃣ Charger le CV par défaut
print("cv par defaut")
with open("./cv_default.md", "r", encoding="utf-8") as f:
    cv_default = f.read()

# 2️⃣ Contexte d’offre de test (contrôlé)
print("job context")
job_context = {
    "title": "Technicien chimie en industrie",
    "company": "Entreprise test",
    "contract": "CDI",
    "city": "Créteil",
    "source": "TEST"
}

# 3️⃣ Génération du CV personnalisé (MARKDOWN)
print('generation de cv')
cv_generated = generate_custom_cv(cv_default, job_context)

# (optionnel mais très utile pour debug)
print("\n===== CV GENERATED (MARKDOWN) =====\n")
print(cv_generated[:800])  # aperçu
print("\n==================================\n")

cv_generated_clean = strip_markdown_fences(cv_generated)

# 4️⃣ Export direct en PDF
print("export pdf")
output_pdf = "../exports/TEST_CV_PIPELINE.pdf"

export_markdown_to_pdf(
    cv_generated_clean,
    output_path=output_pdf
)

print(f"✅ PIPELINE OK → {output_pdf}")
