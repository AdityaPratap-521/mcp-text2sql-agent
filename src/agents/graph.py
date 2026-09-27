import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.agents.state import AgentState
from src.agents.orchestrator import orchestrator_node, route_after_uat
from src.agents.text2sql_agent import text2sql_node
from src.agents.uat_agent import uat_validation_node
from src.agents.narrative_agent import narrative_node

logger = logging.getLogger("graph_builder")

def create_workflow_graph():
    r"""
    Constructs the Multi-Agent LangGraph workflow:
    [START] -> orchestrator -> text2sql -> uat -> (conditional) -> narrative -> [END]
                                               \---> (revision loop) ---> text2sql
    """
    workflow = StateGraph(AgentState)

    # 1. Add Agent Nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("text2sql", text2sql_node)
    workflow.add_node("uat", uat_validation_node)
    workflow.add_node("narrative", narrative_node)

    # 2. Define Entry Point and Fixed Edges
    workflow.set_entry_point("orchestrator")
    workflow.add_edge("orchestrator", "text2sql")
    workflow.add_edge("text2sql", "uat")

    # 3. Add Conditional Edge for UAT Approval / Revision Loop
    workflow.add_conditional_edges(
        "uat",
        route_after_uat,
        {
            "narrative": "narrative",
            "text2sql": "text2sql",
            "end": END
        }
    )

    # 4. Narrative to END
    workflow.add_edge("narrative", END)

    # 5. Compile graph with memory checkpointer
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    logger.info("LangGraph Multi-Agent StateGraph compiled successfully.")
    return app
