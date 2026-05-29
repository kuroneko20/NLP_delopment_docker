import html
import json
import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
DEFAULT_MESSAGE = "I lost my card and need urgent support"


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --app-bg: #f6f7fb;
                --panel-bg: #ffffff;
                --panel-border: #d8dee9;
                --text-main: #17202a;
                --text-muted: #657386;
                --teal: #0f766e;
                --amber: #b7791f;
                --blue: #2563eb;
                --rose: #be123c;
            }

            .stApp {
                background:
                    linear-gradient(180deg, rgba(15, 118, 110, 0.08), rgba(246, 247, 251, 0) 280px),
                    var(--app-bg);
                color: var(--text-main);
            }

            .block-container {
                max-width: 1180px;
                padding-top: 2.25rem;
                padding-bottom: 2.5rem;
            }

            h1, h2, h3 {
                letter-spacing: 0;
            }

            div[data-testid="stTextArea"] textarea {
                border: 1px solid var(--panel-border);
                border-radius: 8px;
                box-shadow: 0 1px 2px rgba(23, 32, 42, 0.06);
                min-height: 128px;
            }

            div[data-testid="stButton"] button {
                border-radius: 8px;
                border: 0;
                font-weight: 700;
                min-height: 2.9rem;
                background: var(--teal);
                color: #ffffff;
                box-shadow: 0 10px 22px rgba(15, 118, 110, 0.20);
            }

            div[data-testid="stButton"] button:hover {
                background: #0d665f;
                color: #ffffff;
                border: 0;
            }

            .hero {
                margin-bottom: 1.35rem;
            }

            .hero-eyebrow {
                color: var(--teal);
                font-size: 0.78rem;
                font-weight: 800;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.35rem;
            }

            .hero-title {
                color: var(--text-main);
                font-size: clamp(2rem, 5vw, 3.15rem);
                font-weight: 850;
                line-height: 1.02;
                margin: 0;
            }

            .hero-copy {
                color: var(--text-muted);
                font-size: 1rem;
                line-height: 1.65;
                max-width: 760px;
                margin-top: 0.85rem;
            }

            .panel {
                background: var(--panel-bg);
                border: 1px solid var(--panel-border);
                border-radius: 8px;
                box-shadow: 0 12px 28px rgba(23, 32, 42, 0.08);
                min-height: 330px;
                padding: 1.15rem;
            }

            .panel-title {
                align-items: center;
                color: var(--text-main);
                display: flex;
                font-size: 0.95rem;
                font-weight: 800;
                gap: 0.55rem;
                margin-bottom: 0.85rem;
            }

            .panel-dot {
                border-radius: 999px;
                display: inline-block;
                height: 0.68rem;
                width: 0.68rem;
            }

            .panel-dot.reply {
                background: var(--teal);
            }

            .panel-dot.response {
                background: var(--blue);
            }

            .reply-box {
                color: var(--text-main);
                font-size: 1rem;
                line-height: 1.7;
                white-space: normal;
            }

            .json-box {
                background: #101827;
                border-radius: 8px;
                color: #eef4ff;
                font-size: 0.82rem;
                line-height: 1.6;
                margin: 0;
                max-height: 420px;
                overflow: auto;
                padding: 1rem;
                white-space: pre-wrap;
            }

            .empty-box {
                align-items: center;
                border: 1px dashed #bbc5d4;
                border-radius: 8px;
                color: var(--text-muted);
                display: flex;
                min-height: 220px;
                justify-content: center;
                padding: 1rem;
                text-align: center;
            }

            .meta-grid {
                display: grid;
                gap: 0.7rem;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                margin-bottom: 1rem;
            }

            .meta-item {
                background: #f9fafc;
                border: 1px solid #e3e8f0;
                border-radius: 8px;
                padding: 0.7rem 0.75rem;
            }

            .meta-label {
                color: var(--text-muted);
                font-size: 0.72rem;
                font-weight: 800;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }

            .meta-value {
                color: var(--text-main);
                font-size: 0.96rem;
                font-weight: 800;
                margin-top: 0.25rem;
                overflow-wrap: anywhere;
            }

            .status-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.55rem;
                margin: 0.5rem 0 1.1rem;
            }

            .status-pill {
                border-radius: 999px;
                color: #ffffff;
                font-size: 0.78rem;
                font-weight: 800;
                padding: 0.42rem 0.7rem;
            }

            .status-pill.intent {
                background: var(--blue);
            }

            .status-pill.priority-high {
                background: var(--rose);
            }

            .status-pill.priority-medium {
                background: var(--amber);
            }

            .status-pill.priority-normal {
                background: var(--teal);
            }

            .status-pill.validation {
                background: #4b5563;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe_text(value: object) -> str:
    return html.escape(str(value or ""))


def line_breaks(value: str) -> str:
    return safe_text(value).replace("\n", "<br>")


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-eyebrow">Banking AI-Agent</div>
            <h1 class="hero-title">Customer support console</h1>
            <div class="hero-copy">
                Send a banking message through the agent workflow, then review the generated reply
                next to the structured backend response.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.subheader("Backend")
        st.caption(API_BASE_URL)
        if st.button("Load config", use_container_width=True):
            try:
                cfg = requests.get(f"{API_BASE_URL}/config", timeout=10)
                cfg.raise_for_status()
                st.json(cfg.json())
            except Exception as exc:
                st.error(f"Config unavailable: {exc}")


def render_status(result: dict) -> None:
    priority = safe_text(result.get("priority", "normal")).lower()
    if priority not in {"high", "medium", "normal"}:
        priority = "normal"

    st.markdown(
        f"""
        <div class="status-row">
            <span class="status-pill intent">Intent: {safe_text(result.get("intent", "unknown"))}</span>
            <span class="status-pill priority-{priority}">Priority: {safe_text(result.get("priority", "normal"))}</span>
            <span class="status-pill validation">Validation: {safe_text(result.get("validation", "not_checked"))}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_reply_panel(result: dict | None) -> None:
    if not result:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title"><span class="panel-dot reply"></span>Reply</div>
                <div class="empty-box">Run the agent to preview the customer-facing reply.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    reply = result.get("draft_reply") or "No draft reply returned."
    action = result.get("next_recommended_action") or "manual_review"
    missing = result.get("missing_information") or []
    missing_text = ", ".join(missing) if missing else "none"

    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title"><span class="panel-dot reply"></span>Reply</div>
            <div class="reply-box">{line_breaks(reply)}</div>
            <div class="meta-grid" style="margin-top: 1.15rem;">
                <div class="meta-item">
                    <div class="meta-label">Next action</div>
                    <div class="meta-value">{safe_text(action)}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Missing info</div>
                    <div class="meta-value">{safe_text(missing_text)}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_response_panel(result: dict | None) -> None:
    if not result:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title"><span class="panel-dot response"></span>Response</div>
                <div class="empty-box">The backend JSON response will appear here.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    confidence = result.get("confidence", 0.0)
    try:
        confidence_text = f"{float(confidence):.2f}"
    except (TypeError, ValueError):
        confidence_text = safe_text(confidence)

    json_text = html.escape(json.dumps(result, indent=2, ensure_ascii=False))
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title"><span class="panel-dot response"></span>Response</div>
            <div class="meta-grid">
                <div class="meta-item">
                    <div class="meta-label">Confidence</div>
                    <div class="meta-value">{confidence_text}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Reason</div>
                    <div class="meta-value">{safe_text(result.get("reason", "No reason returned."))}</div>
                </div>
            </div>
            <pre class="json-box">{json_text}</pre>
        </div>
        """,
        unsafe_allow_html=True,
    )


def call_agent(message: str) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/run-agent",
        json={"message": message},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


st.set_page_config(page_title="Banking AI-Agent", page_icon="B", layout="wide")
inject_styles()
render_sidebar()
render_hero()

if "message" not in st.session_state:
    st.session_state.message = DEFAULT_MESSAGE
if "agent_result" not in st.session_state:
    st.session_state.agent_result = None
if "agent_error" not in st.session_state:
    st.session_state.agent_error = None

message = st.text_area(
    "Customer message",
    key="message",
    placeholder="Type a customer banking request...",
)

run_agent = st.button("Run agent", type="primary", use_container_width=True)
if run_agent:
    if not message.strip():
        st.session_state.agent_error = "Message must not be empty."
        st.session_state.agent_result = None
    else:
        with st.spinner("Running workflow..."):
            try:
                st.session_state.agent_result = call_agent(message.strip())
                st.session_state.agent_error = None
            except Exception as exc:
                st.session_state.agent_result = None
                st.session_state.agent_error = f"API request failed: {exc}"

if st.session_state.agent_error:
    st.error(st.session_state.agent_error)

result = st.session_state.agent_result
if result:
    render_status(result)

reply_col, response_col = st.columns([1, 1], gap="large")

with reply_col:
    render_reply_panel(result)

with response_col:
    render_response_panel(result)
