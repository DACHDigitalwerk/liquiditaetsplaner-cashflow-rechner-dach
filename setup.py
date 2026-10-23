# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="liqui-dach",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "dach-liqui=liqui_dach.cli:main",
        ],
    },
)
