#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import envoy

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='tinkrbell',
    version=tinkrbell.__version__,
    description='Icon generator',
    long_description=open('README.md').read(),
    author='Allan Lei',
    author_email='allan.lei@orbweb.com',
    url='https://github.com/Kloudian-Systems-Inc/tinkrbell',
    packages=['tinkrbell'],
    install_requires=[
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
