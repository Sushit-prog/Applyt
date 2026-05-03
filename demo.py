from dotenv import load_dotenv
import os
load_dotenv()

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import tempfile, json, base64

# ─────────────────────────────────────────────
#  GLOBAL STYLES
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Applyt — AI Career Toolkit",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    /* Brand palette — deep navy base, electric lime accent */
    --bg:         #0A0F1A;
    --surface:    #0E1525;
    --card:       #131E30;
    --card-hover: #162035;
    --border:     rgba(255,255,255,0.07);
    --border-md:  rgba(255,255,255,0.11);
    --lime:       #C8F135;
    --lime-dim:   #9BBD1C;
    --lime-glow:  rgba(200,241,53,0.18);
    --lime-soft:  rgba(200,241,53,0.08);
    --red:        #FF4E6A;
    --red-soft:   rgba(255,78,106,0.1);
    --amber:      #FFB547;
    --amber-soft: rgba(255,181,71,0.1);
    --text:       #EDF2FF;
    --text-2:     #8A9BB5;
    --text-3:     #4E637A;
    --font-head:  'Space Grotesk', sans-serif;
    --font-body:  'Plus Jakarta Sans', sans-serif;
    --radius:     14px;
    --radius-sm:  9px;
    --shadow:     0 4px 24px rgba(0,0,0,0.35);
    --shadow-lg:  0 8px 48px rgba(0,0,0,0.5);
}

/* ═══════════════════════════════
   BASE
═══════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main .block-container {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}

/* Animated mesh background on main area */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 10% -10%, rgba(200,241,53,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 100%, rgba(13,27,42,0.8) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stHeader"] {
    background: transparent !important;
    border-bottom: none !important;
}

.main .block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1280px !important;
    position: relative;
    z-index: 1;
}

h1, h2, h3, h4 { font-family: var(--font-head) !important; letter-spacing: -0.02em; }

/* ═══════════════════════════════
   SIDEBAR
═══════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}
[data-testid="stSidebar"] * {
    font-family: var(--font-body) !important;
}

/* Sidebar logo zone */
.sb-logo-wrap {
    padding: 22px 20px 18px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 8px;
}

/* Nav items */
.stButton > button {
    width: 100%;
    background: transparent !important;
    color: var(--text-2) !important;
    border: 1px solid transparent !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-body) !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 11px 14px !important;
    transition: all 0.18s ease !important;
    letter-spacing: 0 !important;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.04) !important;
    color: var(--text) !important;
    border-color: var(--border-md) !important;
}

/* Active nav — lime left bar + lime text */
div[data-testid="stSidebar"] .stButton > button:focus,
div[data-testid="stSidebar"] .element-container:has(button[kind="secondary"]:focus) button {
    background: var(--lime-soft) !important;
    color: var(--lime) !important;
    border-color: rgba(200,241,53,0.25) !important;
}

.sidebar-section-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-3);
    padding: 0 6px;
    margin: 20px 0 6px;
    display: block;
}

.sidebar-footer {
    font-size: 11px;
    color: var(--text-3);
    text-align: center;
    padding: 12px 8px;
    border-top: 1px solid var(--border);
    margin-top: 12px;
}

/* ═══════════════════════════════
   HOME HERO
═══════════════════════════════ */
.hero-wrap {
    text-align: center;
    padding: 70px 20px 50px;
    position: relative;
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: var(--lime-soft);
    border: 1px solid rgba(200,241,53,0.22);
    border-radius: 100px;
    padding: 5px 14px 5px 10px;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.09em;
    color: var(--lime);
    text-transform: uppercase;
    margin-bottom: 28px;
}
.hero-eyebrow .dot {
    width: 6px; height: 6px;
    background: var(--lime);
    border-radius: 50%;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.7); }
}

.hero-title {
    font-family: var(--font-head) !important;
    font-size: clamp(2.6rem, 5.5vw, 4rem);
    font-weight: 700;
    line-height: 1.12;
    letter-spacing: -0.03em;
    color: var(--text);
    margin: 0 0 10px;
}
.hero-title .accent {
    background: linear-gradient(135deg, #C8F135 0%, #E8FF70 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-sub {
    font-size: 16px;
    color: var(--text-2);
    max-width: 520px;
    margin: 14px auto 44px;
    line-height: 1.75;
    font-weight: 400;
}

/* Stats row */
.stats-row {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin: 48px auto 0;
    padding: 28px 40px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    max-width: 640px;
}
.stat-item { text-align: center; }
.stat-val {
    font-family: var(--font-head);
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--lime);
    display: block;
    line-height: 1;
}
.stat-lbl {
    font-size: 11px;
    color: var(--text-3);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 5px;
    display: block;
}

/* Feature grid */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    max-width: 1100px;
    margin: 0 auto;
}

.fcard {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px 22px;
    transition: all 0.22s ease;
    cursor: default;
    position: relative;
    overflow: hidden;
}
.fcard::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--lime), transparent);
    opacity: 0;
    transition: opacity 0.22s;
}
.fcard:hover {
    background: var(--card-hover);
    border-color: var(--border-md);
    transform: translateY(-4px);
    box-shadow: var(--shadow);
}
.fcard:hover::before { opacity: 1; }

.fcard-icon {
    font-size: 28px;
    margin-bottom: 14px;
    display: block;
}
.fcard-num {
    font-family: var(--font-head);
    font-size: 11px;
    font-weight: 700;
    color: var(--lime);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.fcard-title {
    font-family: var(--font-head);
    font-size: 15px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 8px;
    letter-spacing: -0.01em;
}
.fcard-desc {
    font-size: 13px;
    color: var(--text-2);
    line-height: 1.65;
}

/* ═══════════════════════════════
   PAGE HEADERS
═══════════════════════════════ */
.page-header {
    padding: 32px 0 24px;
    margin-bottom: 28px;
    position: relative;
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0;
    width: 60px; height: 2px;
    background: var(--lime);
    border-radius: 2px;
}
.page-title {
    font-family: var(--font-head) !important;
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 6px;
    letter-spacing: -0.025em;
}
.page-sub {
    font-size: 14px;
    color: var(--text-2);
    margin: 0;
}

/* ═══════════════════════════════
   SECTION CARDS
═══════════════════════════════ */
.section-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px 26px;
    margin-bottom: 16px;
    transition: border-color 0.2s;
}
.section-card:hover { border-color: var(--border-md); }
.section-card h4 {
    font-family: var(--font-head) !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    color: var(--text-3) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    margin: 0 0 16px !important;
    display: flex;
    align-items: center;
    gap: 7px;
}

/* ═══════════════════════════════
   TAG PILLS
═══════════════════════════════ */
.tag-row { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 2px; }
.tag {
    display: inline-flex;
    align-items: center;
    background: var(--lime-soft);
    border: 1px solid rgba(200,241,53,0.18);
    color: var(--lime);
    padding: 3px 11px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.01em;
    font-family: var(--font-body);
}
.tag.red {
    background: var(--red-soft);
    border-color: rgba(255,78,106,0.2);
    color: var(--red);
}
.tag.green {
    background: var(--lime-soft);
    border-color: rgba(200,241,53,0.2);
    color: var(--lime);
}
.tag.gold {
    background: var(--amber-soft);
    border-color: rgba(255,181,71,0.2);
    color: var(--amber);
}

/* ═══════════════════════════════
   METRICS
═══════════════════════════════ */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 20px 22px !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--lime), transparent);
}
[data-testid="stMetricLabel"] p {
    color: var(--text-3) !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-family: var(--font-body) !important;
}
[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-family: var(--font-head) !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

/* ═══════════════════════════════
   PROGRESS BAR
═══════════════════════════════ */
.stProgress > div > div {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 100px !important;
    height: 6px !important;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--lime-dim), var(--lime)) !important;
    border-radius: 100px !important;
}

/* ═══════════════════════════════
   INPUTS
═══════════════════════════════ */
.stTextArea textarea,
.stTextInput input {
    background: var(--card) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextArea textarea::placeholder,
.stTextInput input::placeholder {
    color: var(--text-3) !important;
}
.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: var(--lime) !important;
    box-shadow: 0 0 0 3px rgba(200,241,53,0.1) !important;
    outline: none !important;
}

/* ═══════════════════════════════
   FILE UPLOADER
═══════════════════════════════ */
[data-testid="stFileUploader"] {
    background: var(--card) !important;
    border: 1.5px dashed rgba(200,241,53,0.2) !important;
    border-radius: var(--radius) !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(200,241,53,0.4) !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
}

/* ═══════════════════════════════
   BUTTONS — ALL
═══════════════════════════════ */

/* Primary CTA — lime on dark */
.stButton > button {
    background: var(--lime) !important;
    color: #0A0F1A !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-body) !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    padding: 11px 22px !important;
    letter-spacing: 0.01em !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 2px 12px rgba(200,241,53,0.25) !important;
}
.stButton > button:hover {
    background: #D9FF50 !important;
    box-shadow: 0 4px 20px rgba(200,241,53,0.4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Download button — ghost style */
[data-testid="stDownloadButton"] button {
    background: transparent !important;
    color: var(--lime) !important;
    border: 1.5px solid rgba(200,241,53,0.35) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px 20px !important;
    box-shadow: none !important;
    transition: all 0.18s ease !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: var(--lime-soft) !important;
    border-color: var(--lime) !important;
    transform: translateY(-1px) !important;
    box-shadow: none !important;
}

/* Sidebar buttons get ghost treatment */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--text-2) !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.04) !important;
    color: var(--text) !important;
    border-color: var(--border-md) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ═══════════════════════════════
   DIVIDER
═══════════════════════════════ */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 24px 0 !important;
}

/* ═══════════════════════════════
   COVER LETTER BOX
═══════════════════════════════ */
.cl-box {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 40px 44px;
    font-family: var(--font-body);
    font-size: 15px;
    line-height: 1.9;
    color: var(--text);
    white-space: pre-wrap;
    position: relative;
}
.cl-box::before {
    content: '"';
    position: absolute;
    top: 20px; left: 28px;
    font-size: 60px;
    color: var(--lime);
    opacity: 0.15;
    font-family: Georgia, serif;
    line-height: 1;
}

/* ═══════════════════════════════
   CHAT
═══════════════════════════════ */
[data-testid="stChatMessage"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    margin-bottom: 10px !important;
    padding: 14px 18px !important;
}
[data-testid="stChatInput"] {
    border-top: 1px solid var(--border) !important;
    background: var(--surface) !important;
    padding: 12px !important;
    border-radius: var(--radius-sm) !important;
}
[data-testid="stChatInput"] textarea {
    background: var(--card) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}

/* ═══════════════════════════════
   ALERTS
═══════════════════════════════ */
.stAlert {
    background: var(--card) !important;
    border-radius: var(--radius-sm) !important;
    border-left-width: 3px !important;
    font-family: var(--font-body) !important;
}
[data-testid="stAlertContentInfo"] { border-left-color: var(--lime) !important; }
[data-testid="stAlertContentSuccess"] { border-left-color: var(--lime) !important; }
[data-testid="stAlertContentWarning"] { border-left-color: var(--amber) !important; }
[data-testid="stAlertContentError"] { border-left-color: var(--red) !important; }

/* ═══════════════════════════════
   SPINNER
═══════════════════════════════ */
.stSpinner svg { color: var(--lime) !important; }
div[data-testid="stSpinner"] > div {
    border-top-color: var(--lime) !important;
}

/* ═══════════════════════════════
   SUGGESTION BUTTONS (coach)
═══════════════════════════════ */
.sug-btn > button {
    background: var(--card) !important;
    border: 1px solid var(--border-md) !important;
    color: var(--text-2) !important;
    border-radius: 100px !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    box-shadow: none !important;
    letter-spacing: 0 !important;
}
.sug-btn > button:hover {
    background: var(--lime-soft) !important;
    border-color: rgba(200,241,53,0.3) !important;
    color: var(--lime) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ═══════════════════════════════
   SCROLLBAR
═══════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(200,241,53,0.3); }

/* ═══════════════════════════════
   CONTAINER WRAPPER (tool pages)
═══════════════════════════════ */
.tool-container {
    animation: fadeUp 0.35s ease both;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ═══════════════════════════════
   IFRAME border (coach resume)
═══════════════════════════════ */
.resume-frame iframe {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LLM CLIENT
# ─────────────────────────────────────────────
@st.cache_resource
def get_chat():
    return ChatOpenAI(
        model="meta-llama/llama-4-scout",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )

chat = get_chat()

# ─────────────────────────────────────────────
#  UTILITIES
# ─────────────────────────────────────────────
def extract_text(uploaded_file) -> tuple[str, str]:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    loader = PyPDFLoader(tmp_path)
    docs = loader.load()
    return "\n\n".join(d.page_content for d in docs), tmp_path


def stream_llm(formatted_prompt: str) -> str:
    response = ""
    for chunk in chat.stream(formatted_prompt):
        response += chunk.content
    return response


def safe_json(raw: str) -> dict:
    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(cleaned)


def tag_list(items: list, variant: str = "") -> str:
    cls = f"tag {variant}".strip()
    return "<div class='tag-row'>" + "".join(f"<span class='{cls}'>{i}</span>" for i in items) + "</div>"


def score_color(val: int, mx: int) -> str:
    pct = val / mx
    if pct >= 0.75:
        return "green"
    if pct >= 0.5:
        return "gold"
    return "red"


# ─────────────────────────────────────────────
#  SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
PAGES = {
    "home":    ("🏠", "Home"),
    "checker": ("🔍", "Quick Resume Checker"),
    "matcher": ("📊", "Resume Matcher & Scorer"),
    "cover":   ("✉️",  "Cover Letter Generator"),
    "coach":   ("🗣️",  "Career Coach"),
}

if "page" not in st.session_state:
    st.session_state.page = "home"

with st.sidebar:
    # Logo
    st.markdown("<div class='sb-logo-wrap'>", unsafe_allow_html=True)
    from PIL import Image as PILImage
    try:
        logo_img = PILImage.open("Applytlogo.png")
        st.image(logo_img, width=130)
    except Exception:
        st.markdown("<span style='font-family:Space Grotesk,sans-serif;font-size:20px;font-weight:700;color:#EDF2FF'>Appl<span style='color:#C8F135'>yt</span></span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<span class='sidebar-section-label'>Tools</span>", unsafe_allow_html=True)

    for key, (icon, label) in PAGES.items():
        if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    st.markdown("""
    <div class='sidebar-footer'>
        Applyt v1.0 &nbsp;·&nbsp; AI Career Toolkit
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE: HOME
# ─────────────────────────────────────────────
def page_home():
    st.markdown("""
    <div class='hero-wrap'>
        <div class='hero-eyebrow'>
            <span class='dot'></span> AI-Powered Career Toolkit
        </div>
        <h1 class='hero-title'>
            Land your dream job<br>with <span class='accent'>AI on your side</span>
        </h1>
        <p class='hero-sub'>
            Applyt gives you a senior recruiter's eye, an ATS optimizer,
            a cover letter writer, and a personal career coach — all in one place.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='feature-grid'>
        <div class='fcard'>
            <span class='fcard-num'>01</span>
            <div class='fcard-icon'>🔍</div>
            <div class='fcard-title'>Quick Resume Checker</div>
            <div class='fcard-desc'>Instant score, strengths, weaknesses, and next-role suggestions in seconds.</div>
        </div>
        <div class='fcard'>
            <span class='fcard-num'>02</span>
            <div class='fcard-icon'>📊</div>
            <div class='fcard-title'>Resume Matcher & Scorer</div>
            <div class='fcard-desc'>Deep ATS + keyword + skill-gap analysis against any job description.</div>
        </div>
        <div class='fcard'>
            <span class='fcard-num'>03</span>
            <div class='fcard-icon'>✉️</div>
            <div class='fcard-title'>Cover Letter Generator</div>
            <div class='fcard-desc'>Tailored, professional cover letters (300–450 words) in one click.</div>
        </div>
        <div class='fcard'>
            <span class='fcard-num'>04</span>
            <div class='fcard-icon'>🗣️</div>
            <div class='fcard-title'>Career Coach</div>
            <div class='fcard-desc'>Conversational AI mentor that knows your resume — prep, strategy, gaps.</div>
        </div>
    </div>

    <div class='stats-row'>
        <div class='stat-item'>
            <span class='stat-val'>4</span>
            <span class='stat-lbl'>AI Tools</span>
        </div>
        <div class='stat-item'>
            <span class='stat-val'>100%</span>
            <span class='stat-lbl'>ATS Aware</span>
        </div>
        <div class='stat-item'>
            <span class='stat-val'>&lt;30s</span>
            <span class='stat-lbl'>Results</span>
        </div>
        <div class='stat-item'>
            <span class='stat-val'>Free</span>
            <span class='stat-lbl'>To Use</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col = st.columns([2, 1, 2])[1]
    with col:
        if st.button("⚡  Get Started Free", use_container_width=True):
            st.session_state.page = "checker"
            st.rerun()


# ─────────────────────────────────────────────
#  PAGE: QUICK RESUME CHECKER
# ─────────────────────────────────────────────
CHECKER_PROMPT = PromptTemplate(
    input_variables=["context", "experience_level", "level_note"],
    template="""
You are a senior technical recruiter and career coach with 15 years of experience across FAANG, startups, and consulting.
You evaluate resumes for {experience_level}-level candidates with the mindset of a hiring manager reviewing 200 applications per week.

DETECTED EXPERIENCE LEVEL: {experience_level}
EVALUATION CONTEXT: {level_note}

RESUME CONTENT:
{context}

SCORING RUBRIC (100 points total):
1. Content Quality (0-20)
2. Skills & Technical Depth (0-20)
3. Structure & Formatting (0-15)
4. Impact & Achievements (0-20)
5. ATS Optimization (0-15)
6. Projects & Practical Work (0-10)

IMPORTANT: Be critical. Do NOT inflate scores. overall_score must equal exact sum of category_scores.
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

RUBRIC_WEIGHTS = {
    "fresher": "No work experience expected. Weight projects, skills, and academics heavily.",
    "mid": "1-4 years expected. Balance experience quality with skills and impact.",
    "senior": "5+ years expected. Weight leadership, system design, and measurable impact heavily.",
}

def detect_level(text: str) -> str:
    t = text.lower()
    if any(s in t for s in ["staff", "principal", "director", "vp ", "8+ years", "10+ years"]):
        return "senior"
    if any(s in t for s in ["2 years", "3 years", "4 years", "senior", "lead"]):
        return "mid"
    return "fresher"


def page_checker():
    st.markdown("<div class='tool-container'>", unsafe_allow_html=True)
    st.markdown("""
    <div class='page-header'>
        <p class='page-title'>🔍 Quick Resume Checker</p>
        <p class='page-sub'>Upload your resume and get a full evaluation in seconds.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="checker_upload")

    if uploaded_file:
        if st.button("⚡  Analyze Resume", use_container_width=True):
            with st.spinner("Analyzing your resume..."):
                try:
                    context, _ = extract_text(uploaded_file)
                    level = detect_level(context)
                    level_note = RUBRIC_WEIGHTS[level]
                    fp = CHECKER_PROMPT.format(context=context, experience_level=level, level_note=level_note)
                    raw = stream_llm(fp)
                    data = safe_json(raw)
                    _render_checker(data)
                except json.JSONDecodeError:
                    st.error("Model returned invalid JSON — please try again.")
                except Exception as e:
                    st.error(f"Error: {e}")


def _render_checker(data: dict):
    score = data["overall_score"]
    ats = data["ats_score_label"].capitalize()
    level = data["experience_level"].capitalize()

    # Top metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Score", f"{score} / 100")
    col2.metric("Experience Level", level)
    col3.metric("ATS Rating", ats)

    st.markdown("<br>", unsafe_allow_html=True)

    # Category scores
    st.markdown("<div class='section-card'><h4>Category Scores</h4>", unsafe_allow_html=True)
    cats = data["category_scores"]
    maxes = {"content_quality": 20, "skills_depth": 20, "structure_formatting": 15,
             "impact_achievements": 20, "ats_optimization": 15, "projects": 10}
    labels = {"content_quality": "Content Quality", "skills_depth": "Skills & Depth",
              "structure_formatting": "Structure", "impact_achievements": "Impact & Achievements",
              "ats_optimization": "ATS Optimization", "projects": "Projects"}

    c1, c2 = st.columns(2)
    items = list(cats.items())
    for i, (key, val) in enumerate(items):
        mx = maxes[key]
        col = c1 if i % 2 == 0 else c2
        with col:
            st.markdown(f"**{labels[key]}** — {val}/{mx}")
            st.progress(val / mx)
    st.markdown("</div>", unsafe_allow_html=True)

    # Strengths & Weaknesses
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-card'><h4>✅ Strengths</h4>", unsafe_allow_html=True)
        for s in data["strengths"]:
            st.success(s)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='section-card'><h4>⚠️ Weaknesses</h4>", unsafe_allow_html=True)
        for w in data["weaknesses"]:
            st.error(w)
        st.markdown("</div>", unsafe_allow_html=True)

    # Skills
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-card'><h4>🛠 Detected Skills</h4>", unsafe_allow_html=True)
        st.markdown(tag_list(data["detected_skills"], "green"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='section-card'><h4>❌ Missing Skills</h4>", unsafe_allow_html=True)
        st.markdown(tag_list(data["missing_skills"], "red"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Next roles
    st.markdown("<div class='section-card'><h4>🎯 Next Roles You Can Target</h4>", unsafe_allow_html=True)
    st.markdown(tag_list(data["next_roles"], "gold"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Suggestions
    st.markdown("<div class='section-card'><h4>💡 Improvement Suggestions</h4>", unsafe_allow_html=True)
    for i, tip in enumerate(data["improvement_suggestions"], 1):
        st.markdown(f"**{i}.** {tip}")
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE: RESUME MATCHER
# ─────────────────────────────────────────────
MATCHER_PROMPT = PromptTemplate(
    input_variables=["context", "job_description"],
    template="""
You are a senior technical recruiter and ATS specialist with 15 years of experience across FAANG, startups, and consulting.
Evaluate how well the candidate's resume matches the given job description.

RESUME:
{context}

JOB DESCRIPTION:
{job_description}

Rules: Be critical. Do not inflate. Base every score strictly on resume vs JD.
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


def page_matcher():
    st.markdown("<div class='tool-container'>", unsafe_allow_html=True)
    st.markdown("""
    <div class='page-header'>
        <p class='page-title'>📊 Resume Matcher & Scorer</p>
        <p class='page-sub'>See exactly how your resume stacks up against any job description.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="matcher_upload")
    with c2:
        job_description = st.text_area("Paste Job Description", height=280,
                                        placeholder="Paste the full JD here...", key="matcher_jd")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔎  Analyze Match", use_container_width=True):
        if not uploaded_file:
            st.warning("Please upload your resume.")
        elif not job_description.strip():
            st.warning("Please paste a job description.")
        else:
            with st.spinner("Matching your resume to the job..."):
                try:
                    context, _ = extract_text(uploaded_file)
                    fp = MATCHER_PROMPT.format(context=context, job_description=job_description)
                    raw = stream_llm(fp)
                    data = safe_json(raw)
                    _render_matcher(data)
                except json.JSONDecodeError:
                    st.error("Model returned invalid JSON — please try again.")
                except Exception as e:
                    st.error(f"Error: {e}")


def _render_matcher(data: dict):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall Score", f"{data['score']} / 100")
    col2.metric("JD Match", f"{data['overall_match']}%")
    col3.metric("ATS Compatibility", f"{data['ats_compatibility']} / 100")
    col4.metric("Reliability", f"{data['reliability_score']} / 100")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-card'><h4>✅ Keywords Matched</h4>", unsafe_allow_html=True)
        st.markdown(tag_list(data["keywords_match"]["matched"], "green"), unsafe_allow_html=True)
        st.markdown(f"<br><b>Match Rate: {data['keywords_match']['match_percentage']}%</b>", unsafe_allow_html=True)
        st.progress(data["keywords_match"]["match_percentage"] / 100)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='section-card'><h4>❌ Missing Keywords</h4>", unsafe_allow_html=True)
        st.markdown(tag_list(data["missing_keywords"], "red"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-card'><h4>📐 Format Analysis</h4>", unsafe_allow_html=True)
        st.write(data["format_analysis"]["summary"])
        for issue in data["format_analysis"]["issues"]:
            st.warning(issue)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='section-card'><h4>🧩 Skill Gap Analysis</h4>", unsafe_allow_html=True)
        st.write(data["skill_gap_analysis"]["gap_summary"])
        st.markdown("**Present:**")
        st.markdown(tag_list(data["skill_gap_analysis"]["present_skills"], "green"), unsafe_allow_html=True)
        st.markdown("<br>**Missing:**", unsafe_allow_html=True)
        st.markdown(tag_list(data["skill_gap_analysis"]["missing_skills"], "red"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'><h4>💡 Improvement Suggestions</h4>", unsafe_allow_html=True)
    for i, s in enumerate(data["improvement_suggestions"], 1):
        st.markdown(f"**{i}.** {s}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'><h4>🏭 Industry-Specific Feedback</h4>", unsafe_allow_html=True)
    st.info(data["industry_specific_feedback"])
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE: COVER LETTER
# ─────────────────────────────────────────────
COVER_PROMPT = PromptTemplate(
    input_variables=["context", "job_description"],
    template="""
You are an expert career coach and professional writer who has helped thousands of candidates land jobs at top companies.
Write a compelling, tailored cover letter based on the candidate's resume and the job description provided.

RESUME:
{context}

JOB DESCRIPTION:
{job_description}

RULES:
- Length: 300-450 words strictly
- Tone: Professional but human, not robotic
- Do NOT start with "I am writing to apply for..."
- Open with a strong hook that shows genuine interest
- Paragraph 1: Hook + role excitement
- Paragraph 2: Match 2-3 key skills/experiences from resume to JD requirements
- Paragraph 3: Unique value — what you bring that others won't
- Paragraph 4: Short, confident closing with a call to action
- Use candidate's actual projects and skills from resume
- Never fabricate experience not present in resume

FORMAT EXACTLY:
[Full Name]
[City]
[Email Address]

[Date]

Hiring Team
[Company Name]

[Body — 4 paragraphs]

Sincerely,
[Full Name]

Extract name, city, email from resume. Output only the cover letter. No labels or extra text.
"""
)


def page_cover():
    st.markdown("<div class='tool-container'>", unsafe_allow_html=True)
    st.markdown("""
    <div class='page-header'>
        <p class='page-title'>✉️ Cover Letter Generator</p>
        <p class='page-sub'>Get a tailored, professional cover letter in one click.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="cover_upload")
    with c2:
        job_description = st.text_area("Paste Job Description", height=280,
                                        placeholder="Paste the full JD here...", key="cover_jd")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✍️  Generate Cover Letter", use_container_width=True):
        if not uploaded_file:
            st.warning("Please upload your resume.")
        elif not job_description.strip():
            st.warning("Please paste a job description.")
        else:
            with st.spinner("Writing your cover letter..."):
                try:
                    context, _ = extract_text(uploaded_file)
                    fp = COVER_PROMPT.format(context=context, job_description=job_description)
                    result = ""
                    placeholder = st.empty()
                    for chunk in chat.stream(fp):
                        result += chunk.content
                        placeholder.markdown(f"<div class='cl-box'>{result}</div>", unsafe_allow_html=True)

                    # Copy button area
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.download_button(
                        "📥  Download Cover Letter (.txt)",
                        data=result,
                        file_name="cover_letter.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Error: {e}")


# ─────────────────────────────────────────────
#  PAGE: CAREER COACH
# ─────────────────────────────────────────────
def page_coach():
    st.markdown("<div class='tool-container'>", unsafe_allow_html=True)
    st.markdown("""
    <div class='page-header'>
        <p class='page-title'>🗣️ Career Coach</p>
        <p class='page-sub'>Your personal AI mentor — upload your resume, then ask anything.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="coach_upload")

    if not uploaded_file:
        st.info("Upload your resume above to start chatting with your career coach.")
        return

    # Init session state on new upload
    if ("coach_context" not in st.session_state
            or st.session_state.get("coach_uploaded_name") != uploaded_file.name):
        with st.spinner("Reading resume..."):
            context, tmp_path = extract_text(uploaded_file)
            st.session_state.coach_context = context
            st.session_state.coach_tmp_path = tmp_path
            st.session_state.coach_uploaded_name = uploaded_file.name
            st.session_state.coach_history = []
            st.session_state.coach_system = SystemMessage(content=f"""
You are an elite AI-powered career coach built into Applyt — a professional career toolkit.

You have deeply studied this candidate's resume and know everything about their background, skills, projects, and experience.

YOUR PERSONA:
- 20 years of recruiting and career coaching at Google, Amazon, and top-tier startups
- Helped 10,000+ candidates land their dream jobs
- Direct, honest, and brutally constructive — never vague or generic
- You speak like a senior mentor, not a customer service bot

SPECIALTIES:
- Career path planning tailored to the candidate's exact background
- Resume line-by-line improvements with specific rewrites
- Mock interviews with real follow-up questions based on their projects
- Job search strategy — which companies, which roles, what order to apply
- Skill gap analysis with ordered learning roadmaps
- Salary negotiation tactics for their specific level and market
- LinkedIn and personal brand building

STRICT RULES:
- Always reference the candidate's actual projects, skills, and experience
- Never give generic advice — make it specific to THIS candidate
- Call out resume weaknesses and fix them on the spot
- Keep responses concise, structured, and actionable

CANDIDATE RESUME:
{context}
""")

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1, 1])

    # Resume viewer
    with left:
        st.markdown("**📄 Your Resume**")
        with open(st.session_state.coach_tmp_path, "rb") as f:
            pdf_bytes = f.read()
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(f"""
            <iframe src="data:application/pdf;base64,{b64}"
                    width="100%" height="680px"
                    style="border:1px solid rgba(255,255,255,0.07);border-radius:14px;display:block;">
            </iframe>
        """, unsafe_allow_html=True)
        st.download_button("📥 Download", pdf_bytes, file_name="resume.pdf",
                           mime="application/pdf", use_container_width=True)

    # Chat
    with right:
        st.markdown("**💬 Career Coach**")

        # Quick suggestion buttons
        suggestions = [
            "What roles should I target?",
            "What are my biggest resume gaps?",
            "Give me a mock interview question",
            "What skills should I learn next?",
        ]
        cols = st.columns(2)
        for i, s in enumerate(suggestions):
            with st.container():
                cols[i % 2].markdown(f"<div class='sug-btn'>", unsafe_allow_html=True)
                if cols[i % 2].button(s, key=f"sug_{i}", use_container_width=True):
                    st.session_state.coach_pending = s
                cols[i % 2].markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Chat history display
        chat_box = st.container(height=430)
        with chat_box:
            for msg in st.session_state.get("coach_history", []):
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                with st.chat_message(role):
                    st.write(msg.content)

        # Input
        pending = st.session_state.pop("coach_pending", None)
        user_input = pending or st.chat_input("Ask your career coach anything...", key="coach_input")

        if user_input:
            with chat_box:
                with st.chat_message("user"):
                    st.write(user_input)

            st.session_state.coach_history.append(HumanMessage(content=user_input))
            messages = [st.session_state.coach_system] + st.session_state.coach_history

            with chat_box:
                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    response_text = ""
                    for chunk in chat.stream(messages):
                        response_text += chunk.content
                        placeholder.markdown(response_text)

            st.session_state.coach_history.append(AIMessage(content=response_text))
            st.rerun()


# ─────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────
page = st.session_state.page
if page == "home":
    page_home()
elif page == "checker":
    page_checker()
elif page == "matcher":
    page_matcher()
elif page == "cover":
    page_cover()
elif page == "coach":
    page_coach()