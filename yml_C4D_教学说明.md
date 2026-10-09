# C4D 教学说明：怎么安装、怎么复现

> 署名：yml（虞梦琳）｜目标：让一个完全没接触过本地大模型的人也能照着跑通。

## 前置条件

- 一台 Windows / macOS / Linux 电脑，内存 ≥ 8GB（本案例用 16GB 笔记本）
- 能访问互联网（仅首次下载模型需要）

## 第一步：安装 Ollama

1. 打开 <https://ollama.com/download>
2. 下载 Windows 安装包，双击安装（一路下一步）
3. 安装完成后，在任意终端输入 `ollama --version` 验证（本案例版本 0.35.1）

## 第二步：下载 Gemma 4 E4B 模型

```bash
ollama pull gemma4:e4b
```

下载约 5.5GB，速度取决于网络（本案例约 10MB/s）。下载完成后 `ollama list` 应能看到：

```
NAME            ID              SIZE      MODIFIED
gemma4:e4b      dc35e8d9c606    6.6 GB    5 minutes ago
```

> 显存/内存更大的机器可换 `gemma4:26b`（MoE）或 `gemma4:31b`（Dense），但需 16GB+ 显存或 24GB+ 内存。

## 第三步：验证函数调用

用 curl 发一条带工具定义的请求，确认模型能发起 tool_call（详见 CHALLENGE.md「快速开始」的 curl 示例）。这是本挑战最关键的一步——确认本地模型支持原生 function calling。

## 第四步：跑 Agent 技能

1. 把技能目录 `yml_C4D_Agent技能/` 放到任意位置（本案例位于 `C4D_本地大模型Agent技能/` 下）。
2. 进入该目录，运行：

```bash
python agent.py "给我生成一个 SIAS University 周边的地图"
```

3. 脚本会：
   - 连接 `http://localhost:11434/v1/chat/completions`
   - 让 Gemma 4 通过 `add_marker` / `get_distance` / `finalize_map` 三个工具逐步生成地点
   - 把结果渲染成 Leaflet 交互式地图，输出到 `../yml_C4D_demo/yml_C4D_map.html`
   - 同时写一份 `运行日志.txt` 到同一目录

4. 双击 `yml_C4D_map.html`，即可在浏览器中查看可缩放、可点击标记的交互式地图。

## 第五步：验证是否「真的在本地跑」

- 断开 Wi-Fi，地图仍能打开、模型仍能推理（证明数据不离开设备）；
- 终端里 `ollama list` 显示模型已落盘；
- 推理时观察 GPU/内存占用，`tok/s` 速率可见（本案例 30.8 tok/s）。

## 常见问题

| 问题 | 排查 |
|------|------|
| `ollama` 不是内部命令 | 未加入 PATH，重启终端或使用安装目录下的 `ollama.exe` 全路径 |
| 连接 11434 失败 | Ollama 服务未启动，先运行 `ollama serve` 或打开 Ollama 桌面应用 |
| 地图空白 | 首次打开需联网加载 Leaflet/OSM 瓦片；标记数据本身已在 HTML 内嵌，离线也保留 |
| 显存不足 | 换更小模型 `gemma4:e2b`，或调低量化级别 |

## 目录结构一览

```
C4D_本地大模型Agent技能/
├─ yml_C4D_Agent技能/        ← Agent 技能代码（agent.py/config.py/tools.py/render_map.py + README）
├─ yml_C4D_demo/             ← demo 产物（yml_C4D_map.html / 运行日志.txt / 运行证明.html）
├─ yml_C4D_output_screenshots/ ← 运行截图（地图 + 运行证明，含模型名/设备/tok/s）
├─ yml_C4D_方案设计.md
├─ yml_C4D_验证报告.md
├─ yml_C4D_教学说明.md        ← 本文件
├─ yml_C4D_AI日志.md
├─ yml_C4D_拿来说明.md
└─ yml_C4D_AAR复盘.md
```
