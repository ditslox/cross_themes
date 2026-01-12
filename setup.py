#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="theme-installer",
    version="1.0.0",
    description="Кроссплатформенный установщик тем",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        'Pillow>=9.0.0',
        'numpy>=1.21.0',
        'colorama>=0.4.4',
    ],
    entry_points={
        'console_scripts': [
            'theme-installer=themes.main:main',
            'themes=themes.main:main',
        ],
    },
    python_requires='>=3.8',
)