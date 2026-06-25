import streamlit as st
import json
from groq_engine import get_client, evaluate_deck
from pydantic import ValidationError
from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    return "".join(page.extract_text() or "" for page in reader.pages)


st.set_page_config(page_title="VC Pitch Deck Analyzer", layout="wide")

st.title("Pitch Deck Analyzer")
st.markdown("Automated VC screening using Llama-3 (via Groq) with strict JSON schema enforcement.")

if "last_result" not in st.session_state:
    st.session_state.last_result = None

st.markdown("### Input Pitch Deck")
uploaded_file = st.file_uploader("Upload Pitch Deck (PDF)", type=["pdf"])
deck_text = st.text_area("Or Paste Pitch Deck Text Here", height=150)

if st.button("Evaluate"):
    final_text = extract_text_from_pdf(uploaded_file) if uploaded_file else deck_text.strip()

    if not final_text:
        st.warning("Please upload a PDF or paste some pitch deck text.")
    else:
        with st.spinner("Evaluating deck against VC rubric..."):
            try:
                client = get_client(st.secrets["GROQ_API_KEY"])
                st.session_state.last_result = evaluate_deck(client, final_text)
            except json.JSONDecodeError:
                st.error("The model returned output that didn't match the expected format. Try again.")
            except Exception as e:
                st.error(f"Evaluation failed: {e}")

if st.session_state.last_result:
    result = st.session_state.last_result
    st.markdown("---")
    
    st.subheader(f"Verdict: {result.verdict.value}")
    st.write(result.verdict_rationale)
    st.markdown(f"**Data Completeness:** {result.data_completeness.value}")
    
    st.markdown("### Rubric Scores")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Communication & Clarity", f"{result.investor_communication_and_clarity.score}/5")
        with st.expander("Rationale"):
            st.write(result.investor_communication_and_clarity.rationale)
            
    with col2:
        st.metric("Narrative & Storytelling", f"{result.narrative_and_storytelling.score}/5")
        with st.expander("Rationale"):
            st.write(result.narrative_and_storytelling.rationale)
            
    with col3:
        st.metric("Problem-Solution Fit", f"{result.problem_solution_fit.score}/5")
        with st.expander("Rationale"):
            st.write(result.problem_solution_fit.rationale)
    
    st.markdown("---")        
    col_str, col_weak, col_risk = st.columns(3)
    
    with col_str:
        st.markdown("#### Strengths")
        for s in result.strengths:
            st.markdown(f"- {s}")
            
    with col_weak:
        st.markdown("#### Weaknesses")
        for w in result.weaknesses:
            st.markdown(f"- {w}")
            
    with col_risk:
        st.markdown("#### Venture Risks")
        for r in result.investor_insights_and_risks:
            st.markdown(f"- {r}")
