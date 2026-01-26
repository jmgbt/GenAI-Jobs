from pdf_exporter import export_markdown_to_pdf

with open("./worker/cv_default.md", "r", encoding="utf-8") as f:
    markdown = f.read()

export_markdown_to_pdf(
    markdown_text=markdown,
    output_path="./exports/TEST_CV.pdf"
)

print("PDF généré : exports/TEST_CV.pdf")
