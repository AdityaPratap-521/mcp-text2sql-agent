import os
from functools import lru_cache
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    db_type: str = os.getenv("DB_TYPE", "postgres")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "analytics_db")
    db_user: str = os.getenv("DB_USER", "analytics_user")
    db_password: str = os.getenv("DB_PASSWORD", "analytics_password")
    
    mcp_server_host: str = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    mcp_server_port: int = int(os.getenv("MCP_SERVER_PORT", "8000"))
    mcp_transport: str = os.getenv("MCP_TRANSPORT", "stdio")
    
    auto_uat_approval: bool = os.getenv("AUTO_UAT_APPROVAL", "true").lower() in ("true", "1", "t", "yes")
    max_revision_cycles: int = int(os.getenv("MAX_REVISION_CYCLES", "3"))

    @property
    def postgres_dsn(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
