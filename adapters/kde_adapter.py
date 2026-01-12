#!/usr/bin/env python3
"""
Адаптер для KDE Plasma.
"""
import os
import configparser
from pathlib import Path
from base_adapter import BaseAdapter
from cross_themes.utils.logger import setup_logger

logger = setup_logger()


class KdeAdapter(BaseAdapter):
    def __init__(self):
        super().__init__()
        self.plasma_config = Path.home() / '.config' / 'plasmarc'
        self.kde_globals = Path.home() / '.config' / 'kdeglobals'

    def apply_colors(self, theme_data):
        """Применение цветов в KDE."""
        try:
            self.create_backup()

            # 1. Обновление kdeglobals
            self._update_kdeglobals(theme_data)

            # 2. Обновление plasmarc
            self._update_plasmarc(theme_data)

            # 3. Обновление цветовой схемы
            self._update_color_scheme(theme_data)

            logger.info("Тема успешно применена для KDE Plasma")
            return True

        except Exception as e:
            logger.error(f"Ошибка применения темы KDE: {e}")
            return False

    def _update_kdeglobals(self, theme_data):
        """Обновление файла kdeglobals."""
        config = configparser.ConfigParser()

        if self.kde_globals.exists():
            config.read(self.kde_globals)

        # Секция Colors
        if 'Colors:Window' not in config.sections():
            config.add_section('Colors:Window')

        config.set('Colors:Window', 'BackgroundNormal', theme_data['background'])
        config.set('Colors:Window', 'ForegroundNormal', theme_data['on_background'])

        # Секция General
        if 'General' not in config.sections():
            config.add_section('General')

        config.set('General', 'ColorScheme', f"Custom_{theme_data['name']}")
        config.set('General', 'Name', theme_data['name'])

        with open(self.kde_globals, 'w') as f:
            config.write(f)

    def _update_plasmarc(self, theme_data):
        """Обновление файла plasmarc."""
        config = configparser.ConfigParser()

        if self.plasma_config.exists():
            config.read(self.plasma_config)

        # Секция Theme
        if 'Theme' not in config.sections():
            config.add_section('Theme')

        config.set('Theme', 'name', f"custom-{theme_data['name'].lower()}")

        with open(self.plasma_config, 'w') as f:
            config.write(f)

    def _update_color_scheme(self, theme_data):
        """Создание цветовой схемы KDE."""
        scheme_dir = Path.home() / '.local' / 'share' / 'color-schemes'
        scheme_dir.mkdir(parents=True, exist_ok=True)

        scheme_file = scheme_dir / f"Custom_{theme_data['name']}.colors"

        scheme_content = f"""[ColorScheme]
Name=Custom_{theme_data['name']}
ColorPalette={theme_data['primary']},{theme_data['secondary']},{theme_data['accent_colors'][0] if theme_data['accent_colors'] else '#000000'}

[Colors:View]
BackgroundNormal={theme_data['background']}
ForegroundNormal={theme_data['on_background']}

[Colors:Window]
BackgroundNormal={theme_data['surface']}
ForegroundNormal={theme_data['on_surface']}
"""

        with open(scheme_file, 'w') as f:
            f.write(scheme_content)

    def set_wallpaper(self, wallpaper_path):
        """Установка обоев в KDE."""
        if not os.path.exists(wallpaper_path):
            logger.error(f"Файл обоев не найден: {wallpaper_path}")
            return False

        try:
            # Используем Plasma desktop scripting
            script = f"""
            var allDesktops = desktops();
            for (var i=0; i<allDesktops.length; i++) {{
                var desktop = allDesktops[i];
                desktop.wallpaperPlugin = "org.kde.image";
                desktop.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
                desktop.writeConfig("Image", "file://{wallpaper_path}");
            }}
            """

            # Сохраняем скрипт во временный файл
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(script)
                script_path = f.name

            # Выполняем скрипт
            cmd = f"qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '{script}'"
            self._execute_command(cmd)

            # Альтернативный метод через dbus-send
            cmd = f"dbus-send --session --dest=org.kde.plasmashell --type=method_call /PlasmaShell org.kde.PlasmaShell.evaluateScript 'string:{script}'"
            self._execute_command(cmd)

            logger.info(f"Обои установлены в KDE: {wallpaper_path}")
            return True

        except Exception as e:
            logger.error(f"Ошибка установки обоев KDE: {e}")

            # Альтернативный метод через конфигурацию
            config_file = Path.home() / '.config' / 'plasma-org.kde.plasma.desktop-appletsrc'
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        content = f.read()

                    # Заменяем путь к обоям
                    import re
                    new_content = re.sub(
                        r'Image=file://.*',
                        f'Image=file://{wallpaper_path}',
                        content
                    )

                    with open(config_file, 'w') as f:
                        f.write(new_content)

                    return True
                except:
                    pass

            return False

    def get_current_theme(self):
        """Получение текущей темы KDE."""
        theme = {}

        try:
            # Чтение kdeglobals
            config = configparser.ConfigParser()
            if self.kde_globals.exists():
                config.read(self.kde_globals)

                if 'General' in config.sections():
                    theme['name'] = config.get('General', 'Name', fallback='')
                    theme['color_scheme'] = config.get('General', 'ColorScheme', fallback='')

            # Чтение plasmarc
            config = configparser.ConfigParser()
            if self.plasma_config.exists():
                config.read(self.plasma_config)

                if 'Theme' in config.sections():
                    theme['plasma_theme'] = config.get('Theme', 'name', fallback='')

            return theme

        except Exception as e:
            logger.error(f"Ошибка получения темы KDE: {e}")
            return {}

    def refresh(self):
        """Обновление KDE."""
        # Перезапуск Plasma
        cmd = "kquitapp5 plasmashell && plasmashell &"
        self._execute_command(cmd)