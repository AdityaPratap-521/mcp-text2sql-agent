import re
import logging
from typing import Dict, Any
from src.agents.state import AgentState
from src.agents.llm_factory import get_llm
from mcp_server.server import MCPSqlServer

logger = logging.getLogger("text2sql_agent")

def text2sql_node(state: AgentState) -> Dict[str, Any]:
    """
    Text-to-SQL Agent Node:
    1. Fetches DB Schema via MCP Server.
    2. Synthesizes dialect-aware SQL based on natural language prompt and schema context.
    3. Handles error correction if revision feedback exists from UAT node.
    """
    logger.info("Executing Text-to-SQL Agent Node...")
    
    # 1. Fetch DB schema via MCP Server tool if not already present
    mcp_server = MCPSqlServer()
    if not state.db_schema:
        schema_res = mcp_server.call_tool("get_db_schema", {})
        db_schema = schema_res.get("schema", {})
    else:
        db_schema = state.db_schema

    # 2. Build detailed context prompt
    revision_context = ""
    if state.uat_feedback:
        revision_context = f"\nATTENTION - PREVIOUS UAT FEEDBACK / ERROR:\n{state.uat_feedback}\nPlease correct the SQL query accordingly."

    prompt = f"""You are an Expert SQL Engineer & Data Architect specialized in PostgreSQL and Apache Hive analytics databases.
Generate a accurate, performant, and safe SQL query to answer the user's business question.

DATABASE SCHEMA METADATA:
{db_schema}

USER QUESTION:
{state.user_query}
{revision_context}

INSTRUCTIONS:
- Use standard SELECT queries only. Non-destructive queries only.
- Output ONLY the SQL enclosed within ```sql ... ``` code blocks.
- Provide a brief 1-2 sentence explanation of your query logic afterwards as 'Explanation: <text>'.
"""

    # 3. Call LLM
    llm = get_llm()
    response = llm.invoke(prompt)
    content = getattr(response, "content", str(response))

    # 4. Extract SQL query and explanation
    sql_match = re.search(r"```sql\s*(.*?)\s*```", content, re.DOTALL | re.IGNORECASE)
    if sql_match:
        sql_query = sql_match.group(1).strip()
    else:
        sql_query = content.strip()

    exp_match = re.search(r"Explanation:\s*(.*)", content, re.IGNORECASE)
    explanation = exp_match.group(1).strip() if exp_match else "Generated SQL query based on database schema."

    return {
        "db_schema": db_schema,
        "generated_sql": sql_query,
        "sql_explanation": explanation,
        "current_step": "TEXT_TO_SQL_COMPLETED",
        "messages": state.messages + [{"role": "text2sql_agent", "content": f"Generated SQL: {sql_query}"}]
    }
