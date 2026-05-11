"""Agent — 支持工具调用的对话机器人"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.llm import call_llm
from core.node import Node, Flow, shared

SYSTEM_PROMPT = (
    "你是一个会调用工具的助手。"
    "当问题涉及最新信息时，优先调用 search 工具。"
    "若问题是本地文件/代码相关，优先使用 read/grep/find/ls 等本地工具。"
)


# --- Tool 定义（简化版，后续章节会扩展） ---

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "搜索互联网获取最新信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                },
                "required": ["query"],
            },
        },
    },
]


def execute_tool(name: str, arguments: dict) -> str:
    """执行工具调用（简化版）"""
    if name == "search":
        return f"搜索结果：关于 [{arguments.get('query', '')}] 的信息..."
    return f"未知工具: {name}"


# --- Node 定义 ---

class ChatNode(Node):
    def exec(self, payload: Any) -> Tuple[str, Any]:
        reply = call_llm(
            messages=shared["messages"],
            tools=TOOLS,
            system_prompt=SYSTEM_PROMPT,
        )
        shared["messages"].append(reply)
        if reply.get("tool_calls"):
            return "tool_call", reply
        return "output", reply


class ToolCallNode(Node):
    def exec(self, payload: Any) -> Tuple[str, Any]:
        for tc in payload.get("tool_calls", []):
            fn = tc["function"]
            name, args_str = fn["name"], fn["arguments"]
            import json
            args = json.loads(args_str) if isinstance(args_str, str) else args_str
            result = execute_tool(name, args)
            print(f"  [Tool] {name}({args}) → {result[:80]}")
            shared["messages"].append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result,
            })
        return "chat", None


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
    tool_call = ToolCallNode()
    output = OutputNode()

    chat - "tool_call" >> tool_call
    tool_call - "chat" >> chat
    chat - "output" >> output

    print("🤖 PuinAgent（支持工具调用，输入 quit 退出）\n")
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
