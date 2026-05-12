"""LLM 调用封装 — 基于 OpenAI 兼容接口"""
from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

def call_llm_simple(prompt: str) -> str:
    """
    简单的 LLM 调用封装，使用 OpenAI 兼容接口。
    """
    client = OpenAI(
        api_key = os.environ.get("OPENAI_API_KEY_DEEPSEEK"),
        base_url = os.environ.get("OPENAI_BASE_URL_DEEPSEEK"),
    )
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[{"role": "user", "content": prompt}],
    )
    '''
    ChatCompletion(                                                                                               
      id="chatcmpl-xxx",                                                                                        
      choices=[                                                                                                 
          Choice(                                                                                               
              index=0,                                                                                          
              message=ChatMessage(                                                                              
                  role="assistant",
                  content="你好，有什么可以帮你？",                                                             
                  tool_calls=None,  # 或者 [ToolCall(...)]  
              ),                                                                                                
              finish_reason="stop"                          
          )                                                                                                     
      ],                                                                                                        
      usage=Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30)                                      
    )                                         
    '''
    message = response.choices[0].message
    return message.content or ""

def call_llm(messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    system_prompt: str | None = None,
) -> dict[str, Any]:
    """
    消息/工具模式接口：返回 assistant message 字典。
    """
    msgs = list(messages)
    if system_prompt:
        msgs = [{"role": "system", "content": system_prompt}, *msgs]
    
    kwargs: dict[str, Any] = {
        "model": "deepseek-v4-pro",
        "messages": msgs,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    client = OpenAI(
        api_key = os.environ.get("OPENAI_API_KEY_DEEPSEEK"),
        base_url = os.environ.get("OPENAI_BASE_URL_DEEPSEEK"),
    )

    response = client.chat.completions.create(**kwargs)
    message = response.choices[0].message
    result: dict[str, Any] = {
        "role": "assitant",
        "content": message.content,
    }

    reasoning_content = getattr(message, "reasoning_content", None)
    if reasoning_content:
        result["reasoning_content"] = reasoning_content
    '''
    当 LLM 决定调用工具时，tool_calls 大致长这样：                                                                                                                                                                        
    message.tool_calls = [   
        ChatCompletionMessageToolCall(                                                                            
            id="call_abc123",                                                                                     
            type="function",                                                                                      
            function=Function(                                                                                    
                name="search",                                                                                    
                arguments='{"query": "Python asyncio 最佳实践"}'                                                  
            )                                                                                                     
        )                                                                                                         
    ]                                                                                                             
                                                                
    model_dump() 把它转成字典，最终 result 就是：                                                                 
    
    result = {                                                                                                    
        "role": "assistant",                                                                                      
        "content": "",                                                                                            
        "tool_calls": [                                                                                           
            {                                                                                                     
                "id": "call_abc123",                                                                              
                "type": "function",                                                                               
                "function": {                                                                                     
                    "name": "search",                                                                             
                    "arguments": '{"query": "Python asyncio 最佳实践"}'                                           
                }                                                                                                 
            }                                                                                                     
        ]                                                                                                         
    }                                                                                                             
                                                                                                                    
    arguments 是 JSON 字符串，用的时候需要 json.loads() 解析。  
    '''
    if message.tool_calls:
        result["tool_calls"] = [tool_call.model_dump() for tool_call in message.tool_calls]
    return result