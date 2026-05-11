"""Chatbot — 简单对话机器人（无工具）"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.llm import call_llm
from core.node import Node, Flow, shared

SYSTEM_PROMPT = "你是一个友好的对话助手，请回答用户的问题。"


class ChatNode(Node):
    def exec(self, payload: Any) -> Tuple[str, Any]:
        messages = shared["messages"]
        reply = call_llm(messages=messages, system_prompt=SYSTEM_PROMPT)
        messages.append(reply)
        return "output", reply


class OutputNode(Node):
    def exec(self, payload: Any) -> Tuple[str, Any]:
        content = payload.get("content", "")
        print(f"\n🤖 Assistant: {content}\n")
        return "default", None


def main() -> None:
    if not os.environ.get("OPENAI_API_KEY") or not os.environ.get("OPENAI_BASE_URL"):
        print("请先设置 OPENAI_API_KEY 和 OPENAI_BASE_URL")
        return

    shared["messages"] = []

    chat = ChatNode()
    output = OutputNode()
    chat - "output" >> output

    print("🤖 PuinAgent Chatbot（输入 quit 退出）\n")
    while True:
        user_input = input("👤 You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue

        shared["messages"].append({"role": "user", "content": user_input})
        Flow(chat).run(None)


if __name__ == "__main__":
    main()
