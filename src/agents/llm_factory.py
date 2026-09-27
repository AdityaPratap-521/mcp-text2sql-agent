import os
import logging
from typing import Optional, Any
from config.settings import get_settings

logger = logging.getLogger("llm_factory")

class MockClaudeOpusLLM:
    """
    Mock LLM provider for zero-credential offline testing and validation.
    Synthesizes domain-aware SQL queries and executive narratives.
    """
    def __init__(self, model_name: str = "claude-3-opus-mock"):
        self.model_name = model_name

    def invoke(self, prompt: str) -> Any:
        class MockResponse:
            def __init__(self, text: str):
                self.content = text

        lower_prompt = prompt.lower()
        if "generate sql" in lower_prompt or "select" in lower_prompt or "sql agent" in lower_prompt:
            if "top" in lower_prompt or "revenue" in lower_prompt or "sales" in lower_prompt:
                sql = """SELECT p.product_name, p.category, SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'COMPLETED'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 5;"""
                explanation = "Calculates total revenue by product category from completed orders and sorts descending."
            else:
                sql = """SELECT c.customer_id, c.first_name || ' ' || c.last_name AS customer_name, c.email, COUNT(o.order_id) AS total_orders, SUM(o.total_amount) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
ORDER BY total_spent DESC;"""
                explanation = "Retrieves customer profile data with aggregated total orders and total expenditure."
            
            response_json = f"```sql\n{sql}\n```\nExplanation: {explanation}"
            return MockResponse(response_json)

        elif "narrative" in lower_prompt or "executive summary" in lower_prompt:
            narrative = """### Executive Summary & Analytical Narrative
- **Primary Finding**: Revenue generation is heavily concentrated in core hardware and software products.
- **Key Insight**: Enterprise Cloud Suite and AI Analytics Server drive the top revenue tier, accounting for over 65% of total Q3 order volume.
- **Operational Recommendation**: Expand inventory buffer for High-Demand Hardware assets and target cross-sell promotions to North America and Europe customer tiers."""
            return MockResponse(narrative)

        return MockResponse("Processed input via Mock Claude Engine.")

def get_llm():
    """Factory method returning active Anthropic Claude instance or Mock LLM."""
    settings = get_settings()
    api_key = settings.anthropic_api_key

    if api_key and settings.anthropic_model != "mock":
        try:
            from langchain_anthropic import ChatAnthropic
            logger.info(f"Initializing Anthropic Claude LLM ({settings.anthropic_model})")
            return ChatAnthropic(
                anthropic_api_key=api_key,
                model_name=settings.anthropic_model,
                temperature=0.0
            )
        except Exception as e:
            logger.warning(f"Failed to initialize ChatAnthropic ({e}). Falling back to Mock Claude LLM engine.")
            return MockClaudeOpusLLM(model_name="claude-3-opus-fallback")
    else:
        logger.info("Using Mock Claude Opus LLM Engine (Offline / Standalone mode).")
        return MockClaudeOpusLLM(model_name="claude-3-opus-mock")
