# C4D 方案设计：本地大模型 Agent 技能（Gemma 4）

> 署名：yml（虞梦琳）｜挑战：C4D 本地大模型 Agent 技能

## 一、目标

在**本机设备**上运行 Gemma 4 模型，用其原生**函数调用（function calling）**能力驱动一个可复用的 Agent，完成「生成 SIAS University（郑州西亚斯学院）周边交互式地图」的完整任务，全程不调用任何云端 API。

## 二、技术选型

| 环节 | 选型 | 理由 |
|------|------|------|
| 模型 | **Gemma 4 E4B**（`gemma4:e4b`） | 见下文「为什么选 E4B」 |
| 量化 | **Q4_K_M**（4-bit） | 4GB 显存设备可稳定加载 |
| 推理引擎 | **Ollama 0.35.1** | 一行命令跑模型，自带 OpenAI 兼容 `/v1/chat/completions` 接口 |
| 地图渲染 | **Leaflet.js 1.9.4** | 纯前端，生成单文件 HTML 直接双击打开 |
| 开发语言 | Python 3（纯标准库） | 零第三方 Python 依赖，可复现 |

## 三、为什么选 Gemma 4 E4B

1. **设备硬约束**：本机 15.3GB 内存 + RTX 5050 Laptop 4GB 显存。
   - 26B MoE 需 ~18GB、31B Dense 需 ~20GB，本机跑不动；
   - E4B（~4.5B effective）4-bit 后仅 6.6GB，可稳定加载并留出推理余量。
2. **能力足够**：E4B 原生支持函数调用、结构化输出、系统提示与 128K 上下文，完全覆盖本次 Agent 需求。
3. **速度达标**：实测平均 **30.8 tok/s**，多步 Agent 任务可流畅完成。

## 四、设备信息（提交必标注）

- 操作系统：Windows 11 家庭版
- CPU：AMD Ryzen 9 8940HX（16 核 32 线程）
- 内存：15.3 GB
- GPU：NVIDIA RTX 5050 Laptop（4 GB VRAM）
- 推理端点：`http://localhost:11434/v1/chat/completions`

## 五、架构设计

```
用户指令（"生成 SIAS University 周边地图"）
        │
        ▼
   agent.py（编排循环：发消息 → 收 tool_call → 执行工具 → 回传结果）
        │
        ├─ tools.py   三个函数工具：add_marker / get_distance / finalize_map
        ├─ config.py  模型名 / 端点 / 设备 / 中心坐标（可配置，无硬编码地点）
        └─ render_map.py  marker 数据 → Leaflet.js 交互式 HTML
```

**分层职责**（4 个模块，职责单一）：

- `config.py`：常量与配置（模型、量化、设备、目标坐标、输出路径）。
- `tools.py`：三个工具的 JSON Schema + 本地实现（haversine 球面距离、标记累积、收尾触发渲染）。
- `agent.py`：函数调用编排循环——维护消息历史、解析 `tool_calls`、执行并回传结果、多步推理直到 `finalize_map`。
- `render_map.py`：把模型生成的 marker 列表渲染成可缩放、可点击的 Leaflet 地图。

**关键设计点**：地点数据**全部由模型通过 `add_marker` 生成**，代码中不硬编码任何地点 JSON，保证「数据由本地 Gemma 4 生成」这一硬性要求。

## 六、数据主权与零成本

全程本地推理，无任何云端 API 调用。模型自 Ollama 官方 registry 下载，下载完成后可离线使用。这体现 C4D 的核心价值：数据不离开设备、零推理成本、不受平台审查与断网影响。
