from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from xavierlabs.agents.base import BaseAgent
from xavierlabs.tools.academic import AcademicDiscoveryTool, AcademicPaper
from xavierlabs.tools.files import WorkspaceInspector


class HypothesisConfig(BaseModel):
    title: str = Field(description="Clear, mathematically or empirically rigorous hypothesis title")
    motivation: str = Field(description="Why this investigation matters and the core problem it solves")
    theoretical_basis: str = Field(description="Underlying mathematical/computational theory and equations")
    parameters: Dict[str, Any] = Field(description="Experimental parameters, hyperparams, baseline vs proposed values")
    metrics: List[str] = Field(description="Concrete quantitative metrics to measure (e.g. loss, accuracy, latency, regret)")
    experimental_design: str = Field(description="Step-by-step computational procedure to evaluate the hypothesis")
    literature_citations: List[str] = Field(description="Relevant academic papers or citations underpinning the idea")


IDEATOR_SYSTEM_PROMPT = """You are 'The Ideator', an elite computational scientist and discovery agent in the XavierLabs AI research swarm.
Your goal is to formulate novel, mathematically sound, and computationally testable hypotheses based on scientific literature and codebase context.

Guiding Principles:
1. Novelty & Rigor: Avoid trivial hypotheses. Connect theoretical concepts with clear measurable outcomes.
2. Computational Feasibility: The hypothesis must be testable via a self-contained Python script within 2-3 minutes of compute.
3. Clean Mathematical Formulation: Clearly specify variables, baseline vs experimental conditions, and exact evaluation metrics.
4. Output JSON: You must format your final output strictly as a JSON object matching the requested schema.
"""


class IdeatorAgent(BaseAgent):
    def __init__(self, discovery_tool: Optional[AcademicDiscoveryTool] = None):
        super().__init__(name="The Ideator", role="ideator")
        self.discovery_tool = discovery_tool or AcademicDiscoveryTool()

    def discover_literature(self, topic: str, max_papers: int = 5) -> List[AcademicPaper]:
        """Queries academic databases for relevant literature."""
        return self.discovery_tool.search(topic, max_results=max_papers)

    def formulate_hypothesis(
        self,
        topic: str,
        literature: List[AcademicPaper],
        workspace_context: str = "",
        critique_feedback: Optional[str] = None,
    ) -> HypothesisConfig:
        """
        Synthesizes literature and context into a structured scientific hypothesis.
        If critique_feedback is provided (from Reviewer), refines the hypothesis accordingly.
        """
        lit_summary = "\n\n".join(p.format_summary() for p in literature) or "No external literature retrieved."

        user_prompt = f"""Target Research Topic:
{topic}

Relevant Academic Literature:
{lit_summary}

Workspace Codebase & Data Summary:
{workspace_context or "No starting files in workspace."}
"""

        if critique_feedback:
            user_prompt += f"""
PREVIOUS REVIEWER CRITIQUE (You MUST address and correct these points):
{critique_feedback}
"""

        user_prompt += """
Please generate a novel, testable computational hypothesis formatted as a strict JSON object with fields:
- "title": (str)
- "motivation": (str)
- "theoretical_basis": (str)
- "parameters": (dict of key-value pairs)
- "metrics": (list of metric names)
- "experimental_design": (str description of algorithm & procedure)
- "literature_citations": (list of paper titles / URLs used)
"""

        json_dict = self.router.generate_json(
            role=self.role,
            system_prompt=IDEATOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.4,
        )

        return HypothesisConfig(**json_dict)
