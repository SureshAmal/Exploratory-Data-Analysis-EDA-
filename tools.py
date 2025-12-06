import pandas as pd
from typing import Dict, List, Any, Union
import eda
import ai_visual_generator


class AgentTools:
    """
    A registry of tools that agents can use.
    Wraps the existing functional logic from eda.py and ai_visual_generator.py.
    """

    @staticmethod
    def get_dataset_profile(df: pd.DataFrame) -> Dict:
        """Get basic stats about the dataset."""
        return eda.basic_profile(df)

    @staticmethod
    def get_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
        """Get descriptive statistics."""
        return eda.summary_stats(df)

    @staticmethod
    def detect_outliers(df: pd.DataFrame, method: str = "iqr") -> pd.DataFrame:
        """Detect outliers in the dataset."""
        return eda.outlier_summary(df, method=method)

    @staticmethod
    def clean_dataset(df: pd.DataFrame, cleaning_actions: Dict) -> pd.DataFrame:
        """
        Apply cleaning actions to the dataset.
        actions format: {'col_name': {'method': 'impute', 'impute': 'mean'}}
        """
        return eda.apply_cleaning(df, cleaning_actions)

    @staticmethod
    def generate_insights(df: pd.DataFrame, query: str = None, api_key: str = None):
        """
        Generate visual insights and text analysis.
        Returns (figures, text, error).
        """
        return ai_visual_generator.generate_insights_with_visuals(
            df, custom_prompt=query, api_key=api_key
        )
