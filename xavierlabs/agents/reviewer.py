from typing import Dict, Any, List
from pydantic import BaseModel, Field
from xavierlabs.agents.base import BaseAgent
from xavierlabs.agents.ideator import HypothesisConfig


class HypothesisReview(BaseModel):
    novelty_score: float = Field(description="Score from 1 to 10 evaluating intellectual novelty")
    rigor_score: float = Field(description="Score from 1 to 10 evaluating theoretical and mathematical soundness")
    feasibility_score: float = Field(description="Score from 1 to 10 evaluating whether it can execute cleanly within standard compute")
    overall_score: float = Field(description="Weighted overall score (1-10)")
    approved: bool = Field(description="True if overall_score >= 7.0 and feasibility >= 6.0")
    strengths: List[str] = Field(description="Key scientific strengths")
    weaknesses: List[str] = Field(description="Scientific weaknesses or potential failure modes")
    modifications_required: str = Field(description="Specific actionable feedback if rejected or refinement suggestions")


class CodeAudit(BaseModel):
    approved: bool = Field(description="True if the script is sound and safe to execute")
    score: float = Field(description="Code quality and execution safety score (1-10)")
    audit_notes: str = Field(description="Review of correctness, dependency risks, and metrics output")
    potential_risks: List[str] = Field(description="Identified risks (e.g. OOM, missing imports, infinite loops)")


REVIEWER_SYSTEM_PROMPT = """You are 'The Reviewer', a senior peer-review scientist and algorithmic auditor in the XavierLabs AI swarm.
You simulate a rigorous, uncompromising academic peer-review committee.

Your Standards:
1. Reject hand-waving or trivial hypotheses.
2. Ensure mathematical rigor and falsifiable empirical predictions.
3. In code reviews: strictly verify that code is self-contained, does not perform unsafe operations, contains proper seed initialization, and writes results to 'metrics.json'.
4. Format output strictly as JSON.
"""


class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="The Reviewer", role="reviewer")

    def review_hypothesis(self, hypothesis: HypothesisConfig) -> HypothesisReview:
        """Peer-reviews the Ideator's hypothesis for novelty, rigor, and feasibility."""
        user_prompt = f"""Review the following scientific research hypothesis:

Title: {hypothesis.title}

Motivation:
{hypothesis.motivation}

Theoretical Basis:
{hypothesis.theoretical_basis}

Parameters & Conditions:
{hypothesis.parameters}

Metrics:
{hypothesis.metrics}

Experimental Design:
{hypothesis.experimental_design}

Citations:
{hypothesis.literature_citations}

Evaluate this hypothesis rigorously. Return a strict JSON object with:
- "novelty_score": (float 1-10)
- "rigor_score": (float 1-10)
- "feasibility_score": (float 1-10)
- "overall_score": (float 1-10)
- "approved": (bool - true only if overall_score >= 7.0 and feasibility_score >= 6.0)
- "strengths": (list of str)
- "weaknesses": (list of str)
- "modifications_required": (str)
"""
        json_dict = self.router.generate_json(
            role=self.role,
            system_prompt=REVIEWER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
        )
        return HypothesisReview(**json_dict)

    def audit_code(self, script_code: str, hypothesis: HypothesisConfig) -> CodeAudit:
        """Audits the Coder's generated experiment.py script before sandbox execution."""
        user_prompt = f"""Perform a pre-flight architectural and safety audit on the following Python research script:

Hypothesis Being Tested:
{hypothesis.title}

Metrics Expected:
{hypothesis.metrics}

Candidate Script (experiment.py):
```python
{script_code}
```

Audit Criteria:
1. Correctness: Does it properly implement the hypothesis and test conditions?
2. Reproducibility: Does it seed numpy/torch/random generators?
3. Output Compliance: Does it save structured numerical results to 'metrics.json' in the current working directory?
4. Safety & Compute Limits: Is it free from infinite loops, malicious file deletions, or runaway memory allocation?

Return a strict JSON object with:
- "approved": (bool)
- "score": (float 1-10)
- "audit_notes": (str)
- "potential_risks": (list of str)
"""
        json_dict = self.router.generate_json(
            role=self.role,
            system_prompt=REVIEWER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
        )
        return CodeAudit(**json_dict)
