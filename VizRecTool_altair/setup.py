#!/usr/bin/env python
import re

from setuptools import find_packages, setup


setup(
    name='VizRecTool',
    version=1.0,
    description='A Data visualization recommendation tool built with Altair and Django',

    author='Daiane Macedo',

    packages=find_packages(exclude=['vizRecTool.*', 'vizRecTool']),
    include_package_data=True,  # declarations in MANIFEST.in

    install_requires=['Django>=1.11', 'MyApplication']
)