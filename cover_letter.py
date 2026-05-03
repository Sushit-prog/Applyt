from dotenv import load_dotenv
import os
load_dotenv()

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
import tempfile

chat = ChatOpenAI(
    model="meta-llama/llama-4-scout",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
# --- PROMPT ---
prompt = PromptTemplate(
    input_variables=["context", "job_description"],
    template="""
You are an expert career coach and professional writer who has helped thousands of candidates land jobs at top companies.
Write a compelling, tailored cover letter based on the candidate's resume and the job description provided.

RESUME:
{context}

JOB DESCRIPTION:
{job_description}

-------------------------
COVER LETTER RULES:
-------------------------
- Length: 300-450 words strictly
- Tone: Professional but human, not robotic
- Do NOT start with "I am writing to apply for..."
- Open with a strong hook that shows genuine interest
- Paragraph 1: Hook + role excitement
- Paragraph 2: Match 2-3 key skills/experiences from resume to JD requirements
- Paragraph 3: What you bring that others won't — unique value
- Paragraph 4: Short, confident closing with a call to action
- Use the candidate's actual projects and skills from the resume
- Never fabricate experience not present in the resume
- Do not use generic filler phrases like "team player" or "hard worker"

FORMAT THE LETTER EXACTLY AS FOLLOWS:
[Full Name]
[City]
[Email Address]

[Date]

Hiring Team
[Company Name]

[Body — 4 paragraphs]

Sincerely,
[Full Name]

Extract name, city, and email directly from the resume. Do not fabricate any contact details.
Output only the cover letter. No explanations, no labels.
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

# --- UI ---
st.set_page_config(page_title="Applyt — Cover Letter Generator", layout="wide")
st.title("Cover Letter Generator")
st.caption("Upload your resume and paste the job description to get a tailored cover letter.")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

with col2:
    job_description = st.text_area(
        "Paste Job Description",
        height=350,
        placeholder="Paste the full job description here..."
    )

st.divider()

if st.button("Generate Cover Letter", use_container_width=True):
    if not uploaded_file:
        st.warning("Please upload your resume.")
    elif not job_description.strip():
        st.warning("Please paste a job description.")
    else:
        with st.spinner("Writing your cover letter..."):
            context = extract_text(uploaded_file)
            formatted_prompt = prompt.format(context=context, job_description=job_description)
            
            result = ""
            placeholder = st.empty()
            for chunk in chat.stream(formatted_prompt):
                result += chunk.content
                placeholder.markdown(result)