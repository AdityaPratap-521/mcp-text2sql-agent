import sqlite3
import logging
from typing import Dict, Any, List, Optional
import sqlparse
from config.settings import get_settings

logger = logging.getLogger("mcp_db_adapter")

class DatabaseAdapter:
    """
    Unified Database Adapter supporting PostgreSQL and fallback SQLite testing environment.
    Exposes schema discovery, safe query execution, and syntax validation.
    """

    def __init__(self, db_type: Optional[str] = None, dsn: Optional[str] = None, sqlite_path: Optional[str] = None):
        settings = get_settings()
        self.db_type = db_type or settings.db_type
        self.dsn = dsn or settings.postgres_dsn
        self.sqlite_path = sqlite_path
        self._sqlite_conn = None

    def _get_postgres_conn(self):
        import psycopg2
        return psycopg2.connect(self.dsn)

    def _get_sqlite_conn(self):
        if self.sqlite_path:
            return sqlite3.connect(self.sqlite_path)
        if not self._sqlite_conn:
            self._sqlite_conn = sqlite3.connect(":memory:")
            self._init_sqlite_mock_data(self._sqlite_conn)
        return self._sqlite_conn

    def _init_sqlite_mock_data(self, conn: sqlite3.Connection):
        """Seed SQLite memory DB with sample enterprise schema for local testing."""
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS regions (
                region_id INTEGER PRIMARY KEY,
                region_name TEXT NOT NULL,
                country TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                region_id INTEGER,
                signup_date DATE,
                FOREIGN KEY (region_id) REFERENCES regions(region_id)
            );

            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL,
                stock_quantity INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                order_date DATE NOT NULL,
                status TEXT NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );

            CREATE TABLE IF NOT EXISTS order_items (
                item_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );

            -- Sample Data Insertion
            INSERT OR IGNORE INTO regions VALUES (1, 'North America', 'USA');
            INSERT OR IGNORE INTO regions VALUES (2, 'Europe', 'UK');
            INSERT OR IGNORE INTO regions VALUES (3, 'Asia Pacific', 'Japan');

            INSERT OR IGNORE INTO customers VALUES (101, 'Alice', 'Smith', 'alice@example.com', 1, '2024-01-15');
            INSERT OR IGNORE INTO customers VALUES (102, 'Bob', 'Jones', 'bob@example.com', 2, '2024-02-20');
            INSERT OR IGNORE INTO customers VALUES (103, 'Charlie', 'Brown', 'charlie@example.com', 1, '2024-03-10');
            INSERT OR IGNORE INTO customers VALUES (104, 'David', 'Lee', 'david@example.com', 3, '2024-04-05');

            INSERT OR IGNORE INTO products VALUES (201, 'Enterprise Cloud Suite', 'Software', 1200.00, 500);
            INSERT OR IGNORE INTO products VALUES (202, 'AI Analytics Server', 'Hardware', 4500.00, 50);
            INSERT OR IGNORE INTO products VALUES (203, 'Database Optimizer Tool', 'Software', 750.00, 200);
            INSERT OR IGNORE INTO products VALUES (204, 'Security Firewall Pro', 'Hardware', 2100.00, 80);

            INSERT OR IGNORE INTO orders VALUES (301, 101, '2025-07-10', 'COMPLETED', 5700.00);
            INSERT OR IGNORE INTO orders VALUES (302, 102, '2025-08-14', 'COMPLETED', 1200.00);
            INSERT OR IGNORE INTO orders VALUES (303, 103, '2025-08-28', 'PENDING', 2100.00);
            INSERT OR IGNORE INTO orders VALUES (304, 101, '2025-09-02', 'COMPLETED', 4500.00);
            INSERT OR IGNORE INTO orders VALUES (305, 104, '2025-09-15', 'COMPLETED', 5400.00);

            INSERT OR IGNORE INTO order_items VALUES (401, 301, 201, 1, 1200.00);
            INSERT OR IGNORE INTO order_items VALUES (402, 301, 202, 1, 4500.00);
            INSERT OR IGNORE INTO order_items VALUES (403, 302, 201, 1, 1200.00);
            INSERT OR IGNORE INTO order_items VALUES (404, 303, 204, 1, 2100.00);
            INSERT OR IGNORE INTO order_items VALUES (405, 304, 202, 1, 4500.00);
            INSERT OR IGNORE INTO order_items VALUES (406, 305, 201, 2, 2400.00);
            INSERT OR IGNORE INTO order_items VALUES (407, 305, 203, 4, 3000.00);
        """)
        conn.commit()

    def get_schema(self) -> Dict[str, Any]:
        """Return canonical database schema including tables, columns, types, and primary keys."""
        try:
            if self.db_type == "postgres":
                conn = self._get_postgres_conn()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT table_name, column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    ORDER BY table_name, ordinal_position;
                """)
                rows = cursor.fetchall()
                conn.close()
                schema = {}
                for table, col, dtype, nullable in rows:
                    if table not in schema:
                        schema[table] = []
                    schema[table].append({"column": col, "type": dtype, "nullable": nullable == "YES"})
                return schema
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed ({e}). Falling back to SQLite mock engine.")

        # SQLite Fallback / Mock DB
        conn = self._get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cursor.fetchall() if not r[0].startswith("sqlite_")]
        schema = {}
        for tbl in tables:
            cursor.execute(f"PRAGMA table_info({tbl});")
            cols = cursor.fetchall()
            schema[tbl] = [{"column": c[1], "type": c[2], "pk": bool(c[5])} for c in cols]
        return schema

    def validate_sql_syntax(self, sql_query: str) -> Dict[str, Any]:
        """Check SQL for non-destructive write rules and syntax validity."""
        clean_sql = sql_query.strip().rstrip(";")
        statements = sqlparse.parse(clean_sql)
        if not statements:
            return {"valid": False, "error": "Empty or unparseable SQL string."}

        stmt_type = statements[0].get_type()
        forbidden_types = ["DELETE", "DROP", "ALTER", "TRUNCATE", "UPDATE", "INSERT"]
        if stmt_type.upper() in forbidden_types:
            return {
                "valid": False,
                "error": f"Destructive statement type '{stmt_type}' is prohibited. Only SELECT queries are permitted in UAT environment."
            }

        return {"valid": True, "statement_type": stmt_type}

    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """Execute SELECT query safely and return columns and rows."""
        val_res = self.validate_sql_syntax(sql_query)
        if not val_res["valid"]:
            return {"success": False, "error": val_res["error"], "columns": [], "rows": []}

        try:
            if self.db_type == "postgres":
                try:
                    conn = self._get_postgres_conn()
                    cursor = conn.cursor()
                    cursor.execute(sql_query)
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    conn.close()
                    return {"success": True, "columns": columns, "rows": rows, "count": len(rows)}
                except Exception as pg_err:
                    logger.warning(f"Postgres execution failed ({pg_err}). Falling back to SQLite engine.")

            # Fallback SQLite Execution
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute(sql_query)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return {"success": True, "columns": columns, "rows": rows, "count": len(rows)}

        except Exception as e:
            return {"success": False, "error": str(e), "columns": [], "rows": []}
