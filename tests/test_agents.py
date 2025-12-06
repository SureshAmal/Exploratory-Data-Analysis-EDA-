import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
from agents import SupervisorAgent
from memory import SessionMemory
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)


def test_agent_workflow():
    print("=== Starting Agent Workflow Test ===")

    # 1. Create a dummy dataset with missing values and outliers
    data = {
        "Age": [25, 30, np.nan, 35, 150],  # 150 is an outlier
        "Income": [50000, 60000, 55000, np.nan, 1000000],  # 1M is an outlier
        "Category": ["A", "B", "A", "C", "B"],
    }
    df = pd.DataFrame(data)
    print("\nOriginal DataFrame:")
    print(df)

    # 2. Initialize Agent System
    memory = SessionMemory()
    supervisor = SupervisorAgent(memory)

    # 3. Test Process Upload (Cleaning)
    print("\n--- Testing Supervisor.process_upload ---")
    df_cleaned = supervisor.process_upload(df)
    print("\nCleaned DataFrame:")
    print(df_cleaned)

    # Verify cleaning happened (simple check)
    assert df_cleaned["Age"].isna().sum() == 0, "Age missing values should be imputed"
    assert df_cleaned["Income"].isna().sum() == 0, (
        "Income missing values should be imputed"
    )

    # 4. Test Query Handling (Analysis)
    print("\n--- Testing Supervisor.handle_query ---")
    # Note: This will fail if no API key is present, but we can check if it tries
    try:
        figures, text = supervisor.handle_query(
            df_cleaned, "What is the average income?", api_key="dummy_key"
        )
        print(f"\nResult: {text}")
    except Exception as e:
        print(f"\nExpected error (no valid API key): {e}")

    # 5. Check Memory
    print("\n--- Checking Agent Memory ---")
    history = memory.get_history()
    for action in history:
        print(f"[{action.agent_name}] {action.action_type}: {action.content}")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_agent_workflow()
