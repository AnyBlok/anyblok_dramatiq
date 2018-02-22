# This file is a part of the AnyBlok / Dramatiq project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.config import Configuration, AnyBlokPlugin
import os


Configuration.add_application_properties('createdb', ['dramatiq-broker'])
Configuration.add_application_properties('updatedb', ['dramatiq-broker'])
Configuration.add_application_properties('nose', ['dramatiq-broker'])
Configuration.add_application_properties('interpreter', ['dramatiq-broker'])
Configuration.add_application_properties('default', ['dramatiq-broker'])

Configuration.add_application_properties('pyramid', ['dramatiq-broker'])
Configuration.add_application_properties('gunicorn', ['dramatiq-broker'],
                                         add_default_group=False)


@Configuration.add('dramatiq-consumer', label="Dramatiq - consumer options",
                   must_be_loaded_by_unittest=True)
def define_dramatiq_consumer(group):
    group.add_argument('--dramatiq-processes', type=int,
                       default=os.environ.get('ANYBLOK_DRAMATIQ_PROCESSES', 4),
                       help="Number of process")
    group.add_argument('--dramatiq-threads', type=int,
                       default=os.environ.get('ANYBLOK_DRAMATIQ_THREADS', 4),
                       help="Number of thread by process")


@Configuration.add('dramatiq-broker', label="Dramatiq - broker options",
                   must_be_loaded_by_unittest=True)
def define_dramatiq_broker(group):
    group.add_argument('--dramatiq-broker', type=AnyBlokPlugin,
                       default=os.environ.get(
                           'ANYBLOK_DRAMATIQ_BROKER',
                           'dramatiq.brokers.rabbitmq:RabbitmqBroker'
                       ),
                       help='broker to use for communication with dramatiq')
    group.add_argument('--dramatiq-broker-url',
                       default=os.environ.get(
                           'ANYBLOK_DRAMATIQ_BROKER_URL',
                           'amqp://guest:guest@127.0.0.1:5672'
                       ),
                       help="url to connect to the broker")
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
