from setuptools import setup

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='xsstrike',
    version='3.1.6',
    packages=['core', 'db', 'modes', 'plugins'],
    install_requires=install_requires,
    package_data={'db': ['*']},    
    scripts=['xsstrike.py'],
)