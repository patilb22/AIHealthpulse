import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


BADGE_STYLES = """
<style>
.kpi-card {
    background: #0f1724;
    border: 1px solid #213547;
    border-radius: 18px;
    padding: 18px;
    min-height: 140px;
}
.kpi-title {
    color: #94a3b8;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}
.kpi-value {
    color: #e2e8f0;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 10px;
}
.kpi-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.45rem 0.85rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
}
.badge-green { background: #073b4c; color: #b7f0d8; border: 1px solid #0f766e; }
.badge-yellow { background: #43380f; color: #f8e77a; border: 1px solid #d4b11a; }
.badge-red { background: #4c1515; color: #f9c2c2; border: 1px solid #9b1c1c; }
</style>
"""


def format_badge(label: str, status: str) -> str:
    return f"<span class='kpi-badge badge-{status}'>{label}</span>"


def render_card(title: str, value: str, badge_html: str) -> None:
    st.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>{title}</div>
            <div class='kpi-value'>{value}</div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_timeseries(df: pd.DataFrame, metric: str) -> go.Figure:
    daily = (
        df.sort_values("date")
        .groupby("date")[metric]
        .mean()
        .reset_index()
    )
    daily[f"{metric}_7d"] = daily[metric].rolling(7, min_periods=1).mean()

    fig = go.Figure(
        [
            go.Scatter(
                x=daily["date"],
                y=daily[metric],
                mode="lines+markers",
                name=metric.replace("_", " ").title(),
                line=dict(color="#63cab7", width=2),
                hovertemplate="%{x|%b %d}: %{y:.1f}",
            ),
            go.Scatter(
                x=daily["date"],
                y=daily[f"{metric}_7d"],
                mode="lines",
                name="7-day avg",
                line=dict(color="#f8b400", width=3, dash="dash"),
                hovertemplate="%{x|%b %d}: %{y:.1f}",
            ),
        ]
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=30),
        xaxis_title="Date",
        yaxis_title=metric.replace("_", " ").title(),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_dark",
    )
    return fig


def create_dual_axis(df: pd.DataFrame) -> go.Figure:
    daily = (
        df.sort_values("date")
        .groupby("date")["steps_count", "sleep_hours"]
        .mean()
        .reset_index()
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=daily["date"],
            y=daily["steps_count"],
            name="Avg Steps",
            marker_color="#5d8aa8",
            opacity=0.8,
            hovertemplate="%{x|%b %d}: %{y:.0f} steps",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=daily["date"],
            y=daily["sleep_hours"],
            name="Avg Sleep Hours",
            line=dict(color="#f78fb3", width=3),
            hovertemplate="%{x|%b %d}: %{y:.1f} hrs",
        ),
        secondary_y=True,
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_dark",
    )
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Steps", secondary_y=False)
    fig.update_yaxes(title_text="Sleep Hours", secondary_y=True)
    return fig


def create_condition_breakdown(df: pd.DataFrame) -> go.Figure:
    patients_by_condition = (
        df[["patient_id", "primary_condition"]]
        .drop_duplicates()
        .groupby("primary_condition")
        .size()
        .reset_index(name="patient_count")
        .sort_values("patient_count", ascending=False)
    )
    return px.bar(
        patients_by_condition,
        x="primary_condition",
        y="patient_count",
        color="primary_condition",
        color_discrete_sequence=px.colors.qualitative.Vivid,
        title="Patients by Condition",
        labels={"primary_condition": "Condition", "patient_count": "Patients"},
        template="plotly_dark",
    )


def create_top_symptoms(df: pd.DataFrame) -> go.Figure:
    top_symptoms = (
        df["symptom"]
        .value_counts()
        .nlargest(8)
        .reset_index()
        .rename(columns={"index": "symptom", "symptom": "count"})
    )
    return px.bar(
        top_symptoms,
        x="count",
        y="symptom",
        orientation="h",
        title="Top Symptoms",
        labels={"count": "Records", "symptom": "Symptom"},
        template="plotly_dark",
    )


def create_mood_pie(df: pd.DataFrame) -> go.Figure:
    mood_counts = df["mood"].value_counts().reset_index()
    mood_counts.columns = ["mood", "count"]
    return px.pie(
        mood_counts,
        names="mood",
        values="count",
        title="Mood Distribution",
        hole=0.4,
        template="plotly_dark",
    )


def create_scatter_matrix(df: pd.DataFrame, x_axis: str, y_axis: str) -> go.Figure:
    return px.scatter(
        df,
        x=x_axis,
        y=y_axis,
        color="primary_condition",
        hover_data=["patient_id", "date", "primary_condition"],
        title=f"{x_axis.replace('_', ' ').title()} vs {y_axis.replace('_', ' ').title()}",
        template="plotly_dark",
        opacity=0.8,
    )


def create_heatmap(df: pd.DataFrame) -> go.Figure:
    heatmap_data = (
        df.assign(day_of_week=df["date"].dt.day_name())
        .groupby(["day_of_week", "primary_condition"])["symptom_severity"]
        .mean()
        .reset_index()
    )
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_pivot = heatmap_data.pivot(index="day_of_week", columns="primary_condition", values="symptom_severity").reindex(order)
    fig = px.imshow(
        heatmap_pivot,
        labels={"x": "Condition", "y": "Day of Week", "color": "Avg Severity"},
        color_continuous_scale="RdYlGn_r",
        title="Symptom Severity by Day and Condition",
        aspect="auto",
        template="plotly_dark",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


def render(df: pd.DataFrame | None = None) -> None:
    st.subheader("Dashboard")
    st.markdown("Use the dashboard filter widgets in the sidebar to narrow the dataset by condition and date range.")
    st.markdown(BADGE_STYLES, unsafe_allow_html=True)

    if df is None or df.empty:
        st.warning("No records are available for the selected filters.")
        return

    avg_systolic = df["systolic_bp"].mean()
    avg_diastolic = df["diastolic_bp"].mean()
    avg_glucose = df["blood_glucose_mgdl"].mean()
    avg_heart = df["heart_rate_bpm"].mean()
    avg_spo2 = df["spo2_percent"].mean()
    avg_steps = df["steps_count"].mean()
    avg_sleep = df["sleep_hours"].mean()
    avg_bmi = df["bmi"].mean()
    total_records = len(df)

    bp_status = "red" if avg_systolic > 140 or avg_diastolic > 90 else "yellow" if avg_systolic > 130 or avg_diastolic > 80 else "green"
    glucose_status = "red" if avg_glucose > 126 else "yellow" if avg_glucose > 100 else "green"
    hr_status = "red" if avg_heart > 100 else "yellow" if avg_heart > 90 else "green"
    spo2_status = "red" if avg_spo2 < 94 else "yellow" if avg_spo2 < 96 else "green"
    steps_status = "green" if avg_steps >= 10000 else "yellow" if avg_steps >= 7000 else "red"
    sleep_status = "green" if avg_sleep >= 7 else "yellow" if avg_sleep >= 6 else "red"
    bmi_status = "red" if avg_bmi >= 30 else "yellow" if avg_bmi >= 25 else "green"

    row1 = st.columns(4)
    row2 = st.columns(4)

    with row1[0]:
        render_card(
            "Blood Pressure",
            f"{avg_systolic:.0f}/{avg_diastolic:.0f} mmHg",
            format_badge("BP Status", bp_status),
        )
    with row1[1]:
        render_card(
            "Blood Glucose",
            f"{avg_glucose:.0f} mg/dL",
            format_badge("Glucose", glucose_status),
        )
    with row1[2]:
        render_card(
            "Heart Rate",
            f"{avg_heart:.0f} bpm",
            format_badge("HR", hr_status),
        )
    with row1[3]:
        render_card(
            "SpO2",
            f"{avg_spo2:.1f}%",
            format_badge("Oxygen", spo2_status),
        )

    with row2[0]:
        render_card(
            "Daily Steps",
            f"{avg_steps:.0f}",
            format_badge("Activity", steps_status),
        )
    with row2[1]:
        render_card(
            "Sleep Hours",
            f"{avg_sleep:.1f}",
            format_badge("Rest", sleep_status),
        )
    with row2[2]:
        render_card(
            "BMI",
            f"{avg_bmi:.1f}",
            format_badge("Body Mass", bmi_status),
        )
    with row2[3]:
        render_card(
            "Total Records",
            f"{total_records:,}",
            format_badge("Dataset", "green"),
        )

    st.markdown("---")

    metric_options = [
        "systolic_bp",
        "diastolic_bp",
        "blood_glucose_mgdl",
        "heart_rate_bpm",
        "spo2_percent",
    ]
    selected_metric = st.selectbox("Vital sign to chart", metric_options, index=0)
    st.plotly_chart(create_timeseries(df, selected_metric), use_container_width=True)

    st.markdown("---")
    st.plotly_chart(create_dual_axis(df), use_container_width=True)

    st.markdown("---")
    chart_cols = st.columns(3)
    with chart_cols[0]:
        st.plotly_chart(create_condition_breakdown(df), use_container_width=True)
    with chart_cols[1]:
        st.plotly_chart(create_top_symptoms(df), use_container_width=True)
    with chart_cols[2]:
        st.plotly_chart(create_mood_pie(df), use_container_width=True)

    st.markdown("---")
    scatter_cols = st.columns(2)
    numeric_columns = [
        "systolic_bp",
        "diastolic_bp",
        "blood_glucose_mgdl",
        "heart_rate_bpm",
        "spo2_percent",
        "steps_count",
        "sleep_hours",
        "bmi",
        "calories_burned",
        "weight_kg",
    ]
    x_axis = scatter_cols[0].selectbox("Scatter X axis", numeric_columns, index=0)
    y_axis = scatter_cols[1].selectbox("Scatter Y axis", numeric_columns, index=3)
    st.plotly_chart(create_scatter_matrix(df, x_axis, y_axis), use_container_width=True)

    st.markdown("---")
    st.plotly_chart(create_heatmap(df), use_container_width=True)
