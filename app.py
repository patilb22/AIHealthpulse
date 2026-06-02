"""
HealthPulse AI — Streamlit Health Tracker Dashboard
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import json
from datetime import datetime, timedelta

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HealthPulse AI",
    page_icon="💓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  .main { background: #0d1117; }
  .block-container { padding: 1.5rem 2rem; max-width: 1400px; }

  /* Header */
  .hp-header {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(99,202,183,0.2);
  }
  .hp-header h1 { font-family: 'Space Mono', monospace; color: #63cab7; margin: 0; font-size: 2rem; }
  .hp-header p { color: #8ba7b5; margin: 0.3rem 0 0; font-size: 0.95rem; }

  /* Metric cards */
  .metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s;
  }
  .metric-card:hover { border-color: #63cab7; }
  .metric-label { color: #8b949e; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.3rem; }
  .metric-value { color: #e6edf3; font-family: 'Space Mono', monospace; font-size: 1.8rem; font-weight: 700; }
  .metric-delta { font-size: 0.8rem; margin-top: 0.2rem; }
  .delta-up { color: #3fb950; }
  .delta-down { color: #f85149; }
  .delta-neutral { color: #8b949e; }

  /* Section headers */
  .section-title {
    font-family: 'Space Mono', monospace;
    color: #63cab7;
    font-size: 1rem;
    border-bottom: 1px solid #30363d;
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
  }

  /* AI Chat */
  .ai-bubble {
    background: #1c2a38;
    border-left: 3px solid #63cab7;
    border-radius: 0 10px 10px 0;
    padding: 0.8rem 1rem;
    margin-bottom: 0.7rem;
    color: #c9d1d9;
    font-size: 0.9rem;
    line-height: 1.6;
  }
  .user-bubble {
    background: #1f2937;
    border-left: 3px solid #5865f2;
    border-radius: 0 10px 10px 0;
    padding: 0.8rem 1rem;
    margin-bottom: 0.7rem;
    color: #c9d1d9;
    font-size: 0.9rem;
  }
  .bubble-label { font-size: 0.72rem; color: #8b949e; margin-bottom: 0.3rem; text-transform: uppercase; letter-spacing: 1px; }

  /* Sidebar */
  [data-testid="stSidebar"] { background: #0d1117; border-right: 1px solid #30363d; }
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stMultiselect label,
  [data-testid="stSidebar"] .stSlider label { color: #8b949e; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.8px; }

  /* Status badges */
  .badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
  .badge-green { background: rgba(63,185,80,0.15); color: #3fb950; border: 1px solid rgba(63,185,80,0.3); }
  .badge-red { background: rgba(248,81,73,0.15); color: #f85149; border: 1px solid rgba(248,81,73,0.3); }
  .badge-yellow { background: rgba(210,153,34,0.15); color: #d2a520; border: 1px solid rgba(210,153,34,0.3); }

  /* Plotly dark overrides */
  .js-plotly-plot { border-radius: 10px; }

  /* Dataframe */
  [data-testid="stDataFrame"] { border-radius: 10px; border: 1px solid #30363d; }
  stButton > button { border-radius: 8px; font-family: 'DM Sans', sans-serif; }
</style>
""", unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    paper_bgcolor="#161b22",
    plot_bgcolor="#161b22",
    font_color="#c9d1d9",
    font_family="DM Sans",
    margin=dict(l=20, r=20, t=40, b=20),
    colorway=["#63cab7", "#5865f2", "#f85149", "#d2a520", "#3fb950", "#a371f7"],
)

# ── Helper functions ──────────────────────────────────────────────────────────

def bp_status(systolic, diastolic):
    if systolic >= 140 or diastolic >= 90: return "High", "badge-red"
    if systolic >= 130 or diastolic >= 80: return "Elevated", "badge-yellow"
    return "Normal", "badge-green"

def glucose_status(g):
    if g >= 126: return "High", "badge-red"
    if g >= 100: return "Pre-diabetic", "badge-yellow"
    return "Normal", "badge-green"

def bmi_status(b):
    if b >= 30: return "Obese", "badge-red"
    if b >= 25: return "Overweight", "badge-yellow"
    if b < 18.5: return "Underweight", "badge-yellow"
    return "Normal", "badge-green"

@st.cache_data
def load_data(uploaded=None):
    if uploaded is not None:
        df = pd.read_csv(uploaded)
    else:
        try:
            df = pd.read_csv("health_tracker_data.csv")
        except FileNotFoundError:
            df = pd.read_csv("data/health_tracker_data.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["dow"] = df["date"].dt.day_name()
    return df

def call_claude_api(messages, system_prompt):
    """Call Anthropic API for AI insights."""
    import urllib.request
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 800,
        "system": system_prompt,
        "messages": messages,
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())["content"][0]["text"]
    except Exception as e:
        return f"⚠️ API call failed: {e}\n\nTo enable AI insights, add your Anthropic API key to Streamlit secrets."

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💓 HealthPulse AI")
    st.markdown("---")

    uploaded_file = st.file_uploader("📂 Upload CSV Dataset", type=["csv"])
    df_raw = load_data(uploaded_file)

    st.markdown("#### Filters")
    patients = ["All Patients"] + sorted(
        df_raw["name"].fillna("Unknown").astype(str).unique().tolist()
    )
    selected_patient = st.selectbox("Patient", patients)

    conditions = ["All"] + sorted(
        df_raw["primary_condition"].fillna("Unknown").astype(str).unique().tolist()
    )
    selected_condition = st.selectbox("Condition", conditions)

    date_range = st.date_input(
        "Date Range",
        value=(df_raw["date"].min().date(), df_raw["date"].max().date()),
        min_value=df_raw["date"].min().date(),
        max_value=df_raw["date"].max().date(),
    )

    gender_filter = st.multiselect("Gender", ["M", "F"], default=["M", "F"])
    age_range = st.slider("Age Range", 18, 90, (df_raw["age"].min(), df_raw["age"].max()))

    st.markdown("---")
    page = st.radio("Navigation", ["📊 Dashboard", "🩺 Patient Profile", "🤖 AI Insights", "📋 Raw Data"])

# ── Filter Data ───────────────────────────────────────────────────────────────
df = df_raw.copy()
if selected_patient != "All Patients":
    df = df[df["name"] == selected_patient]
if selected_condition != "All":
    df = df[df["primary_condition"] == selected_condition]
if len(date_range) == 2:
    df = df[(df["date"] >= pd.Timestamp(date_range[0])) & (df["date"] <= pd.Timestamp(date_range[1]))]
df = df[df["gender"].isin(gender_filter)]
df = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hp-header">
  <h1>💓 HealthPulse AI</h1>
  <p>Medical Health Tracker · AI-Powered Insights · Interactive Dashboard</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if "Dashboard" in page:

    # KPI Row
    avg_sys = df["systolic_bp"].mean()
    avg_dia = df["diastolic_bp"].mean()
    avg_hr = df["heart_rate_bpm"].mean()
    avg_glucose = df["blood_glucose_mgdl"].mean()
    avg_steps = df["steps_count"].mean()
    avg_sleep = df["sleep_hours"].mean()
    avg_spo2 = df["spo2_percent"].mean()
    avg_bmi = df["bmi"].mean()

    bp_label, bp_badge = bp_status(avg_sys, avg_dia)
    gl_label, gl_badge = glucose_status(avg_glucose)
    bmi_label, bmi_badge = bmi_status(avg_bmi)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">Blood Pressure</div>
          <div class="metric-value">{avg_sys:.0f}/{avg_dia:.0f}</div>
          <div class="metric-delta"><span class="badge {bp_badge}">{bp_label}</span></div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">Blood Glucose (mg/dL)</div>
          <div class="metric-value">{avg_glucose:.0f}</div>
          <div class="metric-delta"><span class="badge {gl_badge}">{gl_label}</span></div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">Avg Heart Rate (bpm)</div>
          <div class="metric-value">{avg_hr:.0f}</div>
          <div class="metric-delta"><span class="badge badge-green">Normal</span></div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">SpO₂ %</div>
          <div class="metric-value">{avg_spo2:.1f}%</div>
          <div class="metric-delta"><span class="badge {'badge-green' if avg_spo2 >= 95 else 'badge-red'}">{'Normal' if avg_spo2 >= 95 else 'Low'}</span></div>
        </div>""", unsafe_allow_html=True)

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">Daily Steps</div>
          <div class="metric-value">{avg_steps:,.0f}</div>
          <div class="metric-delta"><span class="badge {'badge-green' if avg_steps >= 7500 else 'badge-yellow'}">{'Active' if avg_steps >= 7500 else 'Low'}</span></div>
        </div>""", unsafe_allow_html=True)
    with col6:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">Sleep Hours</div>
          <div class="metric-value">{avg_sleep:.1f} h</div>
          <div class="metric-delta"><span class="badge {'badge-green' if 7 <= avg_sleep <= 9 else 'badge-yellow'}">{'Healthy' if 7 <= avg_sleep <= 9 else 'Review'}</span></div>
        </div>""", unsafe_allow_html=True)
    with col7:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">BMI</div>
          <div class="metric-value">{avg_bmi:.1f}</div>
          <div class="metric-delta"><span class="badge {bmi_badge}">{bmi_label}</span></div>
        </div>""", unsafe_allow_html=True)
    with col8:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">Total Records</div>
          <div class="metric-value">{len(df):,}</div>
          <div class="metric-delta"><span class="badge badge-green">{df['name'].nunique()} Patients</span></div>
        </div>""", unsafe_allow_html=True)

    # ── Row 2: Time Series ────────────────────────────────────────────────────
    st.markdown('<p class="section-title">📈 Vital Signs Over Time</p>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        ts_metric = st.selectbox("Metric", ["systolic_bp", "diastolic_bp", "heart_rate_bpm",
                                             "blood_glucose_mgdl", "spo2_percent", "body_temp_celsius"])
        agg = df.groupby("date")[ts_metric].mean().reset_index()
        rolling = agg[ts_metric].rolling(7).mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=agg["date"], y=agg[ts_metric], name="Daily", line=dict(color="#63cab7", width=1), opacity=0.4))
        fig.add_trace(go.Scatter(x=agg["date"], y=rolling, name="7-day avg", line=dict(color="#63cab7", width=2.5)))
        fig.update_layout(**PLOT_LAYOUT, title=f"{ts_metric.replace('_', ' ').title()} Trend", height=280,
                          xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        ts2 = df.groupby("date")[["steps_count", "sleep_hours", "calories_burned"]].mean().reset_index()
        fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08)
        fig2.add_trace(go.Bar(x=ts2["date"], y=ts2["steps_count"], name="Steps", marker_color="#5865f2"), row=1, col=1)
        fig2.add_trace(go.Scatter(x=ts2["date"], y=ts2["sleep_hours"].rolling(7).mean(),
                                   name="Sleep (7d avg)", line=dict(color="#d2a520", width=2)), row=2, col=1)
        fig2.update_layout(**PLOT_LAYOUT, title="Steps & Sleep", height=280,
                           xaxis2=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"), yaxis2=dict(gridcolor="#21262d"))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 3: Distributions ──────────────────────────────────────────────────
    st.markdown('<p class="section-title">📊 Health Distributions & Patterns</p>', unsafe_allow_html=True)
    col_c, col_d, col_e = st.columns(3)

    with col_c:
        cond_counts = df.groupby("primary_condition")["patient_id"].nunique().reset_index()
        cond_counts.columns = ["Condition", "Patients"]
        fig3 = px.bar(cond_counts.sort_values("Patients"), x="Patients", y="Condition", orientation="h",
                      color="Patients", color_continuous_scale="Teal")
        fig3.update_layout(**PLOT_LAYOUT, title="Patients by Condition", height=260, showlegend=False,
                           coloraxis_showscale=False, xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"))
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        symptom_df = df[df["symptom"] != "None"].groupby("symptom").size().reset_index(name="Count")
        symptom_df = symptom_df.sort_values("Count", ascending=False).head(8)
        fig4 = px.bar(symptom_df, x="Count", y="symptom", orientation="h", color="Count",
                      color_continuous_scale="Reds_r")
        fig4.update_layout(**PLOT_LAYOUT, title="Top Symptoms", height=260, showlegend=False,
                           coloraxis_showscale=False, xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"))
        st.plotly_chart(fig4, use_container_width=True)

    with col_e:
        mood_counts = df["mood"].value_counts().reset_index()
        mood_counts.columns = ["Mood", "Count"]
        mood_order = ["Excellent", "Good", "Fair", "Poor", "Very Poor"]
        mood_colors = {"Excellent": "#3fb950", "Good": "#63cab7", "Fair": "#d2a520", "Poor": "#f85149", "Very Poor": "#b22222"}
        fig5 = px.pie(mood_counts, values="Count", names="Mood",
                      color="Mood", color_discrete_map=mood_colors, hole=0.5)
        fig5.update_layout(**PLOT_LAYOUT, title="Mood Distribution", height=260)
        fig5.update_traces(textposition="inside", textinfo="percent")
        st.plotly_chart(fig5, use_container_width=True)

    # ── Row 4: Scatter & Heatmap ───────────────────────────────────────────────
    col_f, col_g = st.columns(2)
    with col_f:
        scatter_x = st.selectbox("X Axis", ["bmi", "age", "sleep_hours", "steps_count"], key="sx")
        scatter_y = st.selectbox("Y Axis", ["systolic_bp", "blood_glucose_mgdl", "heart_rate_bpm"], key="sy")
        sample = df.sample(min(800, len(df)), random_state=42)
        fig6 = px.scatter(sample, x=scatter_x, y=scatter_y, color="primary_condition",
                          hover_data=["name", "age", "gender"], opacity=0.7,
                          color_discrete_sequence=["#63cab7","#5865f2","#f85149","#d2a520","#3fb950","#a371f7","#f0883e"])
        fig6.update_layout(**PLOT_LAYOUT, title=f"{scatter_x} vs {scatter_y}", height=300,
                           xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"))
        st.plotly_chart(fig6, use_container_width=True)

    with col_g:
        pivot = df.groupby(["dow", "primary_condition"])["symptom_severity"].mean().unstack(fill_value=0)
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        pivot = pivot.reindex([d for d in day_order if d in pivot.index])
        fig7 = px.imshow(pivot, color_continuous_scale="Teal", aspect="auto")
        fig7.update_layout(**PLOT_LAYOUT, title="Avg Symptom Severity by Day & Condition", height=300)
        st.plotly_chart(fig7, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PATIENT PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif "Patient" in page:
    st.markdown('<p class="section-title">🩺 Individual Patient View</p>', unsafe_allow_html=True)

    if selected_patient == "All Patients":
        st.info("Select a specific patient from the sidebar to see their profile.")
    else:
        pt_df = df[df["name"] == selected_patient].sort_values("date")
        if pt_df.empty:
            st.warning("No data for this patient in the selected range.")
        else:
            info = pt_df.iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Name", selected_patient)
            c2.metric("Age", int(info["age"]))
            c3.metric("Gender", info["gender"])
            c4.metric("Condition", info["primary_condition"])

            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=pt_df["date"], y=pt_df["systolic_bp"], name="Systolic", line=dict(color="#f85149")))
                fig.add_trace(go.Scatter(x=pt_df["date"], y=pt_df["diastolic_bp"], name="Diastolic", line=dict(color="#63cab7")))
                fig.add_hline(y=140, line_dash="dot", line_color="#d2a520", annotation_text="High BP threshold")
                fig.update_layout(**PLOT_LAYOUT, title="Blood Pressure History", height=280,
                                  xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=pt_df["date"], y=pt_df["blood_glucose_mgdl"],
                                          name="Glucose", line=dict(color="#d2a520")))
                fig2.add_hline(y=126, line_dash="dot", line_color="#f85149", annotation_text="Diabetic threshold")
                fig2.update_layout(**PLOT_LAYOUT, title="Blood Glucose History", height=280,
                                   xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"))
                st.plotly_chart(fig2, use_container_width=True)

            col3, col4 = st.columns(2)
            with col3:
                fig3 = px.scatter(pt_df, x="date", y="steps_count", color="mood",
                                  color_discrete_sequence=["#3fb950","#63cab7","#d2a520","#f85149","#b22222"])
                fig3.update_layout(**PLOT_LAYOUT, title="Daily Steps by Mood", height=260,
                                   xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"))
                st.plotly_chart(fig3, use_container_width=True)

            with col4:
                fig4 = go.Figure()
                fig4.add_trace(go.Scatter(x=pt_df["date"], y=pt_df["weight_kg"],
                                          fill="tozeroy", name="Weight", line=dict(color="#a371f7")))
                fig4.update_layout(**PLOT_LAYOUT, title="Weight Over Time", height=260,
                                   xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"))
                st.plotly_chart(fig4, use_container_width=True)

            st.markdown("**Recent Records**")
            cols_show = ["date","systolic_bp","diastolic_bp","heart_rate_bpm","blood_glucose_mgdl",
                         "spo2_percent","steps_count","sleep_hours","mood","symptom","medication_taken"]
            st.dataframe(pt_df[cols_show].tail(30).set_index("date"), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AI INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
elif "AI" in page:
    st.markdown('<p class="section-title">🤖 AI-Powered Health Insights</p>', unsafe_allow_html=True)
    st.markdown("Ask questions about the health data in natural language. Powered by Claude.")

    # Prepare data summary
    summary_stats = {
        "total_patients": df["name"].nunique(),
        "total_records": len(df),
        "date_range": f"{df['date'].min().date()} to {df['date'].max().date()}",
        "conditions": df["primary_condition"].value_counts().to_dict(),
        "avg_systolic": round(df["systolic_bp"].mean(), 1),
        "avg_diastolic": round(df["diastolic_bp"].mean(), 1),
        "avg_glucose": round(df["blood_glucose_mgdl"].mean(), 1),
        "avg_heart_rate": round(df["heart_rate_bpm"].mean(), 1),
        "avg_steps": round(df["steps_count"].mean(), 0),
        "avg_sleep": round(df["sleep_hours"].mean(), 2),
        "avg_bmi": round(df["bmi"].mean(), 1),
        "top_symptoms": df[df["symptom"] != "None"]["symptom"].value_counts().head(5).to_dict(),
        "mood_distribution": df["mood"].value_counts().to_dict(),
        "medication_adherence": df[df["medication"] != "None"]["medication_taken"].value_counts(normalize=True).to_dict(),
    }

    SYSTEM_PROMPT = f"""You are HealthPulse AI, a clinical data analyst assistant.
You have access to an aggregated health tracker dataset:
{json.dumps(summary_stats, indent=2)}

Rules:
- Be concise, clinically accurate, and evidence-based.
- Reference specific numbers from the data.
- Flag concerning patterns clearly.
- Never diagnose — always recommend consulting a physician.
- Format your response with clear sections using markdown.
- Keep responses under 300 words.
"""

    # Suggested questions
    st.markdown("**Suggested questions:**")
    suggested = [
        "What are the most common health concerns in this dataset?",
        "Which patients might be at risk for cardiovascular issues?",
        "How does sleep affect blood pressure in this cohort?",
        "What patterns do you see in medication adherence?",
        "Summarize the overall health of this patient population.",
    ]
    q_cols = st.columns(len(suggested))
    for i, q in enumerate(suggested):
        if q_cols[i].button(q[:35] + "…", key=f"sq{i}"):
            st.session_state["ai_input"] = q

    # Chat interface
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Your question:", value=st.session_state.get("ai_input", ""),
                                placeholder="e.g. Which condition has the worst blood pressure control?",
                                key="chat_input")
    if "ai_input" in st.session_state:
        del st.session_state["ai_input"]

    col_send, col_clear = st.columns([1, 5])
    with col_send:
        send = st.button("Ask →", type="primary")
    with col_clear:
        if st.button("Clear chat"):
            st.session_state.chat_history = []
            st.rerun()

    if send and user_input.strip():
        with st.spinner("Analyzing health data…"):
            messages = st.session_state.chat_history + [{"role": "user", "content": user_input}]
            response = call_claude_api(messages, SYSTEM_PROMPT)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Render chat
    for msg in reversed(st.session_state.chat_history):
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble"><div class="bubble-label">You</div>{msg["content"]}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-bubble"><div class="bubble-label">HealthPulse AI</div>{msg["content"]}</div>',
                        unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown("""<div class="ai-bubble">
          <div class="bubble-label">HealthPulse AI</div>
          👋 Hello! I can analyze the health tracker data and answer clinical questions. 
          Try one of the suggested questions above, or ask your own.
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: RAW DATA
# ══════════════════════════════════════════════════════════════════════════════
elif "Raw" in page:
    st.markdown('<p class="section-title">📋 Raw Data Explorer</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("Search patient name:")
    with col2:
        cols_to_show = st.multiselect("Columns", df.columns.tolist(),
                                       default=["date","name","primary_condition","systolic_bp",
                                                "diastolic_bp","heart_rate_bpm","blood_glucose_mgdl",
                                                "steps_count","sleep_hours","mood","symptom"])

    display_df = df.copy()
    if search:
        display_df = display_df[display_df["name"].str.contains(search, case=False)]

    if cols_to_show:
        display_df = display_df[cols_to_show]

    st.markdown(f"Showing **{len(display_df):,}** records")
    st.dataframe(display_df, use_container_width=True, height=500)

    csv_bytes = display_df.to_csv(index=False).encode()
    st.download_button("⬇️ Download filtered data", data=csv_bytes,
                        file_name="healthpulse_filtered.csv", mime="text/csv")

    st.markdown("**Dataset Statistics**")
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""<div style='text-align:center; color: #8b949e; font-size: 0.78rem; padding: 1rem 0;'>
  HealthPulse AI · Demo Dataset · Not for clinical use · Built with Streamlit + Plotly + Claude AI
</div>""", unsafe_allow_html=True)
