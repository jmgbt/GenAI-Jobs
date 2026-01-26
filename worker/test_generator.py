import os
from cv_generator import generate_custom_cv

def run_test():
    # 1. Load your default CV
    cv_path = "cv_default.md"
    
    if not os.path.exists(cv_path):
        print(f"❌ Error: {cv_path} not found.")
        return

    with open(cv_path, "r", encoding="utf-8") as f:
        cv_default_content = f.read()

    # 2. Define the Job Context (the France Travail block)
    job_context = {
        "title": "Technicien chimie en industrie",
        "company": "Entreprise test",
        "contract": "CDI",
        "city": "Créteil",
        "source": "TEST"
    }

    print("--- 🚀 RUNNING GENERATION TEST ---")
    
    cv_generated = generate_custom_cv(cv_default_content, job_context)

    # 4. Print with visual "End of Line" markers to see hidden spaces
    print("\n--- 📄 GENERATED OUTPUT BELOW ---")
    print(cv_generated)
    print("\n--- ✅ TEST COMPLETE ---")

if __name__ == "__main__":
    run_test()