# C4D 拿来说明：用了哪些库 / 工具 / 参考了什么

> 署名：yml（虞梦琳）

## 一、用了哪些库与工具

| 名称 | 用途 | 备注 |
|------|------|------|
| **Ollama 0.35.1** | 本地模型推理引擎，提供 OpenAI 兼容接口 | 官方 <https://ollama.com> |
| **Gemma 4 E4B**（`gemma4:e4b`） | 本地大模型，驱动 Agent 函数调用 | Apache 2.0 协议 |
| **Leaflet.js 1.9.4** | 渲染交互式地图（缩放/点击标记） | 纯前端，单文件 HTML |
| **OpenStreetMap 瓦片** | 地图底图 | 地图 HTML 中通过 tile layer 加载 |
| **Microsoft Edge（headless）** | 无头截图，生成运行证据截图 | 本机自带，未装额外依赖 |
| Python 标准库 | 技能代码全部依赖 | `json`/`os`/`sys`/`time`/`urllib.request`/`math`/`html` |

> 技能代码（agent.py / config.py / tools.py / render_map.py）**零第三方 Python 依赖**，仅用标准库即可运行。

## 二、参考了什么

| 资源 | 用在哪里 |
|------|----------|
| CHALLENGE.md（挑战原文） | 模型选型表、四级任务、交付物清单、截图要求 |
| Ollama Gemma 4 官方页 <https://ollama.com/library/gemma4> | 模型变体与 `gemma4:e4b` 拉取命令 |
| Leaflet.js 官方文档 <https://leafletjs.com> | `circleMarker` / `bindPopup` / `fitBounds` 用法 |
| haversine 公式（通用地理公式） | `get_distance` 球面距离计算 |

## 三、拿了 / 改了 / 没拿

- **拿了（直接使用）**：Ollama、Gemma 4 E4B、Leaflet.js、OpenStreetMap 瓦片——均为开源/免费，符合协议。
- **改了（二次封装）**：把 Leaflet 的 marker 渲染封装进 `render_map.py`，用模型生成的 JSON 动态填充；把 Ollama 的 function calling 封装成 `agent.py` 的三工具编排循环。
- **没拿（自研）**：`tools.py` 的三个工具 Schema 与执行逻辑、`agent.py` 的多步推理循环、`config.py` 的配置结构，均为本挑战自行设计。

## 四、许可与合规

- Gemma 4：Apache 2.0，可自由本地运行与商用。
- Leaflet.js：BSD-2-Clause，开源免费。
- OpenStreetMap 数据：ODbL，地图 HTML 内已保留 attribution（© OpenStreetMap contributors）。
