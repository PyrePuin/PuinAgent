# PuinAgent

从零构建一个 Agent，学习笔记与实现记录。

参考教程：[Learn-OpenClaw](https://github.com/lasywolf/Learn-OpenClaw)

## 核心公式

```
workflow = node + node
chatbot  = workflow + loop
agent    = chatbot + tools
```

## 项目结构

```
PuinAgent/
├── core/
│   ├── node.py      # Node + Flow 框架
│   └── llm.py       # LLM 调用封装（DeepSeek API）
├── examples/
│   ├── workflow/            # node + node：三个节点串联
│   ├── chatbot/             # workflow + loop：循环对话
│   └── chatbot_with_tools/  # chatbot + tools：支持工具调用
└── tools/                   # 工具实现（bash, read, write, search...）
```

## 环境配置

```bash
export OPENAI_API_KEY_DEEPSEEK="sk-xxx"
export OPENAI_BASE_URL_DEEPSEEK="https://api.deepseek.com"
```

---

## 学习日志

### Step 1 — Node / Flow 框架

Agent 的最小抽象。所有代码在 [`core/node.py`](./core/node.py)。

#### Node

每个节点做一件事：接收数据，处理后返回**走哪条路 + 传什么数据**。

```python
exec(payload) → (action, next_payload)
```

- `payload` — 节点之间传递的数据，可以是任何类型
- `action` — 字符串标签，告诉 Flow "下一步走谁"
- `_exec` 是框架调的（包了重试），`exec` 是子类写的（业务逻辑）

#### Flow

编排器。从起始节点开始，根据 action 路由到下一个节点，直到没有后继。

```python
action, payload = curr._exec(payload)
curr = curr.successors[action]
```

#### 连接语法

```python
a >> b              # a 的 default 后继 → b
a - "tool_call" >> b  # a 返回 "tool_call" 时 → b
```

`-` 运算符记录 action 标签，`>>` 运算符把目标节点注册到 `successors` 字典。`return other` 支持链式 `a >> b >> c`。

### Step 2 — LLM 调用封装

[`core/llm.py`](./core/llm.py)，基于 OpenAI 兼容接口，使用 DeepSeek API。

两个函数：
- `call_llm_simple(prompt) → str`：传字符串，回字符串。Workflow 用。
- `call_llm(messages, tools, system_prompt) → dict`：传消息列表，支持 tools，返回完整字典（可能含 `tool_calls`）。Agent 用。

OpenAI response 结构：
```python
response.choices[0].message.content      # 文本回复
response.choices[0].message.tool_calls   # 工具调用列表
```

当 LLM 决定调用工具时，`tool_calls` 格式：
```python
[{
    "id": "call_abc123",
    "type": "function",
    "function": {
        "name": "search",
        "arguments": '{"query": "Python asyncio"}'
    }
}]
```

### Step 3 — 三层递进（进行中）

| 层级 | 模式 | 例子 |
|------|------|------|
| Workflow | `node >> node >> node`，跑一次 | Query → Search → Summarize |
| Chatbot | `(node >> node) + while True` | Chat → Output，循环对话 |
| Agent | Chatbot + 条件分支 + tools | Chat ↔ ToolCall → Output |

Agent 的关键：ChatNode 根据 `tool_calls` 分支——有工具调用走 ToolCallNode，执行完回到 ChatNode 再思考；没有就直接输出。

---

## 进度

- [x] Node + Flow 框架
- [x] LLM 调用封装
- [ ] Workflow 例子（编写中）
- [ ] Chatbot 例子
- [ ] Agent 例子
- [ ] RAG
- [ ] Tool / MCP / Skill
- [ ] 阅读 pi-mono
- [ ] 改造 OpenClaw
