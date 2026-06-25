# 🚀 Pitch Deck Analyzer MVP

An automated, hallucination-resistant venture capital screening tool built for a 48-hour technical challenge.

## 🧠 Architecture Overview

This MVP evaluates startup pitch decks against a strict VC rubric (Investor Communication, Narrative & Storytelling, Problem-Solution Fit). To build a deterministic, production-ready pipeline in 48 hours, I focused on three main layers:

1. **Hardware-Accelerated Inference (Groq + Llama 3.3):** Instead of using standard APIs, this engine runs on Groq's LPUs using the `llama-3.3-70b-versatile` model. This turns a traditionally slow batch process into an instantaneous, sub-second feedback loop.
2. **Strict Type Safety & Hallucination Boundaries (Pydantic):** To eliminate structural hallucinations, the analytical engine is constrained by a Pydantic JSON schema. Furthermore, all rubric scores are explicitly bound mathematically (1 ≤ score ≤ 5) using Pydantic `Field` objects, ensuring the LLM can never output an out-of-bounds score.
3. **Optimized UI State (Streamlit):** The frontend leverages Streamlit's native session state to preserve parsed PDF text and JSON payloads across re-renders. This ensures the dynamic UI remains fast and interactive without triggering redundant downstream API calls.

## ⚙️ Quickstart

To make the review process as frictionless as possible, **a live API key is hardcoded into the backend**. You do not need to hunt for your own credentials to test the MVP.

```bash
# 1. Clone the repository
git clone https://github.com/TheOnly-Bob/pitch_deck_analyzer.git
cd pitch_deck_analyzer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the application
python -m streamlit run app.py
```

## 📂 Features
- **PDF Ingestion:** Uses `pypdf` to programmatically extract text layers from uploaded pitch decks.
- **Few-Shot Calibration:** The system prompt is anchored with real-world historical benchmarks (e.g., Airbnb's 2008 deck) to calibrate the AI's grading strictness.
- **Venture Risks Extraction:** Automatically isolates core investment risks into a standalone structured list for rapid partner review.

---
*Built with Python, Streamlit, Groq, and Pydantic.*
