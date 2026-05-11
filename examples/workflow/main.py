"""Workflow Example — 搜索工作流: Query → Search → Summarize"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.llm import call_llm_simple
from core.node import Node, Flow


class QueryNode(Node):
    def exec(self, payload: Any) -> Tuple[str, Any]:
        return "search", str(payload)


class SearchNode(Node):
    def exec(self, payload: Any) -> Tuple[str, Any]:
        # TODO: 接入真实搜索工具
        mock_results = f"关于 [{payload}] 的搜索结果..."
        return "summarize", mock_results


class SummarizeNode(Node):
    def exec(self, payload: Any) -> Tuple[str, Any]:
        prompt = f"基于以下内容写一句话摘要：{payload}"
        text = call_llm_simple(prompt)
        return "default", text


def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        print("请先设置环境变量 OPENAI_API_KEY")
        return

    query = QueryNode()
    search = SearchNode()
    summarize = SummarizeNode()

    query - "search" >> search
    search - "summarize" >> summarize

    flow = Flow(query)
    _, result = flow.run("Python asyncio 最佳实践")
    print("Workflow 输出：", result)


if __name__ == "__main__":
    main()
