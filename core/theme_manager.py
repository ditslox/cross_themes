#!/usr/bin/env python3
"""
Менеджер тем для управления установкой на разные платформы.
"""
import importlib
from pathlib import Path
from cross_themes.utils.logger import setup_logger

logger = setup_logger()


class ThemeManager:
    def __init__(self, platform):
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
            logger.error(f"Адаптер для {self.platform} не найден: {e}")
            # Возвращаем заглушку
            from adapters.base_adapter import BaseAdapter
            return BaseAdapter()
        except Exception as e:
            logger.error(f"Ошибка загрузки адаптера: {e}")
            raise

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
            return False

    def _save_theme_config(self, theme_data):
        """Сохранение конфигурации темы."""
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

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info(f"Конфигурация сохранена: {config_file}")

    def get_current_theme(self):
        """Получение текущей темы."""
        return self.adapter.get_current_theme()

    def list_themes(self):
        """Список доступных тем."""
        return self.adapter.list_themes()

    def restore_backup(self):
        """Восстановление из резервной копии."""
        if hasattr(self.adapter, 'restore_backup'):
            return self.adapter.restore_backup()
        return False