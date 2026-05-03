from dotenv import load_dotenv
import os
load_dotenv()

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
import tempfile, json

# --- CONFIG ---
chat = ChatOpenAI(
    model="meta-llama/llama-4-scout",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# --- PROMPT ---
prompt = PromptTemplate(
    input_variables=["context", "job_description"],
    template="""
You are a senior technical recruiter and ATS specialist with 15 years of experience across FAANG, startups, and consulting.
Evaluate how well the candidate's resume matches the given job description.

RESUME:
{context}

JOB DESCRIPTION:
{job_description}

EVALUATION RULES:
- Be critical, not polite
- Do not inflate scores
- Base every score strictly on what is present in the resume vs what the JD demands
- Never fabricate skills or experience not in the resume

Return ONLY valid JSON. Zero prose outside JSON.

{{
  "score": integer,
  "overall_match": integer,
  "keywords_match": {{
    "matched": ["keyword1", "keyword2"],
    "match_percentage": integer
  }},
  "missing_keywords": ["keyword1", "keyword2"],
  "reliability_score": integer,
  "ats_compatibility": integer,
  "format_analysis": {{
    "summary": "2-3 sentence assessment",
    "issues": ["issue1", "issue2"]
  }},
  "skill_gap_analysis": {{
    "present_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"],
    "gap_summary": "1-2 sentence summary"
  }},
  "improvement_suggestions": ["suggestion1", "suggestion2"],
  "industry_specific_feedback": "2-3 sentences"
}}
"""
)

# --- PDF EXTRACTION ---
def extract_text(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    loader = PyPDFLoader(tmp_path)
    documents = loader.load()
    return "\n\n".join(doc.page_content for doc in documents)

# --- EVALUATE ---
def evaluate(context, job_description):
    formatted_prompt = prompt.format(context=context, job_description=job_description)
    response = ""
    for chunk in chat.stream(formatted_prompt):
        response += chunk.content
    response = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(response)

# --- DISPLAY ---
def display(data):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall Score", f"{data['score']}/100")
    col2.metric("JD Match", f"{data['overall_match']}%")
    col3.metric("ATS Compatibility", f"{data['ats_compatibility']}/100")
    col4.metric("Reliability", f"{data['reliability_score']}/100")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Keywords Matched")
        st.success(", ".join(data["keywords_match"]["matched"]))
        st.write(f"Match Rate: **{data['keywords_match']['match_percentage']}%**")

    with col2:
        st.subheader("Missing Keywords")
        st.error(", ".join(data["missing_keywords"]))

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Format Analysis")
        st.write(data["format_analysis"]["summary"])
        for issue in data["format_analysis"]["issues"]:
            st.warning(issue)

    with col2:
        st.subheader("Skill Gap Analysis")
        st.write(data["skill_gap_analysis"]["gap_summary"])
        st.write("**Present:**", ", ".join(data["skill_gap_analysis"]["present_skills"]))
        st.error("**Missing:** " + ", ".join(data["skill_gap_analysis"]["missing_skills"]))

    st.divider()

    st.subheader("Improvement Suggestions")
    for i, s in enumerate(data["improvement_suggestions"], 1):
        st.write(f"{i}. {s}")

    st.divider()

    st.subheader("Industry Specific Feedback")
    st.info(data["industry_specific_feedback"])

# --- UI ---
st.set_page_config(page_title="Applyt — Resume Matcher", layout="wide")
st.title("Resume Matcher & Scorer")
st.caption("Upload your resume and paste the job description to see how well you match.")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
with col2:
    job_description = st.text_area("Paste Job Description", height=350, placeholder="Paste the full job description here...")

st.divider()

if st.button("Analyze Match", use_container_width=True):
    if not uploaded_file:
        st.warning("Please upload your resume.")
    elif not job_description.strip():
        st.warning("Please paste a job description.")
    else:
        with st.spinner("Analyzing your resume against the job description..."):
            try:
                context = extract_text(uploaded_file)
                data = evaluate(context, job_description)
                display(data)
            except json.JSONDecodeError:
                st.error("Model returned invalid JSON. Try again.")
            except Exception as e:
                st.error(f"Error: {e}")