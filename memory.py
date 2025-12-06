from typing import List, Dict, Any
import time
from dataclasses import dataclass, field


@dataclass
class AgentAction:
    agent_name: str
    action_type: str  # 'thought', 'tool_call', 'result', 'error'
    content: str
    timestamp: float = field(default_factory=time.time)


class SessionMemory:
    """
    Manages the short-term memory (session context) for the agents.
    Stores a history of actions, thoughts, and data transformations.
    """

    def __init__(self):
        self.actions: List[AgentAction] = []
        self.context: Dict[str, Any] = {}

    def add_action(self, agent_name: str, action_type: str, content: str):
        """Record an action taken by an agent."""
        action = AgentAction(agent_name, action_type, content)
        self.actions.append(action)

    def get_history(self) -> List[AgentAction]:
        """Retrieve the full history of actions."""
        return self.actions

    def get_recent_history(self, limit: int = 5) -> List[AgentAction]:
        """Retrieve the most recent actions."""
        return self.actions[-limit:]

    def set_context(self, key: str, value: Any):
        """Store a piece of context (e.g., 'current_dataset_shape')."""
        self.context[key] = value

    def get_context(self, key: str) -> Any:
        """Retrieve a piece of context."""
        return self.context.get(key)

    def clear(self):
        """Reset the memory."""
        self.actions = []
        self.context = {}
