# 💓 HealthPulse AI

> **AI-powered health tracker dashboard** built with Streamlit, Plotly, and Claude AI.

![Status](https://img.shields.io/badge/status-demo-teal) ![Python](https://img.shields.io/badge/python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/streamlit-1.35+-red)

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r app/requirements.txt

# 2. Generate fake dataset (5,475 records)
cd data && python generate_data.py

# 3. Run the app
cd ../app && streamlit run app.py
```

App runs at: **http://localhost:8501**

---

## What's Inside

| Page | Features |
|---|---|
| 📊 Dashboard | 8 KPI cards · Time series · Scatter · Heatmap · Distributions |
| 🩺 Patient Profile | Individual drilldown · BP history · Glucose · Steps · Weight |
| 🤖 AI Insights | Claude-powered chat · Suggested questions · Multi-turn dialog |
| 📋 Raw Data | Filterable table · Column selector · CSV download |

---

## Dataset

`data/health_tracker_data.csv` — 5,475 rows, 26 columns  
15 fake patients × 365 days, all synthetically generated.

---

## AI Features (Optional)

Add your Anthropic API key to `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

---

## Docs

- `docs/ARCHITECTURE.md` — System blueprint with diagrams
- `docs/HealthPulse_Docs.docx` — Full project documentation

---

> ⚠️ **Demo only. Not for clinical use.**
