import sys
import argparse
import logging
from src.agents.graph import create_workflow_graph
from src.agents.state import AgentState

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("main_cli")

def run_agent_workflow(query_text: str):
    """Run the multi-agent Text-to-SQL system with a natural language query."""
    print("=" * 80)
    print(f"[+] Launching MCP Text-to-SQL Multi-Agent System")
    print(f"[?] Prompt: {query_text}")
    print("=" * 80)

    graph = create_workflow_graph()
    initial_state = AgentState(user_query=query_text)
    config = {"configurable": {"thread_id": "session_uat_001"}}

    final_state_dict = graph.invoke(initial_state, config=config)
    
    # Extract values from resulting dictionary / Pydantic object
    if isinstance(final_state_dict, dict):
        sql = final_state_dict.get("generated_sql", "")
        uat_status = final_state_dict.get("uat_status", "")
        narrative = final_state_dict.get("executive_narrative", "")
    else:
        sql = final_state_dict.generated_sql
        uat_status = final_state_dict.uat_status
        narrative = final_state_dict.executive_narrative

    print("\n" + "=" * 80)
    print(f"[OK] UAT Validation Status: {uat_status}")
    print("=" * 80)
    print(narrative)
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="MCP Text-to-SQL Multi-Agent Intelligence System (UAT Staging)")
    parser.add_argument("--query", "-q", type=str, help="Natural language SQL query prompt", default="Show top 3 revenue generating products in Q3 2025 across all regions")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run interactive prompt loop")
    args = parser.parse_args()

    if args.interactive:
        print("Entering Interactive MCP Text-to-SQL Agent Shell. Type 'exit' or 'quit' to stop.\n")
        while True:
            try:
                user_input = input("\nSQL-Agent> ")
                if user_input.strip().lower() in ["exit", "quit", "q"]:
                    break
                if user_input.strip():
                    run_agent_workflow(user_input.strip())
            except (KeyboardInterrupt, EOFError):
                break
    else:
        run_agent_workflow(args.query)

if __name__ == "__main__":
    main()
