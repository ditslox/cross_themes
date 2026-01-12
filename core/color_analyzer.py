#!/usr/bin/env python3
"""
Анализ изображения и генерация цветовых тем.
"""
import colorsys
import json
from collections import Counter
from PIL import Image
import numpy as np
from pathlib import Path


class ColorAnalyzer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = None

    def load_image(self):
        """Загрузка изображения с оптимизацией."""
        try:
            self.image = Image.open(self.image_path).convert('RGB')

            # Оптимизация размера для быстрой обработки
            max_size = 400
            if max(self.image.size) > max_size:
                ratio = max_size / max(self.image.size)
                new_size = (int(self.image.size[0] * ratio),
                            int(self.image.size[1] * ratio))
                self.image = self.image.resize(new_size, Image.Resampling.LANCZOS)

            return True
        except Exception as e:
            raise Exception(f"Ошибка загрузки изображения: {e}")

    @staticmethod
    def rgb_to_hex(rgb):
        return '#{:02x}{:02x}{:02x}'.format(*rgb)

    @staticmethod
    def hex_to_rgb(hex_color):
        hex_value = hex_color.lstrip('#')
        return tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hsl(rgb):
        r, g, b = [x / 255.0 for x in rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return h, s, l

    @staticmethod
    def hsl_to_rgb(hsl):
        h, s, l = hsl
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return int(r * 255), int(g * 255), int(b * 255)

    @staticmethod
    def calculate_luminance(rgb):
        """Расчет относительной яркости (WCAG 2.0)."""
        r, g, b = rgb
        r = r / 255.0
        g = g / 255.0
        b = b / 255.0

        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4

        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def extract_colors(self, num_colors=8, color_tolerance=32):
        """Извлечение доминирующих цветов."""
        if not self.image:
            self.load_image()

        img_array = np.array(self.image)
        pixels = img_array.reshape(-1, 3)

        # Квантование цветов для группировки похожих
        simplified = (pixels // color_tolerance) * color_tolerance

        # Фильтрация слишком темных и слишком светлых цветов
        brightness = np.mean(simplified, axis=1)
        mask = (brightness > 20) & (brightness < 240)
        filtered = simplified[mask] if mask.any() else simplified

        # Подсчет цветов
        color_counts = Counter(map(tuple, filtered))

        # Отбор наиболее контрастных цветов
        selected_colors = []
        for color, count in color_counts.most_common(num_colors * 5):
            if len(selected_colors) >= num_colors:
                break

            rgb_color = tuple(int(c) for c in color)

            # Проверка контраста с уже выбранными цветами
            if selected_colors:
                min_contrast = min(
                    self.get_color_distance(rgb_color, existing)
                    for existing in selected_colors
                )
                if min_contrast < 70:
                    continue

            # Проверка на серость (слишком мало насыщенности)
            h, s, l = self.rgb_to_hsl(rgb_color)
            if s < 0.1:
                continue

            selected_colors.append(rgb_color)

        return [self.rgb_to_hex(color) for color in selected_colors]

    @staticmethod
    def get_color_distance(color1, color2):
        """Расчет расстояния между цветами."""
        return sum(abs(a - b) for a, b in zip(color1, color2))

    def get_contrast_ratio(self, color1, color2):
        """Расчет контрастного соотношения (WCAG)."""
        rgb1 = self.hex_to_rgb(color1)
        rgb2 = self.hex_to_rgb(color2)

        l1 = self.calculate_luminance(rgb1)
        l2 = self.calculate_luminance(rgb2)

        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)

    def select_base_colors(self, colors):
        """Выбор основной пары цветов с лучшим контрастом."""
        if len(colors) < 2:
            return colors[0] if colors else '#3498db', '#2ecc71'

        best_pair = (colors[0], colors[1])
        best_contrast = 0

        for i in range(len(colors)):
            for j in range(i + 1, len(colors)):
                contrast = self.get_contrast_ratio(colors[i], colors[j])
                if contrast > best_contrast:
                    best_contrast = contrast
                    best_pair = (colors[i], colors[j])

        return best_pair

    def generate_color_variations(self, base_color, variations_count=5):
        """Генерация вариаций цвета."""
        rgb = self.hex_to_rgb(base_color)
        h, s, l = self.rgb_to_hsl(rgb)

        variations = {}

        # Светлые варианты
        variations['light'] = self.hsl_to_rgb((h, max(s * 0.4, 0.1), min(l * 1.4, 0.95)))
        variations['lighter'] = self.hsl_to_rgb((h, max(s * 0.3, 0.05), min(l * 1.6, 0.98)))

        # Темные варианты
        variations['dark'] = self.hsl_to_rgb((h, min(s * 1.2, 1.0), max(l * 0.4, 0.1)))
        variations['darker'] = self.hsl_to_rgb((h, min(s * 1.4, 1.0), max(l * 0.2, 0.05)))

        # Насыщенные варианты
        variations['vibrant'] = self.hsl_to_rgb((h, min(s * 1.3, 1.0), min(l * 1.1, 0.8)))
        variations['muted'] = self.hsl_to_rgb((h, s * 0.6, l * 0.9))

        # Комплиментарные цвета
        variations['complementary'] = self.hsl_to_rgb(((h + 0.5) % 1.0, s, l))

        return {k: self.rgb_to_hex(v) for k, v in list(variations.items())[:variations_count]}

    def generate_theme(self, colors, mode='light'):
        """Генерация полной темы."""
        primary, secondary = self.select_base_colors(colors)
        accent_colors = [c for c in colors if c not in [primary, secondary]][:6]

        primary_vars = self.generate_color_variations(primary)
        secondary_vars = self.generate_color_variations(secondary)

        if mode == 'light':
            return {
                'name': 'Light Theme',
                'mode': 'light',
                'primary': primary,
                'primary_variants': primary_vars,
                'secondary': secondary,
                'secondary_variants': secondary_vars,
                'accent_colors': accent_colors,
                'background': '#ffffff',
                'surface': '#f8f9fa',
                'error': '#dc3545',
                'warning': '#ffc107',
                'success': '#28a745',
                'info': '#17a2b8',
                'on_primary': '#ffffff',
                'on_secondary': '#ffffff',
                'on_background': '#212529',
                'on_surface': '#495057',
                'on_error': '#ffffff'
            }
        elif mode == 'dark':
            return {
                'name': 'Dark Theme',
                'mode': 'dark',
                'primary': primary,
                'primary_variants': primary_vars,
                'secondary': secondary,
                'secondary_variants': secondary_vars,
                'accent_colors': accent_colors,
                'background': '#121212',
                'surface': '#1e1e1e',
                'error': '#cf6679',
                'warning': '#ffb74d',
                'success': '#81c784',
                'info': '#4fc3f7',
                'on_primary': '#000000',
                'on_secondary': '#000000',
                'on_background': '#ffffff',
                'on_surface': '#e0e0e0',
                'on_error': '#000000'
            }
        else:  # mixed
            return {
                'name': 'Mixed Theme',
                'mode': 'mixed',
                'primary': primary,
                'primary_variants': primary_vars,
                'secondary': secondary,
                'secondary_variants': secondary_vars,
                'accent_colors': accent_colors,
                'background': primary_vars.get('lighter', '#f0f0f0'),
                'surface': '#ffffff',
                'error': '#e53935',
                'warning': '#fb8c00',
                'success': '#43a047',
                'info': '#1e88e5',
                'on_primary': '#ffffff',
                'on_secondary': '#000000',
                'on_background': '#000000',
                'on_surface': '#000000',
                'on_error': '#ffffff'
            }

    def analyze(self):
        """Основной метод анализа."""
        try:
            self.load_image()
            colors = self.extract_colors(10)

            themes = {
                'light': self.generate_theme(colors, 'light'),
                'dark': self.generate_theme(colors, 'dark'),
                'mixed': self.generate_theme(colors, 'mixed')
            }

            return {
                'source_image': str(self.image_path),
                'image_size': self.image.size,
                'dominant_colors': colors,
                'primary_pair': self.select_base_colors(colors),
                'themes': themes,
                'color_scheme': {
                    'analogous': self.generate_analogous_scheme(colors[0]),
                    'complementary': self.generate_complementary_scheme(colors[0]),
                    'triadic': self.generate_triadic_scheme(colors[0])
                }
            }

        except Exception as e:
            print(f"Ошибка анализа: {e}")
            return self.get_default_themes()

    def generate_analogous_scheme(self, base_color, num_colors=5):
        """Генерация аналогичной цветовой схемы."""
        rgb = self.hex_to_rgb(base_color)
        h, s, l = self.rgb_to_hsl(rgb)

        scheme = []
        step = 0.1  # 36 градусов

        for i in range(-(num_colors // 2), num_colors // 2 + 1):
            new_h = (h + i * step) % 1.0
            scheme.append(self.rgb_to_hex(self.hsl_to_rgb((new_h, s, l))))

        return scheme

    def generate_complementary_scheme(self, base_color):
        """Генерация комплиментарной схемы."""
        rgb = self.hex_to_rgb(base_color)
        h, s, l = self.rgb_to_hsl(rgb)

        complementary_h = (h + 0.5) % 1.0
        complementary = self.rgb_to_hex(self.hsl_to_rgb((complementary_h, s, l)))

        return [base_color, complementary]

    def generate_triadic_scheme(self, base_color):
        """Генерация триадной схемы."""
        rgb = self.hex_to_rgb(base_color)
        h, s, l = self.rgb_to_hsl(rgb)

        color1 = self.rgb_to_hex(self.hsl_to_rgb(((h + 1 / 3) % 1.0, s, l)))
        color2 = self.rgb_to_hex(self.hsl_to_rgb(((h + 2 / 3) % 1.0, s, l)))

        return [base_color, color1, color2]

    def get_default_themes(self):
        """Резервные темы при ошибке."""
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']

        return {
            'dominant_colors': colors,
            'primary_pair': (colors[0], colors[1]),
            'themes': {
                'light': self.generate_theme(colors, 'light'),
                'dark': self.generate_theme(colors, 'dark'),
                'mixed': self.generate_theme(colors, 'mixed')
            }
        }