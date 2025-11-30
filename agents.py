from typing import Dict, Any, List, Tuple
import pandas as pd
from memory import SessionMemory
from tools import AgentTools
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, name: str, memory: SessionMemory):
        self.name = name
        self.memory = memory

    def log_thought(self, thought: str):
        self.memory.add_action(self.name, "thought", thought)
        logger.info(f"[{self.name}] Thought: {thought}")

    def log_action(self, action: str):
        self.memory.add_action(self.name, "action", action)
        logger.info(f"[{self.name}] Action: {action}")

class CleaningAgent(BaseAgent):
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        self.log_thought("Checking dataset for missing values and outliers...")
        
        # 1. Profile the data
        profile = AgentTools.get_dataset_profile(df)
        missing_info = profile.get('missing', {})
        
        # 2. Simple heuristic: Impute numeric columns with median if missing > 0
        cleaning_actions = {}
        for col, missing_count in missing_info.items():
            if missing_count > 0:
                if pd.api.types.is_numeric_dtype(df[col]):
                    self.log_thought(f"Column '{col}' has {missing_count} missing values. Plan to impute with median.")
                    cleaning_actions[col] = {'method': 'impute', 'impute': 'median'}
                else:
                    self.log_thought(f"Column '{col}' has {missing_count} missing values. Plan to drop missing rows for categorical data.")
                    cleaning_actions[col] = {'method': 'drop', 'mask': df[col].isna()}
        
        if cleaning_actions:
            self.log_action(f"Applying cleaning actions: {list(cleaning_actions.keys())}")
            df_cleaned = AgentTools.clean_dataset(df, cleaning_actions)
            return df_cleaned
        else:
            self.log_thought("Dataset looks clean. No actions needed.")
            return df

class AnalysisAgent(BaseAgent):
    def run(self, df: pd.DataFrame, query: str, api_key: str) -> Tuple[List[Any], str]:
        self.log_thought(f"Analyzing dataset with query: '{query}'")
        
        # Use the AI Visual Generator tool
        figures, text, error = AgentTools.generate_insights(df, query=query, api_key=api_key)
        
        if error:
            self.log_thought(f"Encountered error during analysis: {error}")
            return [], f"Error: {error}"
            
        self.log_action("Generated insights and visualizations.")
        return figures, text

class SupervisorAgent(BaseAgent):
    def __init__(self, memory: SessionMemory):
        super().__init__("Supervisor", memory)
        self.cleaner = CleaningAgent("Cleaner", memory)
        self.analyst = AnalysisAgent("Analyst", memory)

    def process_upload(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Orchestrates the initial processing of a new dataset.
        Delegates to Cleaner if necessary.
        """
        self.log_thought("New dataset uploaded. Delegating to CleaningAgent for initial check.")
        df_cleaned = self.cleaner.run(df)
        self.log_action("Dataset processing complete.")
        return df_cleaned

    def handle_query(self, df: pd.DataFrame, query: str, api_key: str) -> Tuple[List[Any], str]:
        """
        Orchestrates the response to a user query.
        Delegates to Analyst.
        """
        self.log_thought(f"Received user query: '{query}'. Delegating to AnalysisAgent.")
        return self.analyst.run(df, query, api_key)
