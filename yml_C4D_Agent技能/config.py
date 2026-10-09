# -*- coding: utf-8 -*-
"""C4D Agent 技能 —— 配置与常量。

本地大模型 Agent：由 Gemma 4（Ollama 运行）驱动，通过**函数调用**
(function calling) 生成 SIAS University（郑州西亚斯学院）周边交互式地图。
"""
from __future__ import annotations

# ---- Ollama OpenAI 兼容端点 ----
OLLAMA_ENDPOINT = "http://localhost:11434/v1/chat/completions"

# ---- 使用的模型（提交时必须标注：模型 + 量化 + 设备）----
MODEL = "gemma4:e4b"          # Gemma 4 E4B（~4.5B effective，推荐入门款）
QUANTIZATION = "Q4_K_M"       # Ollama 默认 4-bit 量化
DEVICE = (
    "Windows 11 家庭版 / AMD Ryzen 9 8940HX (16C32T) / "
    "15.3GB RAM / NVIDIA RTX 5050 Laptop 4GB VRAM"
)

# ---- 目标地点：SIAS University（郑州西亚斯学院，河南新郑）----
SIAS_CENTER = (34.40, 113.73)   # (纬度, 经度)

# ---- 输出目录（demo 交付物目录，位于技能包同级）----
import os
DEMO_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "yml_C4D_demo")
)
MAP_OUTPUT = os.path.join(DEMO_DIR, "yml_C4D_map.html")
RUNLOG_OUTPUT = os.path.join(DEMO_DIR, "运行日志.txt")
