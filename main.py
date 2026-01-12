#!/usr/bin/env python3
"""
Основной модуль установщика тем.
"""
import argparse
import sys
import os
import platform

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.color_analyzer import ColorAnalyzer
    from core.theme_manager import ThemeManager
    from utils.helpers import print_results, display_color_palette
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что все файлы в правильных директориях:")
    print("  core/color_analyzer.py")
    print("  core/theme_manager.py")
    print("  utils/helpers.py")
    sys.exit(1)


def detect_platform():
    """Автоматическое определение платформы."""
    system = platform.system().lower()

    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        # Проверяем DE для Linux
        de = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        if "gnome" in de:
            return "gnome"
        elif "kde" in de:
            return "kde"
        elif "xfce" in de:
            return "xfce"
        elif "mate" in de:
            return "mate"
        elif "cinnamon" in de:
            return "cinnamon"
        return "linux"
    elif "android" in platform.platform().lower():
        return "android"

    return "unknown"


def main():
    parser = argparse.ArgumentParser(
        description='Установщик тем - кроссплатформенная система применения цветовых схем'
    )

    parser.add_argument(
        'image',
        nargs='?',
        help='Путь к изображению для анализа'
    )

    parser.add_argument(
        '--platform',
        choices=['auto', 'gnome', 'kde', 'android', 'windows', 'macos', 'xfce', 'mate', 'cinnamon'],
        default='auto',
        help='Целевая платформа'
    )

    parser.add_argument(
        '--mode',
        choices=['auto', 'light', 'dark', 'mixed'],
        default='auto',
        help='Режим темы'
    )

    parser.add_argument(
        '--apply',
        action='store_true',
        help='Применить тему после анализа'
    )

    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Только анализ без применения'
    )

    parser.add_argument(
        '--output',
        help='Сохранить палитру в файл (JSON)'
    )

    parser.add_argument(
        '--list-platforms',
        action='store_true',
        help='Показать доступные платформы'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Подробный вывод'
    )

    args = parser.parse_args()

    if args.list_platforms:
        print("Доступные платформы:")
        platforms = ['gnome', 'kde', 'windows', 'android', 'macos', 'xfce', 'mate', 'cinnamon']
        for p in platforms:
            print(f"  • {p}")
        return

    # Определение платформы
    if args.platform == 'auto':
        detected = detect_platform()
        if detected == 'unknown':
            print("Не удалось определить платформу. Укажите явно через --platform")
            return
        print(f"Определена платформа: {detected}")
        platform_name = detected
    else:
        platform_name = args.platform

    if not args.image:
        print("Укажите путь к изображению")
        parser.print_help()
        return

    # Проверка существования файла
    if not os.path.exists(args.image):
        print(f"Файл не найден: {args.image}")
        return

    try:
        # Анализ изображения
        print(f"Анализ изображения: {args.image}")
        analyzer = ColorAnalyzer(args.image)
        results = analyzer.analyze()

        # Вывод результатов
        print_results(results)

        # Сохранение в файл
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nПалитра сохранена в: {args.output}")

        if args.analyze_only:
            return
            # Применение темы
        if args.apply:
            print(f"\nПрименение темы для {platform_name}...")
            # Создаем менеджер тем с платформой
            manager = ThemeManager(platform_name)

            # Определение режима темы
            # В функции main(), после анализа изображения:
            if args.mode == 'auto':
                # Автоопределение на основе яркости основного цвета
                import colorsys
                primary_rgb = analyzer.hex_to_rgb(results['themes']['light']['primary'])
                r, g, b = [x/255 for x in primary_rgb]
                h, l, s = colorsys.rgb_to_hls(r, g, b)
                # Если яркость меньше 50% - выбираем тёмную тему
                theme_mode = 'dark' if l < 0.5 else 'light'
            else:
                theme_mode = args.mode

            print(f"Режим темы: {theme_mode}")
            theme_data = results['themes'][theme_mode]

            # Применение
            success = manager.apply_theme(theme_data, args.image)

            if success:
                print(f"Тема успешно применена!")

                # Показ превью
                print("\nЦветовая палитра примененной темы:")
                display_color_palette(theme_data)
            else:
                print("Не удалось применить тему")

    except Exception as e:
        print(f"Ошибка: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
