import json
import logging
from typing import Dict, Any, List, Optional
from mcp_server.db_adapter import DatabaseAdapter

logger = logging.getLogger("mcp_sql_server")

class MCPSqlServer:
    """
    Model Context Protocol (MCP) Server exposing standard SQL Database inspection and execution tools.
    Allows LLM multi-agent systems to interface securely with PostgreSQL / Hive databases.
    """

    def __init__(self, db_adapter: Optional[DatabaseAdapter] = None):
        self.db = db_adapter or DatabaseAdapter()

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return list of tool declarations compatible with MCP specification."""
        return [
            {
                "name": "get_db_schema",
                "description": "Extract the schema metadata (tables, column names, data types, primary keys) of the PostgreSQL/Hive analytics database.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "validate_sql_syntax",
                "description": "Validate syntax and check SQL query against non-destructive safety constraints prior to execution.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql_query": {"type": "string", "description": "The SQL query to validate"}
                    },
                    "required": ["sql_query"]
                }
            },
            {
                "name": "execute_sql_query",
                "description": "Execute a validated SELECT SQL query against the database and return column names and structured rows.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql_query": {"type": "string", "description": "The SELECT SQL query string to run"}
                    },
                    "required": ["sql_query"]
                }
            }
        ]

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch MCP tool execution to database adapter."""
        logger.info(f"MCP Tool Call Invoked: {tool_name} with args: {arguments}")
        if tool_name == "get_db_schema":
            return {"status": "success", "schema": self.db.get_schema()}
        elif tool_name == "validate_sql_syntax":
            query = arguments.get("sql_query", "")
            return self.db.validate_sql_syntax(query)
        elif tool_name == "execute_sql_query":
            query = arguments.get("sql_query", "")
            return self.db.execute_query(query)
        else:
            return {"status": "error", "error": f"Tool '{tool_name}' not found."}

if __name__ == "__main__":
    server = MCPSqlServer()
    print("MCP SQL Server initialized. Tools available:")
    for tool in server.list_tools():
        print(f" - {tool['name']}: {tool['description']}")
