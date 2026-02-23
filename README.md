# 🔍 Smart Code Reviewer

AI-powered code review assistant that analyses your code for **readability**, **structure**, and **maintainability** — before it ever reaches a human reviewer.

**[🚀 Try the Live Demo](https://smart-code-reviewer-demo.streamlit.app/)**

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![Groq](https://img.shields.io/badge/Groq-Free%20Tier-green)

---

## ✨ Features

| Dimension | What it checks |
|---|---|
| **Readability** | Naming conventions, comments, formatting, clarity |
| **Structure** | Separation of concerns, class/function organisation, design patterns |
| **Maintainability** | Coupling, complexity, error handling, extensibility |

- 🎯 **Scored feedback** (1–10) per dimension with an overall score
- 💡 **Actionable suggestions** citing specific lines/symbols
- 📊 **Visual score breakdown** chart
- 📂 **Built-in sample snippets** (Python, JavaScript, Java) to try instantly
- ⚡ Powered by **Llama 3.3 70B via Groq** (free tier)

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone <repo-url>
cd Smart-Code-Reviewer
uv sync          # or: pip install -e .
```

### 2. Get a free Groq API key and configure

Go to **https://console.groq.com/keys** and create a key. Copy it and update your `.env` file:

```bash
cp .env.example .env
# Edit .env and paste your Groq API key
```

### 3. Run the app

```bash
streamlit run app.py
```

Then open **http://localhost:8501** in your browser and start reviewing!

---

## 📁 Project Structure

```
Smart-Code-Reviewer/
├── app.py            # Streamlit UI
├── reviewer.py       # AI analysis engine (Gemini integration)
├── samples.py        # Built-in sample code snippets
├── pyproject.toml    # Project metadata & dependencies
├── .env.example      # Environment variable template
└── README.md
```

---

## 🛠 Tech Stack

- **[Streamlit](https://streamlit.io)** — interactive web UI
- **[Groq](https://groq.com)** — fast LLM inference (Llama 3.3 70B)
- **[Pygments](https://pygments.org)** — syntax highlighting support

---

## 📝 License

MIT
