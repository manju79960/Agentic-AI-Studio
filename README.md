# 🤖 Agentic AI Studio

### Intelligent IT Helpdesk Automation

Agentic AI Studio is an AI-powered IT helpdesk prototype that analyzes technical complaints, classifies issues, assigns priority levels, recommends troubleshooting steps, and drafts support responses.

## ✨ Features

- **Ticket Intake:** Accepts IT complaints from users.
- **Classification Agent:** Identifies the type of technical issue.
- **Priority Agent:** Assesses urgency and impact.
- **Resolution Agent:** Recommends troubleshooting steps.
- **Response Agent:** Drafts a support response.
- **Ticket History:** Displays analyzed requests during the session.
- **Report Export:** Downloads ticket reports in Markdown and exports ticket history to CSV.
- **Gemini AI:** Uses Google's Gemini model for AI-powered analysis, with a rule-based fallback when configured in the application.

## 🛠️ Technology Stack

- Python
- Streamlit
- Google Gemini API
- Python-dotenv
- DuckDuckGo Search library (DDGS)

## 📁 Project Structure

```text
Agentic-AI-Studio/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env.example
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/manju79960/Agentic-AI-Studio.git
cd Agentic-AI-Studio
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project folder and add:

```text
GEMINI_API_KEY=your_actual_api_key
```

Replace the placeholder with your own Gemini API key. Keep `.env` private and never commit it to GitHub.

Alternatively, use the API-key input provided in the application if supported by your version.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal.

## 🔄 Workflow

1. Submit an IT complaint.
2. Classify the technical issue.
3. Assess its priority.
4. Generate troubleshooting recommendations.
5. Draft a support response.
6. Review and export the ticket report.

## ⚠️ Disclaimer

This is a prototype. It provides support recommendations but does not automatically access devices, reset accounts, contact IT staff, or create tickets in an external helpdesk system.

## 👨‍💻 Project Purpose

Developed as an educational project to demonstrate AI-assisted IT support, workflow orchestration, and interactive web application development.
