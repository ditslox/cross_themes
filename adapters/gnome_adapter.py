#!/usr/bin/env python3
"""
Адаптер для GNOME.
"""
import subprocess
import json
import os
from pathlib import Path
from adapters.base_adapter import BaseAdapter

class GnomeAdapter(BaseAdapter):
    def init(self):
        super().init()
        self.gsettings_schema = "org.gnome.desktop.interface"
        
    def apply_colors(self, theme_data):
        """Применение цветов в GNOME."""
        try:
            self.create_backup()
            
            # Установка цветовой схемы
            color_scheme = 'prefer-dark' if theme_data.get('mode') == 'dark' else 'default'
            self._execute_command(f"gsettings set org.gnome.desktop.interface color-scheme '{color_scheme}'")
            
            # Установка GTK темы
            self._execute_command(f"gsettings set {self.gsettings_schema} gtk-theme 'Adwaita'")
            
            # Установка акцентного цвета
            if 'primary' in theme_data:
                self._execute_command(f"gsettings set org.gnome.desktop.interface accent-color '{theme_data['primary']}'")
            
            print("Тема успешно применена для GNOME")
            return True
            
        except Exception as e:
            print(f"Ошибка применения темы GNOME: {e}")
            return False
    
    def set_wallpaper(self, wallpaper_path):
        """Установка обоев в GNOME."""
        if not os.path.exists(wallpaper_path):
            print(f"Файл обоев не найден: {wallpaper_path}")
            return False
        
        try:
            cmd = f"gsettings set org.gnome.desktop.background picture-uri 'file://{wallpaper_path}'"
            self._execute_command(cmd)
            
            cmd = f"gsettings set org.gnome.desktop.screensaver picture-uri 'file://{wallpaper_path}'"
            self._execute_command(cmd)
            
            print(f"Обои установлены: {wallpaper_path}")
            return True
        except Exception as e:
            print(f"Ошибка установки обоев: {e}")
            return False
    
    def _execute_command(self, command):
        """Выполнение команды оболочки."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Ошибка выполнения команды: {result.stderr}")
                return False
            
            return True
        except Exception as e:
            print(f"Ошибка выполнения команды: {e}")
            return False
