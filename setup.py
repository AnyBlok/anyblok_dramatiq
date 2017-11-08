#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for dramatiq"""

from setuptools import setup, find_packages
import os
import sys

version = '0.1.0'


if sys.version_info < (3, 6):
    sys.stderr.write("This package requires Python 3.6 or newer. "
                     "Yours is " + sys.version + os.linesep)
    sys.exit(1)


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), 'r',
          encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(
    os.path.join(here, 'doc', 'CHANGES.rst'), 'r', encoding='utf-8'
) as change:
    CHANGES = change.read()

with open(
    os.path.join(here, 'doc', 'FRONT.rst'), 'r', encoding='utf-8'
) as front:
    FRONT = front.read()

with open(
    os.path.join(here, 'doc', 'MEMENTO.rst'), 'r', encoding='utf-8'
) as memento:
    MEMENTO = front.read()

anyblok_init = [
]

requirements = [
    'anyblok',
    'dramatiq',
]

setup(
    name='anyblok_dramatiq',
    version=version,
    description="test simple usecase between anyblok and dramatiq",
    long_description=readme + '\n' + MEMENTO + '\n' + FRONT + '\n' + CHANGES,
    author="jssuzanne",
    author_email='jssuzanne@anybox.fr',
    url='https://github.com/jssuzanne/dramatiq',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'anyblok_dramatiq=anyblok_dramatiq.scripts:anyblok_dramatiq',
        ],
        'bloks': [
            'dramatiq=anyblok_dramatiq.bloks.dramatiq:DramatiqBlok'
        ],
        'anyblok.init': [
            'dramatiq_config=anyblok_dramatiq:anyblok_init_config',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='dramatiq',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=requirements + ['nose'],
)
