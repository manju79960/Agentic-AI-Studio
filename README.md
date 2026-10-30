# AURA Agentic AI Studio (Visual Workflow UI)

Windows setup:
1. Extract this ZIP.
2. Open the folder in File Explorer, click the address bar, type `cmd`, press Enter.
3. Run:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   streamlit run app.py
   ```
4. Open the local URL shown in the terminal, usually http://localhost:8501.

For live AI planning, analysis, and report generation, paste a Gemini API key into the sidebar. Without it, the app can demonstrate the workflow and web search tool, but AI synthesis is labelled as disabled. Never share or publish your API key.
