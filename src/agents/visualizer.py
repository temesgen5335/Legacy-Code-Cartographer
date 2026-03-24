"""
VisualizerAgent — interactive graph visualizations for the Brownfield Cartographer.

Features (v2):
 - Node search with real-time highlight
 - Click-to-inspect panel: full node metadata, upstream/downstream neighbours
 - Color-coded by node type + dead-code flagging
 - PageRank / betweenness sizing
 - Suspicious hub warnings
 - Separate optimized renderers for Module Graph and Lineage Graph
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import networkx as nx
from pyvis.network import Network

from src.graph.knowledge_graph import KnowledgeGraph


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

class VisualizerAgent:
    """Generates rich interactive HTML visualizations of the KnowledgeGraph."""

    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg

    def generate_module_graph(self, output_path: str) -> dict[str, Any]:
        return render_module_graph(self.kg.graph, Path(output_path))

    def generate_lineage_graph(self, output_path: str) -> dict[str, Any]:
        return render_lineage_graph(self.kg.graph, Path(output_path))

    def generate_html(self, output_path: str, filter_type: str = "all") -> dict[str, Any]:
        """Convenience wrapper — routes to the correct renderer."""
        if filter_type == "lineage":
            return self.generate_lineage_graph(output_path)
        return self.generate_module_graph(output_path)


# ─────────────────────────────────────────────────────────────────────────────
# Module graph renderer
# ─────────────────────────────────────────────────────────────────────────────

def render_module_graph(graph: nx.DiGraph, output_html: Path) -> dict[str, Any]:
    sanitized, warnings = _preprocess_module_graph(graph)
    report = _build_report(sanitized, warnings)
    report["graph_type"] = "module"

    if sanitized.number_of_nodes() == 0:
        _write_empty_html(output_html, "No module graph data found.")
        report["labeled_nodes"] = 0
        return report

    pagerank = nx.pagerank(sanitized) if sanitized.number_of_edges() > 0 else {}
    degrees = dict(sanitized.degree())
    ranked_nodes = _rank_nodes(sanitized, pagerank)
    n_labels = min(18, max(8, int(math.sqrt(sanitized.number_of_nodes()))))
    labeled_nodes = set(ranked_nodes[:n_labels])

    net = Network(height="900px", width="100%", directed=True, notebook=False, bgcolor="#fbfbf7")
    net.set_options(_module_options())

    # Build serialisable node data for the JS detail panel
    node_data_map: dict[str, dict] = {}

    for node_id, attrs in sanitized.nodes(data=True):
        score = pagerank.get(node_id, 0.0)
        degree = degrees.get(node_id, 0)
        is_dead = bool(attrs.get("is_dead_code_candidate", False))
        is_key = node_id in labeled_nodes
        color = _module_color(is_dead=is_dead, is_key=is_key)
        size = _scale(degree + (score * 500.0), lower=10, upper=42)
        label = _module_label(node_id) if is_key else ""
        title = _module_tooltip(node_id, attrs, degree, score)

        net.add_node(
            node_id,
            label=label,
            title=title,
            color=color,
            size=size,
            mass=2.2 if is_key else 0.8,
            font={"size": 18 if is_key else 10, "color": "#1f2933", "face": "Georgia"},
        )

        node_data_map[node_id] = {
            "id": node_id,
            "label": _module_label(node_id),
            "node_type": attrs.get("node_type", "module"),
            "language": attrs.get("language", ""),
            "loc": attrs.get("loc", 0),
            "complexity": attrs.get("complexity_score", 0),
            "pagerank": round(score, 6),
            "degree": degree,
            "velocity_30d": attrs.get("change_velocity_30d", 0),
            "is_dead_code": is_dead,
            "purpose": attrs.get("purpose_statement", ""),
            "imports": list(sanitized.successors(node_id)),
            "imported_by": list(sanitized.predecessors(node_id)),
        }

    for source, target, attrs in sanitized.edges(data=True):
        edge_type = str(attrs.get("edge_type", "IMPORTS"))
        is_key_edge = source in labeled_nodes or target in labeled_nodes
        net.add_edge(
            source, target,
            title=edge_type, arrows="to",
            width=2 if is_key_edge else 1,
            color="#6c757d" if is_key_edge else "#adb5bd",
        )

    report["labeled_nodes"] = len(labeled_nodes)
    report["top_nodes_by_degree"] = _top_nodes_by_degree(sanitized)

    html = _assemble_html(
        net,
        node_data_map=node_data_map,
        legend_html=_legend_html("module"),
        graph_type="module",
    )
    output_html.write_text(html, encoding="utf-8")
    return report


# ─────────────────────────────────────────────────────────────────────────────
# Lineage graph renderer
# ─────────────────────────────────────────────────────────────────────────────

def render_lineage_graph(graph: nx.DiGraph, output_html: Path) -> dict[str, Any]:
    sanitized, warnings = _preprocess_lineage_graph(graph)
    report = _build_report(sanitized, warnings)
    report["graph_type"] = "lineage"

    if sanitized.number_of_nodes() == 0:
        _write_empty_html(output_html, "No lineage graph data found.")
        report["labeled_nodes"] = 0
        return report

    degrees = dict(sanitized.degree())
    betweenness = (
        nx.betweenness_centrality(sanitized)
        if sanitized.number_of_nodes() <= 250
        else {}
    )
    ranked_nodes = _rank_nodes(sanitized, betweenness)
    n_labels = min(14, max(6, int(math.sqrt(sanitized.number_of_nodes()))))
    labeled_nodes = {
        n for n in ranked_nodes[:n_labels] if degrees.get(n, 0) > 0
    }

    net = Network(height="900px", width="100%", directed=True, notebook=False, bgcolor="#fffdfa")
    net.set_options(_lineage_options(sanitized.number_of_nodes()))

    node_data_map: dict[str, dict] = {}

    for node_id, attrs in sanitized.nodes(data=True):
        node_type = _infer_node_type(node_id, attrs)
        degree = degrees.get(node_id, 0)
        is_key = node_id in labeled_nodes or degree >= 2
        size = _scale(degree, lower=14, upper=34)
        label = _lineage_label(node_id, attrs) if is_key else ""
        title = _lineage_tooltip(node_id, attrs, degree)

        net.add_node(
            node_id,
            label=label,
            title=title,
            color=_lineage_color(node_type),
            size=size,
            level=_lineage_level(node_type),
            font={"size": 18 if is_key else 10, "color": "#1f2933", "face": "Georgia"},
            shape="dot",
        )

        node_data_map[node_id] = {
            "id": node_id,
            "label": _lineage_label(node_id, attrs),
            "node_type": node_type,
            "degree": degree,
            "source_file": attrs.get("source_file", ""),
            "storage_type": attrs.get("storage_type", ""),
            "upstream": list(sanitized.predecessors(node_id)),
            "downstream": list(sanitized.successors(node_id)),
        }

    for source, target, attrs in sanitized.edges(data=True):
        edge_type = str(attrs.get("edge_type", ""))
        is_key_edge = source in labeled_nodes or target in labeled_nodes
        net.add_edge(
            source, target,
            arrows="to", title=edge_type,
            width=2 if is_key_edge else 1,
            color="#7f8c8d", smooth=False,
        )

    report["labeled_nodes"] = len(labeled_nodes)
    report["top_nodes_by_degree"] = _top_nodes_by_degree(sanitized)

    html = _assemble_html(
        net,
        node_data_map=node_data_map,
        legend_html=_legend_html("lineage"),
        graph_type="lineage",
    )
    output_html.write_text(html, encoding="utf-8")
    return report


# ─────────────────────────────────────────────────────────────────────────────
# HTML assembly — injects search bar + detail panel into pyvis output
# ─────────────────────────────────────────────────────────────────────────────

def _assemble_html(
    net: Network,
    *,
    node_data_map: dict[str, dict],
    legend_html: str,
    graph_type: str,
) -> str:
    base_html = net.generate_html(notebook=False)
    node_json = json.dumps(node_data_map, ensure_ascii=False)

    ui_html = f"""
    {legend_html}

    <!-- Search bar -->
    <div id="search-container" style="
        position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:9999;
        background:rgba(255,255,255,0.96);border:1px solid #d0d7de;border-radius:32px;
        padding:8px 18px;display:flex;gap:10px;align-items:center;
        box-shadow:0 4px 20px rgba(0,0,0,0.1);font-family:Georgia,serif;min-width:340px;">
        <span style="font-size:18px;">🔍</span>
        <input id="node-search" type="text" placeholder="Search nodes…"
            style="border:none;outline:none;font-size:14px;width:260px;background:transparent;" />
        <button id="search-clear" style="border:none;background:none;cursor:pointer;font-size:16px;color:#888;">✕</button>
    </div>

    <!-- Node detail panel -->
    <div id="node-panel" style="
        display:none;position:fixed;right:20px;top:50%;transform:translateY(-50%);z-index:9998;
        background:rgba(255,255,255,0.98);border:1px solid #d0d7de;border-radius:16px;
        padding:20px 22px;width:320px;max-height:70vh;overflow-y:auto;
        font-family:Georgia,serif;font-size:13px;box-shadow:0 8px 32px rgba(0,0,0,0.15);">
        <button id="panel-close" style="
            position:absolute;top:10px;right:14px;border:none;background:none;
            cursor:pointer;font-size:18px;color:#666;">✕</button>
        <div id="panel-content"></div>
    </div>

    <script>
    (function() {{
        // ── node data injected from Python ───────────────────────────────
        const NODE_DATA = {node_json};

        // ── wait for vis network to be ready ─────────────────────────────
        function waitForNetwork(cb) {{
            if (typeof network !== 'undefined') {{ cb(); }}
            else {{ setTimeout(() => waitForNetwork(cb), 100); }}
        }}

        waitForNetwork(function() {{
            // ── Search ───────────────────────────────────────────────────
            const searchInput = document.getElementById('node-search');
            const clearBtn    = document.getElementById('search-clear');

            let highlightedNodes = new Set();

            searchInput.addEventListener('input', function() {{
                const q = this.value.trim().toLowerCase();
                if (!q) {{
                    network.unselectAll();
                    highlightedNodes.clear();
                    return;
                }}
                const matched = Object.keys(NODE_DATA).filter(id =>
                    id.toLowerCase().includes(q) ||
                    (NODE_DATA[id].label && NODE_DATA[id].label.toLowerCase().includes(q)) ||
                    (NODE_DATA[id].purpose && NODE_DATA[id].purpose.toLowerCase().includes(q))
                );
                highlightedNodes = new Set(matched);
                if (matched.length > 0) {{
                    network.selectNodes(matched);
                    if (matched.length === 1) {{
                        network.focus(matched[0], {{scale:1.4, animation:true}});
                        showPanel(matched[0]);
                    }}
                }} else {{
                    network.unselectAll();
                }}
            }});

            clearBtn.addEventListener('click', function() {{
                searchInput.value = '';
                network.unselectAll();
                highlightedNodes.clear();
                hidePanel();
            }});

            // ── Node click → detail panel ─────────────────────────────────
            network.on('click', function(params) {{
                if (params.nodes.length > 0) {{
                    showPanel(params.nodes[0]);
                }} else {{
                    hidePanel();
                }}
            }});

            // ── Double-click → focus neighbours ──────────────────────────
            network.on('doubleClick', function(params) {{
                if (params.nodes.length > 0) {{
                    const nodeId = params.nodes[0];
                    const data = NODE_DATA[nodeId];
                    if (!data) return;
                    const neighbours = [
                        ...( data.imports || data.downstream || []),
                        ...(data.imported_by || data.upstream || []),
                        nodeId
                    ];
                    network.selectNodes(neighbours);
                    network.fit({{ nodes: neighbours, animation: true }});
                }}
            }});

            // ── Hover highlight ───────────────────────────────────────────
            network.on('hoverNode', function(params) {{
                const nodeId = params.node;
                const data = NODE_DATA[nodeId];
                if (!data) return;
                const related = [
                    ...(data.imports || data.downstream || []),
                    ...(data.imported_by || data.upstream || []),
                    nodeId
                ];
                network.selectNodes(related);
            }});

            network.on('blurNode', function() {{
                if (document.getElementById('node-panel').style.display === 'none') {{
                    network.unselectAll();
                }}
            }});
        }});

        // ── Panel rendering ───────────────────────────────────────────────
        function showPanel(nodeId) {{
            const data = NODE_DATA[nodeId];
            if (!data) return;

            const panel = document.getElementById('node-panel');
            const content = document.getElementById('panel-content');

            const importList = (data.imports || data.downstream || []);
            const importedByList = (data.imported_by || data.upstream || []);

            const badge = (t) => `<span style="
                display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;
                background:#e8f4fd;color:#1a6fa8;margin:2px;">${{t}}</span>`;

            const section = (title, items) => items.length === 0 ? '' : `
                <div style="margin-top:12px;">
                    <div style="font-weight:700;font-size:11px;color:#6c757d;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:4px;">${{title}} (${{items.length}})</div>
                    <div style="display:flex;flex-wrap:wrap;gap:4px;">
                        ${{items.slice(0, 20).map(n => `<span onclick="focusNode('${{n}}')" style="
                            cursor:pointer;display:inline-block;padding:2px 8px;border-radius:10px;
                            font-size:11px;background:#f0f4f8;color:#2d3748;margin:2px;
                            border:1px solid #d0d7de;" title="${{n}}">${{NODE_DATA[n]?.label || n.split('/').pop() || n}}</span>`).join('')}}
                        ${{items.length > 20 ? `<span style="font-size:11px;color:#888;">+${{items.length - 20}} more</span>` : ''}}
                    </div>
                </div>`;

            const deadBadge = data.is_dead_code
                ? '<span style="background:#fef3f2;color:#c0392b;padding:2px 8px;border-radius:8px;font-size:11px;margin-left:8px;">⚠ Dead Code</span>'
                : '';

            content.innerHTML = `
                <div style="font-weight:700;font-size:15px;margin-bottom:4px;word-break:break-all;">
                    ${{data.label || data.id}} ${{deadBadge}}
                </div>
                <div style="color:#6c757d;font-size:11px;margin-bottom:12px;word-break:break-all;">${{data.id}}</div>

                <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px;">
                    ${{data.node_type ? `<div><b>Type</b><br>${{badge(data.node_type)}}</div>` : ''}}
                    ${{data.language ? `<div><b>Language</b><br>${{badge(data.language)}}</div>` : ''}}
                    ${{data.loc ? `<div><b>Lines</b><br><span style="font-size:14px;font-weight:600;">${{data.loc}}</span></div>` : ''}}
                    ${{data.complexity ? `<div><b>Complexity</b><br><span style="font-size:14px;font-weight:600;">${{data.complexity}}</span></div>` : ''}}
                    ${{data.pagerank !== undefined ? `<div><b>PageRank</b><br><span style="font-size:14px;font-weight:600;">${{data.pagerank.toFixed(5)}}</span></div>` : ''}}
                    ${{data.degree !== undefined ? `<div><b>Degree</b><br><span style="font-size:14px;font-weight:600;">${{data.degree}}</span></div>` : ''}}
                    ${{data.velocity_30d !== undefined && data.velocity_30d ? `<div><b>Velocity 30d</b><br><span style="font-size:14px;font-weight:600;">${{data.velocity_30d}}</span></div>` : ''}}
                    ${{data.storage_type ? `<div><b>Storage</b><br>${{badge(data.storage_type)}}</div>` : ''}}
                </div>

                ${{data.purpose ? `
                <div style="margin-top:12px;padding:10px;background:#f8f9fa;border-radius:8px;font-size:12px;color:#495057;line-height:1.5;border-left:3px solid #d95f02;">
                    ${{data.purpose}}
                </div>` : ''}}

                ${{data.source_file ? `<div style="margin-top:8px;font-size:11px;color:#888;">📄 ${{data.source_file}}</div>` : ''}}

                ${{section('Imports / Downstream', importList)}}
                ${{section('Imported By / Upstream', importedByList)}}

                <div style="margin-top:16px;border-top:1px solid #eee;padding-top:10px;display:flex;gap:8px;">
                    <button onclick="focusNeighbours('${{nodeId}}')" style="
                        border:1px solid #d0d7de;border-radius:8px;padding:5px 12px;
                        cursor:pointer;font-size:12px;background:#f8f9fa;">
                        🔭 Focus neighbours
                    </button>
                    <button onclick="network.unselectAll();hidePanel()" style="
                        border:1px solid #d0d7de;border-radius:8px;padding:5px 12px;
                        cursor:pointer;font-size:12px;background:#f8f9fa;">
                        ✕ Dismiss
                    </button>
                </div>
            `;

            panel.style.display = 'block';
        }}

        function hidePanel() {{
            document.getElementById('node-panel').style.display = 'none';
        }}

        window.focusNode = function(nodeId) {{
            if (!NODE_DATA[nodeId]) return;
            network.focus(nodeId, {{scale:1.6, animation:true}});
            network.selectNodes([nodeId]);
            showPanel(nodeId);
        }};

        window.focusNeighbours = function(nodeId) {{
            const data = NODE_DATA[nodeId];
            if (!data) return;
            const all = [
                ...(data.imports || data.downstream || []),
                ...(data.imported_by || data.upstream || []),
                nodeId
            ];
            network.selectNodes(all);
            network.fit({{nodes: all, animation: true}});
        }};

        window.hidePanel = hidePanel;

        document.getElementById('panel-close').addEventListener('click', hidePanel);
    }})();
    </script>
    """

    # Inject UI and message handler into body
    message_handler = _message_handler_script()
    return base_html.replace("<body>", f"<body>{ui_html}{message_handler}", 1)


# ─────────────────────────────────────────────────────────────────────────────
# Graph pre-processing (adapted from inspiration draft)
# ─────────────────────────────────────────────────────────────────────────────

def _preprocess_module_graph(graph: nx.DiGraph) -> tuple[nx.DiGraph, list[str]]:
    clean = nx.DiGraph()
    warnings: list[str] = []

    for node_id, attrs in graph.nodes(data=True):
        if not node_id:
            continue
        node_type = _infer_node_type(str(node_id), attrs)
        if node_type != "module":
            continue
        merged_attrs = {**attrs, "node_type": "module"}
        clean.add_node(str(node_id), **merged_attrs)

    for source, target, attrs in graph.edges(data=True):
        if not source or not target:
            continue
        if source not in clean or target not in clean:
            continue
        edge_type = str(attrs.get("edge_type", ""))
        if edge_type and edge_type != "IMPORTS":
            continue
        clean.add_edge(str(source), str(target), **attrs)

    if clean.number_of_edges() == 0:
        warnings.append("Module graph has no import edges; visualization may be sparse.")

    return clean, warnings + _suspicious_hub_warnings(clean, "module graph")


def _preprocess_lineage_graph(graph: nx.DiGraph) -> tuple[nx.DiGraph, list[str]]:
    clean = nx.DiGraph()

    for node_id, attrs in graph.nodes(data=True):
        if not node_id:
            continue
        node_type = _infer_node_type(str(node_id), attrs)
        merged_attrs = {**attrs, "node_type": node_type}
        clean.add_node(str(node_id), **merged_attrs)

    for source, target, attrs in graph.edges(data=True):
        if not source or not target:
            continue
        if source not in clean or target not in clean:
            continue
        clean.add_edge(str(source), str(target), **attrs)

    return clean, _suspicious_hub_warnings(clean, "lineage graph")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _infer_node_type(node_id: str, attrs: dict[str, Any]) -> str:
    nt = str(attrs.get("node_type") or attrs.get("type") or "").strip().lower()
    if nt:
        return nt
    if node_id.startswith("dataset::"):
        return "dataset"
    if node_id.startswith("transform::"):
        return "transformation"
    if node_id.startswith("config::"):
        return "config"
    if node_id.startswith("pipeline::"):
        return "pipeline"
    if "::" in node_id:
        return "function"
    return "module"


def _rank_nodes(graph: nx.DiGraph, score_map: dict[str, float]) -> list[str]:
    degrees = dict(graph.degree())
    return [
        node
        for node, _ in sorted(
            graph.nodes(data=True),
            key=lambda item: (
                -(score_map.get(item[0], 0.0)),
                -(degrees.get(item[0], 0)),
                item[0],
            ),
        )
    ]


def _top_nodes_by_degree(graph: nx.DiGraph, limit: int = 10) -> list[dict[str, Any]]:
    top = sorted(graph.degree(), key=lambda item: (-item[1], item[0]))[:limit]
    return [{"id": nid, "degree": deg} for nid, deg in top]


def _suspicious_hub_warnings(graph: nx.DiGraph, name: str) -> list[str]:
    if graph.number_of_nodes() <= 2:
        return []
    top_node, top_deg = max(graph.degree(), key=lambda item: item[1], default=("", 0))
    ratio = top_deg / max(1, graph.number_of_nodes() - 1)
    if top_deg >= 10 and ratio >= 0.6:
        return [f"Suspicious hub in {name}: {top_node!r} → {top_deg} neighbours."]
    return []


def _build_report(graph: nx.DiGraph, warnings: list[str]) -> dict[str, Any]:
    return {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "warnings": warnings,
        "suspicious_hub_detected": any("Suspicious hub" in w for w in warnings),
    }


def _module_label(node_id: str) -> str:
    return Path(node_id).name or node_id


def _lineage_label(node_id: str, attrs: dict[str, Any]) -> str:
    if attrs.get("name"):
        return str(attrs["name"])
    for prefix in ("dataset::", "transform::", "config::", "pipeline::"):
        if node_id.startswith(prefix):
            tail = node_id[len(prefix):]
            return Path(tail).name or tail
    return node_id


def _module_tooltip(node_id: str, attrs: dict[str, Any], degree: int, score: float) -> str:
    return (
        f"<b>{_module_label(node_id)}</b><br>"
        f"path: {node_id}<br>"
        f"language: {attrs.get('language', '?')}<br>"
        f"loc: {attrs.get('loc', 0)}  |  complexity: {attrs.get('complexity_score', 0)}<br>"
        f"degree: {degree}  |  pagerank: {score:.5f}<br>"
        f"velocity_30d: {attrs.get('change_velocity_30d', 0)}<br>"
        f"dead code: {bool(attrs.get('is_dead_code_candidate', False))}"
    )


def _lineage_tooltip(node_id: str, attrs: dict[str, Any], degree: int) -> str:
    nt = _infer_node_type(node_id, attrs)
    return (
        f"<b>{_lineage_label(node_id, attrs)}</b><br>"
        f"type: {nt}<br>"
        f"degree: {degree}<br>"
        f"source_file: {attrs.get('source_file', '')}<br>"
        f"storage_type: {attrs.get('storage_type', '')}"
    )


def _module_color(*, is_dead: bool, is_key: bool) -> str:
    if is_dead:
        return "#b0b7bf"
    if is_key:
        return "#d95f02"
    return "#9ecae1"


def _lineage_color(node_type: str) -> str:
    return {
        "dataset": "#2b8cbe",
        "transformation": "#f28e2b",
        "config": "#8e44ad",
        "pipeline": "#27ae60",
        "function": "#e67e22",
    }.get(node_type, "#9aa5b1")


def _lineage_level(node_type: str) -> int:
    return {"dataset": 1, "transformation": 2, "function": 2}.get(node_type, 3)


def _scale(value: float, *, lower: int, upper: int) -> int:
    bounded = max(0.0, min(float(value), 50.0))
    return int(lower + (upper - lower) * (bounded / 50.0))


def _module_options() -> str:
    return """
    const options = {
      "layout": { "improvedLayout": true },
      "interaction": {
        "hover": true, "navigationButtons": true, "keyboard": true,
        "tooltipDelay": 150, "hideEdgesOnDrag": true,
        "dragNodes": true, "dragView": true, "zoomView": true
      },
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -8000,
          "centralGravity": 0.3,
          "springLength": 95,
          "springConstant": 0.04,
          "damping": 0.09,
          "avoidOverlap": 0.1
        },
        "stabilization": { "enabled": true, "iterations": 250 }
      },
      "edges": { "smooth": { "type": "dynamic" } }
    }
    """


def _lineage_options(node_count: int) -> str:
    physics = "true" if node_count > 80 else "false"
    return f"""
    const options = {{
      "layout": {{
        "hierarchical": {{
          "enabled": true, "direction": "LR", "sortMethod": "directed",
          "nodeSpacing": 180, "levelSeparation": 220, "treeSpacing": 260,
          "blockShifting": true, "edgeMinimization": true, "parentCentralization": true
        }}
      }},
      "interaction": {{
        "hover": true, "navigationButtons": true, "keyboard": true,
        "dragNodes": true, "dragView": true, "zoomView": true, "tooltipDelay": 150
      }},
      "physics": {{
        "enabled": {physics},
        "hierarchicalRepulsion": {{ "nodeDistance": 180, "avoidOverlap": 1 }},
        "stabilization": {{ "enabled": true, "iterations": 150 }}
      }},
      "edges": {{ "smooth": false }}
    }}
    """


def _legend_html(graph_type: str) -> str:
    items = (
        [
            ("#d95f02", "High-centrality module"),
            ("#9ecae1", "Module"),
            ("#b0b7bf", "Dead code candidate"),
        ]
        if graph_type == "module"
        else [
            ("#2b8cbe", "Dataset"),
            ("#f28e2b", "Transformation"),
            ("#27ae60", "Pipeline"),
            ("#8e44ad", "Config"),
            ("#9aa5b1", "Other"),
        ]
    )
    title = "Module Graph" if graph_type == "module" else "Lineage Graph"
    entries = "".join(
        f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0;">'
        f'<span style="width:12px;height:12px;border-radius:50%;background:{c};display:inline-block;"></span>'
        f'<span style="font-size:12px;">{lbl}</span></div>'
        for c, lbl in items
    )
    return (
        '<div style="position:fixed;top:70px;right:16px;z-index:9997;'
        'background:rgba(255,255,255,0.94);border:1px solid #d0d7de;border-radius:12px;'
        'padding:12px 16px;font-family:Georgia,serif;box-shadow:0 4px 16px rgba(0,0,0,0.10);">'
        f'<div style="font-weight:700;font-size:12px;margin-bottom:6px;">{title}</div>{entries}</div>'
    )


def _message_handler_script() -> str:
    """
    JavaScript for iframe-to-parent window communication.
    Enables zoom controls, node selection, and Navigator tool integration.
    """
    return """
    <script>
    (function() {
        // Notify parent window when graph is fully loaded
        window.addEventListener('load', function() {
            window.parent.postMessage({ type: 'graphLoaded' }, '*');
        });
        
        // Wait for network to be ready
        function waitForNetwork(callback) {
            if (typeof network !== 'undefined') {
                callback();
            } else {
                setTimeout(() => waitForNetwork(callback), 100);
            }
        }
        
        waitForNetwork(function() {
            // Send node click events to parent
            network.on('click', function(params) {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    const nodeData = NODE_DATA[nodeId] || {};
                    window.parent.postMessage({
                        type: 'nodeClick',
                        node: {
                            id: nodeId,
                            label: nodeData.label || nodeId,
                            node_type: nodeData.node_type,
                            path: nodeData.id || nodeId,
                            ...nodeData
                        }
                    }, '*');
                }
            });
            
            // Listen for commands from parent window
            window.addEventListener('message', function(event) {
                const action = event.data.action;
                
                if (action === 'zoomIn') {
                    const currentScale = network.getScale();
                    network.moveTo({ scale: currentScale * 1.2 });
                } else if (action === 'zoomOut') {
                    const currentScale = network.getScale();
                    network.moveTo({ scale: currentScale * 0.8 });
                } else if (action === 'fitView') {
                    network.fit({ animation: true });
                } else if (action === 'focusNode') {
                    const nodeId = event.data.nodeId;
                    if (nodeId && network.body.data.nodes.get(nodeId)) {
                        network.focus(nodeId, { scale: 1.5, animation: true });
                        network.selectNodes([nodeId]);
                    }
                } else if (action === 'blastRadius') {
                    highlightBlastRadius(event.data.nodePath);
                } else if (action === 'traceLineage') {
                    highlightLineage(event.data.nodePath);
                }
            });
            
            // Highlight blast radius (downstream dependencies)
            window.highlightBlastRadius = function(nodePath) {
                // Find node by path
                const nodeId = Object.keys(NODE_DATA).find(id => 
                    NODE_DATA[id].id === nodePath || 
                    NODE_DATA[id].path === nodePath ||
                    id === nodePath
                );
                
                if (!nodeId) return;
                
                const data = NODE_DATA[nodeId];
                const downstream = data.imports || data.downstream || [];
                
                // Highlight in orange/red
                const allNodes = network.body.data.nodes.getIds();
                const updates = allNodes.map(id => {
                    if (id === nodeId) {
                        return { id, color: '#e74c3c', borderWidth: 3 };
                    } else if (downstream.includes(id)) {
                        return { id, color: '#e67e22', borderWidth: 2 };
                    } else {
                        return { id, color: { background: '#ecf0f1', border: '#bdc3c7' }, opacity: 0.3 };
                    }
                });
                
                network.body.data.nodes.update(updates);
                network.selectNodes([nodeId, ...downstream]);
                network.fit({ nodes: [nodeId, ...downstream], animation: true });
            };
            
            // Highlight lineage (upstream path)
            window.highlightLineage = function(nodePath) {
                // Find node by path
                const nodeId = Object.keys(NODE_DATA).find(id => 
                    NODE_DATA[id].id === nodePath || 
                    NODE_DATA[id].path === nodePath ||
                    id === nodePath
                );
                
                if (!nodeId) return;
                
                const data = NODE_DATA[nodeId];
                const upstream = data.imported_by || data.upstream || [];
                
                // Highlight in blue/cyan
                const allNodes = network.body.data.nodes.getIds();
                const updates = allNodes.map(id => {
                    if (id === nodeId) {
                        return { id, color: '#3498db', borderWidth: 3 };
                    } else if (upstream.includes(id)) {
                        return { id, color: '#5dade2', borderWidth: 2 };
                    } else {
                        return { id, color: { background: '#ecf0f1', border: '#bdc3c7' }, opacity: 0.3 };
                    }
                });
                
                network.body.data.nodes.update(updates);
                network.selectNodes([nodeId, ...upstream]);
                network.fit({ nodes: [nodeId, ...upstream], animation: true });
            };
        });
    })();
    </script>
    """


def _write_empty_html(output_html: Path, message: str) -> None:
    Path(output_html).write_text(
        "<html><head><meta charset='utf-8'><title>Cartography Graph</title></head>"
        "<body style='font-family:Georgia,serif;background:#fbfbf7;color:#1f2933;"
        "display:flex;align-items:center;justify-content:center;height:100vh;'>"
        f"<div style='padding:24px 32px;border:1px solid #d0d7de;border-radius:12px;"
        f"background:#ffffff;'>{message}</div></body></html>",
        encoding="utf-8",
    )
