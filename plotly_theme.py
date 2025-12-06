import plotly.io as pio
import plotly.graph_objects as go

BRAND_TEMPLATE = go.layout.Template()

brand_overrides = {
    "font": dict(family="IBM Plex Sans, Fraunces, serif", size=14),
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "margin": dict(l=50, r=40, t=60, b=40),
    "colorway": [
        "#d4a64e",
        "#2e6f85",
        "#b7343c",
        "#49c185",
        "#334454",
        "#c07d2b",
    ],
    "xaxis": {"gridcolor": "rgba(0,0,0,0.08)", "title": {"font": {"size": 13}}},
    "yaxis": {"gridcolor": "rgba(0,0,0,0.08)", "title": {"font": {"size": 13}}},
    "legend": {"title": {"font": {"size": 13}}, "font": {"size": 12}},
}

BRAND_TEMPLATE.layout = go.Layout(**brand_overrides)

pio.templates["brand"] = BRAND_TEMPLATE
