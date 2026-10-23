"""
renderer.py — Professional PNG renderer (CLEAN & FIXED)
"""

import os
from typing import Dict, Optional
from graphviz import Digraph
from types_data import TYPE_INFO, TYPE_ICONS
from builder import build_class_tree, tree_stats


def render_png(root_class, png_base, title=None, max_depth=3):
    """PNG — arrows perfectly managed, boxes cross nahi"""
    title = title or f"{root_class.__name__} Hierarchy"
    tree = build_class_tree(root_class, TYPE_INFO, max_depth=max_depth)
    total, max_width, depth = tree_stats(tree)

    # ── BADA FONT ──
    if total <= 10:
        base_fonts = {'leaf': 18, 'parent': 20, 'cluster': 22, 'doc': 14, 'margin': '0.4,0.2'}
        dpi_val, img_size = '300', '36,54'
    elif total <= 20:
        base_fonts = {'leaf': 17, 'parent': 19, 'cluster': 21, 'doc': 13, 'margin': '0.38,0.19'}
        dpi_val, img_size = '300', '40,60'
    elif total <= 40:
        base_fonts = {'leaf': 16, 'parent': 18, 'cluster': 20, 'doc': 12, 'margin': '0.35,0.18'}
        dpi_val, img_size = '320', '46,70'
    elif total <= 80:
        base_fonts = {'leaf': 15, 'parent': 17, 'cluster': 19, 'doc': 11, 'margin': '0.32,0.16'}
        dpi_val, img_size = '340', '52,80'
    else:
        base_fonts = {'leaf': 14, 'parent': 16, 'cluster': 18, 'doc': 10, 'margin': '0.3,0.15'}
        dpi_val, img_size = '360', '58,90'

    IMPORTANT_TYPES = {'exception', 'decorator', 'abstract', 'protocol'}
    IMPORTANT_EXTRA = 4

    rankdir = 'LR' if max_width > 5 else 'TB'
    nodesep = '0.8' if max_width > 8 else ('0.6' if max_width > 4 else '0.4')
    ranksep = '0.9' if depth > 3 else '0.7'

    counts = tree.get('counts', {})

    dot = Digraph(format='png', name=title)
    dot.attr(
        rankdir=rankdir, bgcolor='#ffffff',
        nodesep=nodesep, ranksep=ranksep,
        fontname='Segoe UI', fontsize='28',
        labelloc='t', label=title,
        size=img_size, ratio='compress', dpi=dpi_val,
        compound='true', newrank='true',
        splines='ortho',
    )
    dot.attr('node', shape='box', style='rounded,filled',
             fontname='Segoe UI', fontsize=str(base_fonts['leaf']),
             penwidth='1.5', margin=base_fonts['margin'],
             width='2.4', fixedsize='false', color='#90a4ae')
    dot.attr('edge', color='#607d8b', penwidth='1.2',
             arrowsize='0.6', style='solid',
             headclip='false', tailclip='false')

    # 🎯 SIRF YAHAN 3 LINES — bas ek hi baar
    node_counter: Dict[str, int] = {'id': 0}
    cluster_counter: Dict[str, int] = {'id': 0}
    root_nid: Dict[str, Optional[str]] = {'id': None}

    def get_font(node, base_key):
        t = node.get('type', 'concrete')
        base = base_fonts[base_key]
        if t in IMPORTANT_TYPES:
            return base + IMPORTANT_EXTRA
        return base

    def make_label(node, compact=False):
        info = node['info']
        t = node.get('type', 'concrete')
        icon = TYPE_ICONS.get(t, '⚙️')
        mod = node.get('module', '')
        mod_short = mod.split('.')[-1] if '.' in mod else mod
        parent = node.get('parent', '')
        name = node['name'].replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')

        main_font = get_font(node, 'leaf' if compact else 'parent')
        doc_f = base_fonts['doc']
        text_color = info['text']

        parts = [
            f"<B><FONT POINT-SIZE='{main_font}' COLOR='{text_color}'>{icon} {name}</FONT></B>",
            f"<FONT POINT-SIZE='{doc_f}' COLOR='#37474f'><B>{info['name']}</B></FONT>",
        ]

        if mod_short and mod_short != 'builtins':
            if t == 'concrete':
                parts.append(f"<FONT POINT-SIZE='{doc_f-1}' COLOR='#455a64'>📦 {mod_short}</FONT>")
            else:
                parts.append(f"<FONT POINT-SIZE='{doc_f-1}' COLOR='#37474f'>📦 {mod_short}</FONT>")

        if not compact and parent and parent != 'object' and len(parent) < 20:
            p_esc = parent.replace('<', '&lt;').replace('>', '&gt;')
            parts.append(f"<FONT POINT-SIZE='{doc_f}' COLOR='#455a64'>⬆ {p_esc}</FONT>")

        if node.get('hidden'):
            parts.append(f"<FONT POINT-SIZE='{doc_f}' COLOR='#455a64'>➕{node['hidden']} more</FONT>")

        child_count = len(node.get('children', []))
        if child_count > 0 and not compact:
            parts.append(f"<FONT POINT-SIZE='{doc_f-1}' COLOR='#455a64'>▼ {child_count} children</FONT>")

        return '<' + '<BR ALIGN="LEFT"/>'.join(parts) + '>'

    def add_node(graph, node, compact=False, level=0):
        nid = f"n{node_counter['id']}"
        node_counter['id'] += 1
        info = node['info']
        t = node.get('type', 'concrete')
        is_imp = t in IMPORTANT_TYPES
        base_font = get_font(node, 'leaf' if compact else 'parent')

        # type: ignore
        graph.node(
            nid, label=make_label(node, compact=compact),
            fillcolor=info['color'], fontcolor=info['text'],
            color=info['border'], fontsize=str(base_font),
            penwidth='2.5' if is_imp else '1.5',
            margin='0.4,0.2' if is_imp else base_fonts['margin'],
            width='2.4', fixedsize='false',
        )
        return nid

    def add_nested(node, parent_graph, level=0):
        info = node['info']
        is_imp = node.get('type') in IMPORTANT_TYPES

        if node['children'] and level < max_depth - 1:
            cluster_counter['id'] += 1
            cname = f"cluster_{cluster_counter['id']}"
            with parent_graph.subgraph(name=cname) as c:
                cluster_font = get_font(node, 'cluster')
                # type: ignore
                c.attr(
                    style='rounded,filled',
                    fillcolor=info['color'] + '15',
                    color=info['border'],
                    penwidth='3' if is_imp else '2',
                    fontname='Segoe UI', fontsize=str(cluster_font),
                    fontcolor=info['text'],
                    label=f"{TYPE_ICONS.get(node['type'], '⚙️')} {node['name']}   ({info['name']})",
                    labeljust='l', margin='12',
                )
                parent_nid = add_node(c, node, compact=False, level=level + 1)

                # 🎯 root_nid — bas assign karo, reset NAHI
                if level == 0 and root_nid['id'] is None:
                    root_nid['id'] = parent_nid

                for child in node['children']:
                    if child['children'] and level + 1 < max_depth - 1:
                        add_nested(child, c, level + 1)
                    else:
                        cid = add_node(c, child, compact=True, level=level + 2)
                        # type: ignore
                        c.edge(parent_nid, cid,
                               color='#607d8b', penwidth='1.2',
                               arrowsize='0.6', style='solid',
                               headport='w', tailport='s',
                               headclip='false', tailclip='false')
        else:
            nid = add_node(parent_graph, node, compact=(level > 0), level=level)
            # 🎯 root_nid — bas assign karo, reset NAHI
            if level == 0 and root_nid['id'] is None:
                root_nid['id'] = nid

    add_nested(tree, dot, level=0)

    # ── LEGEND ──
    legend_rows = []
    total_counted = sum(counts.values()) or 1
    for t, info in TYPE_INFO.items():
        c = counts.get(t, 0)
        if c > 0:
            is_imp = t in IMPORTANT_TYPES
            fsize = 16 if is_imp else 14
            pct = round(c * 100 / total_counted, 1)
            icon = TYPE_ICONS.get(t, '⚙️')
            legend_rows.append(
                f"<TR>"
                f"<TD BGCOLOR='{info['color']}' ALIGN='CENTER' WIDTH='70' "
                f"BORDER='1' COLOR='{info['border']}'>"
                f"<FONT COLOR='{info['text']}' POINT-SIZE='{fsize}'><B>{icon} {info['short']}</B></FONT></TD>"
                f"<TD ALIGN='LEFT'><FONT COLOR='{info['text']}' POINT-SIZE='{fsize}'>"
                f"<B>{info['name']}</B></FONT> "
                f"<FONT COLOR='#37474f' POINT-SIZE='11'>— {info['desc']}</FONT></TD>"
                f"<TD ALIGN='CENTER' WIDTH='70'>"
                f"<FONT COLOR='{info['text']}' POINT-SIZE='{fsize}'><B>{c}</B></FONT>"
                f"<BR/><FONT COLOR='#37474f' POINT-SIZE='10'>({pct}%)</FONT></TD>"
                f"</TR>"
            )

    legend_html = (
        '<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="5" '
        'COLOR="#90a4ae" STYLE="rounded">'
        f'<TR><TD COLSPAN="3" ALIGN="CENTER" BGCOLOR="#eceff1">'
        f'<FONT POINT-SIZE="16" COLOR="#263238"><B>📖 LEGEND</B></FONT>'
        f'<BR/><FONT POINT-SIZE="11" COLOR="#37474f">Total: {total} • Depth: {depth}</FONT>'
        f'</TD></TR>' + "".join(legend_rows) + '</TABLE>>'
    )

    dot.node('legend', label=legend_html, shape='plaintext',
             fontname='Segoe UI', fontcolor='#263238')

    if root_nid['id']:
        dot.edge('legend', root_nid['id'],
                 style='invis', weight='50')

    # ── RENDER ──
    try:
        dot.render(png_base, cleanup=True)
        print(f"   ✅ PNG: {png_base}.png ({total} nodes, {depth} levels)")
        return True, total
    except Exception as e:
        print(f"   ⚠️ PNG fail: {e}")
        return False, total


# ============================================================
# ANALYSIS PNG
# ============================================================

def render_analysis_png(root_class, png_base, title=None, max_depth=3):
    """Analysis Dashboard PNG — bar chart + stats + top classes"""
    title = title or f"{root_class.__name__} — Analysis"
    tree = build_class_tree(root_class, TYPE_INFO, max_depth=max_depth)
    total, max_width, depth = tree_stats(tree)

    type_counts = {}
    top_classes = []

    def walk(node):
        t = node.get('type', 'concrete')
        type_counts[t] = type_counts.get(t, 0) + 1
        child_count = len(node.get('children', []))
        if child_count > 0:
            top_classes.append((node['name'], child_count, t))
        for c in node['children']:
            walk(c)

    walk(tree)
    top_classes.sort(key=lambda x: x[1], reverse=True)
    top_classes = top_classes[:10]

    dot = Digraph(format='png', name=title)
    dot.attr(
        rankdir='TB', bgcolor='#ffffff',
        fontname='Segoe UI', fontsize='24',
        labelloc='t', label=title,
        size='20,30', ratio='compress', dpi='300',
        nodesep='0.5', ranksep='0.6',
    )

    # Header
    dot.node('header', label=(
        f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="10">'
        f'<TR><TD ALIGN="CENTER">'
        f'<FONT POINT-SIZE="32" COLOR="#1a237e"><B>📊 {root_class.__name__} Analysis</B></FONT>'
        f'<BR/><FONT POINT-SIZE="14" COLOR="#546e7a">Total: {total} nodes • Depth: {depth} • Max Width: {max_width}</FONT>'
        f'</TD></TR></TABLE>>'
    ), shape='plaintext')

    # Bar chart
    max_count = max(type_counts.values()) if type_counts else 1
    bar_rows = []
    for t, info in TYPE_INFO.items():
        c = type_counts.get(t, 0)
        if c == 0:
            continue
        bar_width = int((c / max_count) * 200) if max_count > 0 else 0
        icon = TYPE_ICONS.get(t, '⚙️')
        bar_rows.append(
            f'<TR>'
            f'<TD ALIGN="RIGHT" WIDTH="90"><FONT POINT-SIZE="12" COLOR="{info["text"]}"><B>{icon} {info["name"]}</B></FONT></TD>'
            f'<TD ALIGN="LEFT" WIDTH="220">'
            f'<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">'
            f'<TR><TD WIDTH="{bar_width}" HEIGHT="20" BGCOLOR="{info["border"]}"></TD>'
            f'<TD WIDTH="{200 - bar_width}" HEIGHT="20"></TD></TR></TABLE></TD>'
            f'<TD ALIGN="LEFT" WIDTH="60"><FONT POINT-SIZE="14" COLOR="{info["text"]}"><B>{c}</B></FONT></TD>'
            f'<TD ALIGN="LEFT" WIDTH="50"><FONT POINT-SIZE="11" COLOR="#78909c">({round(c * 100 / total, 1)}%)</FONT></TD>'
            f'</TR>'
        )

    bar_chart = (
        '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="4" CELLPADDING="6" '
        'COLOR="#cfd8dc" STYLE="rounded" BGCOLOR="#ffffff">'
        f'<TR><TD COLSPAN="4" ALIGN="CENTER" BGCOLOR="#eceff1">'
        f'<FONT POINT-SIZE="16" COLOR="#263238"><B>📈 Type Distribution</B></FONT>'
        f'</TD></TR>' + "".join(bar_rows) + '</TABLE>>'
    )
    dot.node('bar_chart', label=bar_chart, shape='plaintext')

    # Top 10
    top_rows = []
    for i, (name, count, t) in enumerate(top_classes, 1):
        info = TYPE_INFO.get(t, TYPE_INFO['concrete'])
        icon = TYPE_ICONS.get(t, '⚙️')
        top_rows.append(
            f'<TR>'
            f'<TD ALIGN="CENTER" WIDTH="30"><FONT POINT-SIZE="12" COLOR="#546e7a">{i}</FONT></TD>'
            f'<TD ALIGN="LEFT" WIDTH="200"><FONT POINT-SIZE="12" COLOR="{info["text"]}"><B>{icon} {name}</B></FONT></TD>'
            f'<TD ALIGN="RIGHT" WIDTH="80"><FONT POINT-SIZE="12" COLOR="#455a64"><B>{count} children</B></FONT></TD>'
            f'</TR>'
        )

    top_table = (
        '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="4" CELLPADDING="6" '
        'COLOR="#cfd8dc" STYLE="rounded" BGCOLOR="#ffffff">'
        f'<TR><TD COLSPAN="3" ALIGN="CENTER" BGCOLOR="#eceff1">'
        f'<FONT POINT-SIZE="16" COLOR="#263238"><B>🏆 Top 10 Classes (by children)</B></FONT>'
        f'</TD></TR>' + "".join(top_rows) + '</TABLE>>'
    )
    dot.node('top_table', label=top_table, shape='plaintext')

    # Legend
    legend_rows = []
    for t, info in TYPE_INFO.items():
        c = type_counts.get(t, 0)
        if c == 0:
            continue
        icon = TYPE_ICONS.get(t, '⚙️')
        legend_rows.append(
            f'<TR>'
            f'<TD BGCOLOR="{info["color"]}" ALIGN="CENTER" WIDTH="60" '
            f'BORDER="1" COLOR="{info["border"]}">'
            f'<FONT COLOR="{info["text"]}" POINT-SIZE="14"><B>{icon} {info["short"]}</B></FONT></TD>'
            f'<TD ALIGN="LEFT"><FONT COLOR="{info["text"]}" POINT-SIZE="14">'
            f'<B>{info["name"]}</B></FONT> <FONT COLOR="#546e7a" POINT-SIZE="11">— {info["desc"]}</FONT></TD>'
            f'</TR>'
        )

    legend_table = (
        '<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" '
        'COLOR="#90a4ae" STYLE="rounded">'
        f'<TR><TD COLSPAN="2" ALIGN="CENTER" BGCOLOR="#eceff1">'
        f'<FONT POINT-SIZE="14" COLOR="#263238"><B>📖 LEGEND</B></FONT>'
        f'</TD></TR>' + "".join(legend_rows) + '</TABLE>>'
    )
    dot.node('legend', label=legend_table, shape='plaintext')

    # Layout
    with dot.subgraph() as s:  # type: ignore
        s.attr(rank='same')
        s.node('bar_chart')
        s.node('top_table')

    try:
        dot.render(png_base, cleanup=True)
        print(f"   ✅ Analysis PNG: {png_base}.png")
        return True, total
    except Exception as e:
        print(f"   ⚠️ Analysis PNG fail: {e}")
        return False, total