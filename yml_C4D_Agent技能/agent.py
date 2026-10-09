# -*- coding: utf-8 -*-
"""C4D Agent 技能 —— 本地 Gemma 4 驱动的函数调用 Agent。

流程：
  用户指令 → Gemma 4 决策调用工具 (add_marker / get_distance / finalize_map)
          → Agent 执行工具并回传结果 → 模型继续决策
          → finalize_map 触发交互式地图渲染

用法：
  python agent.py "给我生成一个 SIAS University 周边的地图"
"""
from __future__ import annotations
import json
import os
import sys
import time
import urllib.request

from config import OLLAMA_ENDPOINT, MODEL, QUANTIZATION, DEVICE, SIAS_CENTER, MAP_OUTPUT, RUNLOG_OUTPUT
from tools import TOOL_SCHEMAS, execute_tool
from render_map import render_map

SYSTEM_PROMPT = (
    "你是一个运行在用户本地设备上的地理助手 Agent，由 Gemma 4 模型驱动。"
    "你的任务是：为 SIAS University（郑州西亚斯学院，河南新郑）及周边，"
    "生成一批真实地点的地图标记。学校中心坐标约为 "
    f"纬度 {SIAS_CENTER[0]}，经度 {SIAS_CENTER[1]}。\n"
    "要求：\n"
    "1. 调用 add_marker 工具逐个添加地点（至少 8 个），覆盖校门、图书馆、宿舍、食堂，"
    "以及周边真实地标（如新郑机场、郑州南站方向等）。\n"
    "2. 每个地点给出真实合理的经纬度（学校在 34.4°N, 113.7°E 附近），中英文双语描述。\n"
    "3. 可调用 get_distance 工具计算某地点到学校的距离，并把结果写进该地点的描述里。\n"
    "4. 全部添加完后调用 finalize_map 结束。不要直接输出 JSON，必须通过工具调用完成。"
)


def _chat(messages: list, tools: list | None = None) -> tuple[dict, dict]:
    payload = {"model": MODEL, "messages": messages, "stream": False}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_ENDPOINT, data=data, headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as r:
        resp = json.loads(r.read())
    dt = time.time() - t0
    usage = resp.get("usage", {})
    n_out = int(usage.get("completion_tokens", 0))
    return resp, {"wall_s": dt, "completion_tokens": n_out,
                  "tok_s": n_out / dt if dt else 0.0}


def run(instruction: str) -> tuple[dict, list, list]:
    state: dict = {"markers": [], "finalized": False, "n_tool_calls": 0}
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": instruction},
    ]
    stats: list = []
    log: list = []

    for step in range(1, 40):  # 安全上限，防止死循环
        resp, s = _chat(messages, TOOL_SCHEMAS)
        stats.append(s)
        msg = resp["choices"][0]["message"]
        content = (msg.get("content") or "").strip()
        tool_calls = msg.get("tool_calls") or []

        if content:
            log.append(f"[step {step}] model: {content}")

        if not tool_calls:
            if state["finalized"]:
                break
            # 模型没有走工具也没 finalize：追加提示，引导它走函数调用
            messages.append({"role": "assistant", "content": content or ""})
            messages.append(
                {"role": "user",
                 "content": "请通过工具调用完成任务（先 add_marker，最后 finalize_map）。"}
            )
            continue

        messages.append(
            {"role": "assistant", "content": content or "", "tool_calls": tool_calls}
        )
        for tc in tool_calls:
            fn = tc["function"]
            name = fn["name"]
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            result = execute_tool(name, args, state)
            log.append(
                f"[step {step}] tool {name}({json.dumps(args, ensure_ascii=False)}) "
                f"-> {result}"
            )
            messages.append(
                {"role": "tool", "tool_call_id": tc.get("id", ""), "content": result}
            )

    return state, stats, log


def main() -> None:
    instruction = (
        sys.argv[1] if len(sys.argv) > 1
        else "给我生成一个 SIAS University 周边的地图"
    )

    os.makedirs(os.path.dirname(MAP_OUTPUT), exist_ok=True)

    banner = [
        "=" * 66,
        "C4D 本地大模型 Agent —— 运行证明",
        f"模型: {MODEL}    量化: {QUANTIZATION}",
        f"设备: {DEVICE}",
        f"服务: {OLLAMA_ENDPOINT}",
        "=" * 66,
    ]
    print("\n".join(banner))

    state, stats, log = run(instruction)

    for line in log:
        print(line)

    markers = state["markers"]
    total_tok = sum(s["completion_tokens"] for s in stats)
    total_wall = sum(s["wall_s"] for s in stats)
    avg = total_tok / total_wall if total_wall else 0.0

    title = state.get("title") or "SIAS University 周边地图"
    out_path = render_map(markers, title, MAP_OUTPUT)

    footer = [
        "-" * 66,
        f"地点标记数: {len(markers)}",
        f"工具调用次数: {state['n_tool_calls']}",
        f"生成 tokens: {total_tok}",
        f"平均推理速度: {avg:.1f} tok/s",
        f"输出地图: {out_path}",
    ]
    print("\n".join(footer))

    with open(RUNLOG_OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(banner + log + footer) + "\n")


if __name__ == "__main__":
    main()
