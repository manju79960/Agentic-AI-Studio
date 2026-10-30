import os
import re
import json
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Agentic AI Studio | IT Helpdesk",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Styling ---------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --bg:#080d1a; --panel:#111a2c; --line:#253653; --text:#edf3ff; --muted:#9aaac5; --blue:#7895ff; --purple:#a78bfa; --green:#46dfb0; --orange:#ffbf69; }
.stApp { background: radial-gradient(ellipse at 75% 0%, #1b2850 0%, #0b1222 42%, #080d1a 78%); color:var(--text); font-family:'DM Sans',sans-serif; }
.block-container { max-width:1450px; padding-top:1.5rem; padding-bottom:3rem; }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; color:#f6f8ff !important; }
p, label, .stMarkdown { color:inherit; }
[data-testid="stSidebar"] { background:#0b1324; border-right:1px solid #263653; }
[data-testid="stSidebar"] * { color:#e7efff; }
.hero { padding:1.7rem 1.8rem; border:1px solid #30446c; border-radius:24px; background:linear-gradient(120deg,rgba(35,53,100,.95),rgba(17,26,46,.94)); margin-bottom:1.2rem; box-shadow:0 16px 50px rgba(0,0,0,.18); }
.eyebrow { color:#aabaff; font-size:.75rem; letter-spacing:.17em; text-transform:uppercase; font-weight:800; }
.hero h1 { margin:.35rem 0 .3rem; font-size:2.5rem; }
.hero p { color:#c0cbe1; margin:0; font-size:1.02rem; }
.section-title { font-family:'Space Grotesk',sans-serif; font-size:1.18rem; font-weight:700; margin:.8rem 0 .65rem; color:#f2f5ff; }
.panel { background:rgba(17,26,44,.86); border:1px solid #283958; border-radius:18px; padding:1rem 1.1rem; }
.metric { background:linear-gradient(145deg,rgba(22,34,58,.95),rgba(14,22,39,.95)); border:1px solid #293a5a; border-radius:17px; padding:1rem 1.1rem; min-height:105px; }
.metric-label { color:#9aaccb; font-size:.74rem; letter-spacing:.1em; font-weight:700; text-transform:uppercase; }
.metric-value { color:#f5f7ff; font-family:'Space Grotesk',sans-serif; font-size:1.75rem; font-weight:700; margin-top:.25rem; }
.metric-sub { color:#91a3c2; font-size:.78rem; margin-top:.15rem; }
.agent-card { border:1px solid #2b3d5d; background:linear-gradient(145deg,#131f35,#10192b); border-radius:16px; padding:1rem .7rem; min-height:140px; text-align:center; }
.agent-icon { font-size:1.8rem; margin-bottom:.3rem; }
.agent-name { color:#f4f7ff; font-weight:800; font-size:.86rem; }
.agent-desc { color:#a4b4ce; font-size:.72rem; margin-top:.3rem; }
.agent-state { margin-top:.65rem; color:#aabaff; font-size:.68rem; font-weight:800; letter-spacing:.08em; }
.agent-done { border-color:#258c70; background:linear-gradient(145deg,#12382f,#11272a); }
.agent-done .agent-state { color:#55e5b5; }
.pill { display:inline-block; border:1px solid #3b5280; background:#172744; color:#b8c8ff; padding:.25rem .6rem; border-radius:999px; font-size:.73rem; font-weight:700; }
.logline { border-left:2px solid #536fa9; padding:.25rem 0 .55rem .8rem; margin:.2rem 0 .4rem .2rem; color:#c2cde1; font-size:.85rem; }
div.stButton > button[kind="primary"], div.stFormSubmitButton > button { border:0; border-radius:11px; background:linear-gradient(90deg,#6687ff,#9b79ff); color:white; font-weight:800; min-height:2.9rem; }
div.stButton > button { border-radius:10px; }
[data-testid="stExpander"] { border:1px solid #293a5a; border-radius:12px; background:rgba(17,26,44,.5); }
div[data-testid="stAlert"] { border-radius:12px; }
.small-muted { color:#9aacc7; font-size:.83rem; }
</style>
""", unsafe_allow_html=True)

# ----------------------------- Helpers ---------------------------------
def get_gemini_response(api_key: str, prompt: str) -> str:
    from google import genai
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    text = (response.text or "").strip()
    if not text:
        raise ValueError("Gemini returned an empty response.")
    return text

def parse_json_response(text: str) -> dict:
    """Parse JSON from a model response, including fenced JSON."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start >= 0 and end > start:
        cleaned = cleaned[start:end + 1]
    return json.loads(cleaned)

def rule_based_analysis(complaint: str, urgency: str, impact: str) -> dict:
    text = complaint.lower()
    rules = [
        (("wifi", "wi-fi", "internet", "network", "connection"), "Network / Wi-Fi"),
        (("password", "login", "log in", "account", "locked"), "Account / Login"),
        (("printer", "printing", "scanner"), "Printer / Peripheral"),
        (("email", "outlook", "mailbox"), "Email"),
        (("slow", "freez", "crash", "computer", "laptop", "software", "application", "app"), "Computer / Software"),
        (("projector", "display", "monitor", "keyboard", "mouse"), "Hardware"),
    ]
    category = "General IT Support"
    for keywords, label in rules:
        if any(word in text for word in keywords):
            category = label
            break

    high_words = ("exam", "deadline", "entire department", "whole class", "server down", "security", "breach", "urgent")
    if urgency == "Critical" or impact == "Many users" or any(word in text for word in high_words):
        priority = "High"
    elif urgency == "Soon" or impact == "My work is blocked":
        priority = "Medium"
    else:
        priority = "Low"

    tips = {
        "Network / Wi-Fi": [
            "Check whether Wi-Fi is enabled and airplane mode is off.",
            "Reconnect to the approved network and restart Wi-Fi.",
            "If multiple users are affected or the issue continues, escalate to IT to check access points and network status."
        ],
        "Account / Login": [
            "Check the username and keyboard Caps Lock setting.",
            "Use the organization's official password-reset process.",
            "Never share passwords or one-time codes. Escalate if the account remains locked."
        ],
        "Printer / Peripheral": [
            "Check power, cables, paper, and any error lights.",
            "Confirm the correct printer is selected and the queue is not paused.",
            "If unresolved, provide IT with the printer name and displayed error."
        ],
        "Email": [
            "Check internet access and the organization's email service status.",
            "Confirm the correct account and review any storage or sign-in warning.",
            "Escalate with the exact error message; do not share passwords."
        ],
        "Computer / Software": [
            "Save your work if possible and close/reopen the affected application.",
            "Restart the device if it is safe to do so and check for any displayed error.",
            "If the issue repeats, record the application name, device, and error for IT."
        ],
        "Hardware": [
            "Check power, cable connections, and whether the device is selected correctly.",
            "Reconnect the peripheral and test another port if appropriate.",
            "If the device appears damaged, stop using it and contact IT."
        ],
        "General IT Support": [
            "Record the exact error message and when the issue started.",
            "Try a safe restart of the affected application or device if appropriate.",
            "If the issue persists, send the details to IT support for investigation."
        ]
    }
    return {
        "category": category,
        "priority": priority,
        "summary": f"The request appears to concern {category.lower()}.",
        "resolution": tips[category],
        "reply": (
            f"Hello, thank you for reporting this {category.lower()} issue. "
            "Please try the suggested troubleshooting steps. If the issue continues, "
            "reply with the exact error message and we will escalate it to the IT support team."
        ),
        "escalation": "Escalate to IT support if the suggested steps do not resolve the issue."
    }

def analyze_ticket(complaint: str, urgency: str, impact: str, api_key: str) -> tuple[dict, str]:
    if api_key:
        prompt = f"""
You are an IT helpdesk triage assistant. Analyze the user complaint and return ONLY valid JSON.
Do not claim to have accessed real systems, fixed anything, opened a real ticket, or contacted IT.
Keep advice safe, practical, and concise. Never ask for passwords or one-time codes.
Use priority High, Medium, or Low. Consider urgency and impact.
JSON schema:
{{
  "category": "short category",
  "priority": "High|Medium|Low",
  "summary": "one-sentence issue summary",
  "resolution": ["step 1", "step 2", "step 3"],
  "reply": "polite response that support staff can review",
  "escalation": "when/how to escalate"
}}
Complaint: {complaint}
User-selected urgency: {urgency}
Impact: {impact}
"""
        try:
            result = parse_json_response(get_gemini_response(api_key, prompt))
            result.setdefault("category", "General IT Support")
            result.setdefault("priority", "Medium")
            result.setdefault("summary", "IT issue identified from the submitted complaint.")
            result.setdefault("resolution", ["Review the issue details.", "Try a safe basic troubleshooting step.", "Contact IT support if it persists."])
            result.setdefault("reply", "Thank you for reporting the issue. IT support will review the details and advise on the next steps.")
            result.setdefault("escalation", "Escalate to IT support if the issue persists.")
            if result["priority"] not in ("High", "Medium", "Low"):
                result["priority"] = "Medium"
            if not isinstance(result["resolution"], list):
                result["resolution"] = [str(result["resolution"])]
            return result, "Gemini AI"
        except Exception as exc:
            fallback = rule_based_analysis(complaint, urgency, impact)
            return fallback, f"Rule-based fallback (Gemini unavailable: {exc})"
    return rule_based_analysis(complaint, urgency, impact), "Rule-based demo mode"

def safe_ticket_id() -> str:
    return "IT-" + datetime.now().strftime("%y%m%d-%H%M%S")

if "tickets" not in st.session_state:
    st.session_state.tickets = []
if "latest_ticket" not in st.session_state:
    st.session_state.latest_ticket = None

# ----------------------------- Sidebar ---------------------------------
with st.sidebar:
    st.markdown("## 🤖 Agentic AI Studio")
    st.caption("Intelligent IT Helpdesk")
    st.markdown("---")
    api_key = st.text_input(
        "Gemini API key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Optional. Add a Gemini API key for AI-powered analysis. Without it, the app uses a rule-based demo mode."
    )
    st.markdown(
        f'<span class="pill">{"GEMINI AI ENABLED" if api_key else "DEMO MODE"}</span>',
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown("**WORKFLOW AGENTS**")
    st.markdown("🎫 Ticket Intake")
    st.markdown("🔍 Classification Agent")
    st.markdown("🚦 Priority Agent")
    st.markdown("🧠 Resolution Agent")
    st.markdown("✉️ Response Agent")
    st.markdown("---")
    st.caption("Prototype only: recommendations are not sent to a real IT system.")

# ----------------------------- Header ----------------------------------
st.markdown("""
<div class="hero">
  <div class="eyebrow">AI Operations · Helpdesk Automation</div>
  <h1>🤖 Agentic AI Studio</h1>
  <p>Turn IT complaints into prioritized, actionable support guidance — with a workflow you can inspect.</p>
</div>
""", unsafe_allow_html=True)

total = len(st.session_state.tickets)
high = sum(1 for t in st.session_state.tickets if t["priority"] == "High")
open_count = total  # All items are recommendations; no real ticket closure is performed.
m1, m2, m3, m4 = st.columns(4)
for col, label, value, sub in [
    (m1, "Tickets analyzed", total, "This session"),
    (m2, "High priority", high, "Needs faster review"),
    (m3, "Workflow agents", "05", "Coordinated stages"),
    (m4, "Mode", "AI" if api_key else "DEMO", "Analysis engine"),
]:
    with col:
        st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-sub">{sub}</div></div>', unsafe_allow_html=True)

# ----------------------------- Workflow UI -----------------------------
st.markdown('<div class="section-title">01 / Interactive agent workflow</div>', unsafe_allow_html=True)
st.caption("Submit a support request to run each stage and inspect its output.")
agent_cols = st.columns(5)
agent_specs = [
    ("🎫", "TICKET INTAKE", "Capture the request"),
    ("🔍", "CLASSIFICATION", "Identify issue type"),
    ("🚦", "PRIORITY", "Assess urgency"),
    ("🧠", "RESOLUTION", "Recommend next steps"),
    ("✉️", "RESPONSE", "Draft a reply"),
]
workflow_complete = st.session_state.latest_ticket is not None
for col, (icon, name, desc) in zip(agent_cols, agent_specs):
    with col:
        state = "✓ COMPLETED" if workflow_complete else "○ WAITING"
        card_class = "agent-card agent-done" if workflow_complete else "agent-card"
        st.markdown(
            f'<div class="{card_class}"><div class="agent-icon">{icon}</div>'
            f'<div class="agent-name">{name}</div><div class="agent-desc">{desc}</div>'
            f'<div class="agent-state">{state}</div></div>',
            unsafe_allow_html=True
        )

left, right = st.columns([1.05, 0.95], gap="large")
with left:
    st.markdown('<div class="section-title">02 / Submit an IT request</div>', unsafe_allow_html=True)
    with st.form("ticket_form", clear_on_submit=False):
        complaint = st.text_area(
            "Describe the technical issue",
            placeholder="Example: My Wi-Fi stopped working and I have an online exam in 10 minutes...",
            height=145,
            help="Do not enter passwords, one-time codes, or sensitive personal information."
        )
        c1, c2 = st.columns(2)
        with c1:
            urgency = st.selectbox("How soon is help needed?", ["Whenever possible", "Soon", "Critical"])
        with c2:
            impact = st.selectbox("Who is affected?", ["Only me", "My work is blocked", "Many users"])
        submitted = st.form_submit_button("▶  ANALYZE SUPPORT REQUEST", type="primary", use_container_width=True)
    st.markdown('<p class="small-muted">Try a sample below to see the workflow in action.</p>', unsafe_allow_html=True)
    sample_cols = st.columns(3)
    samples = [
        ("📶 Wi-Fi", "My Wi-Fi is not working and I have an online exam in 10 minutes.", "Critical", "My work is blocked"),
        ("🔐 Login", "I forgot my college account password and cannot log in.", "Soon", "Only me"),
        ("🖨️ Printer", "The office printer is showing an error and several staff cannot print.", "Soon", "Many users"),
    ]
    for col, (label, text, urg, imp) in zip(sample_cols, samples):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.sample_complaint = text
                st.session_state.sample_urgency = urg
                st.session_state.sample_impact = imp
                st.rerun()

    # Sample buttons populate the form on the next rerun through session state.
    # The form values are assigned below by using defaults on the next render.
with right:
    st.markdown('<div class="section-title">03 / What this system does</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="panel">
      <h3 style="margin-top:0">From complaint to next action</h3>
      <p class="small-muted">The workflow organizes a support request into a consistent, reviewable result.</p>
      <hr style="border-color:#2a3b58">
      <p>🧭 <b>Understand</b><br><span class="small-muted">Identify the type of issue.</span></p>
      <p>🚦 <b>Prioritize</b><br><span class="small-muted">Use urgency and impact to flag requests.</span></p>
      <p>🛠️ <b>Recommend</b><br><span class="small-muted">Suggest safe troubleshooting steps.</span></p>
      <p>✉️ <b>Communicate</b><br><span class="small-muted">Draft a reply for staff to review.</span></p>
      <hr style="border-color:#2a3b58">
      <p class="small-muted">The app does not access real devices, reset accounts, or create tickets in an external helpdesk.</p>
    </div>
    """, unsafe_allow_html=True)

# Make sample selection usable by copying it into the input area through a separate explicit button.
if "sample_complaint" in st.session_state:
    st.info("Sample selected. Copy the sample text into the complaint box above, or click the button below to analyze it directly.")
    if st.button("Run selected sample", type="primary"):
        sample_result, sample_mode = analyze_ticket(
            st.session_state.sample_complaint,
            st.session_state.sample_urgency,
            st.session_state.sample_impact,
            api_key
        )
        sample_ticket = {
            "id": safe_ticket_id(),
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "complaint": st.session_state.sample_complaint,
            "urgency": st.session_state.sample_urgency,
            "impact": st.session_state.sample_impact,
            "category": sample_result["category"],
            "priority": sample_result["priority"],
            "summary": sample_result["summary"],
            "resolution": sample_result["resolution"],
            "reply": sample_result["reply"],
            "escalation": sample_result["escalation"],
            "mode": sample_mode,
        }
        st.session_state.tickets.insert(0, sample_ticket)
        st.session_state.latest_ticket = sample_ticket
        del st.session_state.sample_complaint
        del st.session_state.sample_urgency
        del st.session_state.sample_impact
        st.rerun()

if submitted:
    if not complaint.strip():
        st.warning("Please describe the issue before running the workflow.")
    else:
        with st.status("Running the agent workflow...", expanded=True) as status:
            st.write("🎫 Ticket Intake Agent — capturing the request")
            ticket_id = safe_ticket_id()
            st.write("🔍 Classification and Priority Agents — analyzing issue type and impact")
            st.write("🧠 Resolution Agent — preparing troubleshooting guidance")
            result, mode_used = analyze_ticket(complaint.strip(), urgency, impact, api_key.strip())
            st.write("✉️ Response Agent — drafting a reply for staff review")
            status.update(label="Workflow complete", state="complete", expanded=False)
        ticket = {
            "id": ticket_id,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "complaint": complaint.strip(),
            "urgency": urgency,
            "impact": impact,
            "category": result["category"],
            "priority": result["priority"],
            "summary": result["summary"],
            "resolution": result["resolution"],
            "reply": result["reply"],
            "escalation": result["escalation"],
            "mode": mode_used,
        }
        st.session_state.tickets.insert(0, ticket)
        st.session_state.latest_ticket = ticket

# ----------------------------- Results ----------------------------------
ticket = st.session_state.latest_ticket
if ticket:
    st.markdown('<div class="section-title">04 / Analysis result</div>', unsafe_allow_html=True)
    p1, p2, p3 = st.columns([1, 1, 2])
    p1.metric("Ticket ID", ticket["id"])
    p2.metric("Priority", ticket["priority"])
    p3.metric("Category", ticket["category"])
    if ticket["priority"] == "High":
        st.error("High priority: review promptly. This is a recommendation, not an automatic escalation.")
    elif ticket["priority"] == "Medium":
        st.warning("Medium priority: review and follow up.")
    else:
        st.success("Low priority: handle through the normal support queue.")

    a, b = st.columns([1, 1], gap="large")
    with a:
        with st.container(border=True):
            st.markdown("#### 🧠 Issue summary")
            st.write(ticket["summary"])
            st.markdown("#### 🛠️ Recommended troubleshooting")
            for i, step in enumerate(ticket["resolution"], 1):
                st.markdown(f"**{i}.** {step}")
            st.markdown("#### 🚨 Escalation guidance")
            st.write(ticket["escalation"])
    with b:
        with st.container(border=True):
            st.markdown("#### ✉️ Draft customer response")
            st.write(ticket["reply"])
            st.caption(f"Analysis mode: {ticket['mode']}")
            report = (
                "# Agentic AI Studio — IT Helpdesk Analysis\n\n"
                f"- **Ticket ID:** {ticket['id']}\n"
                f"- **Created:** {ticket['created']}\n"
                f"- **Category:** {ticket['category']}\n"
                f"- **Priority:** {ticket['priority']}\n"
                f"- **Urgency selected:** {ticket['urgency']}\n"
                f"- **Impact selected:** {ticket['impact']}\n"
                f"- **Analysis mode:** {ticket['mode']}\n\n"
                f"## Complaint\n{ticket['complaint']}\n\n"
                f"## Summary\n{ticket['summary']}\n\n"
                "## Recommended troubleshooting\n" +
                "\n".join(f"{i}. {step}" for i, step in enumerate(ticket["resolution"], 1)) +
                f"\n\n## Escalation guidance\n{ticket['escalation']}\n\n"
                f"## Draft response\n{ticket['reply']}\n"
            )
            st.download_button("⬇ Download ticket report (.md)", data=report, file_name=f"{ticket['id']}.md", mime="text/markdown", use_container_width=True)

    with st.expander("🔎 View agent results", expanded=False):
        st.caption("Each stage's output from this request.")
        with st.container(border=True):
            st.markdown("**🎫 1. Ticket Intake Agent** · Completed")
            st.write(f"Captured complaint: {ticket['complaint']}")
            st.caption(f"Urgency: {ticket['urgency']} · Impact: {ticket['impact']} · Ticket: {ticket['id']}")
        with st.container(border=True):
            st.markdown("**🔍 2. Classification Agent** · Completed")
            st.write(f"Category: {ticket['category']}")
            st.write(f"Summary: {ticket['summary']}")
        with st.container(border=True):
            st.markdown("**🚦 3. Priority Agent** · Completed")
            st.write(f"Recommended priority: {ticket['priority']}")
        with st.container(border=True):
            st.markdown("**🧠 4. Resolution Agent** · Completed")
            for i, step in enumerate(ticket["resolution"], 1):
                st.write(f"{i}. {step}")
            st.write(f"Escalation: {ticket['escalation']}")
        with st.container(border=True):
            st.markdown("**✉️ 5. Response Agent** · Completed")
            st.write(ticket["reply"])

# ----------------------------- History ----------------------------------
st.markdown('<div class="section-title">05 / Recent ticket history</div>', unsafe_allow_html=True)
if st.session_state.tickets:
    rows = [{
        "Ticket ID": t["id"],
        "Time": t["created"],
        "Category": t["category"],
        "Priority": t["priority"],
        "Complaint": t["complaint"][:75] + ("…" if len(t["complaint"]) > 75 else ""),
        "Mode": t["mode"],
    } for t in st.session_state.tickets]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    csv_lines = ["Ticket ID,Time,Category,Priority,Complaint,Mode"]
    for row in rows:
        vals = [str(row[k]).replace('"', '""') for k in ["Ticket ID", "Time", "Category", "Priority", "Complaint", "Mode"]]
        csv_lines.append(",".join(f'"{v}"' for v in vals))
    st.download_button("⬇ Export ticket history (.csv)", data="\n".join(csv_lines), file_name="it_helpdesk_history.csv", mime="text/csv")
    if st.button("Clear session history"):
        st.session_state.tickets = []
        st.session_state.latest_ticket = None
        st.rerun()
else:
    st.markdown('<div class="panel"><b>No tickets analyzed yet</b><p class="small-muted">Submit a request or choose a sample to populate the dashboard and history.</p></div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;color:#8092b1;font-size:.78rem;margin-top:2rem;padding-top:1rem;border-top:1px solid #24334e">
Agentic AI Studio · Educational prototype · Review AI recommendations before acting
</div>
""", unsafe_allow_html=True)
