import logging
from typing import Dict, Any
from src.agents.state import AgentState

logger = logging.getLogger("orchestrator")

def orchestrator_node(state: AgentState) -> Dict[str, Any]:
    """
    Master Orchestrator Agent Node:
    Acts as the entry dispatcher, initializing agent state, logging intent, 
    and preparing workflow execution paths.
    """
    logger.info(f"Orchestrator received prompt: '{state.user_query}'")
    return {
        "current_step": "ORCHESTRATED",
        "messages": state.messages + [{"role": "orchestrator", "content": f"Orchestrator dispatched query: {state.user_query}"}]
    }

def route_after_uat(state: AgentState) -> str:
    """
    Conditional Routing Logic after UAT Agent validation:
    - If APPROVED -> Proceed to Narrative Agent.
    - If REJECTED & revision_count < max_revisions -> Loop back to Text-to-SQL Agent for auto-repair.
    - If max_revisions reached -> Terminate with error.
    """
    if state.uat_status == "APPROVED":
        return "narrative"
    elif state.revision_count < state.max_revisions:
        logger.info(f"Routing back to text2sql for auto-repair (Attempt {state.revision_count}/{state.max_revisions})")
        return "text2sql"
    else:
        logger.error("Max revision cycles reached in UAT validation.")
        return "end"
