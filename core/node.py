from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, Iterable
import time
shared = {}

class Node:
    def __init__(self, max_retries: int=1, wait: float=0) -> None:
        self.max_retries = max_retries
        self.wait = wait

        self.successors: Dict[str, "Node"] = {}
        self._action: str = "default"
    
    def exec(self, payload: Any) -> Tuple[str, Any]:  # pragma: no cover - 需要子类实现)
        '''
        执行节点的核心逻辑。
        返回一个 (action, payload) 的元组，action 是下一个节点的标识，payload 是传递给下一个节点的数据。
        '''
        raise NotImplementedError
    
    def _exec(self, payload: Any) -> Tuple[str, Any]:
        for cur_retry in range(self.max_retries):
            try:
                return self.exec(payload)
            except Exception as e:
                if cur_retry == self.max_retries - 1:
                    raise e
                if self.wait > 0:
                    time.sleep(self.wait)
        raise RuntimeError("Unexpected error in Node._exec")
    
    def __rshift__(self, other: "Node") -> "Node":
        '''
        用于连接节点，把other注册为当前节点的后续，用之前存的aciton作为索引
        '''
        self.successors[self._action] = other
        self._action = "default"
        return other
    
    def __sub__(self, action: str) -> "Node":
        '''
        用于起名，将当前节点的action设置为制定字符串，把下一个链接应该匹配那个action记下来
        '''
        if not isinstance(action, str):
            raise ValueError("Action must be a string")
        self._action = action or "default"
        return self
    
class Flow:
    """
    同步编排器：按 action 依次执行节点。
    """
    def __init__(self, start: Optional[Node]=None) -> None:
        self.start = start

    def run(self, payload: Any) -> Tuple[Optional[str], Any]:
        curr, last_action = self.start, "default"
        while curr:
            last_action, payload = curr._exec(payload)
            curr = curr.successors.get(last_action)
        return last_action, payload