import sys
from pathlib import Path

import altair as alt
import joblib
import pandas as pd
import streamlit as st


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
            :root {
                --bg: #0f1115;
                --panel: #171a20;
                --panel-2: #1e2229;
                --border: #303640;
                --muted: #a8b0bb;
                --text: #f5f7fa;
                --green: #31c48d;
                --red: #f05252;
                --amber: #f59e0b;
                --cyan: #22d3ee;
            }

            .block-container {
                max-width: 1280px;
                padding-top: 2rem;
                padding-bottom: 4rem;
            }

            h1, h2, h3 {
                letter-spacing: 0;
            }

            div[data-testid="stMetric"] {
                background: linear-gradient(180deg, #1a1e25 0%, #14171d 100%);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 14px 16px;
            }

            div[data-testid="stMetric"] label {
                color: var(--muted);
            }

            div[data-testid="stMetricValue"] {
                color: var(--text);
                font-size: 1.45rem;
            }

            .hero {
                border: 1px solid var(--border);
                border-left: 5px solid var(--cyan);
                border-radius: 8px;
                padding: 22px 24px;
                margin-bottom: 22px;
                background:
                    linear-gradient(135deg, rgba(34, 211, 238, 0.14), transparent 34%),
                    linear-gradient(180deg, #171a20 0%, #11141a 100%);
            }

            .hero h1 {
                margin: 0;
                font-size: 2rem;
                line-height: 1.15;
            }

            .hero p {
                margin: 10px 0 0 0;
                max-width: 960px;
                color: var(--muted);
                font-size: 1rem;
                line-height: 1.55;
            }

            .status-row {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 16px;
            }

            .chip {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 6px 10px;
                color: var(--muted);
                background: rgba(255, 255, 255, 0.03);
                font-size: 0.82rem;
            }

            .section-title {
                margin: 28px 0 12px 0;
                padding-bottom: 10px;
                border-bottom: 1px solid var(--border);
            }

            .section-title h2 {
                margin: 0;
                font-size: 1.45rem;
            }

            .section-title p {
                margin: 6px 0 0 0;
                color: var(--muted);
                line-height: 1.5;
            }

            .result-panel {
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 18px;
                background: linear-gradient(180deg, #171a20 0%, #12151a 100%);
                margin-top: 12px;
            }

            .panel-title {
                margin: 0 0 12px 0;
                color: var(--text);
                font-size: 1.08rem;
                font-weight: 700;
            }

            .badge {
                display: inline-block;
                border-radius: 999px;
                padding: 5px 10px;
                font-weight: 700;
                font-size: 0.8rem;
                border: 1px solid transparent;
            }

            .badge-critical {
                color: #ffe4e6;
                background: rgba(240, 82, 82, 0.18);
                border-color: rgba(240, 82, 82, 0.45);
            }

            .badge-high {
                color: #ffedd5;
                background: rgba(245, 158, 11, 0.18);
                border-color: rgba(245, 158, 11, 0.45);
            }

            .badge-medium {
                color: #cffafe;
                background: rgba(34, 211, 238, 0.15);
                border-color: rgba(34, 211, 238, 0.4);
            }

            .badge-low {
                color: #dcfce7;
                background: rgba(49, 196, 141, 0.16);
                border-color: rgba(49, 196, 141, 0.42);
            }

            .kv-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 10px;
                margin-top: 12px;
            }

            .kv {
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 12px 14px;
                background: rgba(255, 255, 255, 0.025);
            }

            .kv .label {
                color: var(--muted);
                font-size: 0.8rem;
                margin-bottom: 5px;
            }

            .kv .value {
                color: var(--text);
                font-size: 1.05rem;
                font-weight: 700;
                word-break: break-word;
            }

            .recommendations {
                margin: 8px 0 0 0;
                padding-left: 20px;
                color: var(--text);
                line-height: 1.65;
            }

            .small-note {
                color: var(--muted);
                font-size: 0.9rem;
                line-height: 1.55;
            }

            .stButton > button {
                border-radius: 8px;
                border: 1px solid var(--border);
                font-weight: 700;
                min-height: 42px;
            }

            .stDataFrame {
                border-radius: 8px;
                overflow: hidden;
            }

            @media (max-width: 900px) {
                .kv-grid {
                    grid-template-columns: 1fr;
                }

                .hero h1 {
                    font-size: 1.6rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(risk_level):
    css_class = {
        "Critical": "badge-critical",
        "High": "badge-high",
        "Medium": "badge-medium",
        "Low": "badge-low",
    }.get(risk_level, "badge-medium")
    return f'<span class="badge {css_class}">{risk_level}</span>'


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


def render_result_panel(prediction, attack_probability, risk_score, risk_level):
    status = "შესაძლო შეტევა დაფიქსირდა" if prediction == 1 else "ტრაფიკი ნორმალურად შეფასდა"
    status_class = "badge-critical" if prediction == 1 else "badge-low"

    st.markdown(
        f"""
        <div class="result-panel">
            <p class="panel-title">AI Classification Result</p>
            <span class="badge {status_class}">{status}</span>
            <div class="kv-grid">
                <div class="kv">
                    <div class="label">Attack probability</div>
                    <div class="value">{attack_probability:.2f}</div>
                </div>
                <div class="kv">
                    <div class="label">Risk score</div>
                    <div class="value">{risk_score:.2f}</div>
                </div>
                <div class="kv">
                    <div class="label">Risk level</div>
                    <div class="value">{risk_badge(risk_level)}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mitre_panel(mitre_result):
    st.markdown(
        f"""
        <div class="result-panel">
            <p class="panel-title">MITRE ATT&CK Mapping</p>
            <div class="kv-grid">
                <div class="kv">
                    <div class="label">Tactic</div>
                    <div class="value">{mitre_result["tactic"]}</div>
                </div>
                <div class="kv">
                    <div class="label">Technique</div>
                    <div class="value">{mitre_result["technique"]}</div>
                </div>
                <div class="kv">
                    <div class="label">Reason</div>
                    <div class="value">{mitre_result["reason"]}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendations(recommendations):
    items = "".join(f"<li>{recommendation}</li>" for recommendation in recommendations)
    st.markdown(
        f"""
        <div class="result-panel">
            <p class="panel-title">Incident Response Recommendations</p>
            <ul class="recommendations">{items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_table(results):
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
        results[columns],
        hide_index=True,
        use_container_width=True,
        column_config={
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
        st.error("დაფიქსირდა Critical ალერტები. საჭიროა დაუყოვნებლივი რეაგირება.")
    elif high_count > 0:
        st.warning("დაფიქსირდა High რისკის ალერტები. საჭიროა შემოწმება.")
    else:
        st.success("მაღალი რისკის ალერტები არ დაფიქსირდა.")


inject_styles()

with st.sidebar:
    st.markdown("### AI-SOC Assistant")
    st.caption("Prototype status")
    st.success("Model loaded" if MODEL_PATH.exists() else "Model missing")
    st.markdown("**Workflow**")
    st.markdown(
        """
        1. Classify alert traffic
        2. Calculate risk score
        3. Map to MITRE ATT&CK
        4. Recommend response steps
        """
    )
    st.markdown("**Model inputs**")
    for feature in FEATURES:
        st.code(feature, language=None)
    st.caption("Prototype dataset: synthetic sample alerts")

st.markdown(
    """
    <div class="hero">
        <h1>AI-SOC Alert Assistant</h1>
        <p>
            პროფესიონალური SOC dashboard, რომელიც აერთიანებს AI კლასიფიკაციას,
            risk scoring-ს, explainability-ს, MITRE ATT&CK mapping-ს და
            incident response რეკომენდაციებს.
        </p>
        <div class="status-row">
            <span class="chip">Random Forest model</span>
            <span class="chip">Risk-based triage</span>
            <span class="chip">MITRE ATT&CK context</span>
            <span class="chip">Response guidance</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    st.error("მოდელი ვერ მოიძებნა. ჯერ გაუშვი: python src\\train_model.py")
    st.stop()

section(
    "1. ერთი ალერტის ხელით შემოწმება",
    "შეიყვანე ქსელური ალერტის ძირითადი მახასიათებლები და მიიღე classification, risk score, MITRE context და response steps.",
)

input_col1, input_col2, input_col3, input_col4, input_col5 = st.columns(5)
with input_col1:
    duration = st.number_input("duration", min_value=0, value=10)
with input_col2:
    src_bytes = st.number_input("src_bytes", min_value=0, value=9000)
with input_col3:
    dst_bytes = st.number_input("dst_bytes", min_value=0, value=100)
with input_col4:
    packet_count = st.number_input("packet_count", min_value=0, value=80)
with input_col5:
    error_count = st.number_input("error_count", min_value=0, value=10)

run_manual_check = st.button("ალერტის შემოწმება", type="primary")

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
    recommendations = get_incident_recommendations(
        analyzed_alert["risk_level"],
        analyzed_alert["mitre_tactic"],
    )

    render_result_panel(
        analyzed_alert["prediction"],
        analyzed_alert["attack_probability"],
        analyzed_alert["risk_score"],
        analyzed_alert["risk_level"],
    )
    render_mitre_panel(
        {
            "tactic": analyzed_alert["mitre_tactic"],
            "technique": analyzed_alert["mitre_technique"],
            "reason": analyzed_alert["mitre_reason"],
        }
    )
    render_recommendations(recommendations)

section(
    "2. CSV ფაილის ატვირთვა და batch analysis",
    "ატვირთე alert dataset ან გამოიყენე სატესტო CSV. სისტემა თითოეულ ჩანაწერს მიანიჭებს prediction-ს, risk level-ს, MITRE context-ს და response რეკომენდაციებს.",
)

upload_col, sample_col = st.columns([2, 1])
with upload_col:
    uploaded_file = st.file_uploader("ატვირთე CSV ფაილი", type=["csv"])
with sample_col:
    st.write("")
    st.write("")
    use_sample_data = st.button("სატესტო CSV-ის ჩატვირთვა")

if uploaded_file is not None or use_sample_data:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        source_name = uploaded_file.name
    else:
        df = pd.read_csv(SAMPLE_DATA_PATH)
        source_name = "data/sample_alerts.csv"

    missing_features = [feature for feature in FEATURES if feature not in df.columns]

    if missing_features:
        st.error(f"CSV ფაილში აკლია ეს სვეტები: {missing_features}")
    else:
        st.markdown(f'<p class="small-note">Loaded source: <b>{source_name}</b></p>', unsafe_allow_html=True)
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
    "3. მოდელის ახსნადობა — Feature Importance",
    "Random Forest მოდელის feature importance აჩვენებს, რომელმა მახასიათებლებმა მოახდინა ყველაზე დიდი გავლენა classification შედეგზე.",
)

try:
    importance_df = pd.DataFrame(
        {
            "Feature": FEATURES,
            "Importance": model.feature_importances_,
        }
    ).sort_values(by="Importance", ascending=False)

    top_feature = importance_df.iloc[0]["Feature"]
    feature_col1, feature_col2 = st.columns([1, 2])
    with feature_col1:
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
        st.info(
            f"მოდელის მიხედვით ყველაზე მნიშვნელოვანი მახასიათებელია: {top_feature}."
        )
    with feature_col2:
        importance_chart = (
            alt.Chart(importance_df)
            .mark_bar(color="#31c48d", cornerRadiusEnd=4)
            .encode(
                x=alt.X("Importance:Q", title="Importance", axis=alt.Axis(format=".2f")),
                y=alt.Y("Feature:N", title="Feature", sort="-x"),
                tooltip=[
                    alt.Tooltip("Feature:N", title="Feature"),
                    alt.Tooltip("Importance:Q", title="Importance", format=".2f"),
                ],
            )
            .properties(height=320)
        )
        st.altair_chart(importance_chart, use_container_width=True)

except Exception as error:
    st.error(f"Feature Importance ვერ ჩაიტვირთა: {error}")
