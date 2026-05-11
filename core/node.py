"""Node & Flow — Agent 的最小抽象框架

核心思想：
  Node.exec(payload) → (action, next_payload)
  Flow 按 action 标签路由到下一个 Node

用法：
  a >> b          # a 的 "default" 后继 → b
  a - "x" >> b    # a 返回 action="x" 时 → b

公式：
  workflow = node + node
  chatbot  = workflow + loop
  agent    = chatbot + tools
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple

shared: dict[str, Any] = {}


class Node:
    """同步节点：exec(payload) 返回 (action, next_payload)，支持重试。"""

    def __init__(self, max_retries: int = 1, wait: float = 0) -> None:
        self.successors: Dict[str, "Node"] = {}
        self._action: str = "default"
        self.max_retries = max_retries
        self.wait = wait

    def exec(self, payload: Any) -> Tuple[str, Any]:
        raise NotImplementedError

    def _exec(self, payload: Any) -> Tuple[str, Any]:
        for attempt in range(self.max_retries):
            try:
                return self.exec(payload)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                if self.wait > 0:
                    time.sleep(self.wait)
        raise RuntimeError("Unexpected error in Node._exec")

    def __rshift__(self, other: "Node") -> "Node":
        self.successors[self._action] = other
        self._action = "default"
        return other

    def __sub__(self, action: str) -> "Node":
        if not isinstance(action, str):
            raise TypeError("Action must be a string")
        self._action = action or "default"
        return self


class Flow:
    """同步编排器：按 action 依次执行节点。"""

    def __init__(self, start: Optional[Node] = None) -> None:
        self.start = start

    def run(self, payload: Any = None) -> Tuple[Optional[str], Any]:
        curr, last_action = self.start, "default"
        while curr:
            last_action, payload = curr._exec(payload)
            curr = curr.successors.get(last_action)
        return last_action, payload
