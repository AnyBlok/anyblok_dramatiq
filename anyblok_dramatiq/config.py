# This file is a part of the AnyBlok / Dramatiq project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.config import Configuration, AnyBlokPlugin
from .release import version
import os


Configuration.applications.update({
    'dramatiq': {
        'prog': 'Dramatiq app for AnyBlok, version %r' % version,
        'description': 'Distributed actor for AnyBlok',
        'configuration_groups': [
            'dramatiq-broker',
            'dramatiq-consumer',
            'config', 'database',
        ],
    },
})


@Configuration.add('dramatiq-consumer', label="Dramatiq - consumer options",
                   must_be_loaded_by_unittest=True)
def define_dramatiq_consumer(group):
    group.add_argument('--dramatiq-processes', type=int,
                       default=os.environ.get('ANYBLOK_DRAMATIQ_PROCESSES', 4),
                       help="Number of process")
    group.add_argument('--dramatiq-threads', type=int,
                       default=os.environ.get('ANYBLOK_DRAMATIQ_THREADS', 4),
                       help="Number of thread by process")
    group.add_argument('--dramatiq-midlewares', type=AnyBlokPlugin, nargs="+",
                       help='List of the midlewares allow to be load')


@Configuration.add('dramatiq-broker', label="Dramatiq - broker options",
                   must_be_loaded_by_unittest=True)
def define_dramatiq_broker(group):
    group.add_argument('--dramatiq-broker', type=AnyBlokPlugin,
                       default=os.environ.get(
                           'ANYBLOK_DRAMATIQ_BROKER',
                           'dramatiq.brokers.rabbitmq:RabbitmqBroker'
                       ),
                       help='broker to use for communication with dramatiq')
    group.add_argument('--dramatiq-broker-host',
                       default=os.environ.get(
                           'ANYBLOK_DRAMATIQ_BROKER_HOST',
                           'localhost'
                       ),
                       help="Broker's hostname")
    group.add_argument('--dramatiq-broker-port', type=int,
                       default=os.environ.get(
                           'ANYBLOK_DRAMATIQ_BROKER_PORT',
                           5672
                       ),
                       help="Broker port")
    group.add_argument('--dramatiq-broker-heartbeat-interval', type=int,
                       default=os.environ.get(
                           'ANYBLOK_DRAMATIQ_BROKER_HEARTBEAT_INTERVAL',
                           0
                       ),
                       help="Broker heartbeat interval")
    group.add_argument('--dramatiq-broker-connection-attempts', type=int,
                       default=os.environ.get(
                           'ANYBLOK_DRAMATIQ_BROKER_CONNECTION_ATTEMPTS',
                           5
                       ),
                       help="Broker connection attemps")
