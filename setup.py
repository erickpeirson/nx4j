import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='nx4j',
    version='0.1',
    description='Write and retrieve NetworkX graphs from Neo4j',
    author='Erick Peirson',
    author_email='erick.peirson@asu.edu',
    url='https://github.com/erickpeirson/nx4j',
    packages=[
        'nx4j',
    ],
    package_dir={'nx4j':'nx4j'},
    include_package_data=True,
    install_requires=[
        'networkx',
        'py2neo'
    ],
    license='GNU GPL 3',
    test_suite='tests',
)