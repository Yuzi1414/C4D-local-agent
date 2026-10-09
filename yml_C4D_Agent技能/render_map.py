# -*- coding: utf-8 -*-
"""C4D Agent 技能 —— 交互式地图渲染（Leaflet.js）。

把模型通过函数调用生成的 marker 列表渲染成一张可缩放、可点击的交互式地图。
"""
from __future__ import annotations
import html
import json


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>__TITLE__</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html,body,#map{height:100%;margin:0;}
  .legend{position:absolute;z-index:1000;right:10px;top:10px;background:#fff;
    padding:10px 14px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.25);
    font:13px/1.7 -apple-system,"Segoe UI",sans-serif;max-width:300px;}
  .legend b{font-size:15px;}
  .dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;}
  hr{margin:8px 0;border:none;border-top:1px solid #eee;}
</style>
</head>
<body>
<div id="map"></div>
<div class="legend">
  <b>__TITLE__</b><br>
  <span id="cnt"></span><br>
  <small style="color:#888">数据由本地 Gemma 4 模型经函数调用生成</small>
  <hr><div id="legend-items"></div>
</div>
<script>
const points = __POINTS__;
const palette = {"校园建筑":"#e11d48","宿舍":"#f59e0b","餐饮":"#10b981",
  "交通":"#3b82f6","地标":"#8b5cf6","休闲":"#14b8a6","其他":"#64748b"};
const map = L.map('map').setView([__CLAT__, __CLNG__], 14);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);
const layer = L.featureGroup();
const seen = {};
for (const p of points) {
  const cat = p.category || '其他';
  const col = palette[cat] || palette['其他'];
  seen[cat] = (seen[cat] || 0) + 1;
  const m = L.circleMarker([p.lat, p.lng],
    {radius:8, color:col, weight:2, fillColor:col, fillOpacity:0.8});
  m.bindPopup('<b>' + p.name_zh + '</b> (' + p.name + ')<br>' + p.description +
    '<br><small>坐标: ' + p.lat.toFixed(4) + ', ' + p.lng.toFixed(4) + '</small>');
  layer.addLayer(m);
}
layer.addTo(map);
document.getElementById('cnt').textContent = '共 ' + points.length + ' 个标记点';
let html = '';
for (const [cat, n] of Object.entries(seen)) {
  html += '<div><span class="dot" style="background:' + palette[cat] + '"></span>' +
    cat + ' (' + n + ')</div>';
}
document.getElementById('legend-items').innerHTML = html;
if (points.length) map.fitBounds(layer.getBounds().pad(0.15));
</script>
</body>
</html>
"""


def render_map(markers: list, title: str, output_path: str) -> str:
    """渲染交互式地图 HTML 并写入 output_path，返回路径。"""
    points = [
        {
            "name": m["name"],
            "name_zh": m["name_zh"],
            "lat": m["lat"],
            "lng": m["lng"],
            "description": m["description"],
            "category": m.get("category", "地标"),
        }
        for m in markers
    ]
    # 转义 "</" 防止破坏 <script>，其余交给 JSON 处理
    points_js = json.dumps(points, ensure_ascii=False).replace("</", "<\\/")

    if markers:
        clat = sum(m["lat"] for m in markers) / len(markers)
        clng = sum(m["lng"] for m in markers) / len(markers)
    else:
        clat, clng = 34.40, 113.73

    doc = (
        _HTML_TEMPLATE
        .replace("__TITLE__", html.escape(title))
        .replace("__POINTS__", points_js)
        .replace("__CLAT__", str(round(clat, 5)))
        .replace("__CLNG__", str(round(clng, 5)))
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc)
    return output_path
