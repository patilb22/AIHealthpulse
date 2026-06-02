import json
import os
import urllib.request

import pandas as pd
import streamlit as st


SYSTEM_PROMPT = """
You are a clinical data analyst assistant. You analyze the dataset aggregates provided in user messages and answer questions with evidence-based analytics. You must follow these rules exactly:
- Use only the data aggregates and statistics passed in the conversation payload.
- Never provide a medical diagnosis, treatment plan, prescription, or clinical recommendation.
- If a user asks for diagnosis or therapy, respond that you are a data analyst and cannot provide medical diagnoses.
- Keep answers factual, concise, and clearly reference the available metrics.
- If a question cannot be answered from the provided aggregates, say so directly and do not invent data.
"""

QUICK_QUERIES = [
    "What is the average blood pressure across filtered records?",
    "How does average glucose compare by condition?",
    "Summarize activity and sleep patterns.",
    "What are the top symptoms in this dataset?",
    "How many records and patients are included?",
]


def get_anthropic_key() -> str | None:
    return (
        st.secrets.get("anthropic_api_key")
        if hasattr(st, "secrets")
        else None
    ) or os.environ.get("ANTHROPIC_API_KEY")


def call_claude_api(messages, system_prompt):
    api_key = get_anthropic_key()
    if not api_key:
        raise ValueError(
            "Anthropic API key not found. Set anthropic_api_key in Streamlit secrets or ANTHROPIC_API_KEY in the environment."
        )

    payload = {
        "model": "claude-sonnet-4",
        "max_tokens": 800,
        "temperature": 0.2,
        "system": system_prompt,
        "messages": messages,
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": api_key,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        response_json = json.loads(resp.read())
    if "content" in response_json and isinstance(response_json["content"], list):
        return response_json["content"][0].get("text", "(no response text)")
    return response_json.get("completion", "(no response returned)")


def build_data_context(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "No records are available for this dataset."

    record_count = len(df)
    patient_count = df["patient_id"].nunique() if "patient_id" in df.columns else df["patient_name"].nunique()
    date_range = f"{df['date'].min().date()} to {df['date'].max().date()}"
    averages = {
        "systolic_bp": df["systolic_bp"].mean(),
        "diastolic_bp": df["diastolic_bp"].mean(),
        "blood_glucose_mgdl": df["blood_glucose_mgdl"].mean(),
        "heart_rate_bpm": df["heart_rate_bpm"].mean(),
        "sleep_hours": df["sleep_hours"].mean(),
        "steps_count": df["steps_count"].mean(),
        "bmi": df["bmi"].mean(),
    }
    condition_summary = df["primary_condition"].value_counts().to_dict()
    top_symptoms = df["symptom"].value_counts().nlargest(5).to_dict()
    context = [
        f"Records: {record_count}",
        f"Patients: {patient_count}",
        f"Date range: {date_range}",
        "Average metrics:",
        f"  Systolic: {averages['systolic_bp']:.1f} mmHg",
        f"  Diastolic: {averages['diastolic_bp']:.1f} mmHg",
        f"  Glucose: {averages['blood_glucose_mgdl']:.1f} mg/dL",
        f"  Heart rate: {averages['heart_rate_bpm']:.1f} bpm",
        f"  Sleep: {averages['sleep_hours']:.1f} hours",
        f"  Steps: {averages['steps_count']:.0f}",
        f"  BMI: {averages['bmi']:.1f}",
        "Condition counts:",
    ]
    for condition, count in condition_summary.items():
        context.append(f"  {condition}: {count}")
    context.append("Top symptoms:")
    for symptom, count in top_symptoms.items():
        context.append(f"  {symptom}: {count}")
    return "\n".join(context)


def add_user_query(query: str) -> None:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    st.session_state.chat_history.append({"role": "user", "content": query})


def add_assistant_response(response: str) -> None:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    st.session_state.chat_history.append({"role": "assistant", "content": response})


def render(df=None) -> None:
    st.subheader("AI Insights")
    st.write(
        "Use AI Insights to ask clinical data analytics questions about the current filtered dataset. "
        "This interface is for data interpretation only, not medical advice."
    )

    if df is None or df.empty:
        st.warning("AI Insights requires dataset records to be loaded and filtered first.")
        return

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.markdown("#### Quick queries")
    quick_cols = st.columns(len(QUICK_QUERIES))
    clicked_query = None
    for idx, prompt in enumerate(QUICK_QUERIES):
        if quick_cols[idx].button(prompt):
            clicked_query = prompt

    user_input = st.text_input("Ask a question", key="ai_input")
    submit = st.button("Send")

    if clicked_query:
        user_message = clicked_query
    elif submit and user_input:
        user_message = user_input
    else:
        user_message = None

    if user_message:
        with st.spinner("Querying Claude for insights..."):
            add_user_query(user_message)
            try:
                dataset_context = build_data_context(df)
                messages = [
                    {"role": "user", "content": dataset_context + "\n\nUser query: " + user_message}
                ]
                assistant_text = call_claude_api(messages, SYSTEM_PROMPT)
            except Exception as exc:
                st.error(f"AI query failed: {exc}")
                return
            add_assistant_response(assistant_text)

    if st.session_state.chat_history:
        st.markdown("---")
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Claude:** {message['content']}")
