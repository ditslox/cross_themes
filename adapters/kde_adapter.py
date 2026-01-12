#!/usr/bin/env python3
"""
Простой и рабочий адаптер для KDE Plasma.
"""
import os
import shutil
from pathlib import Path
from adapters.base_adapter import BaseAdapter


class KdeAdapter(BaseAdapter):
    def __init__(self):
        super().__init__()
        self.name = "KDE Adapter"
    
    def apply_colors(self, theme_data):
        """Применение цветов в KDE Plasma."""
        print(f"KDE: Применение цветовой темы '{theme_data.get('name', 'Custom')}'")
        
        try:
            # 1. Создаем простую цветовую схему
            scheme_created = self._create_color_scheme(theme_data)
            
            # 2. Устанавливаем темную/светлую тему
            self._set_theme_mode(theme_data)
            
            if scheme_created:
                print("KDE: Цветовая схема создана и применена")
                return True
            else:
                print("KDE: Цветовая схема создана, но не применена автоматически")
                print("KDE: Примените её вручную в настройках KDE")
                return True
                
        except Exception as e:
            print(f"KDE: Ошибка применения цветов: {e}")
            return False
    
    def _create_color_scheme(self, theme_data):
        """Создание простой цветовой схемы KDE."""
        # Генерируем имя схемы
        scheme_name = f"Custom_{theme_data.get('name', 'Theme').replace(' ', '_')}"
        
        # Создаем директорию для схем
        scheme_dir = Path.home() / '.local' / 'share' / 'color-schemes'
        scheme_dir.mkdir(parents=True, exist_ok=True)
        
        # Файл цветовой схемы
        scheme_file = scheme_dir / f"{scheme_name}.colors"
        
        # Получаем цвета
        primary = theme_data.get('primary', '#2980b9')
        background = theme_data.get('background', '#ffffff')
        foreground = theme_data.get('on_background', '#000000')
        
        # Создаем простую цветовую схему
        scheme_content = f"""[ColorScheme]
Name={scheme_name}

[Colors:Button]
BackgroundNormal={primary}
ForegroundNormal={foreground}

[Colors:Selection]
BackgroundNormal={primary}
ForegroundNormal={foreground}

[Colors:Window]
BackgroundNormal={background}
ForegroundNormal={foreground}

[Colors:View]
BackgroundNormal={background}
ForegroundNormal={foreground}
"""
        
        # Записываем файл
        with open(scheme_file, 'w') as f:
            f.write(scheme_content)
        
        print(f"KDE: Создана цветовая схема: {scheme_name}")
        
        # Пытаемся применить через команду
        if self._check_command('plasma-apply-colorscheme'):
            cmd = f"plasma-apply-colorscheme {scheme_name}"
            if self._execute_command(cmd):
                return True
        
        # Альтернатива через kwriteconfig5
        if self._check_command('kwriteconfig5'):
            cmd = f"kwriteconfig5 --file kdeglobals --group General --key ColorScheme {scheme_name}"
            if self._execute_command(cmd):
                return True
        
        return False
    
    def _set_theme_mode(self, theme_data):
        """Устанавливаем светлую или темную тему."""
        mode = theme_data.get('mode', 'light')
        
        if mode == 'dark' and self._check_command('kwriteconfig5'):
            # Устанавливаем темную тему
            cmd = "kwriteconfig5 --file kdeglobals --group General --key ColorScheme BreezeDark"
            self._execute_command(cmd)
            print("KDE: Установлена темная тема")
        elif mode == 'light' and self._check_command('kwriteconfig5'):
            # Устанавливаем светлую тему
            cmd = "kwriteconfig5 --file kdeglobals --group General --key ColorScheme BreezeLight"
            self._execute_command(cmd)
            print("KDE: Установлена светлая тема")
    
    def set_wallpaper(self, wallpaper_path):
        """Установка обоев в KDE - ПРОСТОЙ РАБОЧИЙ МЕТОД."""
        if not os.path.exists(wallpaper_path):
            print(f"KDE: Файл не найден: {wallpaper_path}")
            return False
        
        print(f"KDE: Установка обоев: {wallpaper_path}")
        
        # Метод 1: plasma-apply-wallpaperimage (лучший)
        if self._check_command('plasma-apply-wallpaperimage'):
            cmd = f"plasma-apply-wallpaperimage {wallpaper_path}"
            if self._execute_command(cmd):
                print("KDE: Обои установлены через plasma-apply-wallpaperimage")
                return True
        
        # Метод 2: qdbus (старый метод)
        if self._check_command('qdbus'):
            script = f"""
            var allDesktops = desktops();
            for (var i=0; i<allDesktops.length; i++) {{
                var desktop = allDesktops[i];
                desktop.wallpaperPlugin = "org.kde.image";
                desktop.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
                desktop.writeConfig("Image", "file://{wallpaper_path}");
            }}
            """
            # Сохраняем скрипт во временный файл
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(script)
                temp_path = f.name
            
            cmd = f"qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '$(cat {temp_path})'"
            if self._execute_command(cmd):
                os.unlink(temp_path)
                print("KDE: Обои установлены через qdbus")
                return True
        
        # Метод 3: копируем в стандартную папку и устанавливаем через конфиг
        if self._check_command('kwriteconfig5'):
            # Копируем обои в домашнюю директорию
            home_wallpaper = Path.home() / '.local' / 'share' / 'wallpapers' / Path(wallpaper_path).name
            home_wallpaper.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(wallpaper_path, home_wallpaper)
            
            # Устанавливаем через конфиг
            cmd = f"kwriteconfig5 --file plasmarc --group Theme --key wallpaper '{home_wallpaper}'"
            if self._execute_command(cmd):
                print(f"KDE: Обои скопированы и установлены через конфиг: {home_wallpaper}")
                return True
        
        # Метод 4: прямой скрипт Python с dbus
        try:
            import dbus
            bus = dbus.SessionBus()
            plasma = bus.get_object('org.kde.plasmashell', '/PlasmaShell')
            script = f"""
            var allDesktops = desktops();
            for (var i=0; i<allDesktops.length; i++) {{
                var desktop = allDesktops[i];
                desktop.wallpaperPlugin = "org.kde.image";
                desktop.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
                desktop.writeConfig("Image", "file://{wallpaper_path}");
            }}
            """
            plasma.evaluateScript(script, dbus_interface='org.kde.PlasmaShell')
            print("KDE: Обои установлены через Python dbus")
            return True
        except:
            pass
        
        print("KDE: Не удалось установить обои автоматически")
        print("KDE: Установите обои вручную в настройках KDE")
        return False
    
    def get_current_theme(self):
        """Получение текущей темы KDE."""
        theme = {}
        
        try:
            # Проверяем файл kdeglobals
            kdeglobals = Path.home() / '.config' / 'kdeglobals'
            if kdeglobals.exists():
                with open(kdeglobals, 'r') as f:
                    for line in f:
                        if 'ColorScheme=' in line:
                            theme['color_scheme'] = line.split('=')[1].strip()
            
            return theme
        except:
            return {}
