"""
Smart Code Reviewer — Streamlit application.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import os
import streamlit as st
from dotenv import load_dotenv

from reviewer import CategoryFeedback, ReviewResult, configure_groq, review_code
from samples import SAMPLES

# Load environment variables from .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Smart Code Reviewer",
    page_icon="🔍",
    layout="wide",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    /* ── Global ──────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1.5rem; }

    /* ── Hero banner ─────────────────────────────────── */
    .hero {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 1.5rem;
        color: white;
        position: relative;
        overflow: hidden;
    }
    .hero::after {
        content: '';
        position: absolute;
        top: -50%; right: -20%;
        width: 400px; height: 400px;
        background: rgba(255,255,255,0.07);
        border-radius: 50%;
    }
    .hero h1 { font-size: 2.2rem; font-weight: 800; margin: 0 0 .4rem 0; }
    .hero p  { font-size: 1.05rem; opacity: 0.9; margin: 0; max-width: 600px; }

    /* ── Score ring card ─────────────────────────────── */
    .score-ring-card {
        background: linear-gradient(135deg, #f8fafc, #eef2ff);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.8rem 1rem;
        text-align: center;
        box-shadow: 0 4px 24px rgba(99,102,241,0.08);
    }
    .score-ring {
        width: 110px; height: 110px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 0.8rem auto;
        font-size: 2rem; font-weight: 800; color: #fff;
    }
    .ring-high   { background: conic-gradient(#22c55e var(--pct), #e2e8f0 0); }
    .ring-medium { background: conic-gradient(#f59e0b var(--pct), #e2e8f0 0); }
    .ring-low    { background: conic-gradient(#ef4444 var(--pct), #e2e8f0 0); }
    .ring-inner {
        width: 82px; height: 82px;
        background: #fff;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.8rem; font-weight: 800; color: #1e293b;
    }
    .score-ring-label { font-weight: 600; color: #64748b; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }

    /* ── Metric mini cards ───────────────────────────── */
    .metric-card {
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.2rem 1rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99,102,241,0.12);
    }
    .metric-score {
        font-size: 2rem; font-weight: 800;
    }
    .metric-label {
        font-size: 0.8rem; font-weight: 600; color: #64748b;
        text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px;
    }
    .score-high   { color: #16a34a; }
    .score-medium { color: #d97706; }
    .score-low    { color: #dc2626; }

    /* ── TL;DR box ───────────────────────────────────── */
    .tldr-box {
        background: linear-gradient(90deg, #eef2ff, #f5f3ff);
        border-left: 4px solid #6366f1;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        font-size: 0.95rem;
        color: #1e293b;
        line-height: 1.6;
    }

    /* ── Category cards ──────────────────────────────── */
    .cat-card {
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.4rem 1.4rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.03);
    }
    .cat-header {
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 0.6rem;
    }
    .cat-icon {
        font-size: 1.5rem;
    }
    .cat-title {
        font-size: 1.1rem; font-weight: 700; color: #1e293b;
    }
    .cat-score-pill {
        margin-left: auto;
        padding: 3px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        color: #fff;
    }
    .pill-high   { background: #22c55e; }
    .pill-medium { background: #f59e0b; }
    .pill-low    { background: #ef4444; }
    .cat-summary {
        color: #475569;
        font-size: 0.93rem;
        line-height: 1.55;
        margin-bottom: 0.8rem;
    }
    .suggestion-item {
        background: linear-gradient(90deg, #f0f4ff, #faf5ff);
        border-left: 3px solid #8b5cf6;
        padding: 10px 14px;
        margin: 6px 0;
        border-radius: 0 10px 10px 0;
        font-size: 0.88rem;
        color: #334155;
        line-height: 1.5;
    }

    /* ── Sidebar ─────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] strong {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] .stTextInput label {
        color: #c7d2fe !important; font-weight: 600;
    }
    section[data-testid="stSidebar"] .stTextInput input,
    section[data-testid="stSidebar"] .stTextInput input[type="password"] {
        background: rgba(255,255,255,0.15) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        caret-color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    section[data-testid="stSidebar"] .stTextInput input::placeholder {
        color: rgba(255,255,255,0.4) !important;
        -webkit-text-fill-color: rgba(255,255,255,0.4) !important;
    }
    /* password toggle icon inside sidebar */
    section[data-testid="stSidebar"] .stTextInput button svg {
        fill: #c4b5fd !important;
        stroke: #c4b5fd !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.12) !important;
    }
    /* radio buttons in sidebar */
    section[data-testid="stSidebar"] .stRadio label span {
        color: #e2e8f0 !important;
    }
    .sidebar-badge {
        display: inline-block;
        background: rgba(139,92,246,0.3);
        padding: 3px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        color: #c4b5fd !important;
        font-weight: 600;
    }

    /* ── Sidebar collapse/expand arrow ───────────────── */
    button[data-testid="stBaseButton-headerNoPadding"] svg,
    [data-testid="collapsedControl"] svg,
    button[data-testid="baseButton-headerNoPadding"] svg {
        fill: #64748b !important;
        stroke: #64748b !important;
        width: 1.2rem !important;
        height: 1.2rem !important;
    }
    button[data-testid="stBaseButton-headerNoPadding"],
    [data-testid="collapsedControl"] button,
    button[data-testid="baseButton-headerNoPadding"] {
        background: transparent !important;
        border: none !important;
    }

    /* ── Button ──────────────────────────────────────── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.4rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 0.02em;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(99,102,241,0.35) !important;
    }

    /* ── Code input ──────────────────────────────────── */
    .stTextArea textarea {
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
        font-size: 0.88rem !important;
        background: #1e293b !important;
        color: #e2e8f0 !important;
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
        padding: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Helpers ─────────────────────────────────────────────────────────────────


CATEGORY_ICONS = {
    "Readability": "📖",
    "Structure": "🏗️",
    "Maintainability": "🔧",
}


def _score_tier(score: float) -> str:
    if score >= 7:
        return "high"
    if score >= 4:
        return "medium"
    return "low"


def _score_label(score: float) -> str:
    if score >= 9:
        return "Excellent"
    if score >= 7:
        return "Good"
    if score >= 5:
        return "Fair"
    if score >= 3:
        return "Poor"
    return "Critical"


def _render_category_card(cat: CategoryFeedback) -> None:
    """Render a polished category card."""
    tier = _score_tier(cat.score)
    icon = CATEGORY_ICONS.get(cat.category, "📋")
    suggestions_html = "".join(
        f'<div class="suggestion-item">💡 {s}</div>' for s in cat.suggestions
    )
    st.markdown(
        f"""
        <div class="cat-card">
            <div class="cat-header">
                <span class="cat-icon">{icon}</span>
                <span class="cat-title">{cat.category}</span>
                <span class="cat-score-pill pill-{tier}">{cat.score}/10</span>
            </div>
            <div class="cat-summary">{cat.summary}</div>
            {suggestions_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_result(result: ReviewResult) -> None:
    """Render the full review result with a polished dashboard layout."""

    # ── Overall score ring + per-category metric cards ──
    ring_col, spacer, m1, m2, m3 = st.columns([2, 0.3, 1.2, 1.2, 1.2])
    tier = _score_tier(result.overall_score)
    pct = int(result.overall_score * 10)  # 0-100 for conic gradient

    with ring_col:
        st.markdown(
            f"""
            <div class="score-ring-card">
                <div class="score-ring ring-{tier}" style="--pct:{pct}%">
                    <div class="ring-inner">{result.overall_score}</div>
                </div>
                <div class="score-ring-label">{_score_label(result.overall_score)} · {result.language}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with spacer:
        st.empty()

    for col, cat in zip([m1, m2, m3], result.categories):
        t = _score_tier(cat.score)
        icon = CATEGORY_ICONS.get(cat.category, "📋")
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div style="font-size:1.6rem;margin-bottom:4px">{icon}</div>
                    <div class="metric-score score-{t}">{cat.score}/10</div>
                    <div class="metric-label">{cat.category}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TL;DR ──
    st.markdown(
        f'<div class="tldr-box">📝 <strong>TL;DR</strong> — {result.tldr}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Detailed category cards ──
    st.markdown("#### 🔬 Detailed Analysis")
    for cat in result.categories:
        _render_category_card(cat)

    # ── Bar chart ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📊 Score Breakdown")
    chart_data = {cat.category: cat.score for cat in result.categories}
    st.bar_chart(chart_data, horizontal=True, height=200, color="#6366f1")


# ── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:1rem 0 0.5rem;color:#ffffff">
            <div style="font-size:2.5rem">🔍</div>
            <div style="font-size:1.3rem;font-weight:800;letter-spacing:-0.02em;color:#ffffff">Smart Code Reviewer</div>
            <div style="font-size:0.78rem;opacity:0.7;margin-top:2px;color:#e2e8f0">AI-Powered Code Analysis</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Display API key status
    if GROQ_API_KEY:
        st.markdown(
            '<span class="sidebar-badge">✅ API Key Loaded</span>',
            unsafe_allow_html=True,
        )
    else:
        st.warning(
            "⚠️ **No API Key found!**\n\n"
            "1. Go to https://console.groq.com/keys\n"
            "2. Create an API key\n"
            "3. Add it to `.env` file: `GROQ_API_KEY=your_key_here`\n"
            "4. Restart the app"
        )

    st.markdown(
        '<span class="sidebar-badge">⚡ Llama 3.3 70B via Groq</span>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        "**How it works**\n\n"
        "&nbsp;**①** &nbsp;Paste code or pick a sample\n\n"
        "&nbsp;**②** &nbsp;Click **Review Code**\n\n"
        "&nbsp;**③** &nbsp;Get scored feedback with suggestions"
    )

    st.markdown("---")
    st.markdown(
        "**Analyses 3 dimensions:**\n\n"
        "📖 Readability\n\n"
        "🏗️ Structure\n\n"
        "🔧 Maintainability"
    )

    st.markdown("---")
    st.markdown(
        '<div style="text-align:center;font-size:0.75rem;opacity:0.7;color:#c7d2fe">'
        'Built with Streamlit & Groq</div>',
        unsafe_allow_html=True,
    )

# ── Main area ───────────────────────────────────────────────────────────────

# ── Hero banner ─────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="hero">
        <h1>🔍 Smart Code Reviewer</h1>
        <p>Paste your code, pick a sample, and get an instant AI-powered review
        covering readability, structure, and maintainability — before it ever
        reaches a human reviewer.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Input section ───────────────────────────────────────────────────────────

# Initialise session state for the code editor
if "loaded_code" not in st.session_state:
    st.session_state["loaded_code"] = ""

left_col, right_col = st.columns([3, 1.2])

with right_col:
    st.markdown("##### 📂 Quick Samples")
    sample_name = st.radio(
        "Pick a sample to load:",
        options=["— none —"] + list(SAMPLES.keys()),
        label_visibility="collapsed",
    )
    if sample_name != "— none —":
        st.code(SAMPLES[sample_name]["code"][:120] + "…", language=SAMPLES[sample_name]["language"])
        if st.button("📋 Load this sample", use_container_width=True):
            st.session_state["loaded_code"] = SAMPLES[sample_name]["code"]
            st.rerun()

with left_col:
    code_input = st.text_area(
        "✏️ Code to review",
        value=st.session_state["loaded_code"],
        height=380,
        placeholder="Paste your code here…",
    )

review_btn = st.button("🚀  Review Code", type="primary", use_container_width=True)

if not code_input.strip():
    # Show a friendly empty state
    st.markdown(
        """
        <div style="text-align:center;padding:3rem 0;color:#94a3b8">
            <div style="font-size:3rem;margin-bottom:0.5rem">📝</div>
            <div style="font-size:1.1rem;font-weight:600">No code yet</div>
            <div style="font-size:0.9rem">Paste a snippet or pick a sample from the right →</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Run review ──────────────────────────────────────────────────────────────

if review_btn:
    if not GROQ_API_KEY:
        st.error(
            "❌ **API Key not configured!**\n\n"
            "Please add your Groq API key to the `.env` file and restart the app."
        )
        st.stop()
    if not code_input.strip():
        st.warning("⚠️ Please paste some code to review.")
        st.stop()

    configure_groq(GROQ_API_KEY)

    with st.status("🔍 Reviewing your code…", expanded=True) as status:
        st.write("Sending code to Llama 3.3 70B via Groq…")
        try:
            result = review_code(code_input)
        except Exception as exc:
            st.error(f"Review failed: {exc}")
            st.stop()
        st.write("Parsing structured feedback…")
        status.update(label="✅ Review complete!", state="complete", expanded=False)

    st.markdown("---")
    _render_result(result)
