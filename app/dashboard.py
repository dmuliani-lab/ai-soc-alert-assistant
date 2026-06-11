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
SAMPLE_DATA_PATH = ROOT_DIR / "data" / "sample_alerts.csv"
FEATURES = [
    "duration",
    "src_bytes",
    "dst_bytes",
    "packet_count",
    "error_count",
]


st.set_page_config(
    page_title="AI-SOC Alert Assistant",
    page_icon="🛡️",
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
    st.markdown(
        f"""
        <div class="section-title">
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_color(score):
    if score >= 85:
        return "#E84545"
    if score >= 70:
        return "#E8A838"
    if score >= 40:
        return "#E8A838"
    return "#48D597"


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


def analyze_alerts(df, model):
    x = df[FEATURES]
    predictions = model.predict(x)
    probabilities = model.predict_proba(x)[:, 1]

    results = df.copy()
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
                    border: 1px solid #1E2D42;
                    border-radius: 8px;
                    background: rgba(14, 21, 32, 0.78);
                    width: 100%;
                    height: 245px;
                    display: grid;
                    place-items: center;
                }}
                .gauge-ring {{
                    width: 198px;
                    height: 198px;
                    border-radius: 50%;
                    display: grid;
                    place-items: center;
                    background:
                        radial-gradient(circle at center, #0E1520 0 57%, transparent 58%),
                        conic-gradient({risk_color(analyzed_alert["risk_score"])} {analyzed_alert["risk_score"] * 3.6:.1f}deg, #162133 0deg);
                    box-shadow: inset 0 0 0 1px rgba(61, 158, 255, 0.15), 0 0 28px rgba(61, 158, 255, 0.08);
                }}
                .gauge-inner {{
                    width: 138px;
                    height: 138px;
                    border-radius: 50%;
                    display: grid;
                    place-items: center;
                    text-align: center;
                    border: 1px solid #1E2D42;
                    background: #0A0F18;
                }}
                .score {{
                    display: block;
                    font-family: "Space Grotesk", sans-serif;
                    font-size: 48px;
                    line-height: 1;
                    color: #E8EDF5;
                    font-weight: 700;
                }}
                .label {{
                    display: block;
                    margin-top: 8px;
                    color: #5C7090;
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
        use_container_width=True,
        column_config={
            "duration": st.column_config.NumberColumn("duration", help="ms"),
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
        diamond = '<span class="diamond">◆</span>' if index == 0 else ""
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


inject_styles()

try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    st.error("Model file was not found. Run `python src\\train_model.py` first.")
    st.stop()

with st.sidebar:
    st.markdown("### Mission Control")
    st.caption("AI-SOC Alert Assistant")
    st.markdown("**Navigation**")
    st.markdown(
        """
        - Manual alert scan
        - CSV batch analysis
        - Feature importance
        """
    )
    st.markdown("**Telemetry inputs**")
    for feature in FEATURES:
        st.code(feature, language=None)
    st.caption("Prototype dataset: synthetic sample alerts")

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
        <div class="eyebrow">Deep space command center</div>
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
    st.markdown('<div class="input-shell">duration <span class="unit-chip">ms</span></div>', unsafe_allow_html=True)
    duration = st.number_input("duration", min_value=0, value=10, label_visibility="collapsed")
    st.markdown('<div class="input-shell">src_bytes <span class="unit-chip">bytes</span></div>', unsafe_allow_html=True)
    src_bytes = st.number_input("src_bytes", min_value=0, value=9000, label_visibility="collapsed")
    st.markdown('<div class="input-shell">dst_bytes <span class="unit-chip">bytes</span></div>', unsafe_allow_html=True)
    dst_bytes = st.number_input("dst_bytes", min_value=0, value=100, label_visibility="collapsed")
    st.markdown('<div class="input-shell">packet_count <span class="unit-chip">count</span></div>', unsafe_allow_html=True)
    packet_count = st.number_input("packet_count", min_value=0, value=80, label_visibility="collapsed")
    st.markdown('<div class="input-shell">error_count <span class="unit-chip">count</span></div>', unsafe_allow_html=True)
    error_count = st.number_input("error_count", min_value=0, value=10, label_visibility="collapsed")
    run_manual_check = st.button("Run Threat Scan", type="primary", use_container_width=True)
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
        analyzed_alert = analyze_alerts(alert_data, model).iloc[0]
        render_manual_result(analyzed_alert)
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
    uploaded_file = st.file_uploader("Drop CSV file here", type=["csv"])
with sample_col:
    st.write("")
    st.write("")
    use_sample_data = st.button("Load Sample Dataset", use_container_width=True)

if uploaded_file is not None or use_sample_data:
    with st.spinner("Analyzing alert stream..."):
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            source_name = uploaded_file.name
        else:
            df = pd.read_csv(SAMPLE_DATA_PATH)
            source_name = "data/sample_alerts.csv"

        missing_features = [feature for feature in FEATURES if feature not in df.columns]

        if missing_features:
            st.error(f"CSV file is missing required columns: {missing_features}")
        else:
            st.progress(100)
            st.markdown(
                f'<p class="small-note">Loaded source: <b>{source_name}</b></p>',
                unsafe_allow_html=True,
            )
            results = analyze_alerts(df, model)

            st.markdown("#### Alert Summary")
            render_summary_metrics(results)

            st.markdown("#### AI Analysis Table")
            render_table(results)

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
                    <div class="value"><span class="diamond">◆</span>{top_feature}</div>
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
            use_container_width=True,
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
            .mark_bar(color="#3D9EFF", cornerRadiusEnd=3)
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
        st.altair_chart(importance_chart, use_container_width=True)

except Exception as error:
    st.error(f"Feature Importance could not be loaded: {error}")
