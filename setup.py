#!/usr/bin/env python3
"""
Setup script for XSStrike
Advanced XSS Detection Suite
"""

from setuptools import setup, find_packages
import os
import re

# Read version from pyproject.toml to avoid duplication
def read_version():
    pyproject_path = os.path.join(os.path.dirname(__file__), 'pyproject.toml')
    if os.path.exists(pyproject_path):
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    return '3.1.7'  # fallback

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Advanced XSS Detection Suite"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return requirements
    return []

setup(
    name='xsstrike',
    version=read_version(),  # Read from pyproject.toml to avoid duplication
    # description, python_requires, and dependencies are read from pyproject.toml automatically
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='s0md3v',
    author_email='',
    url='https://github.com/s0md3v/XSStrike',
    license='GPL-3.0',
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*']),
    py_modules=['xsstrike'],
    # install_requires is read from pyproject.toml [project.dependencies] automatically
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
        ],
    },
    include_package_data=True,
    package_data={
        '': [
            'db/*.json',
            'README.md',
            'LICENSE',
            'CHANGELOG.md',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    keywords='xss security penetration-testing web-security vulnerability-scanner',
    zip_safe=False,
)
