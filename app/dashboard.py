import sys
from html import escape
from pathlib import Path

import altair as alt
import joblib
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.incident_response import get_incident_recommendations
from src.mitre_mapping import map_alert_to_mitre
from src.risk_score import calculate_risk_score, get_risk_level


MODEL_PATH = ROOT_DIR / "models" / "ai_soc_model.pkl"
FEATURES_PATH = ROOT_DIR / "models" / "features.pkl"
SAMPLE_DATA_PATH = ROOT_DIR / "data" / "sample_alerts.csv"
DEFAULT_FEATURES = [
    "duration",
    "src_bytes",
    "dst_bytes",
    "packet_count",
    "error_count",
]
REPORTS_DIR = ROOT_DIR / "reports"
LIMITATION_NOTE = (
    "This prototype currently uses a small simplified dataset. Therefore, high "
    "accuracy should be interpreted as a demonstration result, not as proof of "
    "production-level SOC performance. Future evaluation should use larger "
    "datasets such as CIC-IDS2017 or UNSW-NB15."
)


st.set_page_config(
    page_title="AI-SOC Alert Assistant",
    page_icon="SOC",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&family=Space+Grotesk:wght@500;600;700&display=swap');

            :root {
                --bg-base: #080C14;
                --bg-surface: #0E1520;
                --bg-elevated: #162133;
                --accent-primary: #3D9EFF;
                --accent-warning: #E8A838;
                --accent-critical: #E84545;
                --accent-success: #48D597;
                --text-primary: #E8EDF5;
                --text-muted: #5C7090;
                --border: #1E2D42;
            }

            html, body, [data-testid="stAppViewContainer"] {
                background:
                    radial-gradient(circle at 12% 8%, rgba(61, 158, 255, 0.12), transparent 26%),
                    radial-gradient(circle at 86% 0%, rgba(232, 168, 56, 0.08), transparent 23%),
                    linear-gradient(180deg, #080C14 0%, #070A11 100%);
                color: var(--text-primary);
                font-family: "Inter", sans-serif;
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0B101A 0%, #090D15 100%);
                border-right: 1px solid var(--border);
            }

            [data-testid="stSidebar"] * {
                font-family: "Inter", sans-serif;
            }

            .block-container {
                max-width: 1360px;
                padding: 1.25rem 2.4rem 4rem;
            }

            h1, h2, h3, .sg {
                font-family: "Space Grotesk", sans-serif;
                letter-spacing: 0;
            }

            .mono, code, [data-testid="stNumberInput"] input {
                font-family: "JetBrains Mono", monospace !important;
            }

            div[data-testid="stToolbar"] {
                display: none;
            }

            .topbar {
                min-height: 56px;
                border: 1px solid var(--border);
                background: rgba(14, 21, 32, 0.82);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 16px;
                margin-bottom: 16px;
                backdrop-filter: blur(16px);
            }

            .topbar-left, .topbar-right {
                display: flex;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
            }

            .brand-mark {
                width: 34px;
                height: 34px;
                border: 1px solid rgba(61, 158, 255, 0.45);
                background: linear-gradient(145deg, rgba(61, 158, 255, 0.18), rgba(61, 158, 255, 0.04));
                display: grid;
                place-items: center;
                border-radius: 8px;
                color: var(--accent-primary);
                font-family: "JetBrains Mono", monospace;
                font-weight: 800;
            }

            .brand-title {
                font-family: "Space Grotesk", sans-serif;
                font-weight: 700;
                color: var(--text-primary);
            }

            .status-pill {
                position: relative;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                border: 1px solid var(--border);
                background: rgba(22, 33, 51, 0.72);
                color: var(--text-primary);
                border-radius: 999px;
                padding: 7px 11px;
                font-size: 0.8rem;
                overflow: hidden;
            }

            .radar {
                position: relative;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: var(--accent-primary);
                box-shadow: 0 0 16px rgba(61, 158, 255, 0.9);
            }

            .radar::before {
                content: "";
                position: absolute;
                inset: -11px;
                border: 1px solid var(--accent-primary);
                border-radius: 50%;
                animation: pulse 3s ease-out infinite;
            }

            @keyframes pulse {
                0% { transform: scale(0.35); opacity: 0; }
                45% { opacity: 0.4; }
                100% { transform: scale(1.25); opacity: 0; }
            }

            .hero {
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 24px;
                margin-bottom: 18px;
                background:
                    linear-gradient(135deg, rgba(61, 158, 255, 0.16), transparent 34%),
                    linear-gradient(180deg, rgba(14, 21, 32, 0.96) 0%, rgba(8, 12, 20, 0.92) 100%);
            }

            .eyebrow {
                color: var(--accent-primary);
                font-size: 0.78rem;
                font-weight: 800;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 9px;
            }

            .hero h1 {
                margin: 0;
                font-size: 2.45rem;
                line-height: 1.05;
            }

            .hero p {
                margin: 12px 0 0 0;
                max-width: 920px;
                color: #9BAAC0;
                font-size: 1rem;
                line-height: 1.58;
            }

            .mission-strip {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 10px;
                margin: 14px 0 18px;
            }

            .mission-item {
                border: 1px solid var(--border);
                border-radius: 8px;
                background: rgba(14, 21, 32, 0.78);
                padding: 13px 14px;
            }

            .mission-item span {
                display: block;
                color: var(--text-muted);
                font-size: 0.72rem;
                text-transform: uppercase;
                font-weight: 800;
                letter-spacing: 0.06em;
            }

            .mission-item strong {
                display: block;
                margin-top: 5px;
                color: var(--text-primary);
                font-family: "Space Grotesk", sans-serif;
                font-size: 1.02rem;
            }

            .section-title {
                margin: 24px 0 12px;
                padding-bottom: 10px;
                border-bottom: 1px solid var(--border);
            }

            .section-title h2 {
                margin: 0;
                font-size: 1.42rem;
            }

            .section-title p {
                margin: 7px 0 0;
                color: #8FA0B8;
                line-height: 1.5;
            }

            .panel {
                border: 1px solid var(--border);
                border-radius: 8px;
                background: linear-gradient(180deg, rgba(14, 21, 32, 0.96), rgba(10, 15, 24, 0.98));
                padding: 18px;
            }

            .panel-title {
                margin: 0 0 12px;
                color: var(--text-primary);
                font-family: "Space Grotesk", sans-serif;
                font-size: 1.08rem;
                font-weight: 700;
            }

            .input-shell {
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 14px;
                background: rgba(14, 21, 32, 0.7);
                margin-bottom: 10px;
            }

            .unit-chip {
                display: inline-flex;
                align-items: center;
                border: 1px solid var(--border);
                background: rgba(61, 158, 255, 0.08);
                color: #A8CFFF;
                border-radius: 999px;
                padding: 2px 8px;
                font-size: 0.7rem;
                font-family: "JetBrains Mono", monospace;
                margin-left: 6px;
            }

            [data-testid="stNumberInput"] input {
                background: var(--bg-surface);
                border: 1px solid var(--border);
                color: var(--text-primary);
                border-radius: 8px;
            }

            .stButton > button {
                border-radius: 8px;
                border: 1px solid rgba(61, 158, 255, 0.55);
                min-height: 44px;
                font-weight: 800;
                background: linear-gradient(90deg, #1D66B8, var(--accent-primary));
                color: white;
                position: relative;
                overflow: hidden;
            }

            .stButton > button:hover {
                border-color: #9DCAFF;
                box-shadow: 0 0 0 1px rgba(61, 158, 255, 0.32), 0 0 24px rgba(61, 158, 255, 0.28);
            }

            .stButton > button::after {
                content: "";
                position: absolute;
                top: 0;
                left: -40%;
                width: 28%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.32), transparent);
                transform: skewX(-18deg);
            }

            .stButton > button:hover::after {
                animation: scan 1.2s ease-in-out infinite;
            }

            @keyframes scan {
                0% { left: -40%; }
                100% { left: 115%; }
            }

            .risk-layout {
                display: grid;
                grid-template-columns: 240px minmax(0, 1fr);
                gap: 16px;
                align-items: stretch;
            }

            .gauge-card {
                border: 1px solid var(--border);
                border-radius: 8px;
                background: rgba(14, 21, 32, 0.78);
                padding: 18px 14px;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .gauge-ring {
                --score-color: var(--accent-primary);
                --score-deg: 0deg;
                width: 198px;
                height: 198px;
                border-radius: 50%;
                display: grid;
                place-items: center;
                background:
                    radial-gradient(circle at center, #0E1520 0 57%, transparent 58%),
                    conic-gradient(var(--score-color) var(--score-deg), #162133 0deg);
                box-shadow: inset 0 0 0 1px rgba(61, 158, 255, 0.15), 0 0 28px rgba(61, 158, 255, 0.08);
            }

            .gauge-inner {
                width: 138px;
                height: 138px;
                border-radius: 50%;
                display: grid;
                place-items: center;
                text-align: center;
                border: 1px solid var(--border);
                background: #0A0F18;
            }

            .gauge-score {
                display: block;
                font-family: "Space Grotesk", sans-serif;
                font-size: 48px;
                line-height: 1;
                color: var(--text-primary);
                font-weight: 700;
            }

            .gauge-label {
                display: block;
                margin-top: 8px;
                color: var(--text-muted);
                font-size: 0.68rem;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                font-weight: 800;
            }

            .threat-summary {
                border: 1px solid var(--border);
                border-radius: 8px;
                background: rgba(14, 21, 32, 0.78);
                padding: 18px;
            }

            .badge {
                display: inline-block;
                border-radius: 999px;
                padding: 5px 10px;
                font-weight: 800;
                font-size: 0.76rem;
                border: 1px solid transparent;
            }

            .badge-critical {
                color: #FFE3E3;
                background: rgba(232, 69, 69, 0.18);
                border-color: rgba(232, 69, 69, 0.58);
            }

            .badge-high, .badge-medium {
                color: #FFE9B8;
                background: rgba(232, 168, 56, 0.17);
                border-color: rgba(232, 168, 56, 0.5);
            }

            .badge-low {
                color: #D6FFE9;
                background: rgba(72, 213, 151, 0.14);
                border-color: rgba(72, 213, 151, 0.42);
            }

            .kv-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 10px;
                margin-top: 14px;
            }

            .kv {
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 12px;
                background: rgba(22, 33, 51, 0.52);
            }

            .kv .label {
                color: var(--text-muted);
                font-size: 0.74rem;
                font-weight: 800;
                letter-spacing: 0.04em;
                text-transform: uppercase;
                margin-bottom: 5px;
            }

            .kv .value {
                color: var(--text-primary);
                font-family: "Space Grotesk", sans-serif;
                font-weight: 700;
                word-break: break-word;
            }

            .tag-row {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin: 12px 0;
            }

            .tag {
                display: inline-flex;
                align-items: center;
                border: 1px solid rgba(61, 158, 255, 0.36);
                color: #C9E4FF;
                background: rgba(61, 158, 255, 0.08);
                border-radius: 999px;
                padding: 7px 10px;
                font-size: 0.8rem;
            }

            .tag:hover {
                box-shadow: 0 0 22px rgba(61, 158, 255, 0.28);
            }

            .recommendations {
                margin: 10px 0 0 0;
                padding-left: 20px;
                line-height: 1.7;
            }

            .recommendations li {
                margin-bottom: 7px;
            }

            div[data-testid="stMetric"] {
                border: 1px solid var(--border);
                border-radius: 8px;
                background: rgba(14, 21, 32, 0.82);
                padding: 14px;
            }

            div[data-testid="stMetric"] label {
                color: var(--text-muted);
            }

            div[data-testid="stMetricValue"] {
                color: var(--text-primary);
                font-family: "Space Grotesk", sans-serif;
            }

            [data-testid="stFileUploader"] {
                border: 1px dashed rgba(61, 158, 255, 0.45);
                border-radius: 8px;
                padding: 10px;
                background: rgba(61, 158, 255, 0.035);
            }

            [data-testid="stFileUploader"]:hover {
                animation: dropPulse 1.5s ease-in-out infinite;
            }

            @keyframes dropPulse {
                0%, 100% { border-color: rgba(61, 158, 255, 0.35); }
                50% { border-color: rgba(61, 158, 255, 0.88); }
            }

            .small-note {
                color: var(--text-muted);
                font-size: 0.9rem;
            }

            .feature-bars {
                display: flex;
                flex-direction: column;
                gap: 12px;
                margin-top: 4px;
            }

            .feature-row {
                display: grid;
                grid-template-columns: 170px minmax(0, 1fr) 58px;
                gap: 12px;
                align-items: center;
                font-family: "JetBrains Mono", monospace;
                color: var(--text-primary);
                font-size: 0.86rem;
            }

            .feature-track {
                height: 12px;
                border-radius: 999px;
                background: rgba(92, 112, 144, 0.18);
                overflow: hidden;
            }

            .feature-fill {
                height: 100%;
                width: 0;
                background: linear-gradient(90deg, #1D66B8, var(--accent-primary));
                border-radius: 999px;
                animation: barIn 0.9s ease forwards;
            }

            .diamond {
                color: var(--accent-primary);
                text-shadow: 0 0 14px rgba(61, 158, 255, 0.7);
                margin-right: 6px;
            }

            @keyframes barIn {
                from { width: 0; }
                to { width: var(--bar-width); }
            }

            .dataframe, [data-testid="stDataFrame"] {
                border-radius: 8px;
                overflow: hidden;
            }

            @media (max-width: 980px) {
                .mission-strip, .risk-layout, .kv-grid {
                    grid-template-columns: 1fr;
                }

                .hero h1 {
                    font-size: 1.75rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def section(title, description):
    section_name = title.split(". ", 1)[-1]
    section_id = section_name.lower().replace(" ", "-")
    st.markdown(
        f"""
        <div class="section-title" id="{section_id}">
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def inject_premium_overrides():
    st.markdown(
        """
        <style>
            :root {
                --bg-base: #0d1117;
                --bg-surface: #111827;
                --bg-sidebar: #161b22;
                --bg-card: #111827;
                --bg-elevated: #1f2937;
                --accent-purple: #7c3aed;
                --accent-pink: #db2777;
                --accent-blue: #3b82f6;
                --accent-cyan: #22d3ee;
                --text-primary: #ffffff;
                --text-body: #e6edf3;
                --text-muted: #8b949e;
                --border: rgba(139, 148, 158, 0.18);
                --shadow-soft: 0 18px 48px rgba(0, 0, 0, 0.32);
                --shadow-glow: 0 0 44px rgba(124, 58, 237, 0.14);
            }

            html, body, [data-testid="stAppViewContainer"] {
                background:
                    radial-gradient(circle at 18% 0%, rgba(124, 58, 237, 0.18), transparent 32%),
                    radial-gradient(circle at 86% 12%, rgba(219, 39, 119, 0.13), transparent 30%),
                    linear-gradient(180deg, #0d1117 0%, #090d14 100%) !important;
                color: var(--text-body) !important;
                font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
            }

            .block-container {
                max-width: 1480px;
                padding: 2rem 2.35rem 4rem !important;
            }

            [data-testid="stHeader"],
            [data-testid="stToolbar"] {
                background: transparent !important;
            }

            [data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, rgba(22, 27, 34, 0.98) 0%, rgba(13, 17, 23, 0.98) 100%) !important;
                border-right: 1px solid var(--border) !important;
                box-shadow: 14px 0 42px rgba(0, 0, 0, 0.24);
            }

            [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
                padding: 1.4rem 1rem;
            }

            [data-testid="stSidebar"] * {
                color: var(--text-body);
            }

            h1, h2, h3, .sg, .brand-title, .panel-title {
                font-family: Inter, system-ui, sans-serif !important;
                color: var(--text-primary) !important;
                letter-spacing: -0.02em;
            }

            p, span, label, div {
                color: inherit;
            }

            .premium-sidebar-logo {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 8px 4px 20px;
            }

            .logo-orb,
            .brand-mark {
                width: 42px;
                height: 42px;
                border-radius: 14px;
                display: grid;
                place-items: center;
                color: #fff;
                font-weight: 900;
                font-size: 0.78rem;
                letter-spacing: 0.08em;
                background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));
                box-shadow: 0 12px 30px rgba(124, 58, 237, 0.35);
                border: 1px solid rgba(255,255,255,0.12);
            }

            .sidebar-title {
                font-size: 1rem;
                font-weight: 800;
                color: #fff;
                line-height: 1.1;
            }

            .sidebar-subtitle {
                margin-top: 4px;
                color: var(--text-muted);
                font-size: 0.76rem;
            }

            .sidebar-label {
                margin: 10px 0 9px;
                color: #fff;
                font-size: 0.82rem;
                font-weight: 800;
                letter-spacing: 0.02em;
            }

            .nav-list {
                display: flex;
                flex-direction: column;
                gap: 7px;
                margin-bottom: 22px;
            }

            .nav-item {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px 12px;
                border-radius: 12px;
                color: var(--text-muted);
                border: 1px solid transparent;
                background: transparent;
                text-decoration: none;
                transition: 0.2s ease;
                font-weight: 650;
                font-size: 0.9rem;
            }

            .nav-item:hover,
            .nav-item.active {
                color: #fff;
                background: linear-gradient(135deg, rgba(124, 58, 237, 0.22), rgba(219, 39, 119, 0.13));
                border-color: rgba(124, 58, 237, 0.35);
            }

            html:not(:has(.section-title:target)) .nav-item[href="#manual-alert-scan"],
            html:has(#manual-alert-scan:target) .nav-item[href="#manual-alert-scan"],
            html:has(#csv-batch-analysis:target) .nav-item[href="#csv-batch-analysis"],
            html:has(#feature-importance:target) .nav-item[href="#feature-importance"],
            html:has(#research-results:target) .nav-item[href="#research-results"] {
                color: #fff;
                background: linear-gradient(135deg, rgba(124, 58, 237, 0.22), rgba(219, 39, 119, 0.13));
                border-color: rgba(124, 58, 237, 0.35);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 10px 24px rgba(124, 58, 237, 0.14);
            }

            .feature-chip-row {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 20px;
            }

            .feature-chip {
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 7px 10px;
                background: rgba(13, 17, 23, 0.64);
                color: #d8e1ee;
                font-family: "Courier New", monospace;
                font-size: 0.78rem;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
            }

            .sidebar-footer {
                margin-top: 10px;
                color: var(--text-muted);
                font-size: 0.78rem;
                line-height: 1.45;
                border-top: 1px solid var(--border);
                padding-top: 14px;
            }

            .topbar {
                min-height: 72px;
                border: 1px solid var(--border);
                background:
                    linear-gradient(135deg, rgba(22, 27, 34, 0.92), rgba(17, 24, 39, 0.86));
                border-radius: 16px;
                padding: 0 20px;
                margin-bottom: 22px;
                box-shadow: var(--shadow-soft), var(--shadow-glow);
                backdrop-filter: blur(18px);
            }

            .brand-title {
                font-size: 1.08rem;
                font-weight: 850;
            }

            .status-pill {
                border-radius: 999px;
                border: 1px solid rgba(124, 58, 237, 0.28);
                background: rgba(22, 27, 34, 0.76);
                color: #e6edf3;
                padding: 8px 12px;
                font-size: 0.8rem;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
            }

            .radar {
                background: #22c55e;
                box-shadow: 0 0 16px rgba(34, 197, 94, 0.88);
            }

            .radar::before {
                border-color: #22c55e;
            }

            .hero {
                border-radius: 16px;
                border: 1px solid rgba(124, 58, 237, 0.18);
                padding: 30px 32px;
                margin-bottom: 22px;
                background:
                    linear-gradient(135deg, rgba(124, 58, 237, 0.18), rgba(219, 39, 119, 0.08) 42%, rgba(59, 130, 246, 0.07)),
                    linear-gradient(180deg, rgba(17, 24, 39, 0.96), rgba(13, 17, 23, 0.9));
                box-shadow: var(--shadow-soft);
            }

            .hero h1 {
                font-size: clamp(2.1rem, 4vw, 4.2rem);
                color: #fff;
                font-weight: 900;
                line-height: 0.98;
            }

            .hero p,
            .section-title p,
            .small-note {
                color: var(--text-muted) !important;
            }

            .eyebrow {
                color: var(--accent-cyan) !important;
                letter-spacing: 0.12em;
                font-size: 0.76rem;
                font-weight: 900;
            }

            .mission-strip {
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 14px;
                margin-bottom: 30px;
            }

            .mission-item,
            .panel,
            .threat-summary,
            div[data-testid="stMetric"],
            .kv {
                border-radius: 16px !important;
                border: 1px solid var(--border) !important;
                background:
                    linear-gradient(145deg, rgba(124, 58, 237, 0.08), rgba(59, 130, 246, 0.04) 45%, rgba(17, 24, 39, 0.92)),
                    #111827 !important;
                box-shadow: var(--shadow-soft);
            }

            .mission-item {
                padding: 16px 18px;
            }

            .mission-item span,
            .kv .label {
                color: var(--text-muted) !important;
            }

            .mission-item strong {
                color: #fff;
                font-size: 1.08rem;
            }

            .section-title {
                margin: 34px 0 16px;
                border-bottom: 0;
                padding: 0;
            }

            .section-title h2 {
                color: #fff !important;
                font-size: clamp(1.7rem, 2.4vw, 2.35rem);
                font-weight: 900;
                line-height: 1.1;
            }

            .section-title p {
                margin-top: 9px;
                font-size: 1rem;
            }

            .panel {
                padding: 22px;
            }

            .panel-title {
                font-size: 1.08rem;
                font-weight: 850;
                margin-bottom: 16px;
            }

            .input-shell {
                border-radius: 12px;
                border: 1px solid var(--border);
                background: rgba(13, 17, 23, 0.64);
                padding: 12px 14px;
                color: #fff;
                font-family: "Courier New", monospace;
                font-weight: 800;
                margin-bottom: 8px;
            }

            .unit-chip,
            .tag,
            .badge {
                border-radius: 999px !important;
            }

            .unit-chip {
                background: rgba(34, 211, 238, 0.11);
                border: 1px solid rgba(34, 211, 238, 0.24);
                color: #67e8f9;
            }

            [data-testid="stNumberInput"] {
                margin-bottom: 14px;
            }

            [data-testid="stNumberInput"] input {
                background: #0d1117 !important;
                border: 1px solid rgba(139, 148, 158, 0.22) !important;
                color: #fff !important;
                border-radius: 12px !important;
                min-height: 44px;
                font-family: "Courier New", monospace !important;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.035);
            }

            [data-testid="stNumberInput"] button {
                background: #111827 !important;
                border: 1px solid rgba(139, 148, 158, 0.24) !important;
                color: #e6edf3 !important;
                border-radius: 10px !important;
                transition: 0.2s ease;
            }

            [data-testid="stNumberInput"] button:hover {
                border-color: rgba(124, 58, 237, 0.66) !important;
                box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.14);
            }

            .stButton > button {
                border-radius: 999px !important;
                border: 0 !important;
                background: linear-gradient(90deg, var(--accent-purple), var(--accent-pink)) !important;
                color: #fff !important;
                min-height: 48px;
                font-weight: 850;
                box-shadow: 0 14px 34px rgba(124, 58, 237, 0.27);
                transition: 0.2s ease;
            }

            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 18px 42px rgba(219, 39, 119, 0.32);
                filter: brightness(1.05);
            }

            [data-testid="stFileUploader"] {
                border-radius: 16px !important;
                border: 1px dashed rgba(59, 130, 246, 0.72) !important;
                background:
                    linear-gradient(145deg, rgba(59, 130, 246, 0.09), rgba(124, 58, 237, 0.06)),
                    rgba(17, 24, 39, 0.72) !important;
                padding: 24px !important;
                box-shadow: var(--shadow-soft);
            }

            [data-testid="stFileUploader"] section {
                border: 0 !important;
                background: transparent !important;
            }

            [data-testid="stFileUploader"] button {
                border-radius: 999px !important;
                background: rgba(37, 99, 235, 0.16) !important;
                color: #bfdbfe !important;
                border: 1px solid rgba(37, 99, 235, 0.42) !important;
            }

            .dropzone-title {
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 0 0 10px;
                color: #fff;
                font-weight: 850;
                font-size: 1.02rem;
            }

            .dropzone-icon {
                width: 34px;
                height: 34px;
                display: inline-grid;
                place-items: center;
                border-radius: 12px;
                background: rgba(59, 130, 246, 0.16);
                color: #93c5fd;
                border: 1px solid rgba(59, 130, 246, 0.28);
            }

            .dropzone-hint {
                margin: -4px 0 12px;
                color: var(--text-muted);
                font-size: 0.88rem;
            }

            .stButton > button[kind="secondary"] {
                background: #2563eb !important;
                color: #fff !important;
                box-shadow: 0 14px 34px rgba(37, 99, 235, 0.28);
            }

            .stButton > button[kind="secondary"]:hover {
                background: #1d4ed8 !important;
                box-shadow: 0 18px 42px rgba(37, 99, 235, 0.36);
            }

            .threat-summary {
                padding: 22px;
            }

            .badge {
                padding: 6px 11px;
            }

            .badge-critical {
                background: linear-gradient(90deg, rgba(220, 38, 38, 0.24), rgba(219, 39, 119, 0.18));
                border-color: rgba(248, 113, 113, 0.42);
            }

            .badge-high,
            .badge-medium {
                background: rgba(234, 179, 8, 0.16);
                border-color: rgba(234, 179, 8, 0.38);
            }

            .badge-low {
                background: rgba(34, 197, 94, 0.14);
                border-color: rgba(34, 197, 94, 0.34);
            }

            .tag {
                background: rgba(124, 58, 237, 0.12);
                border: 1px solid rgba(124, 58, 237, 0.32);
                color: #ddd6fe;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
            }

            .kv-grid {
                gap: 12px;
            }

            .kv .value {
                color: #fff !important;
                font-weight: 850;
            }

            .recommendations {
                color: #d8e1ee;
            }

            .feature-row {
                grid-template-columns: minmax(130px, 190px) minmax(0, 1fr) 64px;
                background: rgba(13, 17, 23, 0.44);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 10px 12px;
            }

            .feature-track {
                background: rgba(139, 148, 158, 0.14);
                height: 13px;
            }

            .feature-fill {
                background: linear-gradient(90deg, #2563eb, #3b82f6);
                box-shadow: 0 0 24px rgba(59, 130, 246, 0.32);
            }

            .diamond {
                color: #60a5fa;
                text-shadow: 0 0 18px rgba(59, 130, 246, 0.82);
            }

            [data-testid="stDataFrame"],
            .dataframe {
                border-radius: 16px !important;
                border: 1px solid var(--border) !important;
                background: #111827 !important;
                box-shadow: var(--shadow-soft);
            }

            [data-testid="stTable"] {
                border-radius: 16px;
                overflow: hidden;
            }

            div[data-testid="stAlert"] {
                border-radius: 16px;
                border: 1px solid rgba(59, 130, 246, 0.24);
                background: rgba(59, 130, 246, 0.09);
            }

            [data-testid="stExpander"] {
                border-radius: 16px !important;
                border: 1px solid var(--border) !important;
                background: rgba(17, 24, 39, 0.7) !important;
            }

            code, pre, .mono, [data-testid="stText"] {
                font-family: "Courier New", ui-monospace, monospace !important;
            }

            .research-report {
                border-radius: 16px;
                border: 1px solid var(--border);
                background: #0d1117;
                padding: 18px;
                color: #d8e1ee;
                font-family: "Courier New", monospace;
                white-space: pre-wrap;
                overflow-x: auto;
                box-shadow: var(--shadow-soft);
            }

            @media (max-width: 980px) {
                .mission-strip,
                .kv-grid {
                    grid-template-columns: 1fr !important;
                }

                .topbar {
                    align-items: flex-start;
                    padding: 16px;
                }

                .topbar-right {
                    justify-content: flex-start;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def risk_color(score):
    if score >= 85:
        return "#db2777"
    if score >= 70:
        return "#f59e0b"
    if score >= 40:
        return "#f59e0b"
    return "#22c55e"


def risk_badge(risk_level):
    css_class = {
        "Critical": "badge-critical",
        "High": "badge-high",
        "Medium": "badge-medium",
        "Low": "badge-low",
    }.get(risk_level, "badge-medium")
    return f'<span class="badge {css_class}">{risk_level}</span>'


def gauge_html(score, risk_level):
    progress = max(0, min(score, 100))
    degrees = progress * 3.6
    color = risk_color(score)
    return f"""
    <div class="gauge-ring" style="--score-color:{color}; --score-deg:{degrees:.1f}deg;" aria-label="Risk score {score:.0f}">
        <div class="gauge-inner">
            <div>
                <span class="gauge-score">{score:.0f}</span>
                <span class="gauge-label">{risk_level} risk</span>
            </div>
        </div>
    </div>
    """


def prepare_features(df, feature_names):
    prepared = df.copy()
    prepared.columns = prepared.columns.str.strip()
    prepared = prepared.reindex(columns=feature_names, fill_value=0)
    prepared = prepared.apply(pd.to_numeric, errors="coerce")
    prepared = prepared.replace([float("inf"), float("-inf")], pd.NA)
    return prepared.fillna(0)


def analyze_alerts(df, model, feature_names):
    x = prepare_features(df, feature_names)
    predictions = model.predict(x)
    probabilities = model.predict_proba(x)[:, 1]

    results = x.copy()
    results["prediction"] = predictions
    results["prediction_text"] = results["prediction"].apply(
        lambda value: "ATTACK" if value == 1 else "BENIGN"
    )
    results["attack_probability"] = probabilities
    results["risk_score"] = results["attack_probability"].apply(calculate_risk_score)
    results["risk_level"] = results["risk_score"].apply(get_risk_level)

    mitre_results = results.apply(
        lambda row: map_alert_to_mitre(row.to_dict(), row["risk_level"]),
        axis=1,
    )
    results["mitre_tactic"] = mitre_results.apply(lambda value: value["tactic"])
    results["mitre_technique"] = mitre_results.apply(lambda value: value["technique"])
    results["mitre_reason"] = mitre_results.apply(lambda value: value["reason"])
    results["recommendations"] = results.apply(
        lambda row: " | ".join(
            get_incident_recommendations(row["risk_level"], row["mitre_tactic"])
        ),
        axis=1,
    )
    return results


def render_manual_result(analyzed_alert):
    recommendations = get_incident_recommendations(
        analyzed_alert["risk_level"],
        analyzed_alert["mitre_tactic"],
    )
    status = "Possible attack detected" if analyzed_alert["prediction"] == 1 else "Normal traffic"
    status_class = "badge-critical" if analyzed_alert["prediction"] == 1 else "badge-low"
    items = "".join(f"<li>{escape(recommendation)}</li>" for recommendation in recommendations)
    tactic = escape(str(analyzed_alert["mitre_tactic"]))
    technique = escape(str(analyzed_alert["mitre_technique"]))
    reason = escape(str(analyzed_alert["mitre_reason"]))
    risk_level = escape(str(analyzed_alert["risk_level"]))

    gauge_markup = f"""
    <html>
        <head>
            <style>
                body {{
                    margin: 0;
                    background: transparent;
                    display: grid;
                    place-items: center;
                    min-height: 250px;
                    font-family: "Inter", sans-serif;
                }}
                .gauge-wrap {{
                    border: 1px solid rgba(139, 148, 158, 0.18);
                    border-radius: 16px;
                    background:
                        linear-gradient(145deg, rgba(124, 58, 237, 0.08), rgba(59, 130, 246, 0.04) 45%, rgba(17, 24, 39, 0.92)),
                        #111827;
                    width: 100%;
                    height: 245px;
                    display: grid;
                    place-items: center;
                    box-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
                }}
                .gauge-ring {{
                    width: 198px;
                    height: 198px;
                    border-radius: 50%;
                    display: grid;
                    place-items: center;
                    background:
                        radial-gradient(circle at center, #111827 0 57%, transparent 58%),
                        conic-gradient({risk_color(analyzed_alert["risk_score"])} {analyzed_alert["risk_score"] * 3.6:.1f}deg, #162133 0deg);
                    box-shadow: inset 0 0 0 1px rgba(124, 58, 237, 0.18), 0 0 34px rgba(124, 58, 237, 0.12);
                }}
                .gauge-inner {{
                    width: 138px;
                    height: 138px;
                    border-radius: 50%;
                    display: grid;
                    place-items: center;
                    text-align: center;
                    border: 1px solid rgba(139, 148, 158, 0.18);
                    background: #0d1117;
                }}
                .score {{
                    display: block;
                    font-family: Inter, system-ui, sans-serif;
                    font-size: 48px;
                    line-height: 1;
                    color: #ffffff;
                    font-weight: 700;
                }}
                .label {{
                    display: block;
                    margin-top: 8px;
                    color: #8b949e;
                    font-size: 0.68rem;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    font-weight: 800;
                }}
            </style>
        </head>
        <body>
            <div class="gauge-wrap">
                <div class="gauge-ring">
                    <div class="gauge-inner">
                        <div>
                            <span class="score">{analyzed_alert["risk_score"]:.0f}</span>
                            <span class="label">{risk_level} risk</span>
                        </div>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

    gauge_col, summary_col = st.columns([0.52, 1.48], gap="medium")
    with gauge_col:
        components.html(gauge_markup, height=255)
    with summary_col:
        st.html(
        f"""
            <div class="threat-summary">
                <p class="panel-title">Threat Assessment</p>
                <span class="badge {status_class}">{status}</span>
                <div class="kv-grid">
                    <div class="kv">
                        <div class="label">Attack probability</div>
                        <div class="value mono">{analyzed_alert["attack_probability"]:.2f}</div>
                    </div>
                    <div class="kv">
                        <div class="label">Risk level</div>
                        <div class="value">{risk_badge(risk_level)}</div>
                    </div>
                    <div class="kv">
                        <div class="label">Primary tactic</div>
                        <div class="value">{tactic}</div>
                    </div>
                </div>
                <div class="tag-row">
                    <span class="tag">MITRE: {tactic}</span>
                    <span class="tag">{technique}</span>
                    <span class="tag">Risk score {analyzed_alert["risk_score"]:.0f}</span>
                </div>
                <div class="kv">
                    <div class="label">Detection rationale</div>
                    <div class="value">{reason}</div>
                </div>
                <p class="panel-title" style="margin-top:16px;">Response Guidance</p>
                <ul class="recommendations">{items}</ul>
            </div>
        """
        )


def render_table(results):
    display_results = results.copy()
    display_results["risk_level"] = display_results["risk_level"].apply(
        lambda level: f"{level}"
    )
    columns = [
        "duration",
        "src_bytes",
        "dst_bytes",
        "packet_count",
        "error_count",
        "prediction_text",
        "attack_probability",
        "risk_score",
        "risk_level",
        "mitre_tactic",
        "mitre_technique",
        "recommendations",
    ]
    st.dataframe(
        display_results[columns],
        hide_index=True,
        width="stretch",
        column_config={
            "duration": st.column_config.NumberColumn("duration", help="ns"),
            "src_bytes": st.column_config.NumberColumn("src_bytes", help="bytes"),
            "dst_bytes": st.column_config.NumberColumn("dst_bytes", help="bytes"),
            "attack_probability": st.column_config.NumberColumn(
                "attack_probability",
                format="%.2f",
            ),
            "risk_score": st.column_config.NumberColumn("risk_score", format="%.2f"),
            "recommendations": st.column_config.TextColumn(
                "recommendations",
                width="large",
            ),
            "mitre_technique": st.column_config.TextColumn(
                "mitre_technique",
                width="medium",
            ),
        },
    )


def render_summary_metrics(results):
    critical_count = int((results["risk_level"] == "Critical").sum())
    high_count = int((results["risk_level"] == "High").sum())
    medium_count = int((results["risk_level"] == "Medium").sum())
    low_count = int((results["risk_level"] == "Low").sum())
    attack_count = int((results["prediction_text"] == "ATTACK").sum())

    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
    metric_col1.metric("ATTACK", attack_count)
    metric_col2.metric("Critical", critical_count)
    metric_col3.metric("High", high_count)
    metric_col4.metric("Medium", medium_count)
    metric_col5.metric("Low", low_count)

    if critical_count > 0:
        st.error("Critical alerts detected. Immediate review is recommended.")
    elif high_count > 0:
        st.warning("High-risk alerts detected. Review and escalation may be required.")
    else:
        st.success("No high-risk alerts detected.")


def render_feature_bars(importance_df):
    max_value = importance_df["Importance"].max()
    rows = []
    for index, row in importance_df.reset_index(drop=True).iterrows():
        percent = (row["Importance"] / max_value) * 100 if max_value else 0
        diamond = '<span class="diamond">&#9670;</span>' if index == 0 else ""
        rows.append(
            f"""
            <div class="feature-row">
                <div>{diamond}{row["Feature"]}</div>
                <div class="feature-track">
                    <div class="feature-fill" style="--bar-width:{percent:.1f}%; animation-delay:{index * 80}ms;"></div>
                </div>
                <div>{row["Importance"]:.2f}</div>
            </div>
            """
        )
    st.html(f'<div class="feature-bars">{"".join(rows)}</div>')


def load_feature_names():
    if FEATURES_PATH.exists():
        return joblib.load(FEATURES_PATH)
    return DEFAULT_FEATURES


def render_limitations_note():
    st.info(LIMITATION_NOTE)


def render_research_results():
    section(
        "4. Research Results",
        "Evaluation artifacts that strengthen the experimental part of the prototype.",
    )

    comparison_path = REPORTS_DIR / "model_comparison.csv"
    cross_validation_path = REPORTS_DIR / "cross_validation_results.csv"
    metrics_path = REPORTS_DIR / "metrics.txt"

    if comparison_path.exists():
        st.markdown("#### Model Comparison")
        st.dataframe(pd.read_csv(comparison_path), hide_index=True, width="stretch")
    else:
        st.caption("Run `python src\\model_comparison.py` to generate model comparison results.")

    if cross_validation_path.exists():
        st.markdown("#### Stratified K-Fold Cross-Validation")
        st.dataframe(pd.read_csv(cross_validation_path), hide_index=True, width="stretch")
    else:
        st.caption("Run `python src\\cross_validation.py` to generate cross-validation results.")

    if metrics_path.exists():
        st.markdown("#### Evaluation Report")
        metrics_text = escape(metrics_path.read_text(encoding="utf-8"))
        st.markdown(
            f'<div class="research-report">{metrics_text}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.caption("Run `python src\\evaluate_model.py` to generate the evaluation report.")


inject_styles()
inject_premium_overrides()

try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    st.error("Model file was not found. Run `python src\\train_model.py` first.")
    st.stop()

FEATURES = load_feature_names()

with st.sidebar:
    feature_chips = "".join(
        f'<span class="feature-chip">{escape(str(feature))}</span>' for feature in FEATURES
    )
    st.markdown(
        f"""
        <div class="premium-sidebar-logo">
            <div class="logo-orb">SOC</div>
            <div>
                <div class="sidebar-title">AI-SOC</div>
                <div class="sidebar-subtitle">Alert Assistant</div>
            </div>
        </div>
        <div class="sidebar-label">Mission Control</div>
        <div class="nav-list">
            <a class="nav-item" href="#manual-alert-scan">01 Manual Alert Scan</a>
            <a class="nav-item" href="#csv-batch-analysis">02 CSV Batch Analysis</a>
            <a class="nav-item" href="#feature-importance">03 Feature Importance</a>
            <a class="nav-item" href="#research-results">04 Research Results</a>
        </div>
        <div class="sidebar-label">Telemetry inputs</div>
        <div class="feature-chip-row">{feature_chips}</div>
        <div class="sidebar-footer">Prototype dataset: synthetic sample alerts. Results are for thesis demonstration and analyst triage support.</div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="topbar">
        <div class="topbar-left">
            <div class="brand-mark">SOC</div>
            <div class="brand-title">AI-SOC Alert Assistant</div>
        </div>
        <div class="topbar-right">
            <span class="status-pill"><span class="radar"></span>Model loaded</span>
            <span class="status-pill">Last scan: live session</span>
            <span class="status-pill">Threat watch: active</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Premium SOC dashboard</div>
        <h1>Instant clarity for alert triage.</h1>
        <p>
            Classify network alerts, score severity, map behavior to MITRE ATT&CK,
            and surface immediate response guidance in one analyst-grade dashboard.
        </p>
    </div>
    <div class="mission-strip">
        <div class="mission-item"><span>Model</span><strong>Random Forest</strong></div>
        <div class="mission-item"><span>Decision</span><strong>BENIGN / ATTACK</strong></div>
        <div class="mission-item"><span>Context</span><strong>MITRE ATT&CK</strong></div>
        <div class="mission-item"><span>Action</span><strong>Response steps</strong></div>
    </div>
    """,
    unsafe_allow_html=True,
)

section(
    "1. Manual Alert Scan",
    "Enter telemetry values for a single network alert. Inputs use monospace styling and unit chips for fast analyst reading.",
)

scan_col, result_col = st.columns([0.78, 1.9], gap="large")

with scan_col:
    st.markdown('<div class="panel"><p class="panel-title">Alert Telemetry</p>', unsafe_allow_html=True)
    st.markdown('<div class="input-shell">duration <span class="unit-chip">ns</span></div>', unsafe_allow_html=True)
    duration = st.number_input("duration", min_value=0, value=10, label_visibility="collapsed")
    st.markdown('<div class="input-shell">src_bytes <span class="unit-chip">bytes</span></div>', unsafe_allow_html=True)
    src_bytes = st.number_input("src_bytes", min_value=0, value=9000, label_visibility="collapsed")
    st.markdown('<div class="input-shell">dst_bytes <span class="unit-chip">bytes</span></div>', unsafe_allow_html=True)
    dst_bytes = st.number_input("dst_bytes", min_value=0, value=100, label_visibility="collapsed")
    st.markdown('<div class="input-shell">packet_count <span class="unit-chip">count</span></div>', unsafe_allow_html=True)
    packet_count = st.number_input("packet_count", min_value=0, value=80, label_visibility="collapsed")
    st.markdown('<div class="input-shell">error_count <span class="unit-chip">count</span></div>', unsafe_allow_html=True)
    error_count = st.number_input("error_count", min_value=0, value=10, label_visibility="collapsed")
    run_manual_check = st.button("Run Threat Scan", type="primary", width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

with result_col:
    if run_manual_check:
        alert_data = pd.DataFrame(
            [
                {
                    "duration": duration,
                    "src_bytes": src_bytes,
                    "dst_bytes": dst_bytes,
                    "packet_count": packet_count,
                    "error_count": error_count,
                }
            ]
        )
        analyzed_alert = analyze_alerts(alert_data, model, FEATURES).iloc[0]
        render_manual_result(analyzed_alert)
        render_limitations_note()
    else:
        st.markdown(
            """
            <div class="panel" style="min-height: 520px; display: grid; place-items: center;">
                <div style="text-align:center; max-width:520px;">
                    <div class="eyebrow">Awaiting scan</div>
                    <h2 class="sg" style="margin:0 0 10px 0;">Threat assessment will appear here.</h2>
                    <p class="small-note">
                        Run a manual scan to reveal the risk gauge, MITRE tags, detection rationale,
                        and incident response steps without leaving the screen.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

section(
    "2. CSV Batch Analysis",
    "Upload a CSV or load the sample dataset. The table provides sortable analysis with risk, MITRE context, and response guidance.",
)

upload_col, sample_col = st.columns([2, 1])
with upload_col:
    st.markdown(
        """
        <div class="dropzone-title"><span class="dropzone-icon">&#8593;</span>Drop CSV file here</div>
        <div class="dropzone-hint">200MB per file &bull; CSV</div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Drop CSV file here", type=["csv"])
with sample_col:
    st.write("")
    st.write("")
    use_sample_data = st.button("Load Sample Dataset", width="stretch", type="secondary")

if uploaded_file is not None or use_sample_data:
    with st.spinner("Analyzing alert stream..."):
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            source_name = uploaded_file.name
        else:
            df = pd.read_csv(SAMPLE_DATA_PATH)
            source_name = "data/sample_alerts.csv"

        df.columns = df.columns.str.strip()
        missing_features = [feature for feature in FEATURES if feature not in df.columns]

        if missing_features:
            st.error(f"CSV file is missing required columns: {missing_features}")
        else:
            st.progress(100)
            st.markdown(
                f'<p class="small-note">Loaded source: <b>{source_name}</b></p>',
                unsafe_allow_html=True,
            )
            results = analyze_alerts(df, model, FEATURES)

            st.markdown("#### Alert Summary")
            render_summary_metrics(results)

            st.markdown("#### AI Analysis Table")
            render_table(results)
            render_limitations_note()

            st.markdown("#### MITRE Mapping Notes")
            for index, row in results.head(5).iterrows():
                with st.expander(f"Alert #{index + 1}: {row['mitre_tactic']} / {row['mitre_technique']}"):
                    st.write(row["mitre_reason"])
                    st.write("Recommendations:")
                    for recommendation in get_incident_recommendations(
                        row["risk_level"],
                        row["mitre_tactic"],
                    ):
                        st.write("- " + recommendation)

section(
    "3. Feature Importance",
    "Ranked model signals show which telemetry fields most influenced the Random Forest classifier.",
)

try:
    importance_df = pd.DataFrame(
        {
            "Feature": FEATURES,
            "Importance": model.feature_importances_,
        }
    ).sort_values(by="Importance", ascending=False)

    top_feature = importance_df.iloc[0]["Feature"]
    feature_col1, feature_col2 = st.columns([1, 1.7], gap="large")
    with feature_col1:
        st.markdown(
            f"""
            <div class="panel">
                <p class="panel-title">Top signal</p>
                <div class="kv">
                    <div class="label">Most important feature</div>
                    <div class="value"><span class="diamond">&#9670;</span>{top_feature}</div>
                </div>
                <p class="small-note" style="margin-top:12px;">
                    Feature importance gives analysts a lightweight explainability layer:
                    what mattered most to the model before the final decision.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(
            importance_df,
            hide_index=True,
            width="stretch",
            column_config={
                "Importance": st.column_config.NumberColumn(
                    "Importance",
                    format="%.2f",
                )
            },
        )
    with feature_col2:
        render_feature_bars(importance_df)
        importance_chart = (
            alt.Chart(importance_df)
            .mark_bar(color="#3b82f6", cornerRadiusEnd=3)
            .encode(
                x=alt.X("Importance:Q", title="Importance", axis=alt.Axis(format=".2f")),
                y=alt.Y("Feature:N", title="Feature", sort="-x"),
                tooltip=[
                    alt.Tooltip("Feature:N", title="Feature"),
                    alt.Tooltip("Importance:Q", title="Importance", format=".2f"),
                ],
            )
            .properties(height=210)
        )
        st.altair_chart(importance_chart, width="stretch")

except Exception as error:
    st.error(f"Feature Importance could not be loaded: {error}")

render_research_results()
