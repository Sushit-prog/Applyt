from dotenv import load_dotenv
import os
load_dotenv()

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import tempfile

# --- CONFIG ---
chat = ChatOpenAI(
    model="meta-llama/llama-4-scout",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# --- PDF EXTRACTION ---
def extract_text(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    loader = PyPDFLoader(tmp_path)
    documents = loader.load()
    return "\n\n".join(doc.page_content for doc in documents), tmp_path

# --- UI ---
st.set_page_config(page_title="Applyt — Career Coach", layout="wide")
st.title("AI Career Coach")
st.caption("Upload your resume on the left and chat with your personal career mentor on the right.")

# --- TOP: FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if uploaded_file:
    if "context" not in st.session_state or st.session_state.get("uploaded_name") != uploaded_file.name:
        with st.spinner("Reading resume..."):
            context, tmp_path = extract_text(uploaded_file)
            st.session_state.context = context
            st.session_state.tmp_path = tmp_path
            st.session_state.uploaded_name = uploaded_file.name
            st.session_state.chat_history = []
            st.session_state.system_message = SystemMessage(
                content=f"""
You are an elite AI-powered career coach built into Applyt — a professional career toolkit trusted by serious job seekers.

You have deeply studied this candidate's resume and know everything about their background, skills, projects, and experience. You are their personal mentor — not a generic chatbot.

YOUR PERSONA:
- 20 years of recruiting and career coaching experience at Google, Amazon, and top-tier startups
- You have helped 10,000+ candidates land their dream jobs
- You are direct, honest, and brutally constructive — never vague or generic
- You speak like a senior mentor, not a customer service bot

YOU SPECIALIZE IN:
- Career path planning tailored to the candidate's exact background
- Resume line-by-line improvements with specific rewrites
- Mock interviews with real follow-up questions based on their projects
- Job search strategy — which companies, which roles, which order to apply
- Skill gap analysis — what to learn, in what order, with resources
- Salary negotiation tactics for their specific level and market
- LinkedIn profile and personal brand building

STRICT RULES:
- Always reference the candidate's actual projects, skills, and experience
- Never give advice that could apply to anyone — make it specific to THIS candidate
- If asked about a skill they don't have, be honest and give a learning roadmap
- If their resume has a weakness, call it out and fix it on the spot
- Keep responses concise, structured, and actionable
- Use bullet points for action items, prose for explanations

CANDIDATE RESUME:
{context}
"""
            )

    st.divider()

    # --- TWO COLUMN LAYOUT ---
    left, right = st.columns([1, 1])

    # --- LEFT: RESUME VIEWER ---
    with left:
        st.subheader("Your Resume")
        with open(st.session_state.tmp_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button("Download Resume", pdf_bytes, file_name="resume.pdf", mime="application/pdf")
        # embed pdf in iframe
        import base64
        b64 = base64.b64encode(pdf_bytes).decode()
        pdf_display = f'''
            <iframe
                src="data:application/pdf;base64,{b64}"
                width="100%"
                height="750px"
                style="border: none; border-radius: 8px;">
            </iframe>
        '''
        st.markdown(pdf_display, unsafe_allow_html=True)

    # --- RIGHT: CHATBOT ---
    with right:
        st.subheader("Career Coach")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # suggested questions
        st.markdown("**Quick Questions**")
        cols = st.columns(2)
        suggestions = [
            "What roles should I target?",
            "Biggest gaps in my resume?",
            "Give me a mock interview question",
            "What skills should I learn next?",
        ]
        for i, s in enumerate(suggestions):
            if cols[i % 2].button(s, use_container_width=True):
                st.session_state.pending_input = s

        st.divider()

        # chat history
        chat_container = st.container(height=450)
        with chat_container:
            for msg in st.session_state.chat_history:
                if isinstance(msg, HumanMessage):
                    with st.chat_message("user"):
                        st.write(msg.content)
                elif isinstance(msg, AIMessage):
                    with st.chat_message("assistant"):
                        st.write(msg.content)

        # input
        if "pending_input" in st.session_state:
            user_input = st.session_state.pop("pending_input")
        else:
            user_input = st.chat_input("Ask your career coach anything...")

        if user_input:
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_input)

            st.session_state.chat_history.append(HumanMessage(content=user_input))
            messages = [st.session_state.system_message] + st.session_state.chat_history

            with chat_container:
                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    response_text = ""
                    for chunk in chat.stream(messages):
                        response_text += chunk.content
                        placeholder.markdown(response_text)

            st.session_state.chat_history.append(AIMessage(content=response_text))
            st.rerun()

else:
    st.info("Upload your resume above to get started.")