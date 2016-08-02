#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='tinkrbell',
    version='2.0.0',
    description='Thumbnail generator',
    author='Allan Lei',
    author_email='allanlei@helveticode.com',
    url='https://github.com/allanlei/tinkrbell',
    packages=find_packages(),
    install_requires=[
        'Flask>=0.10,<0.11',
        'Flask-Cache>=0.13,<0.14',
        'requests>=2.8',
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
