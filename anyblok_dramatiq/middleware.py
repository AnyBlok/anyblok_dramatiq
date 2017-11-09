# This file is a part of the AnyBlok / Dramatiq project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from logging import getLogger
from anyblok.config import Configuration
from anyblok.registry import RegistryManager
from dramatiq.middleware import Middleware
from datetime import datetime

logger = getLogger(__name__)


class DramatiqMessageMiddleware(Middleware):

    def before_enqueue(self, broker, message, delay):
        logger.debug("[before_enqueue] update message(%s) status ",
                     message.message_id)
        registry = RegistryManager.get(Configuration.get('db_name'))
        m = registry.Dramatiq.Message.get_instance_of(message)
        if m:
            m.status = registry.Dramatiq.Message.STATUS_ENQUEUED
            if delay:
                m.status = registry.Dramatiq.Message.STATUS_DELAYED

            m.updated_at = datetime.now()
            registry.commit()

    def before_process_message(self, broker, message):
        logger.debug("[before_process_message] update message(%s) status ",
                     message.message_id)
        registry = RegistryManager.get(Configuration.get('db_name'))
        m = registry.Dramatiq.Message.get_instance_of(message)
        if m:
            m.status = registry.Dramatiq.Message.STATUS_RUNNING
            m.updated_at = datetime.now()
            registry.commit()

    def after_process_message(self, broker, message, *,
                              result=None, exception=None):
        logger.debug("[after_process_message] update message(%s) status "
                     "with result %r and exception %r",
                     message.message_id, result, exception)
        registry = RegistryManager.get(Configuration.get('db_name'))
        try:
            m = registry.Dramatiq.Message.get_instance_of(message)
            if m:
                m.status = registry.Dramatiq.Message.STATUS_DONE
                if exception is not None:
                    m.status = registry.Dramatiq.Message.STATUS_FAILED

                m.updated_at = datetime.now()
                registry.commit()
        except Exception as e:
            registry.rollback()
            m = registry.Dramatiq.Message.get_instance_of(message)
            if m:
                m.status = registry.Dramatiq.Message.STATUS_FAILED
                m.updated_at = datetime.now()
                registry.commit()
            raise e
        finally:
            registry.session.expire_all()

    def _rollback_connection(self, *args, **kwargs):
        registry = RegistryManager.get(Configuration.get('db_name'))
        registry.rollback()

    before_consumer_thread_shutdown = _rollback_connection
    before_worker_thread_shutdown = _rollback_connection
    before_worker_shutdown = _rollback_connection
