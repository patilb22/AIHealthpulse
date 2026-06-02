import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def get_name_column(df: pd.DataFrame) -> str:
    return "patient_name" if "patient_name" in df.columns else "name"


def render_patient_card(patient: pd.Series) -> None:
    st.markdown(
        f"""
        <div style='background:#0f1724;border:1px solid #213547;border-radius:18px;padding:18px;'>
            <h3 style='margin:0 0 10px;color:#cbd5e1;'>Demographics</h3>
            <div style='display:flex;gap:14px;flex-wrap:wrap;'>
                <div><strong>Name:</strong> {patient['name']}</div>
                <div><strong>Patient ID:</strong> {patient['patient_id']}</div>
                <div><strong>Age:</strong> {patient['age']}</div>
                <div><strong>Gender:</strong> {patient['gender']}</div>
                <div><strong>Condition:</strong> {patient['primary_condition']}</div>
                <div><strong>Location:</strong> {patient.get('city', '')}{' ' + patient.get('state', '') if patient.get('state') else ''}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_bp_chart(patient_df: pd.DataFrame) -> go.Figure:
    patient_df = patient_df.sort_values("date")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=patient_df["date"],
            y=patient_df["systolic_bp"],
            name="Systolic",
            mode="lines+markers",
            line=dict(color="#ff7f50", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=patient_df["date"],
            y=patient_df["diastolic_bp"],
            name="Diastolic",
            mode="lines+markers",
            line=dict(color="#1f77b4", width=2),
        )
    )
    fig.add_hline(y=140, line_dash="dash", line_color="#f94144", annotation_text="Systolic Alert", annotation_position="top left")
    fig.add_hline(y=90, line_dash="dash", line_color="#f8961e", annotation_text="Diastolic Alert", annotation_position="bottom left")
    fig.update_layout(
        title="Blood Pressure History",
        xaxis_title="Date",
        yaxis_title="mmHg",
        template="plotly_dark",
        margin=dict(l=10, r=10, t=35, b=20),
    )
    return fig


def create_glucose_chart(patient_df: pd.DataFrame) -> go.Figure:
    patient_df = patient_df.sort_values("date")
    fig = px.line(
        patient_df,
        x="date",
        y="blood_glucose_mgdl",
        markers=True,
        labels={"blood_glucose_mgdl": "Glucose (mg/dL)", "date": "Date"},
        title="Blood Glucose History",
        template="plotly_dark",
    )
    fig.add_hline(y=126, line_dash="dash", line_color="#f94144", annotation_text="Diabetes Alert", annotation_position="top left")
    fig.update_layout(margin=dict(l=10, r=10, t=35, b=20))
    return fig


def create_activity_chart(patient_df: pd.DataFrame) -> go.Figure:
    patient_df = patient_df.sort_values("date")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=patient_df["date"],
            y=patient_df["steps_count"],
            name="Steps",
            marker_color="#5f8ea0",
            opacity=0.7,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=patient_df["date"],
            y=patient_df["sleep_hours"],
            name="Sleep Hours",
            line=dict(color="#9d4edd", width=3),
            mode="lines+markers",
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="Steps and Sleep History",
        xaxis_title="Date",
        yaxis=dict(title="Steps"),
        yaxis2=dict(title="Sleep Hours", overlaying="y", side="right"),
        template="plotly_dark",
        margin=dict(l=10, r=10, t=35, b=20),
    )
    return fig


def render(df=None) -> None:
    st.subheader("Patient Profile")
    st.write("Use the patient dropdown below to view individual demographic details and clinical history.")

    if df is None or df.empty:
        st.warning("No data available for patient profile view.")
        return

    name_col = get_name_column(df)
    patients = ["Select a patient"] + sorted(df[name_col].unique().tolist())
    selected_patient = st.selectbox("Patient", patients)

    if selected_patient == "Select a patient":
        st.info("Choose a patient above to load their profile and historical vitals.")
        return

    patient_df = df[df[name_col] == selected_patient].copy()
    if patient_df.empty:
        st.warning("No records exist for the selected patient.")
        return

    latest_record = patient_df.sort_values("date").iloc[-1]
    patient_row = {
        "name": latest_record[name_col],
        "patient_id": latest_record.get("patient_id", "N/A"),
        "age": latest_record.get("age", "N/A"),
        "gender": latest_record.get("gender", "N/A"),
        "primary_condition": latest_record.get("primary_condition", "N/A"),
        "city": latest_record.get("city", ""),
        "state": latest_record.get("state", ""),
    }
    render_patient_card(patient_row)

    avg_bp = patient_df[["systolic_bp", "diastolic_bp"]].mean()
    avg_glucose = patient_df["blood_glucose_mgdl"].mean()
    avg_step = patient_df["steps_count"].mean()
    avg_sleep = patient_df["sleep_hours"].mean()

    stats_cols = st.columns(4)
    stats_cols[0].metric("Avg Systolic", f"{avg_bp['systolic_bp']:.0f} mmHg")
    stats_cols[1].metric("Avg Diastolic", f"{avg_bp['diastolic_bp']:.0f} mmHg")
    stats_cols[2].metric("Avg Glucose", f"{avg_glucose:.0f} mg/dL")
    stats_cols[3].metric("Avg Sleep", f"{avg_sleep:.1f} hrs")

    st.markdown("---")
    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.plotly_chart(create_bp_chart(patient_df), use_container_width=True)
    with chart_cols[1]:
        st.plotly_chart(create_glucose_chart(patient_df), use_container_width=True)

    st.markdown("---")
    st.plotly_chart(create_activity_chart(patient_df), use_container_width=True)
