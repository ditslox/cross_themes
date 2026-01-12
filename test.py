#!/usr/bin/env python3
import sys
import os

# Добавляем путь к проекту
project_root = os.path.dirname(os.path.abspath(/home/ditslox/Downloads/cross_themes/tests/2.jpg))
sys.path.insert(0, project_root)

print("Тестируем импорт...")

# 1. Тест импорта ThemeManager
try:
    from core.theme_manager import ThemeManager
    print("✓ ThemeManager импортирован")
    
    # 2. Тест создания экземпляра
    manager = ThemeManager('gnome')
    print("✓ ThemeManager создан с platform='gnome'")
    
    # 3. Проверка адаптера
    print(f"Адаптер: {type(manager.adapter).name}")
    
    # 4. Тест применения темы
    test_theme = {
        'name': 'Test Theme',
        'mode': 'dark',
        'primary': '#3498db',
        'secondary': '#2ecc71',
        'background': '#121212',
        'surface': '#1e1e1e',
        'on_background': '#ffffff',
        'on_surface': '#e0e0e0'
    }
    
    result = manager.apply_theme(test_theme)
    print(f"Результат применения темы: {result}")
    
except Exception as e:
    print(f"✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()
