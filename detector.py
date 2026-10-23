"""
detector.py — Class type detection + module/parent info
"""

import inspect
from importlib import import_module


def classify_class(cls):
    try:
        for base in getattr(cls, '__mro__', []):
            if base.__name__ == 'Protocol' and base.__module__ == 'typing':
                return 'protocol'
        if hasattr(cls, '__abstractmethods__') and cls.__abstractmethods__:
            return 'abstract'
        if isinstance(cls, type) and issubclass(cls, type):
            return 'meta'
        if issubclass(cls, BaseException):
            return 'exception'
        if callable(cls) and hasattr(cls, '__call__'):
            try:
                init_sig = inspect.signature(cls.__init__)
                params = list(init_sig.parameters.values())
                for p in params[1:]:
                    if p.name in ('func', 'function', 'f', 'wrapped', 'fn'):
                        return 'decorator'
            except (ValueError, TypeError):
                pass
        return 'concrete'
    except Exception:
        return 'concrete'


def get_type_info(cls, TYPE_INFO):
    t = classify_class(cls)
    return TYPE_INFO.get(t, TYPE_INFO['concrete']), t


def get_module_of_class(cls):
    try:
        return getattr(cls, '__module__', 'builtins') or 'builtins'
    except Exception:
        return '?'


def get_parent_class(cls):
    try:
        bases = cls.__bases__
        if not bases:
            return 'object'
        parents = [b.__name__ for b in bases if b is not object]
        return ', '.join(parents) if parents else 'object'
    except Exception:
        return '?'


def get_classes_from_module(module_name):
    classes = []
    try:
        mod = import_module(module_name)
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
