"""LLM 调用封装 — 基于 OpenAI 兼容接口"""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

MODEL = os.environ.get("LLM_MODEL", "kimi-k2.5")


def _client() -> OpenAI:
    return OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL"),
    )


def call_llm_simple(prompt: str) -> str:
    """简单文本生成：输入 prompt，返回字符串。"""
    resp = _client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content or ""


def call_llm(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    system_prompt: str | None = None,
) -> dict[str, Any]:
    """消息/工具模式接口：返回 assistant message 字典。"""
    msgs = list(messages)
    if system_prompt:
        msgs = [{"role": "system", "content": system_prompt}, *msgs]

    kwargs: dict[str, Any] = {"model": MODEL, "messages": msgs}
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    resp = _client().chat.completions.create(**kwargs)
    message = resp.choices[0].message

    result: dict[str, Any] = {
        "role": "assistant",
        "content": message.content or "",
    }

    if hasattr(message, "reasoning_content") and message.reasoning_content:
        result["reasoning_content"] = message.reasoning_content

    if message.tool_calls:
        result["tool_calls"] = [tc.model_dump() for tc in message.tool_calls]

    return result


if __name__ == "__main__":
    print(call_llm_simple("用一句话解释什么是 Agent。"))
