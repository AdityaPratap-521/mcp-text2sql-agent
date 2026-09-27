import pytest
from src.agents.graph import create_workflow_graph
from src.agents.state import AgentState

def test_full_graph_execution():
    graph = create_workflow_graph()
    initial_state = AgentState(user_query="What were the top 3 product categories by revenue in Q3 2025?")
    config = {"configurable": {"thread_id": "test_thread_001"}}

    result = graph.invoke(initial_state, config=config)
    
    if isinstance(result, dict):
        uat_status = result.get("uat_status")
        narrative = result.get("executive_narrative")
        sql = result.get("generated_sql")
    else:
        uat_status = result.uat_status
        narrative = result.executive_narrative
        sql = result.generated_sql

    assert uat_status == "APPROVED"
    assert sql != ""
    assert narrative != ""
    assert "Executive Summary" in narrative or "Raw Result Preview" in narrative
