#!/usr/bin/env python3
"""
Инициализация модуля адаптеров.
"""
import os
import importlib
from pathlib import Path


def get_available_adapters():
    """Получение списка доступных адаптеров."""
    adapters_dir = Path(file).parent
    adapters = []
    
    for file in adapters_dir.glob("*_adapter.py"):
        if file.name != "base_adapter.py":
            platform = file.name.replace("_adapter.py", "")
            adapters.append(platform)
    
    return sorted(adapters)


def load_adapter(platform):
    """Загрузка адаптера по имени платформы."""
    try:
        module_name = f"adapters.{platform}_adapter"
        module = importlib.import_module(module_name)
        adapter_class = getattr(module, f"{platform.capitalize()}Adapter")
        return adapter_class()
    except ImportError:
        raise ImportError(f"Адаптер для платформы '{platform}' не найден")
