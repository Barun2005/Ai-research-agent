import streamlit as st
import time
from datetime import datetime
from agent import ResearchAgent

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%); }

[data-testid="stSidebar"] {
    background: #0d0d16 !important;
    border-right: 1px solid #1e1e2e !important;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #38bdf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    text-align: center;
    margin-bottom: 0.4rem;
}

.hero-subtitle {
    color: #64748b;
    font-size: 1rem;
    font-weight: 300;
    text-align: center;
    margin-bottom: 1.5rem;
}

.step-card {
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    border-left: 3px solid #a78bfa;
}
.step-card.thinking  { border-left-color: #f59e0b; }
.step-card.searching { border-left-color: #38bdf8; }
.step-card.analyzing { border-left-color: #a78bfa; }
.step-card.writing   { border-left-color: #f472b6; }
.step-card.done      { border-left-color: #34d399; }
.step-card.error     { border-left-color: #ef4444; }

.step-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #64748b;
}
.step-text { color: #cbd5e1; font-size: 0.9rem; margin-top: 0.3rem; }

.metric-pill {
    display: inline-block;
    background: #1e1e2e;
    border: 1px solid #2d2d3e;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    color: #94a3b8;
    margin: 2px;
}

.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #0f0f1a !important;
    border: 1px solid #1e1e2e !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.2) !important;
}

.stSelectbox > div > div {
    background: #0f0f1a !important;
    border-color: #1e1e2e !important;
    color: #e2e8f0 !important;
}

hr { border-color: #1e1e2e !important; }
code { background: #1e1e2e !important; color: #a78bfa !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2d2d3e; border-radius: 4px; }

.api-tip {
    background: #1a1a2e;
    border: 1px solid #2d2d45;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    font-size: 0.8rem;
    color: #94a3b8;
    margin-top: 0.5rem;
    line-height: 1.6;
}
.api-tip a { color: #38bdf8; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "template_query" not in st.session_state:
    st.session_state.template_query = ""

with st.sidebar:
    st.markdown("### 🔑 API Configuration")
    api_key_input = st.text_input("Gemini API Key", type="password", placeholder="AIza...")
    if api_key_input:
        api_key = api_key_input
        st.success("Using your custom API key!")
    else:
        api_key = None
        st.info("💡 Using system default key from .env")
    
    st.markdown("---")
    st.markdown("### 🔌 Developer API")
    st.markdown("""
    **Endpoint:** `http://localhost:8000/research`
    
    **Example Curl:**
    ```bash
    curl -X POST "http://localhost:8000/research" \\
    -H "Content-Type: application/json" \\
    -d '{"query": "Future of AI"}'
    ```
    """)

    st.markdown("---")
    st.markdown("### 🎯 Agent Settings")

    depth = st.selectbox(
        "Research Depth",
        ["Quick (3 steps)", "Standard (5 steps)", "Deep (7 steps)"],
        index=1
    )

    output_format = st.selectbox(
        "Output Format",
        ["Detailed Report", "Executive Summary", "Bullet Points", "Q&A Format"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 📋 Quick Templates")

    templates = {
        "🔬 Explain a concept":  "Explain transformer architecture and how it powers modern LLMs",
        "📊 Compare technologies": "Compare React vs Vue vs Angular for web development in 2025",
        "🗺️ Learning roadmap":   "Create a learning roadmap for machine learning for beginners",
        "💡 Problem analysis":   "Analyze the causes and solutions for climate change",
        "📈 Industry analysis":  "Analyze the current state of generative AI industry in 2025",
    }
    for label, prompt in templates.items():
        if st.button(label, use_container_width=True):
            st.session_state.template_query = prompt
            st.rerun()

    st.markdown("---")
    st.markdown("### 📜 History")
    if st.session_state.history:
        for i, h in enumerate(reversed(st.session_state.history[-5:])):
            st.markdown(f"`{i+1}.` {h['query'][:38]}...")
    else:
        st.markdown(
            "<span style='color:#4a5568;font-size:0.82rem'>No research history yet.</span>",
            unsafe_allow_html=True
        )

# ── Main UI ───────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🤖 AI Research Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Autonomous multi-step research powered by Google Gemini</div>',
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div style="text-align:center;color:#a78bfa;font-size:0.8rem">🧠 PLANS AUTONOMOUSLY</div>',
                unsafe_allow_html=True)
with c2:
    st.markdown('<div style="text-align:center;color:#38bdf8;font-size:0.8rem">🔍 MULTI-STEP REASONING</div>',
                unsafe_allow_html=True)
with c3:
    st.markdown('<div style="text-align:center;color:#34d399;font-size:0.8rem">📝 STRUCTURED OUTPUT</div>',
                unsafe_allow_html=True)

st.markdown("---")

# ── Query Input ───────────────────────────────────────────────────────────────
query = st.text_area(
    "🔍 What do you want to research?",
    value=st.session_state.template_query,
    placeholder="e.g. Explain how neural networks learn, or Compare SQL vs NoSQL databases...",
    height=110,
)

col_run, col_clear = st.columns([1, 5])
with col_run:
    run_btn = st.button("🚀 Run Agent", use_container_width=True)
with col_clear:
    if st.button("🗑️ Clear"):
        st.session_state.template_query = ""
        st.rerun()

# ── Agent Execution ───────────────────────────────────────────────────────────
if run_btn:
    if not api_key:
        st.error("⚠️ Please enter your **Google Gemini API Key** in the left sidebar first.")
        st.info("👈 Look at the sidebar → paste your key in the **Google Gemini API Key** field.")
    elif not query.strip():
        st.warning("⚠️ Please enter a research query above.")
    else:
        st.markdown("---")
        st.markdown("### 🤖 Agent Working...")

        depth_map = {"Quick (3 steps)": 3, "Standard (5 steps)": 5, "Deep (7 steps)": 7}
        max_steps = depth_map[depth]

        steps_container = st.container()
        result_container = st.container()

        agent = ResearchAgent(api_key=api_key, max_steps=max_steps, output_format=output_format)
        all_steps = []

        with steps_container:
            progress_bar = st.progress(0)
            status_text = st.empty()

            icon_map = {
                "thinking":  "🧠",
                "planning":  "📋",
                "searching": "🔍",
                "reading":   "📖",
                "writing":   "✍️",
                "analyzing": "🔬",
                "done":      "✅",
                "error":     "❌",
            }

            for step in agent.run(query):
                all_steps.append(step)

                progress = min(step["step_num"] / max_steps, 1.0)
                progress_bar.progress(progress)
                status_text.markdown(
                    f'<span style="color:#64748b;font-size:0.85rem">'
                    f'Step {step["step_num"]}/{max_steps} — {step["label"]}</span>',
                    unsafe_allow_html=True
                )

                icon = icon_map.get(step["type"], "⚡")
                css = step["type"] if step["type"] in [
                    "thinking", "searching", "analyzing", "writing", "done", "error"
                ] else "thinking"

                st.markdown(f"""
<div class="step-card {css}">
    <div class="step-label">{icon} {step['label']}</div>
    <div class="step-text">{step['text']}</div>
</div>
""", unsafe_allow_html=True)
                time.sleep(0.2)

            progress_bar.progress(1.0)
            status_text.markdown(
                '<span style="color:#34d399;font-size:0.85rem">✅ Research completed!</span>',
                unsafe_allow_html=True
            )

        # ── Final Report ──────────────────────────────────────────────────────
        with result_container:
            st.markdown("---")
            st.markdown("### 📄 Research Report")

            final = agent.final_result
            if final:
                st.markdown(f"""
<div style="margin-bottom:1rem">
    <span class="metric-pill">📅 {datetime.now().strftime('%d %b %Y, %H:%M')}</span>
    <span class="metric-pill">🔢 {len(all_steps)} steps</span>
    <span class="metric-pill">📊 {output_format}</span>
    <span class="metric-pill">🎯 {depth}</span>
    <span class="metric-pill">🤖 Gemini 1.5 Flash</span>
</div>
""", unsafe_allow_html=True)

                st.markdown(final)

                st.download_button(
                    label="📥 Download Report (.md)",
                    data=(
                        f"# AI Research Report\n\n"
                        f"**Query:** {query}\n\n"
                        f"**Date:** {datetime.now().strftime('%d %b %Y, %H:%M')}\n\n"
                        f"**Model:** Google Gemini 1.5 Flash\n\n"
                        f"---\n\n{final}"
                    ),
                    file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown",
                )

                st.session_state.history.append({
                    "query": query,
                    "result": final,
                    "steps": len(all_steps),
                    "timestamp": datetime.now().isoformat(),
                })
                st.session_state.template_query = ""

            else:
                st.error("❌ Agent did not produce a result. Please check your API key and try again.")
