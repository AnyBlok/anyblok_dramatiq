# This file is a part of the AnyBlok / Dramatiq project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from dramatiq import set_broker
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from anyblok.config import Configuration
from .middleware import DramatiqMessageMiddleware


def prepare_broker(withmiddleware=True):
    broker_cls = Configuration.get('dramatiq_broker', RabbitmqBroker)
    middleware = []
    if withmiddleware:
        middleware = Configuration.get('dramatiq_middlewares', [])
        middleware.append(DramatiqMessageMiddleware)
        middleware = [x() for x in middleware]

    options = {
        "host": Configuration.get('dramatiq_broker_host'),
        "port": Configuration.get('dramatiq_broker_port'),
        "heartbeat_interval": Configuration.get(
            'dramatiq_broker_heartbeat_interval'
        ),
        "connection_attempts": Configuration.get(
            'dramatiq_broker_connection_attempts'
        ),
    }
    broker = broker_cls(middleware=middleware, **options)
    set_broker(broker)
    return broker
