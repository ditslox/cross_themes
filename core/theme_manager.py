#!/usr/bin/env python3
"""
Менеджер тем для управления установкой на разные платформы.
"""
import importlib
import sys
from pathlib import Path

class ThemeManager:
    def init(self, platform):
        self.platform = platform
        self.adapter = self._load_adapter()
    
    def _load_adapter(self):
        """Динамическая загрузка адаптера для платформы."""
        try:
            module_name = f"adapters.{self.platform}_adapter"
            module = importlib.import_module(module_name)
            adapter_class = getattr(module, f"{self.platform.capitalize()}Adapter")
            return adapter_class()
        except ImportError as e:
            print(f"Адаптер для {self.platform} не найден: {e}")
            from adapters.base_adapter import BaseAdapter
            return BaseAdapter()
    
    def apply_theme(self, theme_data, wallpaper_path=None):
        """Применение темы."""
        try:
            print(f"Применение темы для {self.platform}")
            
            if wallpaper_path and hasattr(self.adapter, 'set_wallpaper'):
                print(f"Установка обоев: {wallpaper_path}")
                self.adapter.set_wallpaper(wallpaper_path)
            
            print("Применение цветовой схемы...")
            success = self.adapter.apply_colors(theme_data)
            
            if success:
                self._save_theme_config(theme_data)
                
                if hasattr(self.adapter, 'refresh'):
                    self.adapter.refresh()
            
            return success
            
        except Exception as e:
            print(f"Ошибка применения темы: {e}")
            return False
    
    def _save_theme_config(self, theme_data):
        """Сохранение конфигурации темы."""
        config_dir = Path.home() / '.config' / 'theme-installer'
        config_dir.mkdir(parents=True, exist_ok=True)
        
        import json
        from datetime import datetime
        
        config = {
            'platform': self.platform,
            'applied_at': datetime.now().isoformat(),
            'theme': theme_data
        }
        
        with open(config_dir / f"theme_{self.platform}.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Конфигурация сохранена")
