import logging
from typing import Dict, Any
from tabulate import tabulate
from src.agents.state import AgentState
from src.agents.llm_factory import get_llm

logger = logging.getLogger("narrative_agent")

def narrative_node(state: AgentState) -> Dict[str, Any]:
    """
    Narrative Agent Node:
    Converts raw query execution results into clean tabular formatting 
    and synthesizes executive business summaries, insights, and recommendations.
    """
    logger.info("Executing Narrative Agent Node...")
    
    query_res = state.query_result
    columns = query_res.get("columns", [])
    rows = query_res.get("rows", [])
    
    # Format tabular result snippet
    if columns and rows:
        formatted_table = tabulate(rows[:10], headers=columns, tablefmt="github")
    else:
        formatted_table = "No rows returned."

    prompt = f"""You are a Lead Business Intelligence & Executive Analytics Narrative Agent.
Synthesize a clear, concise executive narrative report based on the user's inquiry, executed SQL query, and resulting dataset.

USER QUESTION:
{state.user_query}

EXECUTED SQL QUERY:
{state.generated_sql}

DATASET RESULT (Top rows):
{formatted_table}
Total Rows Returned: {query_res.get('count', 0)}

INSTRUCTIONS:
1. Provide an Executive Summary highlighting top metrics.
2. Outline key strategic insights and observations from the data.
3. Recommend next steps or data drill-downs for leadership.
Format in clean GitHub Markdown with bullet points.
"""

    llm = get_llm()
    response = llm.invoke(prompt)
    narrative_text = getattr(response, "content", str(response))

    full_narrative = f"""## SQL Query Output
```sql
{state.generated_sql}
```

### Raw Result Preview ({query_res.get('count', 0)} rows)
{formatted_table}

---

{narrative_text}
"""

    return {
        "executive_narrative": full_narrative,
        "current_step": "NARRATIVE_GENERATED",
        "messages": state.messages + [{"role": "narrative_agent", "content": "Executive narrative generated."}]
    }
