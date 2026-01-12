#!/usr/bin/env python3
"""
Базовый класс для всех адаптеров.
"""
import json
from pathlib import Path
from abc import ABC, abstractmethod
from cross_themes.utils.logger import setup_logger

logger = setup_logger()


class BaseAdapter(ABC):
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'theme-installer'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_file = self.config_dir / 'backup.json'

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

    def list_themes(self):
        """Список доступных тем."""
        return []

    def refresh(self):
        """Обновление системы."""
        pass

    def create_backup(self):
        """Создание резервной копии текущих настроек."""
        try:
            current_theme = self.get_current_theme()
            backup_data = {
                'platform': self.__class__.__name__.replace('Adapter', '').lower(),
                'theme': current_theme
            }

            with open(self.backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)

            logger.info(f"Резервная копия создана: {self.backup_file}")
            return True
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
            return False

    def restore_backup(self):
        """Восстановление из резервной копии."""
        if not self.backup_file.exists():
            logger.error("Резервная копия не найдена")
            return False

        try:
            with open(self.backup_file, 'r') as f:
                backup_data = json.load(f)

            if 'theme' in backup_data:
                return self.apply_colors(backup_data['theme'])

            return False
        except Exception as e:
            logger.error(f"Ошибка восстановления из резервной копии: {e}")
            return False

    def _execute_command(self, command):
        """Выполнение команды оболочки."""
        import subprocess
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"Ошибка выполнения команды: {result.stderr}")
                return False

            return True
        except Exception as e:
            logger.error(f"Ошибка выполнения команды: {e}")
            return False