# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok / Dramatiq project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from setuptools import setup, find_packages
import os

version = '1.0.3'


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

anyblok_init = [
]

requirements = [
    'simplejson',
    'anyblok',
    'dramatiq>=0.12.0',
]

extras = ("memcached", "rabbitmq", "redis", "watch")
extra_dependencies = {}
for extra in extras:
    extra_dependencies[extra] = ['dramatiq[%s]' % extra]

setup(
    name='anyblok_dramatiq',
    version=version,
    description="test simple usecase between anyblok and dramatiq",
    long_description=readme + '\n' + FRONT + '\n' + CHANGES,
    author="jssuzanne",
    author_email='jssuzanne@anybox.fr',
    url="http://docs.anyblok-dramatiq.anyblok.org/%s" % version,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'anyblok_dramatiq=anyblok_dramatiq.scripts:anyblok_dramatiq',
        ],
        'bloks': [
            'dramatiq=anyblok_dramatiq.bloks.dramatiq:DramatiqBlok',
            'dramatiq-task=anyblok_dramatiq.bloks.task:DramatiqTaskBlok',
        ],
        'anyblok.init': [
            'dramatiq_config=anyblok_dramatiq:anyblok_init_config',
        ],
        'anyblok_configuration.post_load': [
            'dramatiq_broker=anyblok_dramatiq:anyblok_load_broker',
        ],
        'test_bloks': [
            'test_dramatiq_1=anyblok_dramatiq.test_bloks.test_1:TestBlok1',
            'test_dramatiq_2=anyblok_dramatiq.test_bloks.test_2:TestBlok2',
        ],
        'anyblok.model.plugin': [
            'dramatic_actor=anyblok_dramatiq.actor:ActorPlugin',
            'dramatic_actor_send=anyblok_dramatiq.actor:ActorSendPlugin',
        ],
        'anyblok_dramatiq.middleware': [
            'message=anyblok_dramatiq.middleware:DramatiqMessageMiddleware',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    extras_require=extra_dependencies,
    zip_safe=False,
    keywords='dramatiq',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
    tests_require=requirements + ['nose'],
)
