# C4D Agent 技能：本地 Gemma 4 驱动的地图 Agent

由本地 **Gemma 4 E4B**（Ollama 运行）通过**函数调用**驱动的 Agent 技能：
给定一条自然语言指令，模型自动调用工具生成 SIAS University（郑州西亚斯学院）周边的地点数据，并渲染成交互式 Leaflet 地图。

## 文件说明

| 文件 | 职责 |
|------|------|
| `agent.py` | 函数调用编排循环（发消息 → 收 tool_call → 执行工具 → 回传结果，直到 finalize_map） |
| `config.py` | 配置常量：模型名 / 端点 / 量化 / 设备 / 目标坐标 / 输出路径 |
| `tools.py` | 三个工具（add_marker / get_distance / finalize_map）的 JSON Schema 与本地实现 |
| `render_map.py` | 把模型生成的 marker 列表渲染成 Leaflet.js 交互式 HTML |

## 运行环境

- Python 3（**纯标准库**，无第三方依赖）
- Ollama 0.35.1 + `gemma4:e4b`（Q4_K_M，6.6GB）

## 快速开始

```bash
# 1. 确保模型已就位
ollama pull gemma4:e4b

# 2. 运行 Agent
python agent.py "给我生成一个 SIAS University 周边的地图"
```

运行后：
- 交互式地图输出到 `../yml_C4D_demo/yml_C4D_map.html`
- 运行日志输出到 `../yml_C4D_demo/运行日志.txt`

## 关键设计

- **数据由模型生成**：地点 JSON 全部来自模型 `add_marker` 调用，代码不硬编码任何地点。
- **多步推理**：模型会先 `get_distance` 测算距离，再落点标记。
- **零云依赖**：仅连本机 `http://localhost:11434`，断网也可推理。

## 验证记录

- 13 次工具调用 / 3 步推理 / 8 个标记点 / 2511 tokens / 平均 30.8 tok/s。
- 完整证据见 `../yml_C4D_output_screenshots/` 与 `../yml_C4D_验证报告.md`。
