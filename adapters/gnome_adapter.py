#!/usr/bin/env python3
"""
Адаптер для GNOME (GTK, libadwaita, Gradience).
"""
import subprocess
import json
import os
from pathlib import Path
from base_adapter import BaseAdapter
from cross_themes.utils.logger import setup_logger

logger = setup_logger()


class GnomeAdapter(BaseAdapter):
    def __init__(self):
        super().__init__()
        self.gsettings_schema = "org.gnome.desktop.interface"
        self.gtk_theme_key = "gtk-theme"
        self.icon_theme_key = "icon-theme"
        self.cursor_theme_key = "cursor-theme"

    def apply_colors(self, theme_data):
        """Применение цветов в GNOME."""
        try:
            # Создаем резервную копию
            self.create_backup()

            # 1. Генерация Gradience конфигурации
            self._apply_gradience(theme_data)

            # 2. Установка GTK темы
            self._apply_gtk_theme(theme_data)

            # 3. Установка цветов для libadwaita
            self._apply_libadwaita(theme_data)

            # 4. Обновление настроек GNOME Shell
            self._apply_gnome_shell(theme_data)

            logger.info("Тема успешно применена для GNOME")
            return True

        except Exception as e:
            logger.error(f"Ошибка применения темы GNOME: {e}")
            return False

    def _apply_gradience(self, theme_data):
        """Применение темы через Gradience."""
        gradience_config = {
            "name": theme_data['name'],
            "variables": {
                "accent_color": theme_data['primary'],
                "accent_bg_color": theme_data['primary'],
                "window_bg_color": theme_data['background'],
                "view_bg_color": theme_data['surface'],
                "text_color": theme_data['on_background'],
                "window_fg_color": theme_data['on_background']
            }
        }

        config_path = self.config_dir / 'gradience.json'
        with open(config_path, 'w') as f:
            json.dump(gradience_config, f, indent=2)

        # Применение через gradience-cli если установлен
        if self._check_command('gradience'):
            cmd = f"gradience apply {config_path}"
            self._execute_command(cmd)

    def _apply_gtk_theme(self, theme_data):
        """Установка GTK темы."""
        # Создание пользовательской GTK темы
        theme_dir = Path.home() / '.themes' / f"custom-{theme_data['name'].lower()}"
        theme_dir.mkdir(parents=True, exist_ok=True)

        # Создание gtk-3.0/gtk-4.0 тем
        for version in ['3.0', '4.0']:
            gtk_dir = theme_dir / f"gtk-{version}"
            gtk_dir.mkdir(parents=True, exist_ok=True)

            gtk_css = self._generate_gtk_css(theme_data, version)
            with open(gtk_dir / 'gtk.css', 'w') as f:
                f.write(gtk_css)

        # Применение темы
        cmd = f"gsettings set {self.gsettings_schema} {self.gtk_theme_key} '{theme_dir.name}'"
        self._execute_command(cmd)

    def _apply_libadwaita(self, theme_data):
        """Применение темы для libadwaita."""
        config_home = os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')
        adw_dir = Path(config_home) / 'gtk-4.0'
        adw_dir.mkdir(parents=True, exist_ok=True)

        adw_css = f"""
        @define-color accent_color {theme_data['primary']};
        @define-color accent_bg_color {theme_data['primary']};
        @define-color window_bg_color {theme_data['background']};
        @define-color view_bg_color {theme_data['surface']};
        @define-color text_color {theme_data['on_background']};
        """

        with open(adw_dir / 'gtk.css', 'w') as f:
            f.write(adw_css)

    def _apply_gnome_shell(self, theme_data):
        """Обновление GNOME Shell."""
        # Установка цвета акцента
        cmd = f"gsettings set org.gnome.desktop.interface color-scheme 'prefer-{theme_data['mode']}'"
        self._execute_command(cmd)

        # Установка цвета окон
        cmd = f"gsettings set org.gnome.desktop.wm.preferences theme '{theme_data['name']}'"
        self._execute_command(cmd)

    def set_wallpaper(self, wallpaper_path):
        """Установка обоев в GNOME."""
        if not os.path.exists(wallpaper_path):
            logger.error(f"Файл обоев не найден: {wallpaper_path}")
            return False

        try:
            # Для GNOME 42+
            cmd = f"gsettings set org.gnome.desktop.background picture-uri 'file://{wallpaper_path}'"
            self._execute_command(cmd)

            cmd = f"gsettings set org.gnome.desktop.screensaver picture-uri 'file://{wallpaper_path}'"
            self._execute_command(cmd)

            logger.info(f"Обои установлены: {wallpaper_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка установки обоев: {e}")
            return False

    def get_current_theme(self):
        """Получение текущей темы GNOME."""
        try:
            theme = {}

            # GTK тема
            result = subprocess.run(
                ["gsettings", "get", self.gsettings_schema, self.gtk_theme_key],
                capture_output=True,
                text=True
            )
            theme['gtk_theme'] = result.stdout.strip().strip("'")

            # Цветовая схема
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True,
                text=True
            )
            theme['color_scheme'] = result.stdout.strip().strip("'")

            return theme
        except Exception as e:
            logger.error(f"Ошибка получения темы: {e}")
            return {}

    def refresh(self):
        """Обновление GNOME."""
        # Перезапуск GNOME Shell (только в случае Wayland это работает)
        try:
            if os.environ.get('XDG_SESSION_TYPE') == 'wayland':
                self._execute_command("dbus-run-session gsettings reset-recursively org.gnome.desktop.interface")
        except:
            pass

    def _generate_gtk_css(self, theme_data, version='3.0'):
        """Генерация CSS для GTK."""
        return f"""
        /* Custom theme generated by Theme Installer */
        @define-color accent_color {theme_data['primary']};
        @define-color accent_bg_color {theme_data['primary']};
        @define-color window_bg_color {theme_data['background']};
        @define-color view_bg_color {theme_data['surface']};
        @define-color text_color {theme_data['on_background']};

        * {{
            background-color: @window_bg_color;
            color: @text_color;
        }}
        """

    def _check_command(self, command):
        """Проверка наличия команды."""
        try:
            subprocess.run(["which", command], capture_output=True, check=True)
            return True
        except:
            return False