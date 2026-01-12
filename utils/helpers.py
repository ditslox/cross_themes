#!/usr/bin/env python3
"""
Вспомогательные функции.
"""
import json
from pathlib import Path


def print_color_block(color_hex, width=8):
    """Печать цветного блока в терминале."""
    hex_value = color_hex.lstrip('#')
    r = int(hex_value[0:2], 16)
    g = int(hex_value[2:4], 16)
    b = int(hex_value[4:6], 16)
    return f"\033[48;2;{r};{g};{b}m{' ' * width}\033[0m"


def display_color_palette(theme_data):
    """Отображение цветовой палитры."""
    print("\n┌────────────────────────────────────────┐")
    print("│         Цветовая палитра темы         │")
    print("├────────────────────────────────────────┤")

    colors_to_display = [
        ("Основной", theme_data['primary']),
        ("Вторичный", theme_data['secondary']),
        ("Фон", theme_data['background']),
        ("Поверхность", theme_data['surface']),
    ]

    # Добавляем акцентные цвета
    for i, accent in enumerate(theme_data.get('accent_colors', [])[:3], 1):
        colors_to_display.append((f"Акцент {i}", accent))

    for name, color in colors_to_display:
        block = print_color_block(color, 6)
        print(f"│ {block} {name:<12} {color:10} │")

    print("└────────────────────────────────────────┘")


def print_results(results):
    """Вывод результатов анализа."""
    print("РЕЗУЛЬТАТЫ АНАЛИЗА ИЗОБРАЖЕНИЯ".center(60))

    print(f"\nИзображение: {results.get('source_image', 'N/A')}")
    print(f"Размер: {results.get('image_size', (0, 0))}")

    print("\nДоминирующие цвета:")
    colors = results.get('dominant_colors', [])
    for i, color in enumerate(colors[:8], 1):
        block = print_color_block(color, 6)
        print(f"  {i:2}. {block} {color}")

    primary, secondary = results.get('primary_pair', ('#000000', '#000000'))
    print(f"\nОсновная пара:")
    print(f"    Основной:   {print_color_block(primary, 4)} {primary}")
    print(f"    Вторичный:  {print_color_block(secondary, 4)} {secondary}")

    print("\nЦветовые схемы:")
    schemes = results.get('color_scheme', {})
    for scheme_name, scheme_colors in schemes.items():
        print(f"  {scheme_name.capitalize():12}: ", end="")
        for color in scheme_colors[:4]:
            print(print_color_block(color, 3), end="")
        print()

    print("\n" + "=" * 60)


def save_palette(palette, filepath):
    """Сохранение палитры в файл."""
    with open(filepath, 'w') as f:
        json.dump(palette, f, indent=2, ensure_ascii=False)
    print(f"✓ Палитра сохранена: {filepath}")


def load_palette(filepath):
    """Загрузка палитры из файла."""
    with open(filepath, 'r') as f:
        return json.load(f)


def check_dependencies():
    """Проверка зависимостей."""
    dependencies = {
        'PIL': 'Pillow',
        'numpy': 'numpy',
    }

    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    return missing


def create_project_structure():
    """Создание структуры проекта."""
    structure = [
        'themes/__init__.py',
        'themes/main.py',
        'core/__init__.py',
        'core/color_analyzer.py',
        'core/theme_manager.py',
        'adapters/__init__.py',
        'adapters/base_adapter.py',
        'adapters/gnome_adapter.py',
        'adapters/kde_adapter.py',
        'adapters/android_adapter.py',
        'adapters/windows_adapter.py',
        'adapters/macos_adapter.py',
        'config/__init__.py',
        'config/settings.py',
        'utils/__init__.py',
        'utils/helpers.py',
        'utils/logger.py',
        'tests/__init__.py',
        'tests/test_color_analyzer.py',
        'wallpapers/',
        'logs/',
        '.gitignore',
        'requirements.txt',
        'README.md',
        'setup.py'
    ]

    for path in structure:
        if path.endswith('/'):
            Path(path).mkdir(parents=True, exist_ok=True)
        else:
            filepath = Path(path)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            if not filepath.exists():
                filepath.touch()

    print("Cтруктура проекта создана")
