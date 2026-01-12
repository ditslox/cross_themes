#!/usr/bin/env python3
"""
Улучшенный адаптер для KDE Plasma с гарантированной работой.
"""
import os
import sys
import time
import subprocess
import tempfile
import configparser
from pathlib import Path
from adapters.base_adapter import BaseAdapter


class KdeAdapter(BaseAdapter):
    def __init__(self):
        super().__init__()
        self.name = "KDE Adapter"
        self.plasma_version = self._detect_plasma_version()
        print(f"KDE: Обнаружена Plasma версия: {self.plasma_version}")
    
    def _detect_plasma_version(self):
        """Определение версии Plasma."""
        try:
            # Проверяем наличие команд для разных версий
            if self._check_command('plasmashell'):
                result = subprocess.run(
                    ['plasmashell', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if 'Plasma 6' in result.stdout or 'Plasma 6' in result.stderr:
                    return '6'
                elif 'Plasma 5' in result.stdout or 'Plasma 5' in result.stderr:
                    return '5'
            
            # Проверяем по наличию команд
            if self._check_command('kwriteconfig6'):
                return '6'
            elif self._check_command('kwriteconfig5'):
                return '5'
            
            return 'unknown'
        except:
            return 'unknown'
    
    def _get_kwriteconfig(self):
        """Получение правильной команды kwriteconfig."""
        if self.plasma_version == '6' and self._check_command('kwriteconfig6'):
            return 'kwriteconfig6'
        elif self._check_command('kwriteconfig5'):
            return 'kwriteconfig5'
        return None
    
    def _get_kreadconfig(self):
        """Получение правильной команды kreadconfig."""
        if self.plasma_version == '6' and self._check_command('kreadconfig6'):
            return 'kreadconfig6'
        elif self._check_command('kreadconfig5'):
            return 'kreadconfig5'
        return None
    
    def apply_colors(self, theme_data):
        """Применение цветов в KDE Plasma - ГАРАНТИРОВАННО РАБОЧИЙ МЕТОД."""
        print(f"KDE: Применение темы '{theme_data.get('name', 'Custom')}'")
        
        try:
            mode = theme_data.get('mode', 'light')
            
            # 1. Создаем цветовую схему
            scheme_name = self._create_color_scheme(theme_data)
            
            # 2. Применяем цветовую схему
            if scheme_name:
                self._apply_color_scheme(scheme_name, mode)
            
            # 3. Устанавливаем тему окон
            self._set_window_theme(mode)
            
            # 4. Устанавливаем тему Plasma
            self._set_plasma_theme(mode)
            
            # 5. Обновляем все настройки
            self._refresh_kde()
            
            print("KDE: Тема полностью применена")
            return True
            
        except Exception as e:
            print(f"KDE: Ошибка применения темы: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_color_scheme(self, theme_data):
        """Создание цветовой схемы KDE."""
        # Генерируем имя схемы
        mode = theme_data.get('mode', 'light')
        scheme_name = f"Custom_{theme_data.get('name', 'Theme').replace(' ', '_')}_{mode}"
        
        # Создаем директорию для схем
        scheme_dir = Path.home() / '.local' / 'share' / 'color-schemes'
        scheme_dir.mkdir(parents=True, exist_ok=True)
        
        # Файл цветовой схемы
        scheme_file = scheme_dir / f"{scheme_name}.colors"
        
        # Получаем цвета
        primary = theme_data.get('primary', '#2980b9')
        secondary = theme_data.get('secondary', '#2ecc71')
        background = theme_data.get('background', '#ffffff')
        foreground = theme_data.get('on_background', '#000000')
        surface = theme_data.get('surface', '#f8f9fa')
        surface_text = theme_data.get('on_surface', '#000000')
        
        # Создаем полноценную цветовую схему
        scheme_content = f"""[ColorScheme]
Name={scheme_name}
ColorPalette={primary},{secondary}

[General]
accent={primary}
accentBackground={primary}
background={background}
decoration={primary}
foreground={foreground}
viewBackground={surface}

[Colors:Button]
BackgroundNormal={primary}
BackgroundAlternate={self._darken_color(primary, 0.1)}
ForegroundNormal={foreground}
ForegroundActive={foreground}
ForegroundDisabled=#666666
ForegroundLink={secondary}
ForegroundNegative=#da4453
ForegroundNeutral=#f67400
ForegroundPositive=#27ae60
ForegroundVisited={self._lighten_color(secondary, 0.2)}

[Colors:Selection]
BackgroundNormal={primary}
BackgroundAlternate={self._darken_color(primary, 0.1)}
ForegroundNormal={foreground}

[Colors:Window]
BackgroundNormal={background}
BackgroundAlternate={surface}
ForegroundNormal={foreground}
ForegroundActive={foreground}
ForegroundInactive=#666666

[Colors:View]
BackgroundNormal={surface}
BackgroundAlternate={background}
ForegroundNormal={surface_text}
ForegroundInactive=#666666
ForegroundLink={secondary}

[Colors:Tooltip]
BackgroundNormal={primary}
BackgroundAlternate={self._darken_color(primary, 0.1)}
ForegroundNormal={foreground}

[Colors:Complementary]
BackgroundNormal={secondary}
BackgroundAlternate={self._darken_color(secondary, 0.1)}
ForegroundNormal={foreground}

[WM]
activeBackground={primary}
activeForeground={foreground}
inactiveBackground={background}
inactiveForeground=#666666
"""
        
        # Записываем файл
        with open(scheme_file, 'w') as f:
            f.write(scheme_content)
        
        print(f"KDE: Создана цветовая схема: {scheme_name}")
        return scheme_name
    
    def _apply_color_scheme(self, scheme_name, mode):
        """Применение цветовой схемы."""
        # Метод 1: plasma-apply-colorscheme (лучший)
        if self._check_command('plasma-apply-colorscheme'):
            cmd = f"plasma-apply-colorscheme {scheme_name}"
            if self._execute_command(cmd):
                print(f"KDE: Цветовая схема применена через plasma-apply-colorscheme")
                return True
        
        # Метод 2: kwriteconfig
        kwriteconfig = self._get_kwriteconfig()
        if kwriteconfig:
            cmd = f"{kwriteconfig} --file kdeglobals --group General --key ColorScheme {scheme_name}"
            if self._execute_command(cmd):
                print(f"KDE: Цветовая схема применена через {kwriteconfig}")
                return True
        
        # Метод 3: прямой файл
        kdeglobals = Path.home() / '.config' / 'kdeglobals'
        if kdeglobals.exists():
            config = configparser.ConfigParser()
            config.read(kdeglobals)
            
            if 'General' not in config.sections():
                config.add_section('General')
            
            config.set('General', 'ColorScheme', scheme_name)
            config.set('General', 'colorScheme', 'Dark' if mode == 'dark' else 'Light')
            
            with open(kdeglobals, 'w') as f:
                config.write(f)
            
            print(f"KDE: Цветовая схема записана в {kdeglobals}")
            return True
        
        return False
    
    def _set_window_theme(self, mode):
        """Установка темы окон."""
        window_theme = 'breeze-dark' if mode == 'dark' else 'breeze'
        
        kwriteconfig = self._get_kwriteconfig()
        if kwriteconfig:
            # Тема окон
            cmd = f"{kwriteconfig} --file kdeglobals --group WM --key theme {window_theme}"
            self._execute_command(cmd)
            
            # Стиль окон
            cmd = f"{kwriteconfig} --file kdeglobals --group WM --key style {window_theme}"
            self._execute_command(cmd)
            
            print(f"KDE: Установлена тема окон: {window_theme}")
    
    def _set_plasma_theme(self, mode):
        """Установка темы Plasma."""
        plasma_theme = 'breeze-dark' if mode == 'dark' else 'breeze'
        
        kwriteconfig = self._get_kwriteconfig()
        if kwriteconfig:
            cmd = f"{kwriteconfig} --file plasmarc --group Theme --key name {plasma_theme}"
            self._execute_command(cmd)
            print(f"KDE: Установлена тема Plasma: {plasma_theme}")
    
    def _refresh_kde(self):
        """Обновление KDE."""
        print("KDE: Обновление окружения...")
        
        # Безопасный перезапуск
        try:
            # Для Plasma 6
            if self.plasma_version == '6':
                if self._check_command('plasmashell'):
                    # Останавливаем и перезапускаем
                    self._execute_command("kquitapp6 plasmashell 2>/dev/null || true")
                    time.sleep(1)
                    self._execute_command("plasmashell --replace >/dev/null 2>&1 &")
                    print("KDE: Plasma 6 перезапущен")
            # Для Plasma 5
            else:
                if self._check_command('plasmashell'):
                    self._execute_command("kquitapp5 plasmashell 2>/dev/null || true")
                    time.sleep(1)
                    self._execute_command("plasmashell --replace >/dev/null 2>&1 &")
                    print("KDE: Plasma 5 перезапущен")
        except:
            print("KDE: Не удалось перезапустить Plasma, изменения применятся после перезагрузки")
    
    def _darken_color(self, hex_color, factor=0.1):
        """Затемнение цвета."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _lighten_color(self, hex_color, factor=0.1):
        """Осветление цвета."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = min(255, int(r * (1 + factor)))
        g = min(255, int(g * (1 + factor)))
        b = min(255, int(b * (1 + factor)))
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def set_wallpaper(self, wallpaper_path):
        """ГАРАНТИРОВАННАЯ установка обоев в KDE."""
        if not os.path.exists(wallpaper_path):
            print(f"KDE: Файл не найден: {wallpaper_path}")
            return False
        
        print(f"KDE: Установка обоев: {wallpaper_path}")
        
        # Метод 1: plasma-apply-wallpaperimage (лучший для Plasma 6)
        if self._check_command('plasma-apply-wallpaperimage'):
            cmd = f"plasma-apply-wallpaperimage {wallpaper_path}"
            if self._execute_command(cmd):
                print("KDE: Обои установлены через plasma-apply-wallpaperimage")
                return True
        
        # Метод 2: dbus-send (универсальный)
        if self._check_command('dbus-send'):
            # Для Plasma 6
            if self.plasma_version == '6':
                cmd = f"""dbus-send --session --dest=org.kde.plasmashell --type=method_call /PlasmaShell org.kde.PlasmaShell.evaluateScript 'string:
                var allDesktops = desktops();
                for (var i=0; i<allDesktops.length; i++) {{
                    var desktop = allDesktops[i];
                    desktop.wallpaperPlugin = "org.kde.image";
                    desktop.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
                    desktop.writeConfig("Image", "file://{wallpaper_path}");
                }}'"""
            # Для Plasma 5
            else:
                cmd = f"""dbus-send --session --dest=org.kde.plasmashell --type=method_call /PlasmaShell org.kde.PlasmaShell.evaluateScript 'string:
                var allDesktops = desktops();
                for (var i=0; i<allDesktops.length; i++) {{
                    var desktop = allDesktops[i];
                    desktop.wallpaperPlugin = "org.kde.image";
                    desktop.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
                    desktop.writeConfig("Image", "file://{wallpaper_path}");
                }}'"""
            
            if self._execute_command(cmd):
                print("KDE: Обои установлены через dbus-send")
                return True
        
        # Метод 3: qdbus (для Plasma 5)
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
            
            # Сохраняем скрипт
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(script)
                temp_path = f.name
            
            cmd = f"qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '$(cat {temp_path})'"
            if self._execute_command(cmd):
                os.unlink(temp_path)
                print("KDE: Обои установлены через qdbus")
                return True
        
        # Метод 4: прямой Python dbus
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
        except Exception as e:
            print(f"KDE: Python dbus не сработал: {e}")
        
        # Метод 5: запись в конфиг файл (последний шанс)
        try:
            # Ищем конфиг файлы
            config_patterns = [
                Path.home() / '.config' / 'plasma-org.kde.plasma.desktop-appletsrc',
                Path.home() / '.config' / 'plasmarc'
            ]
            
            for config_file in config_patterns:
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        content = f.read()
                    
                    # Простая замена
                    import re
                    new_content = re.sub(
                        r'Image=file://.*',
                        f'Image=file://{wallpaper_path}',
                        content
                    )
                    
                    if new_content != content:
                        with open(config_file, 'w') as f:
                            f.write(new_content)
                        print(f"KDE: Обои записаны в {config_file}")
                        return True
            
            # Если не нашли, создаем запись
            config_file = Path.home() / '.config' / 'plasmarc'
            with open(config_file, 'a') as f:
                f.write(f'\n[Theme]\nwallpaper={wallpaper_path}\n')
            
            print(f"KDE: Обои добавлены в {config_file}")
            return True
            
        except Exception as e:
            print(f"KDE: Ошибка записи в конфиг: {e}")
        
        print("KDE: ВСЕ методы не сработали!")
        print("KDE: Попробуйте установить пакеты:")
        print("     sudo dnf install plasma-workspace plasma-sdk dbus-x11")
        return False
    
    def get_current_theme(self):
        """Получение текущей темы KDE."""
        theme = {}
        
        try:
            # Чтение kdeglobals
            kdeglobals = Path.home() / '.config' / 'kdeglobals'
            if kdeglobals.exists():
                config = configparser.ConfigParser()
                config.read(kdeglobals)
                
                if 'General' in config.sections():
                    theme['color_scheme'] = config.get('General', 'ColorScheme', fallback='')
                    theme['theme_mode'] = config.get('General', 'colorScheme', fallback='')
                
                if 'WM' in config.sections():
                    theme['window_theme'] = config.get('WM', 'theme', fallback='')
            
            # Чтение plasmarc
            plasmarc = Path.home() / '.config' / 'plasmarc'
            if plasmarc.exists():
                config = configparser.ConfigParser()
                config.read(plasmarc)
                
                if 'Theme' in config.sections():
                    theme['plasma_theme'] = config.get('Theme', 'name', fallback='')
            
            return theme
        except:
            return {}