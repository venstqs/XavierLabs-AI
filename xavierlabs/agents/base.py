from abc import ABC
from xavierlabs.llm.router import LLMRouter, router


class BaseAgent(ABC):
    """Base class for all specialized XavierLabs agent personas."""

    def __init__(self, name: str, role: str, llm_router: LLMRouter = router):
        self.name = name
        self.role = role
        self.router = llm_router
