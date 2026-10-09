# C4D 本地大模型 Agent 技能（EduSeed Elite20）

用本地大模型 **Gemma 4 E4B**（Ollama 运行，Q4_K_M 量化，6.6GB）跑通的 Agent 技能：
模型通过 **函数调用**（add_marker / get_distance / finalize_map 三工具）生成 SIAS University（郑州西亚斯学院）周边 8 个地点标记，并产出交互式 Leaflet 地图。

- 模型：`gemma4:e4b`（digest `dc35e8d9c606`）
- 推理引擎：Ollama 0.35.1，端点 `http://localhost:11434/v1/chat/completions`
- 实测：13 次工具调用、3 步推理、2511 tokens、平均 30.8 tok/s
- 完成级别：Level 2（Silver，函数调用 + 交互式地图）完整达成

## 目录

- `yml_C4D_Agent技能/` —— 技能代码（agent.py / tools.py / config.py / render_map.py / README）
- `yml_C4D_demo/` —— 交互式地图 + 运行证明 + 运行日志
- `yml_C4D_output_screenshots/` —— 地图截图 + 运行证明截图
- `yml_C4D_AI日志.md` / `yml_C4D_AAR复盘.md` —— 迭代日志 / 复盘
- `yml_C4D_方案设计.md` / `yml_C4D_验证报告.md` / `yml_C4D_教学说明.md` / `yml_C4D_拿来说明.md` —— 文档

## 运行

```bash
# 需先本地 ollama pull gemma4:e4b
python yml_C4D_Agent技能/agent.py "给我生成一个 SIAS University 周边的地图"
```

纯 Python 标准库，零第三方 Python 依赖；地图为单文件 HTML，双击即可交互。
