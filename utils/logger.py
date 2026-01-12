#!/usr/bin/env python3
"""
Настройка логгирования.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name='ThemeInstaller', log_level=logging.INFO):
    """Настройка логгера."""
    # Создаем директорию для логов
    log_dir = Path.home() / '.cache' / 'theme-installer' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    # Имя файла лога с датой
    log_file = log_dir / f"theme_installer_{datetime.now():%Y%m%d}.log"

    # Настройка форматера
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Логгер
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Обработчик для файла
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_log_file():
    """Получение пути к текущему файлу лога."""
    log_dir = Path.home() / '.cache' / 'theme-installer' / 'logs'
    return log_dir / f"theme_installer_{datetime.now():%Y%m%d}.log"