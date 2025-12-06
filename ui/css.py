import streamlit as st


def inject_modular_css():
    """Load modular CSS files from the `styles/` folder and inject them into Streamlit safely.
    This centralizes CSS injection so the main app remains focused on UI logic.
    """
    css_files = [
        "styles/theme_tokens.css",
        "styles/base.css",
        "styles/components.css",
        "styles/dark.css",
        "styles/motion.css",
    ]
    for path in css_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                st.html(f"<style>{f.read()}</style>")
        except FileNotFoundError:
            st.warning(f"Missing CSS file: {path}")

