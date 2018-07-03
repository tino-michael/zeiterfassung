#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='zeiterfassung',
    version='0.1',
    description='tool to keep track of your working hours',
    author='Tino Michael',
    author_email='tino.michael.87@gamil.com',
    scripts=['zeiterfassung.py'],
    install_requires=['pyyaml', 'pandas']
)
