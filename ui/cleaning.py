"""
Compatibility wrapper for the Cleaning UI.

This module provides a thin `render_cleaning(df)` entrypoint and lazily delegates
to the modular implementation located in the `ui/cleaning` package (i.e.
`ui/cleaning/__init__.py`). The lazy import is performed at runtime so that
import-order issues and circular imports are less likely to occur.

Behavior:
- Attempts to import `ui.cleaning` via importlib.
- If the imported module appears to be this wrapper itself, or import fails,
  it tries a couple of fallback import names.
- If the implementation cannot be imported, it will try to show a Streamlit
  friendly error (if Streamlit is available) or raise an informative ImportError.

This wrapper keeps the original public API stable for the rest of the app.
"""

from importlib import import_module
from typing import Any

__all__ = ["render_cleaning"]


def _attempt_import_impl() -> Any:
    """
    Try to import the implementation module for the cleaning UI.

    Return the module if successful, otherwise raise ImportError.
    """
    tried = []
    candidates = [
        "ui.cleaning",  # preferred (package-level implementation)
        "Exploratory-Data-Analysis-EDA.ui.cleaning",  # explicit package path fallback
    ]

    for name in candidates:
        try:
            mod = import_module(name)
            tried.append((name, getattr(mod, "__file__", None)))
            # Guard: avoid returning this wrapper module itself if it was found under the same name.
            # Compare module file path if available.
            this_file = globals().get("__file__")
            mod_file = getattr(mod, "__file__", None)
            if this_file and mod_file:
                # If the module file is different from this wrapper file, assume it's the real impl.
                if mod_file != this_file:
                    return mod
                # Otherwise it's the same file (this wrapper): skip it.
            else:
                # No __file__ to compare (namespace package or frozen env). If module exposes
                # an implementation function different from this wrapper, prefer it.
                if getattr(mod, "render_cleaning", None) is not render_cleaning:
                    return mod
            # If we reached here, the candidate was not suitable; continue to next.
        except Exception:
            tried.append((name, None))
            continue

    # If we didn't return above, none of the candidates worked.
    raise ImportError(
        "Could not import a separate implementation module for the Cleaning UI. "
        f"Attempted: {', '.join([n for n, _ in tried])}."
    )


def render_cleaning(df: Any) -> Any:
    """
    Top-level rendering function for the Cleaning tab.

    Delegates to the implementation in the `ui.cleaning` package. Accepts the same
    signature as the original single-file implementation: `render_cleaning(df)` where
    `df` is a pandas.DataFrame-like object.

    If the implementation cannot be imported, attempts to show an error inside
    Streamlit (if available), otherwise raises ImportError.
    """
    try:
        impl_mod = _attempt_import_impl()
    except ImportError as exc:
        # Try to notify the user via Streamlit if available, otherwise re-raise.
        try:
            import streamlit as st  # local import to avoid top-level dependency

            st.error(
                "Cleaning UI implementation could not be loaded. "
                "Please ensure the `ui/cleaning` package is present and importable."
            )
            st.write(str(exc))
            return
        except Exception:
            # Streamlit not available or failed to import; raise the original ImportError.
            raise

    render_fn = getattr(impl_mod, "render_cleaning", None)
    if not callable(render_fn):
        # If the module doesn't expose `render_cleaning`, try to provide helpful diagnostics.
        try:
            import streamlit as st  # local import

            st.error(
                "The cleaning UI implementation module was found but does not expose "
                "`render_cleaning(df)`. Please ensure `ui/cleaning/__init__.py` defines "
                "and exports `render_cleaning`."
            )
            st.write("Available attributes: " + ", ".join(dir(impl_mod)))
            return
        except Exception:
            raise AttributeError(
                "Imported module for Cleaning UI does not define callable 'render_cleaning'."
            )

    # Delegate to implementation
    render_fn(df)
