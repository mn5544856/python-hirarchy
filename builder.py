"""
builder.py — Class hierarchy tree builder
"""

# ✅ Sirf detector import karein — baaki kuch nahi
from detector import (
    get_type_info, get_module_of_class, get_parent_class
)


def build_class_tree(cls, TYPE_INFO, max_depth=3, depth=0, visited=None):
    if visited is None:
        visited = set()

    cls_id = id(cls)
    info, t = get_type_info(cls, TYPE_INFO)

    node = {
        'name': cls.__name__,
        'module': get_module_of_class(cls),
        'parent': get_parent_class(cls),
        'children': [],
        'type': t,
        'info': info,
        'counts': {},
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
        child = build_class_tree(sub, TYPE_INFO, max_depth, depth + 1, visited)
        node['children'].append(child)
        for k, v in child.get('counts', {}).items():
            node['counts'][k] = node['counts'].get(k, 0) + v
        node['counts'][child['type']] = node['counts'].get(child['type'], 0) + 1
    node['counts'][t] = node['counts'].get(t, 0) + 1

    return node


def tree_stats(node):
    total = 1
    max_width = len(node['children'])
    max_d = 0
    for c in node['children']:
        t, w, d = tree_stats(c)
        total += t
        max_width = max(max_width, w)
        max_d = max(max_d, d)
    return total, max_width, max_d + 1