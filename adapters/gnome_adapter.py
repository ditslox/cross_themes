#!/usr/bin/env python3
"""
Простой и рабочий адаптер для GNOME.
"""
import os
from pathlib import Path
from adapters.base_adapter import BaseAdapter


class GnomeAdapter(BaseAdapter):
    def __init__(self):
        super().__init__()
        self.name = "GNOME Adapter"
    
    def apply_colors(self, theme_data):
        """Применение цветов в GNOME."""
        print(f"GNOME: Применение цветовой темы '{theme_data.get('name', 'Custom')}'")
        
        try:
            # 1. Установка акцентного цвета (GNOME 42+)
            if self._check_command('gsettings'):
                # Цветовая схема (светлая/темная)
                mode = 'prefer-dark' if theme_data.get('mode') == 'dark' else 'default'
                cmd = f"gsettings set org.gnome.desktop.interface color-scheme '{mode}'"
                self._execute_command(cmd)
                
                # Акцентный цвет (используем первичный цвет)
                primary = theme_data.get('primary', '#3584e4')
                # Для GNOME нужно убрать # и добавить ' в начале
                color_value = primary.lstrip('#')
                cmd = f"gsettings set org.gnome.desktop.interface accent-color '#{color_value}'"
                self._execute_command(cmd)
            
            # 2. Создание простой темы для GTK
            self._create_simple_gtk_theme(theme_data)
            
            print("GNOME: Цвета успешно применены")
            return True
            
        except Exception as e:
            print(f"GNOME: Ошибка применения цветов: {e}")
            return False
    
    def _create_simple_gtk_theme(self, theme_data):
        """Создание простой GTK темы."""
        theme_name = "custom-gnome-theme"
        theme_dir = Path.home() / '.themes' / theme_name
        theme_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем базовый CSS
        css_content = f"""
        * {{
            background-color: {theme_data.get('background', '#ffffff')};
            color: {theme_data.get('on_background', '#000000')};
        }}
        
        button {{
            background-color: {theme_data.get('primary', '#3584e4')};
            color: white;
        }}
        """
        
        # Для GTK 3
        gtk3_dir = theme_dir / 'gtk-3.0'
        gtk3_dir.mkdir(exist_ok=True)
        with open(gtk3_dir / 'gtk.css', 'w') as f:
            f.write(css_content)
        
        # Для GTK 4
        gtk4_dir = theme_dir / 'gtk-4.0'
        gtk4_dir.mkdir(exist_ok=True)
        with open(gtk4_dir / 'gtk.css', 'w') as f:
            f.write(css_content)
    
    def set_wallpaper(self, wallpaper_path):
        """Установка обоев в GNOME - ПРОСТОЙ РАБОЧИЙ МЕТОД."""
        if not os.path.exists(wallpaper_path):
            print(f"GNOME: Файл не найден: {wallpaper_path}")
            return False
        
        print(f"GNOME: Установка обоев: {wallpaper_path}")
        
        # Метод 1: gsettings (основной)
        if self._check_command('gsettings'):
            # Устанавливаем для рабочего стола
            cmd = f"gsettings set org.gnome.desktop.background picture-uri 'file://{wallpaper_path}'"
            if self._execute_command(cmd):
                print("GNOME: Обои установлены через gsettings")
                return True
        
        # Метод 2: через dconf
        if self._check_command('dconf'):
            cmd = f"dconf write /org/gnome/desktop/background/picture-uri '\"file://{wallpaper_path}\"'"
            if self._execute_command(cmd):
                print("GNOME: Обои установлены через dconf")
                return True
        
        # Метод 3: прямой скрипт Python
        try:
            import gi
            gi.require_version('Gio', '2.0')
            from gi.repository import Gio
            
            settings = Gio.Settings.new("org.gnome.desktop.background")
            settings.set_string("picture-uri", f"file://{wallpaper_path}")
            settings.apply()
            print("GNOME: Обои установлены через Gio")
            return True
        except:
            pass
        
        print("GNOME: Не удалось установить обои")
        return False
    
    def get_current_theme(self):
        """Получение текущей темы GNOME."""
        theme = {}
        
        try:
            if self._check_command('gsettings'):
                import subprocess
                
                # Цветовая схема
                result = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    theme['color_scheme'] = result.stdout.strip().strip("'")
                
                # Обои
                result = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.background", "picture-uri"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    theme['wallpaper'] = result.stdout.strip().strip("'")
            
            return theme
        except:
            return {}
