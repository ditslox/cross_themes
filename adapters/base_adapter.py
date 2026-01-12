#!/usr/bin/env python3
"""
Базовый класс для всех адаптеров.
"""
import json
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'theme-installer'
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def apply_colors(self, theme_data):
        """Применение цветовой схемы."""
        pass
    
    @abstractmethod
    def set_wallpaper(self, wallpaper_path):
        """Установка обоев."""
        pass
    
    def get_current_theme(self):
        """Получение текущей темы."""
        return {}
    
    def _execute_command(self, command):
        """Выполнение команды оболочки."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_command(self, command):
        """Проверка наличия команды."""
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
