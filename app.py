import os
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="AURA | Agentic AI Studio", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root { --bg:#0b1020; --panel:#111a2e; --line:#263653; --muted:#9aabc6; --text:#edf3ff; --blue:#6c8cff; --green:#43d9a3; --amber:#ffc76a; }
.stApp { background: radial-gradient(ellipse at 70% 0%, #172746 0%, #0b1020 48%); color:var(--text); }
.block-container { max-width: 1450px; padding-top: 1.6rem; padding-bottom: 3rem; }
h1,h2,h3,p,div,label { color: inherit; }
[data-testid="stSidebar"] { background: #0d1527; border-right:1px solid #263653; }
[data-testid="stSidebar"] * { color:#e7efff; }
.hero { padding: 1.4rem 1.6rem; border:1px solid #2a3b5c; border-radius:22px; background:linear-gradient(120deg,rgba(31,50,88,.95),rgba(17,26,46,.92)); margin-bottom:1.25rem; }
.eyebrow { font-size:.76rem; text-transform:uppercase; letter-spacing:.18em; color:#8fa9ff; font-weight:800; }
.hero h1 { margin:.3rem 0; font-size:2.2rem; color:#f6f8ff; }
.hero p { margin:.25rem 0 0; color:#aebed8; }
.metric { background:rgba(17,26,46,.88); border:1px solid #263653; border-radius:16px; padding:1rem 1.1rem; min-height:95px; }
.metric-label { color:#94a8c7; font-size:.78rem; text-transform:uppercase; letter-spacing:.09em; }
.metric-value { font-size:1.35rem; font-weight:800; color:#f4f7ff; margin-top:.25rem; }
.section-title { font-size:1.18rem; font-weight:800; margin:.7rem 0 .85rem; color:#f1f5ff; }
.node { border:1px solid #2a3b5c; background:#121d32; border-radius:15px; padding:1rem .75rem; text-align:center; min-height:110px; }
.node-active { border:1px solid #7b9aff; background:linear-gradient(145deg,#203b6c,#172642); box-shadow:0 0 0 1px rgba(108,140,255,.25),0 8px 28px rgba(45,90,200,.13); }
.node-done { border:1px solid #2b8f73; background:linear-gradient(145deg,#12382f,#132a2a); }
.node-icon { font-size:1.5rem; margin-bottom:.3rem; }
.node-name { font-size:.82rem; font-weight:800; color:#f4f7ff; }
.node-desc { font-size:.72rem; color:#9fb0ca; margin-top:.25rem; }
.node-state { font-size:.67rem; color:#7f9cff; margin-top:.5rem; font-weight:800; text-transform:uppercase; letter-spacing:.07em; }
.node-done .node-state { color:#52e0b1; }
.arrow { text-align:center; color:#7286ad; font-size:1.4rem; padding:.1rem 0; }
.panel { border:1px solid #263653; border-radius:16px; background:rgba(17,26,46,.82); padding:1rem 1.1rem; }
.logline { border-left:2px solid #39527c; padding:.15rem 0 .5rem .8rem; margin-left:.25rem; color:#b8c7df; font-size:.87rem; }
.pill { display:inline-block; border:1px solid #35507b; background:#152642; color:#a9c0ff; padding:.2rem .55rem; border-radius:99px; font-size:.72rem; margin-right:.3rem; }
div.stButton > button[kind="primary"] { border:0; border-radius:10px; background:linear-gradient(90deg,#6284ff,#8b74ff); color:white; font-weight:800; min-height:3rem; }
div.stDownloadButton > button { border-radius:9px; }
[data-testid="stExpander"] { border:1px solid #263653; border-radius:12px; background:rgba(17,26,46,.45); }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ◈ Agentic Studio")
    st.caption("Agentic workflow console")
    st.markdown("---")
    api_key = st.text_input("Gemini API key", value=os.getenv("GEMINI_API_KEY", ""), type="password", help="Optional. Enables live AI planning, analysis and report generation.")
    mode = "LIVE AI" if api_key else "DEMO MODE"
    st.markdown(f'<span class="pill">{mode}</span>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**SYSTEM COMPONENTS**")
    st.markdown("🧭 Planner Agent")
    st.markdown("🔎 Web Search Tool")
    st.markdown("🧠 Analysis Agent")
    st.markdown("📝 Report Generator")
    st.markdown("---")
    st.caption("A bounded educational prototype. Verify important claims from original sources.")

st.markdown("""
<div class="hero">
  <div class="eyebrow">Autonomous workflow • Research operations</div>
  <h1>◈  <span style="color:#8fa9ff">Agentic AI Studio</span></h1>
  <p>Turn a goal into a plan, invoke tools, synthesize evidence, and deliver a report.</p>
</div>
""", unsafe_allow_html=True)

task = st.text_area("MISSION / TASK INPUT", value="Research five applications of AI in healthcare, explain their benefits and challenges, and generate a concise report with sources.", height=90, label_visibility="visible")
c1, c2 = st.columns([4,1])
with c1:
    st.caption("Tip: use a clear task with a topic, desired analysis, and output.")
with c2:
    run = st.button("▶  RUN WORKFLOW", type="primary", use_container_width=True)

def gemini(key, prompt):
    from google import genai
    client = genai.Client(api_key=key)
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return (response.text or "").strip()

def search_web(query, limit=6):
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS
    with DDGS() as ddgs:
        rows = list(ddgs.text(query, max_results=limit))
    return [{"title": r.get("title", "Untitled"), "url": r.get("href", r.get("url", "")), "snippet": r.get("body", r.get("snippet", ""))} for r in rows]

st.markdown('<div class="section-title">01 / Workflow orchestration</div>', unsafe_allow_html=True)
st.caption("Each card represents a stage in the task execution pipeline.")
nodes = [
    ("🎯","MISSION","User goal"),
    ("🧭","PLANNER","Task decomposition"),
    ("🔎","RESEARCH TOOL","Web evidence"),
    ("🧠","ANALYST","Synthesis"),
    ("📝","REPORT AGENT","Final deliverable"),
]
node_cols = st.columns(5)
node_placeholders = []
for col, node in zip(node_cols, nodes):
    with col:
        ph = st.empty()
        node_placeholders.append(ph)

def draw_nodes(active=-1, done=()):
    for i, (icon, name, desc) in enumerate(nodes):
        state = "DONE" if i in done else ("RUNNING" if i == active else "WAITING")
        klass = "node-done" if i in done else ("node-active" if i == active else "node")
        node_placeholders[i].markdown(
            f'<div class="node {klass}"><div class="node-icon">{icon}</div><div class="node-name">{name}</div><div class="node-desc">{desc}</div><div class="node-state">{state}</div></div>',
            unsafe_allow_html=True
        )
draw_nodes()

# Connector strip between cards.
st.markdown('<div style="text-align:center;color:#6d83ac;letter-spacing:.45em;margin:.45rem 0 1.1rem">● ━━━━━ ▶ ━━━━━ ▶ ━━━━━ ▶ ━━━━━ ▶</div>', unsafe_allow_html=True)

metric_cols = st.columns(4)
metric_specs = [("WORKFLOW STATUS","Ready"),("AGENT STAGES","05"),("TOOLS","01"),("OUTPUT","Markdown report")]
for col, (label, value) in zip(metric_cols, metric_specs):
    col.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

if run:
    if not task.strip():
        st.warning("Enter a task before running the workflow.")
        st.stop()

    st.markdown('<div class="section-title">02 / Live execution console</div>', unsafe_allow_html=True)
    status = st.empty()
    progress = st.progress(0)
    log_panel = st.container()
    results = []
    completed = [0]
    run_started = datetime.now()

    def log_event(tag, message):
        with log_panel:
            st.markdown(f'<div class="logline"><b style="color:#90aaff">{datetime.now().strftime("%H:%M:%S")} · {tag}</b><br>{message}</div>', unsafe_allow_html=True)

    # Planner
    draw_nodes(active=1, done=[0])
    status.info("Planner Agent is decomposing the mission…")
    log_event("PLANNER", "Reading task and preparing an execution plan.")
    try:
        if api_key:
            plan = gemini(api_key, "You are a planning agent. Break the task into 4-6 executable steps. Return a concise numbered list. Do not claim actions have already occurred.\nTask: " + task)
        else:
            plan = "1. Parse the user's goal and expected output.\n2. Search public web results for relevant information.\n3. Inspect and compare the retrieved snippets.\n4. Summarize benefits, challenges, and uncertainty.\n5. Produce a structured report with source URLs."
        completed.append(1)
        log_event("PLAN CREATED", "Execution plan prepared.")
        with st.expander("Inspect planner output", expanded=True):
            st.markdown(plan)
        progress.progress(20)
    except Exception as e:
        st.error(f"Planner failed: {e}")
        st.stop()

    # Search
    draw_nodes(active=2, done=completed)
    status.info("Research tool is retrieving public web results…")
    query = task.strip()
    log_event("TOOL CALL", f"Invoking web search with query: `{query}`")
    try:
        results = search_web(query, limit=6)
        log_event("TOOL RESULT", f"Retrieved {len(results)} search result(s).")
        completed.append(2)
    except Exception as e:
        results = []
        log_event("TOOL ERROR", f"Search could not complete: {e}")
        st.warning(f"Web search unavailable: {e}")
        completed.append(2)
    with st.expander(f"Inspect research tool output · {len(results)} source(s)", expanded=True):
        if results:
            for i, r in enumerate(results, 1):
                st.markdown(f"**{i}. {r['title']}**")
                if r["url"]:
                    st.markdown(r["url"])
                st.write(r["snippet"])
                st.markdown("---")
        else:
            st.write("No results were returned. Check internet access or try a shorter query.")
    progress.progress(45)

    source_text = "\n\n".join(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}" for r in results) or "No web results available."

    # Analysis
    draw_nodes(active=3, done=completed)
    status.info("Analysis Agent is evaluating retrieved evidence…")
    log_event("ANALYSIS", "Passing search snippets to the analysis stage.")
    try:
        if api_key:
            analysis = gemini(api_key, "You are an evidence analysis agent. Use supplied snippets carefully; do not invent facts. Return key findings, benefits, challenges, and claims needing verification.\nTASK:\n" + task + "\n\nSOURCES:\n" + source_text)
        else:
            analysis = "Demo mode: sources have been retrieved, but live AI synthesis is disabled. Add a Gemini API key to enable model-based analysis. Use the source panel to inspect the retrieved evidence."
        completed.append(3)
        with st.expander("Inspect analysis output", expanded=True):
            st.write(analysis)
        log_event("ANALYSIS COMPLETE", "Analysis stage finished.")
        progress.progress(70)
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        st.stop()

    # Report
    draw_nodes(active=4, done=completed)
    status.info("Report Agent is assembling the final deliverable…")
    log_event("REPORT", "Generating the final structured report.")
    try:
        if api_key:
            report = gemini(api_key, "Write a concise, clear report for the task. Include executive summary, findings, benefits, challenges, conclusion, and source list. Only cite URLs in the supplied search results; flag uncertainty. Do not invent citations.\nTASK:\n" + task + "\n\nANALYSIS:\n" + analysis + "\n\nSOURCES:\n" + source_text)
        else:
            parts = ["# Agentic AI Workflow Report", "", f"**Task:** {task}", f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}", "", "## Workflow summary", "The planner prepared execution steps, the research tool collected available web snippets, and the report stage organized the retrieved material.", "", "## Retrieved findings"]
            for i, r in enumerate(results, 1):
                parts += [f"### {i}. {r['title']}", r["snippet"], f"Source: {r['url']}", ""]
            parts += ["## Limitations", "- Demo mode does not perform AI synthesis without an API key.", "- Search snippets can be incomplete; verify important claims on original pages."]
            report = "\n".join(parts)
        completed.append(4)
        log_event("SUCCESS", "Report generated. Workflow execution finished.")
        progress.progress(100)
        draw_nodes(active=-1, done=completed)
        status.success(f"Mission completed in {(datetime.now()-run_started).seconds} seconds.")
    except Exception as e:
        st.error(f"Report generation failed: {e}")
        st.stop()

    st.markdown('<div class="section-title">03 / Deliverable</div>', unsafe_allow_html=True)
    left, right = st.columns([3,1])
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(report)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><b>Run details</b><br><br>Mode: '+("Live Gemini AI" if api_key else "Demo mode")+f'<br><br>Sources: {len(results)}<br><br>Stages: {len(completed)}/5</div>', unsafe_allow_html=True)
        st.download_button("⬇ Download report", data=report, file_name="aura_agentic_report.md", mime="text/markdown", use_container_width=True)
else:
    st.markdown('<div class="panel"><b style="color:#eaf0ff">Ready to execute</b><p style="color:#9aabc6;margin:.4rem 0 0">Enter a mission above and run the workflow. During execution, the node cards, status log, evidence panel, and report update with actual stage outputs.</p></div>', unsafe_allow_html=True)


