"""Workflow Example - 搜索工作流示例

工作流: Query -> Search -> Summarize
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.llm import call_llm_simple
from core.node import Node, Flow


