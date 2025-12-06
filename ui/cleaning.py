from typing import Any
from pandas import DataFrame
from ui.clean import render_clean


def render_cleaning(df: DataFrame) -> Any:
    render_clean(df)
