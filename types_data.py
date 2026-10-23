"""
types_data.py — Type colors, icons, descriptions
"""

TYPE_INFO = {
    'abstract': {
        'symbol': '🔷', 'short': 'A', 'name': 'Abstract',
        'color': '#ffcdd2', 'border': '#e57373', 'text': '#b71c1c',
        'desc': 'Cannot instantiate',
    },
    'concrete': {
        'symbol': '⚙️', 'short': 'C', 'name': 'Concrete',
        'color': '#c8e6c9', 'border': '#81c784', 'text': '#1b5e20',
        'desc': 'Normal class',
    },
    'decorator': {
        'symbol': '🎭', 'short': 'D', 'name': 'Decorator',
        'color': '#e1bee7', 'border': '#ba68c8', 'text': '#4a148c',
        'desc': 'Function wrapper',
    },
    'protocol': {
        'symbol': '🔌', 'short': 'P', 'name': 'Protocol',
        'color': '#b2dfdb', 'border': '#4db6ac', 'text': '#004d40',
        'desc': 'Structural typing',
    },
    'exception': {
        'symbol': '⚠️', 'short': 'E', 'name': 'Exception',
        'color': '#ffccbc', 'border': '#ff8a65', 'text': '#bf360c',
        'desc': 'Error class',
    },
    'meta': {
        'symbol': '🔧', 'short': 'M', 'name': 'Metaclass',
        'color': '#ffe0b2', 'border': '#ffb74d', 'text': '#e65100',
        'desc': 'Class of classes',
    },
}

TYPE_ICONS = {
    'exception': '🚨', 'decorator': '🎭', 'abstract': '📐',
    'protocol': '🔗', 'concrete': '⚙️⚙️', 'meta': '🔧',
}
