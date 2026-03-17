# 🤖 AI Research Agent
### Powered by Google Gemini API (Free!)

An **Agentic AI** project built with Python, Streamlit & Google Gemini.

The agent autonomously plans, searches, analyzes, and writes research reports
using multi-step tool-calling — a core pattern in modern Agentic AI systems.

---

## 🔑 Get Your FREE Google API Key (No Card Needed!)

1. Go to 👉 [aistudio.google.com](https://aistudio.google.com)
2. Sign in with your **Google account**
3. Click **"Get API Key"** → **"Create API Key"**
4. Copy the key (starts with `AIza...`)
5. Create a file named `.env` in the root folder
6. Add your key like this: `GEMINI_API_KEY=your_key_here`

✅ **Completely free** — 15 requests/minute, no credit card required!

---

## 🚀 Setup & Run (3 commands)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py

# 3. Open in browser
# http://localhost:8501
```

---

## 🧠 How the Agent Works (Agentic AI)

```
You type a query
      ↓
🧠 THINK    → Agent plans the research approach
      ↓
🔍 SEARCH   → Gathers info on subtopic 1
      ↓
🔍 SEARCH   → Gathers info on subtopic 2
      ↓
🔬 ANALYZE  → Synthesizes all findings
      ↓
✍️ WRITE    → Drafts report sections
      ↓
✅ FINALIZE → Compiles full report
      ↓
📄 You get a complete research report!
```

This is **Agentic AI** because:
- The model **decides its own next action** at each step
- It uses **tools** to gather and process information
- It **loops autonomously** until the task is complete
- No human intervention needed during research

---

## ✨ New Features
- 🔍 **Real-World Research:** Uses DuckDuckGo search to gather live data instead of imagining facts.
- 🔌 **REST API Server:** Built with FastAPI, allows programmatic research and direct answering.
- 🛡️ **Model Rotation:** Automatically falls back to alternative Gemini models if the primary one hits quota limits.

---

## 📁 Project Structure

```
ai_research_agent/
├── app.py            → Streamlit UI (dark theme, live steps)
├── agent.py          → Core agent logic + Real search + Fallbacks
├── server.py         → FastAPI REST API Server
├── requirements.txt  → Project dependencies
└── README.md         → This file
```

---

## 🔌 REST API Usage

Start the server:
```bash
python server.py
```

### 1. Research Mode (Deep)
`POST /research`
- Performs multi-step research and returns a full report.

### 2. Answer Mode (Fast)
`POST /ask`
- Returns a direct answer to a specific question.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| API Server | FastAPI + Uvicorn |
| AI Model | Google Gemini 2.0 (with Lite Fallbacks) |
| Search API | DuckDuckGo Search |
| Agent Pattern | Tool Use / Function Calling |
| Language | Python 3.9+ |

---

## 🎓 College Submission Notes

**Project Title:** Agentic AI Research Assistant using Multi-Step Tool Calling

**Key Concepts:**
- Agentic AI / Autonomous Agents
- Tool Use / Function Calling
- Multi-step reasoning & planning
- Large Language Models (LLMs)
- Prompt Engineering
- Natural Language Processing (NLP)
- Generative AI

**Abstract:**
This project implements an autonomous AI research agent using Google Gemini's
function-calling capabilities for multi-step research. The agent plans its
approach, gathers information using tools, analyzes findings, and produces
structured reports — demonstrating core Agentic AI concepts.
