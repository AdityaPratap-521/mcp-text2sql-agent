import logging
from typing import Dict, Any
from src.agents.state import AgentState
from mcp_server.server import MCPSqlServer
from config.settings import get_settings

logger = logging.getLogger("uat_agent")

def uat_validation_node(state: AgentState) -> Dict[str, Any]:
    """
    User Validation & Acceptance Testing (UAT) Agent Node:
    - Validates SQL syntax and policy safety via MCP tool interface.
    - Executes test query against PostgreSQL/Hive database.
    - Captures schema/syntax errors and provides feedback for revision loop.
    """
    logger.info("Executing UAT Validation Agent Node...")
    settings = get_settings()
    mcp_server = MCPSqlServer()
    sql_query = state.generated_sql

    # 1. Perform MCP syntax & policy validation
    val_res = mcp_server.call_tool("validate_sql_syntax", {"sql_query": sql_query})
    if not val_res.get("valid", False):
        error_msg = val_res.get("error", "Syntax or safety validation failed.")
        logger.warning(f"UAT REJECTED SQL: {error_msg}")
        return {
            "uat_status": "REJECTED",
            "uat_feedback": f"Syntax/Safety Validation Error: {error_msg}",
            "revision_count": state.revision_count + 1,
            "current_step": "UAT_REJECTED",
            "messages": state.messages + [{"role": "uat_agent", "content": f"Query Rejected: {error_msg}"}]
        }

    # 2. Execute SQL query via MCP tool interface
    exec_res = mcp_server.call_tool("execute_sql_query", {"sql_query": sql_query})
    if not exec_res.get("success", False):
        error_msg = exec_res.get("error", "Database query execution runtime error.")
        logger.warning(f"UAT Execution Error: {error_msg}")
        return {
            "uat_status": "REJECTED",
            "uat_feedback": f"Runtime Execution Error: {error_msg}",
            "revision_count": state.revision_count + 1,
            "current_step": "UAT_EXECUTION_FAILED",
            "messages": state.messages + [{"role": "uat_agent", "content": f"Execution Error: {error_msg}"}]
        }

    # 3. Validation Passed & Execution Succeeded
    logger.info(f"UAT PASSED: Query returned {exec_res.get('count', 0)} rows.")
    return {
        "uat_status": "APPROVED",
        "uat_feedback": "SQL Query passed UAT syntax, safety, and runtime execution validation.",
        "query_result": {
            "columns": exec_res.get("columns", []),
            "rows": exec_res.get("rows", []),
            "count": exec_res.get("count", 0)
        },
        "current_step": "UAT_APPROVED",
        "messages": state.messages + [{"role": "uat_agent", "content": "Query validated and executed successfully."}]
    }
