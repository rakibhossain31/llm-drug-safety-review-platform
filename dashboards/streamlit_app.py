from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from typing import Any

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
PROJECT_ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(
    page_title="LLM Drug Safety Review Fellowship Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# Visual system
# -----------------------------------------------------------------------------
# Design direction: modern clinical / life-sciences SaaS. The palette avoids
# aggressive medical red/green defaults and uses navy + cobalt + teal with
# amber reserved for safety notices. The font stack stays local/system-safe.
st.markdown(
    """
    <style>
    :root {
        --ink-950: #0B1220;
        --ink-900: #111827;
        --ink-700: #344054;
        --ink-500: #667085;
        --line: #E4E7EC;
        --surface: #FFFFFF;
        --surface-2: #F8FAFC;
        --canvas: #F5F7FB;
        --blue: #2563EB;
        --blue-50: #EFF6FF;
        --teal: #0F9F8F;
        --teal-50: #ECFDF8;
        --amber: #B7791F;
        --amber-50: #FFFAEB;
        --red: #C2414B;
        --red-50: #FFF1F2;
        --green: #16855B;
        --green-50: #ECFDF3;
        --shadow-sm: 0 1px 2px rgba(16, 24, 40, .04), 0 1px 3px rgba(16, 24, 40, .06);
        --shadow-md: 0 8px 24px rgba(16, 24, 40, .07);
        --radius: 16px;
    }

    html, body, [class*="css"] {
        font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: var(--ink-900);
    }

    .stApp { background: var(--canvas); }
    .block-container {
        max-width: 1480px;
        padding-top: 1.4rem;
        padding-bottom: 4rem;
    }

    /* Reduce Streamlit chrome without breaking functionality. */
    [data-testid="stHeader"] { background: rgba(245,247,251,.86); }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Hero */
    .pv-hero {
        background: linear-gradient(120deg, #0B1220 0%, #12284C 62%, #123C4A 100%);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 22px;
        padding: 26px 30px;
        box-shadow: var(--shadow-md);
        margin-bottom: 14px;
        position: relative;
        overflow: hidden;
    }
    .pv-hero:after {
        content: "";
        position: absolute;
        right: -80px;
        top: -120px;
        width: 320px;
        height: 320px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(45,212,191,.20), rgba(37,99,235,0));
    }
    .pv-eyebrow {
        color: #93C5FD;
        letter-spacing: .11em;
        text-transform: uppercase;
        font-size: .73rem;
        font-weight: 800;
        margin-bottom: 8px;
    }
    .pv-hero h1 {
        color: white !important;
        font-size: clamp(1.75rem, 2.6vw, 2.55rem) !important;
        letter-spacing: -.035em;
        line-height: 1.05;
        margin: 0 0 8px 0 !important;
        font-weight: 760;
    }
    .pv-hero p {
        color: #CBD5E1;
        max-width: 860px;
        font-size: .96rem;
        line-height: 1.6;
        margin: 0;
    }
    .pv-status-row { margin-top: 16px; display: flex; flex-wrap: wrap; gap: 8px; }
    .pv-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,.15);
        background: rgba(255,255,255,.07);
        color: #E2E8F0;
        font-size: .78rem;
        font-weight: 650;
    }
    .pv-dot { width: 7px; height: 7px; border-radius: 99px; background: #2DD4BF; box-shadow: 0 0 0 3px rgba(45,212,191,.12); }
    .pv-dot.offline { background: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,.12); }

    /* Safety banner */
    .pv-safety {
        display: flex;
        gap: 12px;
        align-items: flex-start;
        padding: 12px 15px;
        border: 1px solid #F2D39B;
        background: var(--amber-50);
        color: #7A4B0D;
        border-radius: 13px;
        margin: 0 0 18px 0;
        font-size: .88rem;
        line-height: 1.45;
    }
    .pv-safety strong { color: #633C08; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #EEF2F7;
        padding: 5px;
        border-radius: 14px;
        margin-bottom: 16px;
        overflow-x: auto;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 10px;
        padding: 0 15px;
        color: var(--ink-700);
        font-weight: 650;
        border: 0;
        white-space: nowrap;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: var(--ink-950) !important;
        box-shadow: var(--shadow-sm);
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }

    /* Section header */
    .pv-section { margin: 3px 0 16px 0; }
    .pv-section .kicker {
        color: var(--blue);
        text-transform: uppercase;
        letter-spacing: .09em;
        font-size: .71rem;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .pv-section h2 {
        margin: 0 !important;
        font-size: 1.52rem !important;
        letter-spacing: -.025em;
        color: var(--ink-950) !important;
    }
    .pv-section p { color: var(--ink-500); margin: 6px 0 0 0; line-height: 1.55; font-size: .91rem; }

    /* Cards */
    .pv-card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: var(--radius);
        padding: 18px 20px;
        box-shadow: var(--shadow-sm);
    }
    .pv-card + .pv-card { margin-top: 12px; }
    .pv-card-label {
        color: var(--ink-500);
        font-size: .75rem;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: .075em;
        margin-bottom: 8px;
    }
    .pv-answer {
        color: var(--ink-900);
        font-size: 1rem;
        line-height: 1.75;
        margin: 0;
    }
    .pv-caption { color: var(--ink-500); font-size: .78rem; line-height: 1.45; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 15px 17px;
        box-shadow: var(--shadow-sm);
    }
    [data-testid="stMetricLabel"] { color: var(--ink-500); font-weight: 650; }
    [data-testid="stMetricValue"] { color: var(--ink-950); font-weight: 760; letter-spacing: -.025em; }

    /* Inputs */
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,
    [data-baseweb="select"] > div {
        background: #FFFFFF !important;
        border-color: #D0D5DD !important;
        border-radius: 11px !important;
    }
    textarea { line-height: 1.55 !important; }
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label,
    [data-testid="stSelectbox"] label {
        color: var(--ink-700) !important;
        font-weight: 650 !important;
    }

    /* Buttons */
    .stButton > button {
        min-height: 42px;
        border-radius: 11px;
        font-weight: 700;
        border: 1px solid #D0D5DD;
        box-shadow: 0 1px 2px rgba(16,24,40,.04);
        transition: transform .12s ease, box-shadow .12s ease;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(16,24,40,.08); }
    .stButton > button[kind="primary"] {
        background: var(--blue);
        border-color: var(--blue);
    }

    /* Progress */
    [data-testid="stProgress"] > div > div > div { background: linear-gradient(90deg, #2563EB, #0F9F8F); }

    /* Dataframes / expanders */
    [data-testid="stDataFrame"], [data-testid="stExpander"] {
        border-radius: 14px;
        overflow: hidden;
    }
    [data-testid="stExpander"] {
        background: #FFFFFF;
        border: 1px solid var(--line);
    }

    /* Evidence cards */
    .pv-source {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 13px;
        padding: 14px 15px;
        min-height: 122px;
        box-shadow: var(--shadow-sm);
    }
    .pv-source-top { display: flex; justify-content: space-between; gap: 8px; align-items: center; margin-bottom: 9px; }
    .pv-source-name { color: var(--ink-950); font-size: .88rem; font-weight: 750; overflow-wrap: anywhere; }
    .pv-source-score { color: var(--teal); font-weight: 800; font-size: .78rem; background: var(--teal-50); padding: 4px 7px; border-radius: 999px; }
    .pv-source-meta { color: var(--ink-500); font-size: .75rem; line-height: 1.5; }

    /* Status chips */
    .pv-chip {
        display: inline-block;
        border-radius: 999px;
        padding: 5px 9px;
        font-size: .76rem;
        font-weight: 750;
        line-height: 1;
    }
    .chip-blue { color: #1D4ED8; background: #EFF6FF; border: 1px solid #BFDBFE; }
    .chip-green { color: #067647; background: #ECFDF3; border: 1px solid #ABEFC6; }
    .chip-amber { color: #92400E; background: #FFFAEB; border: 1px solid #FEDF89; }
    .chip-red { color: #B42318; background: #FFF1F2; border: 1px solid #FECDD3; }
    .chip-gray { color: #475467; background: #F2F4F7; border: 1px solid #E4E7EC; }

    /* Review narrative */
    .pv-narrative {
        background: linear-gradient(180deg, #FFFFFF 0%, #FBFCFE 100%);
        border: 1px solid var(--line);
        border-left: 4px solid var(--blue);
        border-radius: 14px;
        padding: 18px 20px;
        color: var(--ink-900);
        line-height: 1.72;
        font-size: .96rem;
        box-shadow: var(--shadow-sm);
    }

    /* Small responsive improvement */
    @media (max-width: 900px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        .pv-hero { padding: 22px 20px; border-radius: 18px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_post(path: str, payload: dict):
    response = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def api_get(path: str):
    response = requests.get(f"{API_BASE_URL}{path}", timeout=60)
    response.raise_for_status()
    return response.json()


def load_jsonl(relative: str) -> list[dict]:
    path = PROJECT_ROOT / relative
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def section_header(kicker: str, title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="pv-section">
          <div class="kicker">{html.escape(kicker)}</div>
          <h2>{html.escape(title)}</h2>
          <p>{html.escape(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def clean_markdown_text(text: str) -> str:
    """Remove source-document Markdown chrome while preserving readable prose."""
    cleaned_lines: list[str] = []
    for raw in text.splitlines():
        line = re.sub(r"^\s*#{1,6}\s*", "", raw).strip()
        line = re.sub(r"^[-*]\s+", "", line)
        if not line:
            continue
        cleaned_lines.append(line)
    return " ".join(cleaned_lines)


def render_text_card(label: str, text: str, css_class: str = "pv-answer") -> None:
    st.markdown(
        f"""
        <div class="pv-card">
          <div class="pv-card-label">{html.escape(label)}</div>
          <div class="{css_class}">{html.escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chip(label: str, tone: str = "gray") -> str:
    return f'<span class="pv-chip chip-{tone}">{html.escape(str(label))}</span>'


def score_percent(value: Any) -> float:
    try:
        raw = float(value)
    except (TypeError, ValueError):
        return 0.0
    # Scores in this app are normally 0..1. Keep UI robust to percentages too.
    return max(0.0, min(100.0, raw * 100 if raw <= 1 else raw))


def render_sources(citations: list[dict]) -> None:
    if not citations:
        st.info("No retrieval sources were returned for this answer.")
        return
    cols = st.columns(min(3, len(citations)))
    for idx, citation in enumerate(citations):
        source = str(citation.get("source", "Unknown source"))
        chunk_id = str(citation.get("chunk_id", "n/a"))
        pct = score_percent(citation.get("score"))
        with cols[idx % len(cols)]:
            st.markdown(
                f"""
                <div class="pv-source">
                  <div class="pv-source-top">
                    <div class="pv-source-name">📄 {html.escape(source)}</div>
                    <div class="pv-source-score">{pct:.1f}% match</div>
                  </div>
                  <div class="pv-source-meta">
                    Evidence chunk<br><strong>{html.escape(chunk_id)}</strong>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_api_state() -> bool:
    try:
        health = api_get("/health")
        service = str(health.get("service", "FastAPI backend"))
        state = "online"
        dot = "pv-dot"
        detail = f"{service} · localhost"
        online = True
    except Exception:
        state = "backend offline"
        dot = "pv-dot offline"
        detail = "Start FastAPI on port 8000"
        online = False

    st.markdown(
        f"""
        <div class="pv-hero">
          <div class="pv-eyebrow">Fellowship platform · Pharmacovigilance intelligence workspace</div>
          <h1>LLM Drug Safety Review</h1>
          <p>Evidence-grounded review support for synthetic ICSR triage, PV guidance retrieval, literature screening, benchmark evaluation, and governed human approval.</p>
          <div class="pv-status-row">
            <span class="pv-pill"><span class="{dot}"></span>{html.escape(state.title())}</span>
            <span class="pv-pill">Synthetic data only</span>
            <span class="pv-pill">Human-in-the-loop</span>
            <span class="pv-pill">{html.escape(detail)}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return online


# -----------------------------------------------------------------------------
# Application shell
# -----------------------------------------------------------------------------
backend_online = render_api_state()

st.markdown(
    """
    <div class="pv-safety">
      <div>⚠️</div>
      <div><strong>Review-support environment.</strong> Synthetic educational data only. Outputs are not medical or regulatory advice and never constitute a final pharmacovigilance decision. Human reviewer approval required.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not backend_online:
    st.warning("The dashboard is open, but FastAPI is not reachable. In VS Code, run `uvicorn safetyreview_ai.api.main:app --reload` in the backend terminal.")


tabs = st.tabs([
    "Safety Case",
    "PV Guidance",
    "Duplicates",
    "Literature",
    "Benchmark Lab",
    "Monitoring",
    "Review Queue",
])

# -----------------------------------------------------------------------------
# Safety case review
# -----------------------------------------------------------------------------
with tabs[0]:
    section_header(
        "Case intelligence",
        "Review a synthetic safety case",
        "Run the governed review graph and inspect extracted entities, minimum-case validity, seriousness, expectedness, coding support, duplicates, follow-up needs, and the reviewer narrative.",
    )

    cases = load_jsonl("data/cases/synthetic_icsr_cases.jsonl")
    selected = st.selectbox("Synthetic example", ["Custom"] + [c["case_id"] for c in cases])
    default = "" if selected == "Custom" else next(c["narrative"] for c in cases if c["case_id"] == selected)
    narrative = st.text_area(
        "Case narrative",
        value=default,
        height=190,
        placeholder="Paste or write a synthetic safety narrative here. Do not use real patient data.",
    )

    if st.button("Run safety review", type="primary", use_container_width=False) and narrative:
        try:
            with st.spinner("Running the safety review graph…"):
                result = api_post(
                    "/cases/review",
                    {"narrative": narrative, "case_id": None if selected == "Custom" else selected},
                )

            status = result.get("status", "needs_review")
            tone = "amber" if status == "needs_review" else "green"
            st.markdown(
                f"<div style='margin:4px 0 12px 0'>{render_chip(status.replace('_', ' ').title(), tone)}</div>",
                unsafe_allow_html=True,
            )

            st.markdown("<div class='pv-card-label'>Reviewer narrative</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='pv-narrative'>{html.escape(str(result['reviewer_narrative']))}</div>",
                unsafe_allow_html=True,
            )

            st.write("")
            c1, c2, c3, c4 = st.columns(4)
            valid = bool(result["minimum_valid_case"]["is_valid"])
            serious = bool(result["seriousness"]["is_serious"])
            expected = str(result["expectedness"]["classification"])
            c1.metric("Minimum valid case", "Valid" if valid else "Incomplete")
            c2.metric("Seriousness", "Serious" if serious else "Non-serious")
            c3.metric("Expectedness", expected.title())
            c4.metric("Workflow status", status.replace("_", " ").title())

            with st.expander("Structured review evidence", expanded=False):
                st.caption("Machine-readable output for auditability and downstream integration.")
                st.json(result)
        except Exception as exc:
            st.error(f"API request failed: {exc}. Start FastAPI first.")

# -----------------------------------------------------------------------------
# PV Guidance RAG
# -----------------------------------------------------------------------------
with tabs[1]:
    section_header(
        "Retrieval-augmented guidance",
        "Ask the pharmacovigilance knowledge base",
        "Retrieve the most relevant synthetic PV guidance chunks, answer from that evidence, and inspect transparent source-level retrieval signals.",
    )

    question = st.text_input(
        "Reviewer question",
        "What are the four elements of a minimum valid safety case?",
        placeholder="Ask a question about minimum case criteria, seriousness, follow-up, or duplicate review…",
    )

    qcol, _ = st.columns([1, 4])
    ask_clicked = qcol.button("Ask guidance", type="primary", use_container_width=True)

    if ask_clicked and question.strip():
        try:
            with st.spinner("Retrieving guidance and grounding the response…"):
                result = api_post("/guidance/ask", {"question": question, "top_k": 3})

            answer = clean_markdown_text(str(result.get("answer", "")))
            confidence = score_percent(result.get("confidence"))
            citations = list(result.get("citations") or [])

            render_text_card("Grounded answer", answer)

            st.write("")
            c1, c2, c3 = st.columns([1.15, 1, 2.2])
            c1.metric("Answer confidence", f"{confidence:.1f}%")
            c2.metric("Evidence sources", len(citations))
            with c3:
                st.caption("Confidence is a system heuristic. It is not a probability of clinical or regulatory correctness.")
                st.progress(min(max(confidence / 100.0, 0.0), 1.0))

            st.markdown("### Evidence used")
            st.caption("These are the retrieved knowledge-base chunks that grounded the answer. Retrieval match reflects query similarity, not clinical certainty.")
            render_sources(citations)

            with st.expander("Advanced retrieval trace", expanded=False):
                st.caption("Developer/audit metadata. Hidden by default so reviewers see evidence, not raw implementation details.")
                st.json({"question": question, "confidence": result.get("confidence"), "citations": citations})
        except Exception as exc:
            st.error(f"Guidance request failed: {exc}")

# -----------------------------------------------------------------------------
# Duplicate detection
# -----------------------------------------------------------------------------
with tabs[2]:
    section_header(
        "Case similarity",
        "Check for likely duplicates",
        "Compare a new synthetic narrative with prior synthetic ICSRs and rank likely matches using similarity evidence.",
    )
    duplicate_text = st.text_area(
        "Narrative to compare",
        height=170,
        placeholder="Enter a synthetic case narrative to compare with the case history…",
    )
    if st.button("Check duplicates", type="primary") and duplicate_text:
        try:
            with st.spinner("Comparing case similarity…"):
                duplicate_results = api_post("/duplicates/check", {"narrative": duplicate_text, "top_k": 5})
            st.dataframe(duplicate_results, use_container_width=True, hide_index=True)
            with st.expander("Raw duplicate-detection payload"):
                st.json(duplicate_results)
        except Exception as exc:
            st.error(str(exc))

# -----------------------------------------------------------------------------
# Literature review
# -----------------------------------------------------------------------------
with tabs[3]:
    section_header(
        "Literature intelligence",
        "Screen a synthetic safety abstract",
        "Compare rule-based, single-step, multi-step, and bounded-agentic review strategies against the same abstract.",
    )

    abstracts = load_jsonl("data/literature/synthetic_abstracts.jsonl")
    abstract_id = st.selectbox("Synthetic abstract", [a["abstract_id"] for a in abstracts])
    abstract = next(a for a in abstracts if a["abstract_id"] == abstract_id)
    abstract_text = st.text_area("Abstract", abstract["text"], height=170)

    c_arch, c_prompt = st.columns(2)
    with c_arch:
        architecture = st.selectbox("Review architecture", ["multi_step", "agentic", "single_step", "rule_based"])
    with c_prompt:
        prompt_id = st.selectbox(
            "Prompt strategy (single-step)",
            [
                "literature_evidence_first_v1",
                "literature_self_check_v1",
                "literature_few_shot_v1",
                "literature_zero_shot_v1",
            ],
        )

    c1, c2 = st.columns(2)
    if c1.button("Screen abstract", type="primary", use_container_width=True):
        try:
            result = api_post(
                "/literature/screen",
                {"abstract_id": abstract_id, "text": abstract_text, "architecture": architecture, "prompt_id": prompt_id},
            )
            m1, m2, m3 = st.columns(3)
            m1.metric("Classification", str(result["classification"]).replace("_", " ").title())
            m2.metric("Confidence", f"{score_percent(result.get('confidence')):.1f}%")
            m3.metric("Latency", f"{float(result.get('latency_ms', 0)):.1f} ms")
            with st.expander("Screening evidence and trace"):
                st.json(result)
        except Exception as exc:
            st.error(str(exc))

    if c2.button("Compare all architectures", use_container_width=True):
        try:
            results = api_post("/literature/compare", {"abstract_id": abstract_id, "text": abstract_text})
            rows = [
                {
                    "Architecture": str(r["architecture"]).replace("_", " ").title(),
                    "Classification": str(r["classification"]).replace("_", " ").title(),
                    "Confidence": round(score_percent(r.get("confidence")), 1),
                    "Latency (ms)": round(float(r.get("latency_ms", 0)), 1),
                }
                for r in results
            ]
            st.dataframe(rows, use_container_width=True, hide_index=True)
            with st.expander("Architecture traces"):
                st.json(results)
        except Exception as exc:
            st.error(str(exc))

# -----------------------------------------------------------------------------
# Benchmark Lab
# -----------------------------------------------------------------------------
with tabs[4]:
    section_header(
        "Validation science",
        "Benchmark Lab",
        "Evaluate architecture and prompt strategies on the governed synthetic literature benchmark with accuracy, macro-F1, screening sensitivity, specificity, false negatives, and latency.",
    )
    st.markdown(
        "<div class='pv-card'><div class='pv-card-label'>Benchmark design</div><div class='pv-answer'>120 synthetic reviewer-style records · balanced relevance classes · evidence spans · simulated dual review · adjudication · locked train/dev/test splits.</div></div>",
        unsafe_allow_html=True,
    )
    st.write("")
    split = st.selectbox("Evaluation split", ["test", "dev", "train", "all"], key="benchmark-split")
    c1, c2 = st.columns(2)

    if c1.button("Compare architectures", type="primary", use_container_width=True):
        try:
            with st.spinner("Running architecture comparison…"):
                payload = api_post("/benchmarks/literature/architectures", {"split": split})
            rows = []
            for name, report in payload["reports"].items():
                metrics = report["metrics"]
                rows.append({
                    "Architecture": name.replace("_", " ").title(),
                    "Accuracy": round(metrics["accuracy"], 3),
                    "Macro F1": round(metrics["macro_f1"], 3),
                    "Sensitivity": round(metrics["screening_sensitivity"], 3),
                    "Specificity": round(metrics["screening_specificity"], 3),
                    "False negatives": metrics["false_negatives"],
                    "Latency (ms)": round(metrics["average_latency_ms"], 1),
                })
            st.dataframe(rows, use_container_width=True, hide_index=True)
            with st.expander("Full validation output"):
                st.json(payload)
        except Exception as exc:
            st.error(str(exc))

    if c2.button("Compare prompt strategies", use_container_width=True):
        try:
            with st.spinner("Running prompt comparison…"):
                payload = api_post("/benchmarks/literature/prompts", {"split": split})
            rows = []
            for pid, result in payload["results"].items():
                metrics = result["metrics"]
                rows.append({
                    "Prompt": pid,
                    "Strategy": result["strategy"],
                    "Accuracy": round(metrics["accuracy"], 3),
                    "Macro F1": round(metrics["macro_f1"], 3),
                    "Sensitivity": round(metrics["screening_sensitivity"], 3),
                    "False negatives": metrics["false_negatives"],
                })
            st.dataframe(rows, use_container_width=True, hide_index=True)
            with st.expander("Full prompt-study output"):
                st.json(payload)
        except Exception as exc:
            st.error(str(exc))

# -----------------------------------------------------------------------------
# Monitoring
# -----------------------------------------------------------------------------
with tabs[5]:
    section_header(
        "Operational visibility",
        "Monitoring",
        "Inspect activity, confidence, and latency signals recorded by the local review-support platform.",
    )
    if st.button("Refresh monitoring", type="primary"):
        try:
            report = api_get("/monitoring/report")
            c1, c2, c3 = st.columns(3)
            c1.metric("Logged queries", report["query_count"])
            avg_conf = report["average_confidence"]
            c2.metric("Average confidence", "n/a" if avg_conf is None else f"{score_percent(avg_conf):.1f}%")
            avg_latency = report["average_latency_ms"]
            c3.metric("Average latency", "n/a" if avg_latency is None else f"{float(avg_latency):.1f} ms")
            with st.expander("Monitoring report JSON"):
                st.json(report)
        except Exception as exc:
            st.error(str(exc))
    else:
        st.info("Select **Refresh monitoring** to load the latest local telemetry snapshot.")

# -----------------------------------------------------------------------------
# Human review queue
# -----------------------------------------------------------------------------
with tabs[6]:
    section_header(
        "Governance",
        "Human review queue",
        "Approve or reject machine-generated review support with reviewer comments and an auditable case-state transition.",
    )
    try:
        queue = api_get("/cases?status=needs_review")
        if not queue:
            st.success("No cases currently require human review.")
        else:
            st.caption(f"{len(queue)} case(s) awaiting reviewer action")
        for item in queue:
            with st.expander(f"{item['case_id']} · Needs review", expanded=False):
                st.markdown(
                    f"<div class='pv-narrative'>{html.escape(str(item['review']['reviewer_narrative']))}</div>",
                    unsafe_allow_html=True,
                )
                comments = st.text_input("Reviewer comments", key=f"comments-{item['case_id']}")
                col1, col2 = st.columns(2)
                if col1.button("Approve case", type="primary", key=f"approve-{item['case_id']}", use_container_width=True):
                    api_post(f"/cases/{item['case_id']}/approve", {"comments": comments or "Reviewed and approved."})
                    st.rerun()
                if col2.button("Reject / return", key=f"reject-{item['case_id']}", use_container_width=True):
                    api_post(f"/cases/{item['case_id']}/reject", {"comments": comments or "Rejected pending correction."})
                    st.rerun()
    except Exception as exc:
        st.error(f"Unable to load review queue: {exc}")
