#!/usr/bin/env python3
"""
Базовый класс для всех адаптеров.
"""
import json
from pathlib import Path

class BaseAdapter:
    def init(self):
        self.config_dir = Path.home() / '.config' / 'theme-installer'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_file = self.config_dir / 'backup.json'
    
    def apply_colors(self, theme_data):
        """Применение цветовой схемы."""
        print("Базовый адаптер: метод apply_colors не реализован")
        return False
    
    def set_wallpaper(self, wallpaper_path):
        """Установка обоев."""
        print("Базовый адаптер: метод set_wallpaper не реализован")
        return False
    
    def get_current_theme(self):
        """Получение текущей темы."""
        return {}
    
    def create_backup(self):
        """Создание резервной копии текущих настроек."""
        try:
            current_theme = self.get_current_theme()
            backup_data = {
                'platform': self.class.name.replace('Adapter', '').lower(),
                'theme': current_theme
            }
            
            with open(self.backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"Резервная копия создана")
            return True
        except Exception as e:
            print(f"Ошибка создания резервной копии: {e}")
            return False
