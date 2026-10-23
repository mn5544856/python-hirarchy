"""
main_html.py — ALL MODULES → HTML Dashboard
Ek run mein saare modules ka interactive HTML index banayega
"""

import os
import sys
import time
import json
import html as html_lib

os.environ["PATH"] += os.pathsep + r"C:\Program Files (x86)\Graphviz\bin"

from detector import get_classes_from_module
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
# 2️⃣ TREE BUILDER (HTML ke liye — chhota)
# ============================================================

def build_simple_tree(cls, max_depth=2, depth=0, visited=None):
    """Chhota tree — sirf HTML ke liye"""
    if visited is None:
        visited = set()

    cls_id = id(cls)
    from detector import classify_class, get_module_of_class, get_parent_class
    
    t = classify_class(cls)
    info = TYPE_INFO.get(t, TYPE_INFO['concrete'])

    node = {
        'name': cls.__name__,
        'module': get_module_of_class(cls),
        'parent': get_parent_class(cls),
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
        node['children'].append(build_simple_tree(sub, max_depth, depth + 1, visited))

    return node


# ============================================================
# 3️⃣ HTML CHART (Per Module)
# ============================================================

def make_module_html(tree, title, filename):
    """Ek module ka HTML chart"""
    uid = {'n': 0}

    def walk(node, level=0):
        uid['n'] += 1
        node_id = f"node_{uid['n']}"
        info = node['info']
        t = node.get('type', 'concrete')
        icon = TYPE_ICONS.get(t, '⚙️')
        mod = node.get('module', '')
        mod_short = mod.split('.')[-1] if '.' in mod else mod
        parent = node.get('parent', '')
        has_children = bool(node['children'])
        hidden = node.get('hidden', 0)

        h = f'<li class="tree-node">'
        h += '<div class="node-row">'

        # Toggle
        if has_children:
            h += f'<button class="toggle" onclick="toggleNode(\'{node_id}\', this)">▶</button>'
        else:
            h += '<span class="toggle-placeholder"></span>'

        # Node box
        h += (
            f'<span class="node" '
            f'style="background:{info["color"]}; border-color:{info["border"]};">'
            f'<span class="sym">{icon}</span> '
            f'<b style="color:{info["text"]}">{html_lib.escape(node["name"])}</b>'
        )
        h += (
            f'<span class="type-tag" style="background:{info["border"]};">'
            f'{info["name"]}</span>'
        )
        if mod_short and mod_short != 'builtins':
            h += f'<span class="mod-tag">📦 {html_lib.escape(mod_short)}</span>'
        if parent and parent != 'object' and len(parent) < 22:
            h += f'<span class="parent-tag">⬆ {html_lib.escape(parent)}</span>'
        if hidden:
            h += f'<span class="hidden-tag">➕{hidden}</span>'
        h += '</span></div>'

        # Children
        if has_children:
            h += f'<ul id="{node_id}" class="children collapsed">'
            for c in node['children']:
                h += walk(c, level + 1)
            h += '</ul>'

        h += '</li>'
        return h

    # Legend
    legend = '<div class="legend">'
    for t, info in TYPE_INFO.items():
        legend += (
            f'<span style="color:{info["text"]}">'
            f'<b>{info["symbol"]} {info["name"]}</b> — {info["desc"]}'
            f'</span>'
        )
    legend += '</div>'

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html_lib.escape(title)}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif;
         background:#f5f7fa; margin:0; padding:20px; }}
  h1 {{ color:#1a237e; text-align:center; font-size:26px; margin:10px 0; }}
  .back {{ text-align:center; margin:10px 0 20px; }}
  .back a {{ display:inline-block; background:#3949ab; color:white;
            padding:8px 18px; border-radius:20px; text-decoration:none;
            font-size:14px; font-weight:600; }}
  .back a:hover {{ background:#283593; }}
  .legend {{ display:flex; flex-wrap:wrap; gap:12px; justify-content:center;
            background:white; padding:14px 20px; border-radius:12px;
            margin:0 auto 20px; max-width:1100px;
            box-shadow:0 2px 10px rgba(0,0,0,0.08); font-size:13px; }}
  .toolbar {{ text-align:center; margin:15px 0; position:sticky;
             top:0; background:rgba(245,247,250,0.95);
             padding:12px; border-radius:10px; z-index:100;
             backdrop-filter:blur(6px); }}
  .toolbar button {{ background:#3949ab; color:white; border:none;
      padding:9px 18px; border-radius:20px; cursor:pointer;
      margin:4px; font-size:14px; font-weight:600; }}
  .toolbar button:hover {{ background:#283593; }}
  .toolbar input {{ padding:9px 16px; border:2px solid #c5cae9;
      border-radius:20px; font-size:14px; width:260px; outline:none; }}
  .toolbar input:focus {{ border-color:#3949ab; }}
  .tree {{ max-width:1400px; margin:0 auto; padding:25px;
          background:white; border-radius:12px;
          box-shadow:0 2px 10px rgba(0,0,0,0.08);
          overflow-x:auto; }}
  .tree ul {{ list-style:none; padding-left:28px; margin:0; }}
  .tree > ul {{ padding-left:0; }}
  .tree li {{ margin:5px 0; }}
  .node-row {{ display:flex; align-items:center; gap:6px; padding:3px 0; }}
  .toggle {{ width:24px; height:24px; border:none; background:#e8eaf6;
            color:#3949ab; border-radius:50%; cursor:pointer;
            font-size:12px; font-weight:bold; display:flex;
            align-items:center; justify-content:center;
            transition:all 0.15s; flex-shrink:0; }}
  .toggle:hover {{ background:#3949ab; color:white; }}
  .toggle.open {{ background:#3949ab; color:white; }}
  .toggle-placeholder {{ width:24px; height:24px; flex-shrink:0; }}
  .node {{ display:inline-flex; align-items:center; gap:8px;
          padding:8px 16px; border-radius:18px; color:white;
          font-size:14px; font-weight:600; flex-wrap:wrap;
          border:2px solid; box-shadow:0 2px 5px rgba(0,0,0,0.15); }}
  .node .sym {{ font-size:16px; }}
  .type-tag {{ display:inline-block; padding:1px 8px; border-radius:8px;
              font-size:11px; font-weight:700; color:white;
              text-transform:uppercase; letter-spacing:0.3px; }}
  .mod-tag {{ display:inline-block; padding:1px 7px; border-radius:8px;
             font-size:11px; font-weight:600;
             background:rgba(255,255,255,0.4); color:#263238; }}
  .parent-tag {{ display:inline-block; padding:1px 7px; border-radius:8px;
                font-size:11px; font-weight:600;
                background:rgba(0,0,0,0.15); color:#263238; }}
  .hidden-tag {{ display:inline-block; padding:1px 7px; border-radius:8px;
                font-size:11px; font-weight:700;
                background:rgba(0,0,0,0.2); color:#263238; }}
  .children.collapsed {{ display:none; }}
  .node.highlight {{ outline:3px solid #ffd54f; outline-offset:2px; }}
  @media (max-width:600px) {{
    .node {{ font-size:12px; padding:6px 10px; }}
    .tree ul {{ padding-left:16px; }}
  }}
  @media print {{
    .toolbar {{ display:none; }}
    body {{ background:white; padding:0; }}
    .tree {{ box-shadow:none; }}
    .children.collapsed {{ display:block !important; }}
  }}
</style></head><body>
<h1>🌳 {html_lib.escape(title)}</h1>
<div class="back"><a href="index.html">← Back to All Modules</a></div>
{legend}
<div class="toolbar">
  <input type="text" id="search" placeholder="🔍 Search…" oninput="searchTree()">
  <button onclick="expandAll()">➕ Expand All</button>
  <button onclick="collapseAll()">➖ Collapse All</button>
  <button onclick="window.print()">🖨️ Save PDF</button>
</div>
<div class="tree"><ul>{walk(tree)}</ul></div>
<script>
function toggleNode(id, btn) {{
  const ul = document.getElementById(id);
  if (!ul) return;
  ul.classList.toggle('collapsed');
  const isOpen = !ul.classList.contains('collapsed');
  btn.textContent = isOpen ? '▼' : '▶';
  btn.classList.toggle('open', isOpen);
}}
function expandAll() {{
  document.querySelectorAll('.children').forEach(u => {{
    u.classList.remove('collapsed');
    const btn = u.parentElement.querySelector('.toggle');
    if (btn) {{ btn.textContent = '▼'; btn.classList.add('open'); }}
  }});
}}
function collapseAll() {{
  document.querySelectorAll('.children').forEach(u => {{
    u.classList.add('collapsed');
    const btn = u.parentElement.querySelector('.toggle');
    if (btn) {{ btn.textContent = '▶'; btn.classList.remove('open'); }}
  }});
}}
function searchTree() {{
  const q = document.getElementById('search').value.toLowerCase().trim();
  document.querySelectorAll('.node').forEach(n => n.classList.remove('highlight'));
  if (!q) return;
  let firstMatch = null;
  document.querySelectorAll('.node').forEach(n => {{
    if (n.textContent.toLowerCase().includes(q)) {{
      n.classList.add('highlight');
      if (!firstMatch) firstMatch = n;
      let parent = n.closest('.children');
      while (parent) {{
        parent.classList.remove('collapsed');
        const btn = parent.parentElement.querySelector('.toggle');
        if (btn) {{ btn.textContent = '▼'; btn.classList.add('open'); }}
        parent = parent.parentElement.closest('.children');
      }}
    }}
  }});
  if (firstMatch) firstMatch.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
}}
document.addEventListener('DOMContentLoaded', () => {{
  const rootUl = document.querySelector('.tree > ul');
  if (rootUl) {{
    rootUl.querySelectorAll(':scope > li > .children').forEach(u => {{
      u.classList.remove('collapsed');
      const btn = u.parentElement.querySelector('.toggle');
      if (btn) {{ btn.textContent = '▼'; btn.classList.add('open'); }}
    }});
  }}
}});
</script>
</body></html>"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)


# ============================================================
# 4️⃣ MASTER INDEX (Saare modules ka dashboard)
# ============================================================

def make_index_html(modules_data, filename):
    """Saare modules ka index page"""
    total_modules = len(modules_data)
    total_classes = sum(m['classes'] for m in modules_data)

    # Type counts
    type_counts = {}
    for m in modules_data:
        for t, c in m['type_counts'].items():
            type_counts[t] = type_counts.get(t, 0) + c

    # Cards
    cards = ""
    for m in modules_data:
        types_html = ""
        for t, c in m['type_counts'].items():
            if c > 0:
                info = TYPE_INFO.get(t, TYPE_INFO['concrete'])
                types_html += (
                    f'<span class="type-chip" '
                    f'style="background:{info["border"]};">{info["name"][:3]}:{c}</span>'
                )
        cards += f"""
        <a href="{m['html']}" class="card">
          <div class="card-header" style="background:{m['root_type_color']};">
            <span class="card-icon">{m['root_icon']}</span>
            <span class="card-name">{m['module']}</span>
          </div>
          <div class="card-body">
            <div class="card-root">{m['root_class']}</div>
            <div class="card-count">{m['classes']} classes</div>
            <div class="card-types">{types_html}</div>
          </div>
        </a>
        """

    # Type stats
    type_stats_html = ""
    for t, info in TYPE_INFO.items():
        c = type_counts.get(t, 0)
        if c > 0:
            pct = round(c * 100 / total_classes, 1) if total_classes else 0
            type_stats_html += f"""
            <div class="stat-card" style="border-left-color:{info['border']};">
              <div class="stat-icon">{TYPE_ICONS.get(t, '⚙️')}</div>
              <div class="stat-num" style="color:{info['text']}">{c}</div>
              <div class="stat-label">{info['name']}</div>
              <div class="stat-pct">({pct}%)</div>
            </div>
            """

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Python Modules — Dashboard</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif;
         background: linear-gradient(135deg, #f5f7fa 0%, #e8eaf6 100%);
         margin:0; padding:20px; min-height:100vh; }}
  h1 {{ color:#1a237e; text-align:center; font-size:30px; margin:10px 0; }}
  .subtitle {{ text-align:center; color:#666; margin-bottom:30px; font-size:15px; }}
  
  .big-stats {{ display:flex; justify-content:center; gap:20px;
               flex-wrap:wrap; margin-bottom:30px; }}
  .big-card {{ background:white; padding:24px 36px; border-radius:16px;
              box-shadow:0 4px 15px rgba(0,0,0,0.1); text-align:center;
              min-width:180px; }}
  .big-num {{ font-size:42px; font-weight:bold; color:#3949ab; }}
  .big-label {{ color:#666; font-size:14px; margin-top:5px; }}
  
  .type-grid {{ display:grid;
                grid-template-columns:repeat(auto-fill, minmax(160px, 1fr));
                gap:14px; max-width:1200px; margin:0 auto 30px; }}
  .stat-card {{ background:white; padding:16px; border-radius:12px;
               box-shadow:0 2px 10px rgba(0,0,0,0.08);
               border-left:5px solid; text-align:center; }}
  .stat-icon {{ font-size:28px; margin-bottom:5px; }}
  .stat-num {{ font-size:24px; font-weight:bold; }}
  .stat-label {{ color:#555; font-size:13px; margin-top:3px; }}
  .stat-pct {{ color:#999; font-size:11px; }}
  
  .toolbar {{ text-align:center; margin:20px 0 30px;
             position:sticky; top:0; z-index:100;
             background:rgba(245,247,250,0.95);
             padding:12px; border-radius:10px;
             backdrop-filter:blur(8px); }}
  .toolbar input {{ padding:11px 20px; border:2px solid #c5cae9;
      border-radius:26px; font-size:15px; width:340px; outline:none;
      transition:all 0.2s; }}
  .toolbar input:focus {{ border-color:#3949ab;
      box-shadow:0 0 0 4px rgba(57,73,171,0.1); }}
  .toolbar .filter-btn {{ padding:8px 16px; margin:4px; border:none;
      border-radius:20px; cursor:pointer; background:#e8eaf6;
      color:#1a237e; font-weight:600; font-size:12px; }}
  .toolbar .filter-btn.active {{ background:#3949ab; color:white; }}
  
  .grid {{ display:grid;
           grid-template-columns:repeat(auto-fill, minmax(280px, 1fr));
           gap:18px; max-width:1600px; margin:0 auto; }}
  
  .card {{ background:white; border-radius:14px; overflow:hidden;
          box-shadow:0 3px 12px rgba(0,0,0,0.08);
          text-decoration:none; color:inherit;
          transition:transform 0.15s, box-shadow 0.15s; display:block; }}
  .card:hover {{ transform:translateY(-4px);
                box-shadow:0 8px 25px rgba(0,0,0,0.15); }}
  .card-header {{ padding:14px 18px; display:flex; align-items:center; gap:10px;
                 color:white; }}
  .card-icon {{ font-size:20px; }}
  .card-name {{ font-size:16px; font-weight:bold; }}
  .card-body {{ padding:14px 18px; }}
  .card-root {{ color:#1a237e; font-weight:600; font-size:14px;
               margin-bottom:5px; }}
  .card-count {{ color:#777; font-size:12px; margin-bottom:10px; }}
  .card-types {{ display:flex; flex-wrap:wrap; gap:4px; }}
  .type-chip {{ display:inline-block; padding:2px 8px; border-radius:8px;
               color:white; font-size:10px; font-weight:700; }}
  
  .footer {{ text-align:center; color:#999; margin-top:40px;
            font-size:13px; }}
</style></head><body>
<h1>🐍 Python Modules Dashboard</h1>
<p class="subtitle">{total_modules} modules • {total_classes} classes • Interactive HTML Charts</p>

<div class="big-stats">
  <div class="big-card">
    <div class="big-num">{total_modules}</div>
    <div class="big-label">Total Modules</div>
  </div>
  <div class="big-card">
    <div class="big-num">{total_classes}</div>
    <div class="big-label">Total Classes</div>
  </div>
  <div class="big-card">
    <div class="big-num">{len(type_counts)}</div>
    <div class="big-label">Class Types</div>
  </div>
</div>

<div class="type-grid">
{type_stats_html}
</div>

<div class="toolbar">
  <input type="text" id="search" placeholder="🔍 Module ya class search karein…"
         oninput="filterCards()">
  <br>
  <button class="filter-btn active" data-filter="all" onclick="setFilter('all',this)">All</button>
  <button class="filter-btn" data-filter="abstract" onclick="setFilter('abstract',this)">🔷 Abstract</button>
  <button class="filter-btn" data-filter="protocol" onclick="setFilter('protocol',this)">🔌 Protocol</button>
  <button class="filter-btn" data-filter="decorator" onclick="setFilter('decorator',this)">🎭 Decorator</button>
  <button class="filter-btn" data-filter="concrete" onclick="setFilter('concrete',this)">🟢 Concrete</button>
</div>

<div class="grid" id="grid">
{cards}
</div>

<div class="footer">
  Generated by Python Hierarchy Generator
</div>

<script>
let currentFilter = 'all';
function setFilter(f, btn) {{
  currentFilter = f;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  filterCards();
}}
function filterCards() {{
  const q = document.getElementById('search').value.toLowerCase().trim();
  document.querySelectorAll('.card').forEach(c => {{
    const text = c.textContent.toLowerCase();
    const matchSearch = text.includes(q);
    const matchFilter = currentFilter === 'all' ||
                        c.dataset.types?.includes(currentFilter);
    c.style.display = (matchSearch && matchFilter) ? '' : 'none';
  }});
}}
</script>
</body></html>"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)


# ============================================================
# 5️⃣ MAIN — SAARE MODULES
# ============================================================

if __name__ == "__main__":
    print("█" * 60)
    print("   ALL MODULES — HTML DASHBOARD")
    print("█" * 60)

    OUT_HTML = "module_htmls"
    os.makedirs(OUT_HTML, exist_ok=True)

    modules = get_all_modules()
    print(f"\n📦 Total modules: {len(modules)}")

    modules_data = []
    success = 0
    skipped = 0
    start_time = time.time()

    for i, module_name in enumerate(modules, 1):
        print(f"\n[{i}/{len(modules)}] 📂 {module_name}")

        classes = get_classes_from_module(module_name)
        if not classes:
            print(f"   ⏭️  Skip (no classes)")
            skipped += 1
            continue

        # Sabse bada class
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

        # Type counts
        from detector import classify_class
        tree = build_simple_tree(best_class, max_depth=3)

        type_counts = {}
        def walk_count(node):
            t = node.get('type', 'concrete')
            type_counts[t] = type_counts.get(t, 0) + 1
            for c in node['children']:
                walk_count(c)
        walk_count(tree)

        # Root type info
        root_t = classify_class(best_class)
        root_info = TYPE_INFO.get(root_t, TYPE_INFO['concrete'])

        # HTML filename
        html_file = f"{module_name}.html"
        title = f"{module_name} — {best_class.__name__}"

        try:
            # Module HTML banao
            make_module_html(tree, title, os.path.join(OUT_HTML, html_file))

            modules_data.append({
                'module': module_name,
                'root_class': best_class.__name__,
                'classes': sum(type_counts.values()),
                'type_counts': type_counts,
                'root_type_color': root_info['border'],
                'root_icon': TYPE_ICONS.get(root_t, '⚙️'),
                'html': html_file,
            })

            print(f"   ✅ HTML: {html_file}")
            success += 1

        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            skipped += 1

    # Master index banao
    print("\n📊 Building master index...")
    make_index_html(modules_data, os.path.join(OUT_HTML, "index.html"))

    elapsed = time.time() - start_time
    print("\n" + "█" * 60)
    print(f"   ✅ DONE — {success} modules, {skipped} skipped")
    print(f"   ⏱️  Time: {elapsed:.1f} seconds")
    print("█" * 60)
    print(f"\n📂 Folder: {OUT_HTML}/")
    print(f"   🌐 {success} module charts + index.html")
    print(f"\n👉 Browser mein kholein:")
    print(f"   {OUT_HTML}/index.html")