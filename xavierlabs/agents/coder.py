import re
from typing import Optional
from xavierlabs.agents.base import BaseAgent
from xavierlabs.agents.ideator import HypothesisConfig


CODER_SYSTEM_PROMPT = """You are 'The Coder', an expert scientific computing, ML, and simulation engineer in the XavierLabs AI swarm.
Your mission is to generate clean, robust, and reproducible Python experiments (`experiment.py`).

Coding Standards:
1. Self-contained: Use standard scientific libraries (numpy, scipy, math, random, json, time). If using torch or sklearn, provide simple pure-numpy fallbacks where possible so experiments execute without heavy GPU requirements.
2. Seed Everything: Set fixed seeds for numpy, random, and torch.
3. Telemetry Output: Print concise progress and metrics to stdout.
4. MANDATORY File Output: At the completion of the experiment, save a JSON dictionary of all final numerical metrics to a file named 'metrics.json' in the current working directory:
   ```python
   with open('metrics.json', 'w') as f:
       json.dump(results_dict, f, indent=2)
   ```
5. Return Code: Return valid executable Python code only. Wrap your code in ```python ... ```.
"""

DEBUGGER_SYSTEM_PROMPT = """You are 'The Coder' acting in Auto-Debugging mode in the XavierLabs AI swarm.
An experiment script failed during execution in the sandbox.
Your task is to analyze the stderr traceback, identify the bug (e.g. dimension mismatch, missing key, type error, zero division), and rewrite the complete corrected `experiment.py` script.

Requirements:
1. Fix the bug while strictly preserving the scientific hypothesis and experiment methodology.
2. Ensure the script still outputs 'metrics.json'.
3. Return valid executable Python code only, wrapped in ```python ... ```.
"""


class CoderAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="The Coder", role="coder")

    def generate_experiment_code(
        self,
        hypothesis: HypothesisConfig,
        audit_feedback: Optional[str] = None,
    ) -> str:
        """Translates hypothesis into executable experiment.py."""
        user_prompt = f"""Generate an executable computational experiment script for the following hypothesis:

Title: {hypothesis.title}

Theoretical Formulation:
{hypothesis.theoretical_basis}

Experimental Parameters:
{hypothesis.parameters}

Metrics to Compute & Record:
{hypothesis.metrics}

Design & Procedure:
{hypothesis.experimental_design}
"""

        if audit_feedback:
            user_prompt += f"""
Pre-flight Audit Feedback:
{audit_feedback}
Please address any potential issues identified above.
"""

        user_prompt += """
Write the complete Python script (experiment.py).
Ensure it executes self-contained, runs fast (< 60s), prints telemetry, and writes 'metrics.json'.
"""

        response = self.router.generate(
            role=self.role,
            system_prompt=CODER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
        )

        return self._extract_python_code(response)

    def debug_experiment_code(
        self,
        failing_code: str,
        stderr_traceback: str,
        stdout_output: str,
        hypothesis: HypothesisConfig,
    ) -> str:
        """Autonomously analyzes traceback and rewrites corrected experiment.py."""
        user_prompt = f"""The experiment script failed during execution.

Hypothesis:
{hypothesis.title}

Failing Code:
```python
{failing_code}
```

Standard Output before crash:
{stdout_output[-1500:] if stdout_output else "None"}

Error Traceback (stderr):
{stderr_traceback}

Analyze the error, locate the bug, and provide the complete fixed Python script.
"""

        response = self.router.generate(
            role=self.role,
            system_prompt=DEBUGGER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.1,
        )

        return self._extract_python_code(response)

    def _extract_python_code(self, text: str) -> str:
        """Extracts Python code from markdown fences if present."""
        code_match = re.search(r"```(?:python)?\s*([\s\S]*?)\s*```", text)
        if code_match:
            return code_match.group(1).strip()
        return text.strip()
