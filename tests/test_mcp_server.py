import pytest
from mcp_server.db_adapter import DatabaseAdapter
from mcp_server.server import MCPSqlServer

def test_db_adapter_schema():
    adapter = DatabaseAdapter(db_type="sqlite")
    schema = adapter.get_schema()
    assert "customers" in schema
    assert "products" in schema
    assert "orders" in schema
    assert "order_items" in schema

def test_mcp_server_tools_list():
    server = MCPSqlServer(DatabaseAdapter(db_type="sqlite"))
    tools = server.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "get_db_schema" in tool_names
    assert "validate_sql_syntax" in tool_names
    assert "execute_sql_query" in tool_names

def test_mcp_tool_execution():
    server = MCPSqlServer(DatabaseAdapter(db_type="sqlite"))
    
    # 1. Test get schema
    schema_res = server.call_tool("get_db_schema", {})
    assert schema_res["status"] == "success"
    assert "products" in schema_res["schema"]

    # 2. Test validate syntax
    val_res = server.call_tool("validate_sql_syntax", {"sql_query": "SELECT * FROM products;"})
    assert val_res["valid"] is True

    # 3. Test forbidden statement rejection
    drop_res = server.call_tool("validate_sql_syntax", {"sql_query": "DROP TABLE products;"})
    assert drop_res["valid"] is False

    # 4. Test query execution
    exec_res = server.call_tool("execute_sql_query", {"sql_query": "SELECT product_name, unit_price FROM products LIMIT 2;"})
    assert exec_res["success"] is True
    assert len(exec_res["rows"]) == 2
    assert exec_res["columns"] == ["product_name", "unit_price"]
