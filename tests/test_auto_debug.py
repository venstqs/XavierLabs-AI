import pytest
from xavierlabs.agents.coder import CoderAgent
from xavierlabs.agents.ideator import HypothesisConfig


def test_coder_extract_code():
    coder = CoderAgent()
    markdown_wrapped = """
Here is the code:
```python
import json
print("Hello world")
```
Hope that helps!
"""
    clean_code = coder._extract_python_code(markdown_wrapped)
    assert clean_code == 'import json\nprint("Hello world")'
