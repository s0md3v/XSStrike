from codecs import open
from setuptools import setup, find_packages


with open('CHANGELOG.md') as f:
    VERSION = f.readline().strip('### ').rstrip()

setup(
    name="XXStrike",
    version=VERSION,
    description="Cross Site Scripting detection suite",
    long_description="Cross Site Scripting detection suite",
    url="https://github.com/s0md3v/XSStrike",
    author="Somdev Sangwan",
    author_email="s0md3v@gmail.com",
    license="GNU GPL-3.0",
    classifiers=[
        "License :: OSI Approved :: GPL-3.0",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Console :: Curses",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Security",
        "Topic :: Security :: XSS",
        "Topic :: Security :: XSS-Scanner",
        "Topic :: Security :: XSS-Exploit",
        "Topic :: Security :: XSS-Bruteforce",
        "Topic :: Internet",
        "Topic :: Internet :: XSS",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Vulnerability Scanner"
    ],
    packages=find_packages(include=[
        "core",
        "modes",
        'db'
    ]),
    include_package_data=True,
    install_requires=[
        "tld",
        "fuzzywuzzy",
        "requests"
    ],
    # extras_require={
    #     'dev': [
    #         'pytest',
    #         'pytest-timeout',
    #         'pytest-cov',
    #     ],
    # }
)