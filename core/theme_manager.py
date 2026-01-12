#!/usr/bin/env python3
"""
Менеджер тем для управления установкой на разные платформы.
"""
import importlib
import sys
from pathlib import Path
import os

# Добавляем путь к текущей директории для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_logger

logger = setup_logger()


class ThemeManager:
    def __init__(self, platform=None):
        """Инициализация менеджера тем."""
        self.platform = platform or self.detect_platform()
        self.adapter = self._load_adapter()
        logger.info(f"Инициализирован ThemeManager для платформы: {self.platform}")
    
    def detect_platform(self):
        """Автоматическое определение платформы."""
        import platform
        
        system = platform.system().lower()
        
        if system == "linux":
            # Проверяем DE
            de = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
            if "gnome" in de:
                return "gnome"
            elif "kde" in de or "plasma" in de:
                return "kde"
            elif "xfce" in de:
                return "xfce"
            elif "mate" in de:
                return "mate"
            elif "cinnamon" in de:
                return "cinnamon"
            
            # Дополнительные проверки
            try:
                # Проверяем через ps
                import subprocess
                ps_output = subprocess.check_output(["ps", "-e"], text=True, stderr=subprocess.DEVNULL)
                if "gnome-shell" in ps_output:
                    return "gnome"
                elif "plasmashell" in ps_output or "kded" in ps_output:
                    return "kde"
            except:
                pass
            
            return "linux"
        
        elif system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        elif "android" in platform.platform().lower():
            return "android"
        
        return "unknown"
    
    def _load_adapter(self):
        """Динамическая загрузка адаптера для платформы."""
        try:
            module_name = f"adapters.{self.platform}_adapter"
            logger.debug(f"Попытка загрузки модуля: {module_name}")
            
            # Пытаемся импортировать адаптер
            try:
                module = importlib.import_module(module_name)
                adapter_class_name = f"{self.platform.capitalize()}Adapter"
                
                if hasattr(module, adapter_class_name):
                    adapter_class = getattr(module, adapter_class_name)
                    logger.info(f"Загружен адаптер: {adapter_class_name}")
                    return adapter_class()
                else:
                    raise AttributeError(f"Класс {adapter_class_name} не найден в модуле")
                    
            except ImportError as e:
                logger.warning(f"Адаптер для {self.platform} не найден: {e}")
                # Возвращаем базовый адаптер
                from adapters.base_adapter import BaseAdapter
                return BaseAdapter()
                
        except Exception as e:
            logger.error(f"Ошибка загрузки адаптера: {e}")
            # Возвращаем заглушку
            from adapters.base_adapter import BaseAdapter
            return BaseAdapter()
    
    def apply_theme(self, theme_data, wallpaper_path=None):
        """Применение темы."""
        try:
            logger.info(f"Применение темы для {self.platform}")
            
            # Применение обоев
            if wallpaper_path and hasattr(self.adapter, 'set_wallpaper'):
                logger.info(f"Установка обоев: {wallpaper_path}")
                self.adapter.set_wallpaper(wallpaper_path)
            
            # Применение цветовой схемы
            logger.info("Применение цветовой схемы...")
            success = self.adapter.apply_colors(theme_data)
            
            if success:
                # Сохранение темы
                self._save_theme_config(theme_data)
                
                # Обновление системы
                if hasattr(self.adapter, 'refresh'):
                    self.adapter.refresh()
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка применения темы: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _save_theme_config(self, theme_data):
        """Сохранение конфигурации темы."""
        try:
            config_dir = Path.home() / '.config' / 'theme-installer'
            config_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = config_dir / f"theme_{self.platform}.json"
            
            import json
            from datetime import datetime
            
            config = {
                'platform': self.platform,
                'applied_at': datetime.now().isoformat(),
                'theme': theme_data
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Конфигурация сохранена: {config_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")
    
    def get_current_theme(self):
        """Получение текущей темы."""
        try:
            return self.adapter.get_current_theme()
        except Exception as e:
            logger.error(f"Ошибка получения текущей темы: {e}")
            return {}
    
    def list_themes(self):
        """Список доступных тем."""
        try:
            return self.adapter.list_themes()
        except Exception as e:
            logger.error(f"Ошибка получения списка тем: {e}")
            return []
    
    def restore_backup(self):
        """Восстановление из резервной копии."""
        try:
            if hasattr(self.adapter, 'restore_backup'):
                return self.adapter.restore_backup()
            return False
        except Exception as e:
            logger.error(f"Ошибка восстановления из резервной копии: {e}")
            return False


# Для тестирования
if __name__ == "__main__":
    manager = ThemeManager("gnome")
    print(f"Платформа: {manager.platform}")
    print(f"Адаптер: {type(manager.adapter).__name__}")
