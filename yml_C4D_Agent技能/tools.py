# -*- coding: utf-8 -*-
"""C4D Agent 技能 —— 工具集（function calling）。

为 Gemma 4 定义三个可调用工具：
  - add_marker     添加一个地点标记（名称/坐标/描述/类别）
  - get_distance   计算两个经纬度坐标之间的球面距离（km）
  - finalize_map   结束流程，触发地图渲染

地点数据**全部由模型通过 add_marker 生成**，本文件只负责执行与记录，
不硬编码任何地点 JSON。
"""
from __future__ import annotations
import math

R_EARTH_KM = 6371.0


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH_KM * math.asin(math.sqrt(a))


# ---- 工具的 JSON Schema（OpenAI tools 格式，Ollama 兼容）----
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "add_marker",
            "description": "在地图上添加一个真实存在的地点标记，记录名称、坐标与描述。",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "英文地点名"},
                    "name_zh": {"type": "string", "description": "中文地点名"},
                    "latitude": {"type": "number", "description": "纬度（约 34.4）"},
                    "longitude": {"type": "number", "description": "经度（约 113.7）"},
                    "description": {"type": "string", "description": "1-2 句中英文描述"},
                    "category": {
                        "type": "string",
                        "enum": ["校园建筑", "宿舍", "餐饮", "交通", "地标", "休闲"],
                        "description": "地点类别",
                    },
                },
                "required": ["name", "name_zh", "latitude", "longitude", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_distance",
            "description": "计算两个经纬度坐标之间的直线距离（公里）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "lat1": {"type": "number"},
                    "lng1": {"type": "number"},
                    "lat2": {"type": "number"},
                    "lng2": {"type": "number"},
                },
                "required": ["lat1", "lng1", "lat2", "lng2"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finalize_map",
            "description": "所有地点已添加完毕，结束流程并触发地图渲染。",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "地图标题"},
                    "summary": {"type": "string", "description": "一句话总结本次生成内容"},
                },
                "required": ["title"],
            },
        },
    },
]


def execute_tool(name: str, args: dict, state: dict) -> str:
    """执行一次工具调用，返回给模型的文本结果；state 跨工具共享已添加标记。"""
    if name == "add_marker":
        marker = {
            "name": args["name"],
            "name_zh": args["name_zh"],
            "lat": float(args["latitude"]),
            "lng": float(args["longitude"]),
            "description": args["description"],
            "category": args.get("category", "地标"),
        }
        state.setdefault("markers", []).append(marker)
        state["n_tool_calls"] = state.get("n_tool_calls", 0) + 1
        return (
            f"已添加 {marker['name_zh']}({marker['name']}) @ "
            f"({marker['lat']:.4f}, {marker['lng']:.4f})，"
            f"当前共 {len(state['markers'])} 个地点"
        )

    if name == "get_distance":
        d = _haversine(
            float(args["lat1"]), float(args["lng1"]),
            float(args["lat2"]), float(args["lng2"]),
        )
        state["n_tool_calls"] = state.get("n_tool_calls", 0) + 1
        return f"两点直线距离约 {d:.2f} km"

    if name == "finalize_map":
        state["finalized"] = True
        state["title"] = args.get("title", "SIAS University 周边地图")
        state["summary"] = args.get("summary", "")
        state["n_tool_calls"] = state.get("n_tool_calls", 0) + 1
        return f"已结束，共 {len(state.get('markers', []))} 个地点标记"

    raise ValueError(f"未知工具: {name}")
