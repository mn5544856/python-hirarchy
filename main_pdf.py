"""
main_pdf.py — ALL MODULES → PDF (Interactive HTML Jaisa)
"""

import os
import sys
import time
import importlib

os.environ["PATH"] += os.pathsep + r"C:\Program Files (x86)\Graphviz\bin"

from graphviz import Digraph
from detector import get_classes_from_module, classify_class
from types_data import TYPE_INFO, TYPE_ICONS


# ============================================================
# 1️⃣ SAARE MODULES KI LIST
# ============================================================

def get_all_modules():
    modules = []
    if hasattr(sys, "stdlib_module_names"):
        for name in sys.stdlib_module_names:
            if not name.startswith("_") and "." not in name:
                modules.append(name)
    return sorted(set(modules))


# ============================================================
# 2️⃣ SIMPLE TREE BUILDER (PDF ke liye)
# ============================================================

def build_tree(cls, max_depth=3, depth=0, visited=None):
    if visited is None:
        visited = set()

    cls_id = id(cls)
    t = classify_class(cls)
    info = TYPE_INFO.get(t, TYPE_INFO['concrete'])
    
    node = {
        'name': cls.__name__,
        'type': t,
        'info': info,
        'children': [],
    }

    if cls_id in visited or depth >= max_depth:
        try:
            hidden = len(cls.__subclasses__())
        except TypeError:
            hidden = 0
        if hidden:
            node['hidden'] = hidden
        return node

    visited.add(cls_id)
    try:
        subs = cls.__subclasses__()
    except TypeError:
        subs = []

    for sub in subs:
        node['children'].append(build_tree(sub, max_depth, depth + 1, visited))

    return node


# ============================================================
# 3️⃣ MODULE PDF GENERATOR
# ============================================================

def make_module_pdf(tree, title, filename):
    """Ek module ka PDF chart"""
    dot = Digraph(format='pdf', name=title)
    dot.attr(rankdir='TB', bgcolor='#ffffff', fontname='Segoe UI',
             fontsize='24', labelloc='t', label=title,
             size='20,30', ratio='compress')
    
    dot.attr('node', shape='box', style='rounded,filled',
             fontname='Segoe UI', fontsize='14', penwidth='2')
    
    dot.attr('edge', color='#607d8b', penwidth='1.5', arrowsize='0.8')

    node_counter = {'id': 0}
    cluster_counter = {'id': 0}

    def make_label(node):
        info = node['info']
        icon = TYPE_ICONS.get(node['type'], '⚙️')
        name = node['name'].replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
        
        label = f"<B><FONT COLOR='{info['text']}'>{icon} {name}</FONT></B>"
        label += f"<BR/><FONT POINT-SIZE='11' COLOR='#37474f'>{info['name']}</FONT>"
        
        if node.get('hidden'):
            label += f"<BR/><FONT POINT-SIZE='10' COLOR='#455a64'>➕{node['hidden']} more</FONT>"
            
        return '<' + label + '>'

    def add_node(graph, node, parent_id=None):
        nid = f"n{node_counter['id']}"
        node_counter['id'] += 1
        info = node['info']
        
        graph.node(nid, label=make_label(node),
                   fillcolor=info['color'], color=info['border'],
                   fontcolor=info['text'])
                   
        if parent_id:
            graph.edge(parent_id, nid)
            
        for child in node['children']:
            add_node(graph, child, nid)

    add_node(dot, tree)
    
    try:
        dot.render(filename, cleanup=True)
        return True
    except Exception as e:
        print(f"   ⚠️ PDF fail: {e}")
        return False


# ============================================================
# 4️⃣ MASTER INDEX PDF (HTML Dashboard Jaisa)
# ============================================================

def make_index_pdf(modules_data, filename):
    """Saare modules ka Dashboard PDF"""
    dot = Digraph(format='pdf', name="Python Modules Dashboard")
    dot.attr(rankdir='TB', bgcolor='#ffffff', fontname='Segoe UI',
             size='30,40', ratio='compress')
    
    # 1. Header
    dot.node('header', label=(
        f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="15">'
        f'<TR><TD ALIGN="CENTER">'
        f'<FONT POINT-SIZE="40" COLOR="#1a237e"><B>🐍 Python Modules Dashboard</B></FONT>'
        f'<BR/><FONT POINT-SIZE="16" COLOR="#546e7a">'
        f'{len(modules_data)} Modules • PDF Reports'
        f'</FONT>'
        f'</TD></TR></TABLE>>'
    ), shape='plaintext')

    # 2. Grid of Modules
    grid_rows = []
    row = []
    for i, m in enumerate(modules_data):
        icon = m['root_icon']
        color = m['root_type_color']
        name = m['module']
        count = m['classes']
        
        cell = (
            f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="8" '
            f'COLOR="{color}" STYLE="rounded" BGCOLOR="#ffffff" WIDTH="180">'
            f'<TR><TD ALIGN="CENTER" BGCOLOR="{color}">'
            f'<FONT COLOR="white" POINT-SIZE="14"><B>{icon} {name}</B></FONT>'
            f'</TD></TR>'
            f'<TR><TD ALIGN="CENTER">'
            f'<FONT POINT-SIZE="12" COLOR="#37474f">{count} classes</FONT>'
            f'</TD></TR></TABLE>>'
        )
        row.append(f'<TD ALIGN="CENTER" PADDING="10">{cell}</TD>')
        
        if len(row) == 4 or i == len(modules_data) - 1:
            # Fill empty cells if row is incomplete
            while len(row) < 4:
                row.append('<TD></TD>')
            grid_rows.append(f'<TR>{"".join(row)}</TR>')
            row = []

    grid_html = (
        '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="10" CELLPADDING="0">'
        + "".join(grid_rows) + '</TABLE>>'
    )
    
    dot.node('grid', label=grid_html, shape='plaintext')
    
    # Link header to grid
    dot.edge('header', 'grid', style='invis')
    
    try:
        dot.render(filename, cleanup=True)
        print(f"   ✅ Dashboard PDF: {filename}.pdf")
        return True
    except Exception as e:
        print(f"   ⚠️ Dashboard PDF fail: {e}")
        return False


# ============================================================
# 5️⃣ MAIN — RUNTIME
# ============================================================

if __name__ == "__main__":
    print("█" * 60)
    print("   ALL MODULES — PDF GENERATION")
    print("█" * 60)

    OUT_PDF = "module_pdfs"
    os.makedirs(OUT_PDF, exist_ok=True)

    modules = get_all_modules()
    print(f"\n📦 Total modules: {len(modules)}")

    modules_data = []
    success = 0
    skipped = 0
    start_time = time.time()

    for i, module_name in enumerate(modules, 1):
        print(f"[{i}/{len(modules)}] 📂 {module_name}")
        
        classes = get_classes_from_module(module_name)
        if not classes:
            skipped += 1
            continue

        # Best class
        best_class = classes[0][1]
        best_count = -1
        for name, cls in classes:
            try:
                count = len(cls.__subclasses__())
            except TypeError:
                count = 0
            if count > best_count:
                best_count = count
                best_class = cls

        # Build tree
        tree = build_tree(best_class, max_depth=3)
        
        # Count classes
        def count_nodes(n):
            c = 1
            for ch in n['children']: c += count_nodes(ch)
            return c
        total_classes = count_nodes(tree)
        
        # Root info
        root_t = classify_class(best_class)
        root_info = TYPE_INFO.get(root_t, TYPE_INFO['concrete'])

        # Generate PDF
        pdf_base = os.path.join(OUT_PDF, module_name)
        title = f"{module_name} — {best_class.__name__}"
        
        if make_module_pdf(tree, title, pdf_base):
            success += 1
            modules_data.append({
                'module': module_name,
                'classes': total_classes,
                'root_icon': TYPE_ICONS.get(root_t, '⚙️'),
                'root_type_color': root_info['border'],
            })

    # Generate Master Index PDF
    print("\n📊 Building Master Dashboard PDF...")
    make_index_pdf(modules_data, os.path.join(OUT_PDF, "00_Dashboard"))

    elapsed = time.time() - start_time
    print("\n" + "█" * 60)
    print(f"   ✅ DONE — {success} PDFs, {skipped} skipped")
    print(f"   ⏱️  Time: {elapsed:.1f} seconds")
    print("█" * 60)
    print(f"\n📂 Folder: {OUT_PDF}/")
    print(f"   📄 {success} Module PDFs")
    print(f"   📄 00_Dashboard.pdf (Master Index)")