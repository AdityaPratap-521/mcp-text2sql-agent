from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    """
    LangGraph State representing context memory, dynamic state transitions, 
    and output artifacts across the multi-agent Text-to-SQL system.
    """
    user_query: str = ""
    db_schema: Dict[str, Any] = Field(default_factory=dict)
    generated_sql: str = ""
    sql_explanation: str = ""
    uat_status: str = "PENDING"  # PENDING, APPROVED, REJECTED, PASSED
    uat_feedback: str = ""
    query_result: Dict[str, Any] = Field(default_factory=dict)
    executive_narrative: str = ""
    revision_count: int = 0
    max_revisions: int = 3
    current_step: str = "INITIALIZED"
    messages: List[Dict[str, str]] = Field(default_factory=list)
