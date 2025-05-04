from setuptools import setup, find_packages

setup(
    name='xsstrike',
    version='1.0.0',
    description='Advanced XSS detection suite',
    author='s0md3v',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'xsstrike.db': ['*.json'],
    },    
    install_requires=[
        'tld',
        'fuzzywuzzy',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'xsstrike = xsstrike.cli:main',
        ],
    },
    py_modules=['xsstrike'],
    python_requires='>=3.6',
)
