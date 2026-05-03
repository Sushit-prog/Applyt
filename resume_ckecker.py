import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
import tempfile, os, json

# --- CONFIG ---
chat = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    GROQ_API_KEY="API_KEY"
)

# --- PROMPT ---
prompt = PromptTemplate(
    input_variables=["context", "experience_level", "level_note"],
    template="""
You are a senior technical recruiter and career coach with 15 years of experience across FAANG, startups, and consulting.
You evaluate resumes for {experience_level}-level candidates with the mindset of a hiring manager reviewing 200 applications per week.

DETECTED EXPERIENCE LEVEL: {experience_level}
EVALUATION CONTEXT: {level_note}

RESUME CONTENT:
{context}

SCORING RUBRIC (100 points total):
1. Content Quality (0-20) - Relevance and clarity of experience/projects
2. Skills & Technical Depth (0-20) - Actual depth vs. keyword stuffing
3. Structure & Formatting (0-15) - ATS parse-friendly layout
4. Impact & Achievements (0-20) - Quantified results, action-verb sentences
5. ATS Optimization (0-15) - Keyword relevance, parsing-safe formatting
6. Projects & Practical Work (0-10) - Complexity, GitHub/live links add points

IMPORTANT RULES:
- Be critical, not polite
- Do not inflate scores
- overall_score must equal the exact sum of all category_scores
- Penalize vague or generic resumes heavily
- Keep suggestions actionable, not generic

Return ONLY valid JSON. Zero prose outside JSON.

{{
  "overall_score": integer,
  "experience_level": "fresher | mid | senior",
  "ats_score_label": "poor | fair | good | excellent",
  "category_scores": {{
    "content_quality": integer,
    "skills_depth": integer,
    "structure_formatting": integer,
    "impact_achievements": integer,
    "ats_optimization": integer,
    "projects": integer
  }},
  "strengths": ["point 1", "point 2", "point 3"],
  "weaknesses": ["point 1", "point 2", "point 3"],
  "detected_skills": ["skill 1", "skill 2"],
  "missing_skills": ["skill 1", "skill 2"],
  "next_roles": ["role 1", "role 2"],
  "improvement_suggestions": ["actionable fix 1", "actionable fix 2"]
}}
"""
)

# --- LEVEL DETECTION ---
def detect_level(text: str) -> str:
    t = text.lower()
    if any(s in t for s in ["staff", "principal", "director", "vp ", "8+ years", "10+ years"]):
        return "senior"
    if any(s in t for s in ["2 years", "3 years", "4 years", "senior", "lead"]):
        return "mid"
    return "fresher"

RUBRIC_WEIGHTS = {
    "fresher": "No work experience expected. Weight projects, skills, and academics heavily. Do NOT penalize for missing industry experience.",
    "mid": "1-4 years expected. Balance experience quality with skills and impact. Penalize vague role descriptions.",
    "senior": "5+ years expected. Weight leadership, system design, measurable impact, and strategic thinking heavily.",
}

# --- PDF EXTRACTION ---
def extract_text(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    loader = PyPDFLoader(tmp_path)
    documents = loader.load()
    return "\n\n".join(doc.page_content for doc in documents)

# --- EVALUATE ---
def evaluate_resume(context):
    level = detect_level(context)
    level_note = RUBRIC_WEIGHTS[level]
    formatted_prompt = prompt.format(context=context, experience_level=level, level_note=level_note)
    response = ""
    for chunk in chat.stream(formatted_prompt):
        response += chunk.content
    # strip markdown code fences if model wraps in ```json
    response = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(response)

# --- DISPLAY ---
def display_results(data):
    score = data["overall_score"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Score", f"{score}/100")
    col2.metric("Experience Level", data["experience_level"].capitalize())
    col3.metric("ATS Rating", data["ats_score_label"].capitalize())

    st.divider()

    st.subheader("Category Scores")
    cats = data["category_scores"]
    labels = {
        "content_quality": "Content Quality /20",
        "skills_depth": "Skills & Depth /20",
        "structure_formatting": "Structure /15",
        "impact_achievements": "Impact /20",
        "ats_optimization": "ATS Optimization /15",
        "projects": "Projects /10"
    }
    for key, label in labels.items():
        st.write(f"**{label}** — {cats[key]}")
        st.progress(cats[key] / int(label.split("/")[-1]))

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Strengths")
        for s in data["strengths"]:
            st.success(s)
    with col2:
        st.subheader("Weaknesses")
        for w in data["weaknesses"]:
            st.error(w)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Detected Skills")
        st.write(", ".join(data["detected_skills"]))
    with col2:
        st.subheader("Missing Skills")
        st.warning(", ".join(data["missing_skills"]))

    st.divider()

    st.subheader("Next Roles You Can Target")
    for role in data["next_roles"]:
        st.info(role)

    st.subheader("Improvement Suggestions")
    for i, tip in enumerate(data["improvement_suggestions"], 1):
        st.write(f"{i}. {tip}")

# --- UI ---
st.set_page_config(page_title="Applyt — Resume Checker", layout="wide")
st.title("Quick Resume Checker")
st.caption("Upload your resume and get a full evaluation in seconds.")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if uploaded_file:
    if st.button("Analyze Resume"):
        with st.spinner("Analyzing your resume..."):
            try:
                context = extract_text(uploaded_file)
                data = evaluate_resume(context)
                display_results(data)
            except json.JSONDecodeError:
                st.error("Model returned invalid JSON. Try again.")
            except Exception as e:
                st.error(f"Error: {e}")