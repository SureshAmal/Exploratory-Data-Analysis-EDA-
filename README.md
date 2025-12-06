# Data Alchemy Lab

An intelligent, compact Streamlit app for exploratory data analysis (EDA) with optional AI-powered insights.

## Overview

- **Purpose:** Rapid, interactive EDA with automated profiling, cleaning, and optional AI insights.
- **Tech:** `Streamlit`, `pandas`, `plotly`, optional `Google Gemini` for AI-driven analysis.

---

## Quick start
1. clone the Repo:

```bash
git clone https://github.com/Tejas3545/Exploratory-Data-Analysis-EDA-.git
cd Exploratory-Data-Analysis-EDA-
```

2. Install requirements and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

3. (Optional) Add an API key for AI insights:

```bash
    add GOOGLE_API_KEY in .env
```

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=. tests/
```


## Project layout (high level)
- `app.py` — main Streamlit orchestrator
- `ui/` — header, sidebar, css and per-tab renderers
- `eda.py` — profiling, summaries, outlier detection, cleaning helpers
- `agents.py`, `memory.py` — agent system and session memory
- `gemini_client.py` — optional AI integration

## 🗺️ Roadmap

**Planned Features:**

- [ ] PostgreSQL/MySQL database connection support
- [ ] Advanced time series forecasting (ARIMA, Prophet)
- [ ] Automated feature engineering suggestions
- [ ] Export reports as PDF/PowerPoint
- [ ] Collaborative analysis (multi-user sessions)
- [ ] Custom agent creation interface
- [ ] Integration with dbt for data transformation
- [ ] Real-time data streaming support

**Completed:**

- [x] Multi-agent architecture
- [x] Session memory and observability
- [x] Automated data cleaning
- [x] AI-powered insights with Gemini
- [x] Sales analytics dashboard
- [x] Dark theme support
- [x] Column-level profiling

---