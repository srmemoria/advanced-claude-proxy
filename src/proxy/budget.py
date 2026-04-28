from loguru import logger
import json
import os

class BudgetManager:
    """Tracks token usage and enforces a strict daily/session budget."""
    
    def __init__(self):
        self.session_cost = 0.0
        self.max_budget = 1.00 # $1.00 hard limit to protect user's wallet
        
        # Rough estimates for non-local models per 1M tokens
        self.pricing = {
            "openrouter": {"input": 1.5, "output": 2.0}, 
            "deepseek": {"input": 0.14, "output": 0.28},
            "nvidia_nim": {"input": 0.0, "output": 0.0}, # Generous free tier
            "local": {"input": 0.0, "output": 0.0} # Ollama/LM Studio are 100% free
        }

    def check_budget(self) -> bool:
        """Returns False if budget is exceeded."""
        if self.session_cost >= self.max_budget:
            logger.warning("🚨 HARD BUDGET LIMIT REACHED. BLOCKING REQUEST.")
            return False
        return True

    def record_usage(self, provider: str, input_tokens: int, output_tokens: int):
        """Calculates cost and updates the session budget."""
        cost_profile = self.pricing.get(provider, self.pricing["local"])
        
        # Convert from per-million rate to per-token
        input_cost = (cost_profile["input"] / 1_000_000) * input_tokens
        output_cost = (cost_profile["output"] / 1_000_000) * output_tokens
        
        total_request_cost = input_cost + output_cost
        self.session_cost += total_request_cost
        
        if total_request_cost > 0:
            logger.info(f"Cost recorded: ${total_request_cost:.6f} | Total Session: ${self.session_cost:.4f}")

    def get_stats(self) -> dict:
        return {
            "spent": round(self.session_cost, 4),
            "limit": self.max_budget,
            "remaining": round(self.max_budget - self.session_cost, 4),
            "status": "Safe" if self.session_cost < self.max_budget else "Blocked"
        }

# Global singleton for the session
budget_manager = BudgetManager()
