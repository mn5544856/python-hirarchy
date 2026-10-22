"""
Python Modules — Loop Chalao, Har Module Ka Alag Chart (PNG + PDF + HTML)
"""

import os
import sys
import importlib

os.environ["PATH"] += os.pathsep + r"C:\Program Files (x86)\Graphviz\bin"

from graphviz import Digraph


# ============================================================
# 1️⃣ SAARE MODULES KI LIST (loop ke liye)
# ============================================================

def get_all_modules():
    """Saare standard library modules ki list"""
    modules = []

    # Python 3.10+ ka built-in method
    if hasattr(sys, "stdlib_module_names"):
        for name in sys.stdlib_module_names:
            if not name.startswith("_") and "." not in name:
                modules.append(name)
    else:
        # Purane Python ke liye fallback
        modules = [
            "abc", "argparse", "ast", "asyncio", "base64", "bisect",
            "calendar", "cmath", "collections", "concurrent", "configparser",
            "contextlib", "copy", "csv", "ctypes", "datetime", "decimal",
            "difflib", "dis", "email", "enum", "fnmatch", "fractions",
            "ftplib", "functools", "gc", "getpass", "glob", "gzip",
            "hashlib", "heapq", "hmac", "html", "http", "imaplib",
            "importlib", "inspect", "io", "ipaddress", "itertools",
            "json", "keyword", "locale", "logging", "lzma", "mailbox",
            "marshal", "math", "mimetypes", "mmap", "multiprocessing",
            "numbers", "operator", "os", "pathlib", "pickle", "pkgutil",
            "platform", "plistlib", "poplib", "pprint", "profile",
            "pty", "pydoc", "queue", "quopri", "random", "re",
            "readline", "reprlib", "runpy", "sched", "secrets",
            "select", "shelve", "shutil", "signal", "smtplib",
            "socket", "sqlite3", "ssl", "stat", "statistics", "string",
            "stringprep", "struct", "subprocess", "sys", "sysconfig",
            "tabnanny", "tarfile", "tempfile", "textwrap", "threading",
            "time", "timeit", "tkinter", "token", "tokenize",
            "trace", "traceback", "tracemalloc", "types", "typing",
            "unicodedata", "unittest", "urllib", "uuid", "venv",
            "warnings", "wave", "weakref", "webbrowser", "wsgiref",
            "xml", "xmlrpc", "zipfile", "zipimport", "zlib",
        ]

    return sorted(set(modules))


# ============================================================
# 2️⃣ MODULE SE CLASSES NIKALO
# ============================================================

def get_classes_from_module(module):
    """Module ke andar saari classes nikalo (built-in + user-defined)"""
    classes = []
    try:
        mod = importlib.import_module(module)
    except Exception:
        return classes

    for name in dir(mod):
        if name.startswith("_"):
            continue
        try:
            obj = getattr(mod, name)
            if isinstance(obj, type):
                classes.append((name, obj))
        except Exception:
            continue

    return classes


# ============================================================
# 3️⃣ TREE BUILDER (classes ke liye)
# ============================================================

def build_class_tree(cls, max_depth=3, depth=0, visited=None):
    """Class hierarchy tree banao — safe (visited set ke saath)"""
    if visited is None:
        visited = set()

    cls_id = id(cls)
    node = {
        'name': cls.__name__,
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
        node['children'].append(
            build_class_tree(sub, max_depth, depth + 1, visited)
        )

    return node


def tree_stats(node):
    """Tree ki stats: total, max_width, depth"""
    total = 1
    max_width = len(node['children'])
    max_d = 0
    for c in node['children']:
        t, w, d = tree_stats(c)
        total += t
        max_width = max(max_width, w)
        max_d = max(max_d, d)
    return total, max_width, max_d + 1


# ============================================================
# 4️⃣ RENDER FUNCTIONS (PNG + PDF + HTML)
# ============================================================

def render_png_and_pdf(root_class, base_filename, title=None, max_depth=3):
    """Ek class ka HIGH-QUALITY PNG aur PDF dono banao"""
    title = title or f"{root_class.__name__} Hierarchy"
    tree = build_class_tree(root_class, max_depth=max_depth)

    total, max_width, depth = tree_stats(tree)

    # 🎯 BADA FONT — sharpness ke liye
    if total <= 15:
        font, margin = 16, '0.3,0.15'
    elif total <= 30:
        font, margin = 14, '0.25,0.12'
    elif total <= 60:
        font, margin = 12, '0.2,0.1'
    else:
        font, margin = 11, '0.15,0.08'

    rankdir = 'LR' if max_width > 6 else 'TB'
    nodesep = '0.5' if total <= 30 else '0.25'
    ranksep = '0.6' if total <= 30 else '0.4'

    colors = ['#1a237e', '#3949ab', '#5c6bc0', '#7986cb', '#9fa8da']

    # --- PNG version (HIGH QUALITY) ---
    dot = Digraph(format='png', name=title)
    dot.attr(
        rankdir=rankdir, bgcolor='white',
        nodesep=nodesep, ranksep=ranksep,
        fontname='Arial', fontsize='20',
        labelloc='t', label=title,
        size='24,36',           # 🎯 Bada size
        ratio='compress',
        dpi='300',              # 🎯 HIGH DPI — sharp!
    )
    dot.attr('node', shape='box', style='rounded,filled',
             color='#3949ab', fontname='Arial',
             fontsize=str(font), penwidth='2.5',   # 🎯 Mota border
             margin=margin)
    dot.attr('edge', color='#7986cb', penwidth='2', arrowsize='0.9')

    counter = {'id': 0}

    def add(node, parent_id=None, level=0):
        node_id = f"n{counter['id']}"
        counter['id'] += 1
        label = node['name']
        if node.get('hidden'):
            label += f"\n(+{node['hidden']})"
        bg = colors[min(level, len(colors) - 1)]
        fg = 'white' if level < 4 else '#1a237e'
        dot.node(node_id, label, fillcolor=bg, fontcolor=fg)
        if parent_id:
            dot.edge(parent_id, node_id)
        for child in node['children']:
            add(child, node_id, level + 1)

    add(tree)
    try:
        dot.render(base_filename, cleanup=True)
        png_ok = True
    except Exception as e:
        print(f"   ⚠️ PNG fail: {e}")
        png_ok = False

    # --- PDF version (vector — always sharp) ---
    dot2 = Digraph(format='pdf', name=title)
    dot2.attr(rankdir=rankdir, bgcolor='white',
              nodesep=nodesep, ranksep=ranksep,
              fontname='Arial', fontsize='20',
              labelloc='t', label=title)
    dot2.attr('node', shape='box', style='rounded,filled',
              color='#3949ab', fontname='Arial',
              fontsize=str(font), penwidth='2.5', margin=margin)
    dot2.attr('edge', color='#7986cb', penwidth='2', arrowsize='0.9')

    counter2 = {'id': 0}

    def add2(node, parent_id=None, level=0):
        node_id = f"n{counter2['id']}"
        counter2['id'] += 1
        label = node['name']
        if node.get('hidden'):
            label += f"\n(+{node['hidden']})"
        bg = colors[min(level, len(colors) - 1)]
        fg = 'white' if level < 4 else '#1a237e'
        dot2.node(node_id, label, fillcolor=bg, fontcolor=fg)
        if parent_id:
            dot2.edge(parent_id, node_id)
        for child in node['children']:
            add2(child, node_id, level + 1)

    add2(tree)
    try:
        dot2.render(base_filename, cleanup=True)
        pdf_ok = True
    except Exception as e:
        print(f"   ⚠️ PDF fail: {e}")
        pdf_ok = False

    return png_ok, pdf_ok, total

def render_html(root_class, filename, title=None, max_depth=3):
    """HTML chart (responsive, click-expand)"""
    title = title or f"{root_class.__name__} Hierarchy"
    tree = build_class_tree(root_class, max_depth=max_depth)

    def walk(node, level=0):
        html = f'<li><span class="node lv{min(level,4)}">{node["name"]}'
        if node.get('hidden'):
            html += f' <small>(+{node["hidden"]})</small>'
        html += '</span>'
        if node['children']:
            html += '<ul>'
            for c in node['children']:
                html += walk(c, level + 1)
            html += '</ul>'
        html += '</li>'
        return html

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif;
         background:#f5f7fa; margin:0; padding:20px; }}
  h1 {{ color:#1a237e; text-align:center; font-size:22px; }}
  .toolbar {{ text-align:center; margin:15px 0; }}
  .toolbar button {{ background:#3949ab; color:white; border:none;
      padding:8px 16px; border-radius:6px; cursor:pointer;
      margin:4px; font-size:13px; }}
  .toolbar button:hover {{ background:#283593; }}
  .tree {{ max-width:100%; overflow-x:auto; padding:20px;
          background:white; border-radius:12px;
          box-shadow:0 2px 10px rgba(0,0,0,0.08); }}
  .tree ul {{ list-style:none; padding-left:28px; margin:0;
             position:relative; }}
  .tree > ul {{ padding-left:0; }}
  .tree li {{ margin:8px 0; position:relative; }}
  .tree li::before {{ content:''; position:absolute; left:-16px;
      top:0; border-left:2px solid #9fa8da; height:100%; }}
  .tree li::after {{ content:''; position:absolute; left:-16px;
      top:16px; border-top:2px solid #9fa8da; width:12px; }}
  .tree li:last-child::before {{ height:16px; }}
  .tree > ul > li::before, .tree > ul > li::after {{ display:none; }}
  .node {{ display:inline-block; padding:8px 16px; border-radius:18px;
      color:white; font-weight:600; font-size:14px; cursor:pointer;
      box-shadow:0 2px 6px rgba(0,0,0,0.15);
      transition:transform 0.15s; white-space:nowrap; }}
  .node:hover {{ transform:scale(1.05); }}
  .node small {{ opacity:0.8; font-size:11px; }}
  .lv0 {{ background:#1a237e; }}
  .lv1 {{ background:#3949ab; }}
  .lv2 {{ background:#5c6bc0; }}
  .lv3 {{ background:#7986cb; }}
  .lv4 {{ background:#9fa8da; color:#1a237e; }}
  @media (max-width:600px) {{
    .node {{ font-size:12px; padding:6px 12px; }}
    .tree ul {{ padding-left:20px; }}
  }}
  @media print {{
    .toolbar {{ display:none; }}
    body {{ background:white; padding:0; }}
    .tree {{ box-shadow:none; }}
  }}
</style></head><body>
<h1>🌳 {title}</h1>
<div class="toolbar">
  <button onclick="expandAll()">➕ Expand</button>
  <button onclick="collapseAll()">➖ Collapse</button>
  <button onclick="window.print()">🖨️ Save PDF</button>
</div>
<div class="tree"><ul>{walk(tree)}</ul></div>
<script>
function expandAll() {{
  document.querySelectorAll('.tree ul').forEach(u => u.style.display='block');
}}
function collapseAll() {{
  document.querySelectorAll('.tree ul').forEach((u,i) => {{
    if (i > 0) u.style.display='none';
  }});
}}
document.querySelectorAll('.node').forEach(n => {{
  n.onclick = () => {{
    const ul = n.parentElement.querySelector('ul');
    if (ul) ul.style.display = ul.style.display === 'none' ? 'block' : 'none';
  }};
}});
</script>
</body></html>"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    return filename


# ============================================================
# 5️⃣ MASTER INDEX HTML
# ============================================================

def render_index(index_data, filename="index.html"):
    """Saare modules ka index page"""
    cards_html = ""
    for item in index_data:
        cards_html += f"""
        <div class="card">
          <h3>{item['module']}</h3>
          <p class="count">{item['classes']} classes</p>
          <div class="links">
            <a href="{item['html']}" target="_blank">🌐 HTML</a>
            {'<a href="' + item['png'] + '" target="_blank">🖼️ PNG</a>' if item['png_ok'] else ''}
            {'<a href="' + item['pdf'] + '" target="_blank">📄 PDF</a>' if item['pdf_ok'] else ''}
          </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Python Modules Index</title>
<style>
  body {{ font-family:'Segoe UI', Arial, sans-serif; background:#f5f7fa;
         margin:0; padding:20px; }}
  h1 {{ color:#1a237e; text-align:center; }}
  .subtitle {{ text-align:center; color:#555; margin-bottom:20px; }}
  .toolbar {{ text-align:center; margin:20px 0; }}
  .toolbar input {{ padding:10px 16px; border:2px solid #c5cae9;
      border-radius:24px; font-size:14px; width:300px; outline:none; }}
  .toolbar input:focus {{ border-color:#3949ab; }}
  .grid {{ display:grid;
      grid-template-columns:repeat(auto-fill, minmax(240px, 1fr));
      gap:16px; max-width:1600px; margin:0 auto; }}
  .card {{ background:white; border-radius:12px; padding:16px;
      box-shadow:0 2px 10px rgba(0,0,0,0.08);
      border-top:4px solid #3949ab; transition:transform 0.15s; }}
  .card:hover {{ transform:translateY(-3px);
      box-shadow:0 6px 20px rgba(0,0,0,0.12); }}
  .card h3 {{ margin:0 0 6px 0; color:#1a237e; font-size:16px; }}
  .count {{ color:#777; font-size:12px; margin:0 0 10px 0; }}
  .links a {{ display:inline-block; padding:5px 10px; margin:2px;
      background:#e8eaf6; color:#1a237e; text-decoration:none;
      border-radius:12px; font-size:11px; font-weight:600;
      transition:all 0.15s; }}
  .links a:hover {{ background:#3949ab; color:white; }}
</style></head><body>
<h1>🐍 Python Modules Index</h1>
<p class="subtitle">{len(index_data)} modules • Har module ka HTML + PNG + PDF chart</p>
<div class="toolbar">
  <input type="text" id="search" placeholder="🔍 Module search karein…"
         oninput="filterCards()">
</div>
<div class="grid" id="grid">{cards_html}</div>
<script>
function filterCards() {{
  const q = document.getElementById('search').value.toLowerCase();
  document.querySelectorAll('.card').forEach(c => {{
    const name = c.querySelector('h3').textContent.toLowerCase();
    c.style.display = name.includes(q) ? '' : 'none';
  }});
}}
</script>
</body></html>"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ Master Index: {filename}")
    return filename


# ============================================================
# 6️⃣ MAIN — LOOP CHALAO, HAR MODULE KA CHART BANAO
# ============================================================

if __name__ == "__main__":
    print("█" * 60)
    print("   PYTHON MODULES — LOOP → HAR MODULE KA CHART")
    print("█" * 60)

    # Output folder
    OUT_DIR = "module_charts"
    os.makedirs(OUT_DIR, exist_ok=True)

    # Saare modules lo
    modules = get_all_modules()
    print(f"\n📦 Total modules: {len(modules)}")

    index_data = []
    success = 0
    skipped = 0

    # 🔁 LOOP — har module ke liye
    for i, module_name in enumerate(modules, 1):
        print(f"\n[{i}/{len(modules)}] 📂 {module_name}")

        # Classes nikalo
        classes = get_classes_from_module(module_name)
        if not classes:
            print(f"   ⏭️  Koi class nahi mili — skip")
            skipped += 1
            continue

        # Sabse bada class tree dhoondo (root = sab se zyada subs)
        best_class = None
        best_count = -1
        for name, cls in classes:
            try:
                count = len(cls.__subclasses__())
            except TypeError:
                count = 0
            if count > best_count:
                best_count = count
                best_class = cls

        if best_class is None:
            skipped += 1
            continue

        base = os.path.join(OUT_DIR, module_name)
        title = f"{module_name} — {best_class.__name__}"

        try:
            # PNG + PDF
            png_ok, pdf_ok, total = render_png_and_pdf(
                best_class, base, title, max_depth=2
            )
            # HTML
            html_file = render_html(
                best_class, f"{base}.html", title, max_depth=3
            )

            index_data.append({
                'module': module_name,
                'classes': total,
                'html': html_file.replace("\\", "/"),
                'png': f"{base}.png" if png_ok else "",
                'pdf': f"{base}.pdf" if pdf_ok else "",
                'png_ok': png_ok,
                'pdf_ok': pdf_ok,
            })

            print(f"   ✅ HTML + PNG + PDF ({total} nodes)")
            success += 1

        except Exception as e:
            print(f"   ⚠️ Skip: {e}")
            skipped += 1

    # Master index
    render_index(index_data, os.path.join(OUT_DIR, "index.html"))

    print("\n" + "█" * 60)
    print(f"   ✅ DONE — {success} modules, {skipped} skipped")
    print("█" * 60)
    print(f"\n📂 Folder: {OUT_DIR}/")
    print(f"   🌐 Master index: {OUT_DIR}/index.html")
    print(f"   🖼️ {success} PNG files")
    print(f"   📄 {success} PDF files")
    print(f"   🌐 {success} HTML files")
    print(f"\n👉 Browser mein kholein: {OUT_DIR}/index.html")