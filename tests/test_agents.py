import pytest
from src.agents.state import AgentState
from src.agents.orchestrator import orchestrator_node
from src.agents.text2sql_agent import text2sql_node
from src.agents.uat_agent import uat_validation_node
from src.agents.narrative_agent import narrative_node

def test_orchestrator_node():
    state = AgentState(user_query="What are top 5 products?")
    res = orchestrator_node(state)
    assert res["current_step"] == "ORCHESTRATED"
    assert len(res["messages"]) == 1

def test_text2sql_node():
    state = AgentState(user_query="Show revenue by product category")
    res = text2sql_node(state)
    assert res["current_step"] == "TEXT_TO_SQL_COMPLETED"
    assert "generated_sql" in res
    assert "SELECT" in res["generated_sql"].upper()

def test_uat_agent_approved():
    state = AgentState(
        user_query="Show revenue by category",
        generated_sql="SELECT category, SUM(unit_price) FROM products GROUP BY category;"
    )
    res = uat_validation_node(state)
    assert res["uat_status"] == "APPROVED"
    assert res["query_result"]["count"] >= 0

def test_uat_agent_rejected():
    state = AgentState(
        user_query="Malicious intent",
        generated_sql="DELETE FROM products;"
    )
    res = uat_validation_node(state)
    assert res["uat_status"] == "REJECTED"
    assert "Prohibited" in res["uat_feedback"] or "prohibited" in res["uat_feedback"]

def test_narrative_agent_node():
    state = AgentState(
        user_query="Show revenue by category",
        generated_sql="SELECT category, SUM(unit_price) FROM products GROUP BY category;",
        query_result={
            "columns": ["category", "total_price"],
            "rows": [["Software", 2900.00], ["Hardware", 6600.00]],
            "count": 2
        }
    )
    res = narrative_node(state)
    assert "executive_narrative" in res
    assert "Raw Result Preview" in res["executive_narrative"]
