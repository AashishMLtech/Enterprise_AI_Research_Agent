from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchBudget:
    max_queries: int = 8
    max_sources: int = 20
    max_verification_retries: int = 2
    max_context_tokens: int = 4_000
