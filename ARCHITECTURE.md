# HealthPulse AI — Architecture Blueprint

> **Version**: 1.0 | **Stack**: Python · Streamlit · Plotly · Anthropic Claude API  
> **Purpose**: Interactive health tracker dashboard with AI-powered insights

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HealthPulse AI — System Blueprint                   │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────────┐
  │   DATA LAYER     │      │  APP LAYER       │      │   AI LAYER           │
  │                  │      │                  │      │                      │
  │  generate_data   │─────▶│  app.py          │─────▶│  Anthropic Claude    │
  │  .py             │      │  (Streamlit)     │      │  claude-sonnet-4     │
  │                  │      │                  │      │                      │
  │  health_tracker  │      │  ┌────────────┐  │      │  /v1/messages        │
  │  _data.csv       │──────│  │  pandas    │  │      │  endpoint            │
  │                  │      │  │  DataFrame │  │      │                      │
  │  [User Upload]   │──────│  └────────────┘  │      │  Context: stats      │
  │  (CSV drag-drop) │      │                  │      │  summary JSON        │
  └──────────────────┘      └──────────────────┘      └──────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
             ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
             │  DASHBOARD  │  │  PATIENT    │  │  RAW DATA   │
             │  PAGE       │  │  PROFILE    │  │  EXPLORER   │
             │             │  │  PAGE       │  │             │
             │  KPI Cards  │  │             │  │  Filterable │
             │  Time Series│  │  BP History │  │  Table      │
             │  Scatter    │  │  Glucose    │  │  Download   │
             │  Heatmap    │  │  Steps/Mood │  │  Stats      │
             │  Pie Chart  │  │  Weight     │  │             │
             └─────────────┘  └─────────────┘  └─────────────┘
```

---

## Workflow: Step-by-Step

```
STEP 1 — BOILERPLATE                STEP 2 — DATA BACKEND
─────────────────────               ──────────────────────
  Streamlit page config               generate_data.py
  Custom CSS (dark theme)             15 patients × 365 days
  CSS variables & fonts               = 5,475 rows
  Navigation sidebar                  26 health columns
         │                                   │
         ▼                                   ▼
STEP 3 — METRICS                    STEP 4 — VISUALIZATIONS
────────────────────                ───────────────────────
  8 KPI metric cards                  Vital signs time series
  Status badges (R/Y/G)              Steps + Sleep dual-axis
  Rolling averages                   Scatter: BMI vs BP
  Condition detection                Symptom heatmap (day×cond)
  Thresholds: BP 140/90              Mood pie chart
              Glucose 126            Condition bar chart
              BMI 25/30              Patient profile drilldown
         │                                   │
         └──────────────────┬────────────────┘
                            ▼
              STEP 5 — AI INTERACTIVE PROMPTING
              ──────────────────────────────────
                Sidebar filters → filtered DataFrame
                Stats summary → JSON context
                Claude system prompt (clinical role)
                Chat history (multi-turn)
                Suggested question buttons
                Real-time API response rendering
```

---

## Data Schema

```
health_tracker_data.csv — 26 columns
───────────────────────────────────────────────────────────────────────────────

  IDENTITY                    VITALS                      LIFESTYLE
  ──────────                  ──────                      ─────────
  patient_id (PT001–PT015)    systolic_bp                 steps_count
  name                        diastolic_bp                calories_burned
  gender (M/F)                heart_rate_bpm              water_intake_liters
  age (26–68)                 blood_glucose_mgdl          sleep_hours
  location (city)             spo2_percent                sleep_quality
  date (2024-01-01 →)         body_temp_celsius           activity_level
  primary_condition           weight_kg                   mood
                              bmi
  SYMPTOMS                    MEDICATION
  ────────                    ──────────
  symptom                     medication
  symptom_severity (0–10)     medication_taken (Yes/No)
```

---

## AI Prompting Architecture

```
User Question
     │
     ▼
┌────────────────────────────────────────────────────┐
│  SYSTEM PROMPT                                     │
│  Role: HealthPulse AI clinical data analyst        │
│  Context: {stats_summary JSON}                     │
│    - patient count, date range                     │
│    - avg vitals (BP, glucose, HR, BMI)             │
│    - condition distribution                        │
│    - top symptoms, mood distribution               │
│    - medication adherence rate                     │
└────────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────┐
│  CONVERSATION HISTORY (multi-turn)                 │
│  [{"role": "user", "content": "..."},              │
│   {"role": "assistant", "content": "..."},         │
│   {"role": "user", "content": current question}]  │
└────────────────────────────────────────────────────┘
     │
     ▼
  claude-sonnet-4-20250514  (/v1/messages)
     │
     ▼
  Markdown-formatted clinical response
  → Rendered in chat bubble UI
```

---

## File Structure

```
health_tracker/
├── app/
│   ├── app.py                  # Main Streamlit application
│   └── requirements.txt        # Python dependencies
├── data/
│   ├── generate_data.py        # Fake dataset generator
│   └── health_tracker_data.csv # Generated dataset (5,475 rows)
└── docs/
    ├── ARCHITECTURE.md         # This file
    └── HealthPulse_Docs.docx   # Project documentation
```

---

## Deployment

```bash
# Local
pip install -r app/requirements.txt
streamlit run app/app.py

# With data generation
cd data && python generate_data.py
cd ../app && streamlit run app.py

# Streamlit Cloud
# 1. Push to GitHub
# 2. Connect repo at share.streamlit.io
# 3. Set main file: app/app.py
# 4. Add ANTHROPIC_API_KEY to Secrets (for AI features)
```

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Streamlit** | Fastest path from data → interactive UI; no frontend JS needed |
| **Plotly** | Interactive charts with hover, zoom, filter out of the box |
| **CSV backend** | Zero infrastructure, drag-and-drop replacement with real data |
| **Claude API** | Natural language queries over structured data; no ML model needed |
| **Dark theme** | Medical dashboards benefit from reduced eye strain |
| **Sidebar filters** | Global filters propagate across all pages without re-coding |
| **Rolling averages** | 7-day smoothing removes daily noise in vital signs |

---

*HealthPulse AI · Demo Only · Not for clinical use*
