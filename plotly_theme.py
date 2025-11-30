import plotly.io as pio
import plotly.graph_objects as go
import copy

# Safely deep-copy base template (Template lacks .copy())
base = pio.templates['plotly_white']
BRAND_TEMPLATE = copy.deepcopy(base)

# Font family aligns with tokens (will be loaded via CSS)
BRAND_TEMPLATE.layout.font = dict(family='IBM Plex Sans, Fraunces, serif', size=14)
BRAND_TEMPLATE.layout.paper_bgcolor = 'rgba(0,0,0,0)'
BRAND_TEMPLATE.layout.plot_bgcolor = 'rgba(0,0,0,0)'
BRAND_TEMPLATE.layout.margin = dict(l=50, r=40, t=60, b=40)
BRAND_TEMPLATE.layout.colorway = [
    '#d4a64e',  # accent gold
    '#2e6f85',  # deep teal
    '#b7343c',  # danger red
    '#49c185',  # success green
    '#334454',  # steel neutral
    '#c07d2b',  # warm amber
]
BRAND_TEMPLATE.layout.xaxis.update(gridcolor='rgba(0,0,0,0.08)', title=dict(font=dict(size=13)))
BRAND_TEMPLATE.layout.yaxis.update(gridcolor='rgba(0,0,0,0.08)', title=dict(font=dict(size=13)))
BRAND_TEMPLATE.layout.legend.update(title=dict(font=dict(size=13)), font=dict(size=12))

# Register template name for convenience
pio.templates['brand'] = BRAND_TEMPLATE
