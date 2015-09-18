#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='tinkrbell',
    version='1.0.0',
    description='Icon generator',
    author='Allan Lei',
    author_email='allan.lei@orbweb.com',
    url='https://github.com/Kloudian-Systems-Inc/tinkrbell',
    packages=find_packages(),
    install_requires=[
        'Flask>=0.10,<0.11',
        'Flask-Cache>=0.13,<0.14',
        'mimeparse==0.1.3',
        'requests>=2.5',
        'Wand>=0.3,<0.4',
    ],
    license='MIT',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
    ),
)
