from setuptools import setup

REQUIREMENTS = [
    'fuzzywuzzy',
    'python-Levenshtein',
    'prettytable',
    'requests'
]

setup(
    name='xsstrike',
    packages=['xsstrike', 'xsstrike.core'],
    scripts=['xsstrike/xsstrike'],
    version=2.0,
    python_requires='>=3.6.1',
    install_requires=REQUIREMENTS
)
