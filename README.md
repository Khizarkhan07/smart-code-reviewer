# 🔍 Smart Code Reviewer

AI-powered code review assistant that analyses your code for **readability**, **structure**, and **maintainability** — before it ever reaches a human reviewer.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![Gemini](https://img.shields.io/badge/Google%20Gemini-Free%20Tier-yellow)

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
- ⚡ Powered by **Google Gemini 2.0 Flash** (free tier)

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone <repo-url>
cd Smart-Code-Reviewer
uv sync          # or: pip install -e .
```

### 2. Get a free Gemini API key

Go to **https://aistudio.google.com/apikey** and create a key.

### 3. Run the app

```bash
streamlit run app.py
```

Then open **http://localhost:8501** in your browser, paste your API key in the sidebar, and start reviewing!

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
- **[Google Gemini](https://ai.google.dev)** — LLM-powered code analysis
- **[Pygments](https://pygments.org)** — syntax highlighting support

---

## 📝 License

MIT
