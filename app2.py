import os

import pandas as pd
import streamlit as st

from pages import ai_insights, dashboard, patient_profile, raw_data_explorer

PAGE_CONFIG = {
    "page_title": "HealthPulse AI",
    "page_icon": "💓",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

PAGES = {
    "📊 Dashboard": dashboard,
    "🩺 Patient Profile": patient_profile,
    "🤖 AI Insights": ai_insights,
    "📋 Raw Data Explorer": raw_data_explorer,
}


def get_data_path() -> str:
    root = os.path.dirname(__file__)
    paths = [
        os.path.join(root, "data", "health_tracker_data.csv"),
        os.path.join(root, "health_tracker_data.csv"),
    ]
    for candidate in paths:
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(
        "Could not find health_tracker_data.csv in data/ or project root."
    )


@st.cache_data
def load_data() -> pd.DataFrame:
    path = get_data_path()
    df = pd.read_csv(path, parse_dates=["date"])
    df["primary_condition"] = df["primary_condition"].fillna("Unknown").astype(str)
    return df


def render_sidebar(df: pd.DataFrame) -> tuple[str, str, tuple[date, date]]:
    st.sidebar.title("HealthPulse AI")
    st.sidebar.write("Build the next generation of patient-facing clinical analytics.")
    st.sidebar.divider()

    st.sidebar.markdown("### Filters")
    conditions = ["All"] + sorted(df["primary_condition"].unique().tolist())
    selected_condition = st.sidebar.selectbox("Condition", conditions, index=0)

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    selected_date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    st.sidebar.divider()
    selected_page = st.sidebar.radio("Go to", list(PAGES.keys()), index=0)
    return selected_page, selected_condition, selected_date_range


def main() -> None:
    st.set_page_config(**PAGE_CONFIG)

    df_raw = load_data()
    selected_page, selected_condition, selected_date_range = render_sidebar(df_raw)

    df = df_raw.copy()
    if selected_condition != "All":
        df = df[df["primary_condition"] == selected_condition]
    if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
        df = df[(df["date"] >= pd.Timestamp(selected_date_range[0])) & (df["date"] <= pd.Timestamp(selected_date_range[1]))]

    page_module = PAGES[selected_page]
    st.header(selected_page)
    st.markdown(
        "Use the sidebar navigation and filters to explore HealthPulse AI metrics and records."
    )
    st.divider()

    page_module.render(df)


if __name__ == "__main__":
    main()
