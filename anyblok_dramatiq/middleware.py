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
from anyblok.environment import EnvironmentManager

logger = getLogger(__name__)


class DramatiqMessageMiddleware(Middleware):

    def before_enqueue(self, broker, message, delay):
        registry = RegistryManager.get(Configuration.get('db_name'))
        logger.debug("[before_enqueue] %s: update message(%s) status ",
                     id(registry.session), message.message_id)
        M = registry.Dramatiq.Message
        m = M.get_instance_of(message)
        if m:
            m.update_status(M.STATUS_DELAYED if delay else M.STATUS_ENQUEUED)
            registry.commit()

    def before_process_message(self, broker, message):
        registry = RegistryManager.get(Configuration.get('db_name'))
        logger.debug("[before_process_message] %s: update message(%s) status ",
                     id(registry.session), message.message_id)
        # cache may have change, then we do the invalidation in the dramatiq
        # side
        registry.System.Cache.clear_invalidate_cache()

        M = registry.Dramatiq.Message
        m = M.get_instance_of(message)
        if m:
            m.update_status(M.STATUS_RUNNING)
            registry.commit()
            EnvironmentManager.set('is_called_by_dramatiq_actor', True)

    def after_process_message(self, broker, message, *,
                              result=None, exception=None):
        registry = RegistryManager.get(Configuration.get('db_name'))
        logger.debug("[after_process_message] %s: update message(%s) status "
                     "with result %r and exception %r",
                     id(registry.session), message.message_id, result,
                     exception)
        EnvironmentManager.set('is_called_by_dramatiq_actor', False)
        M = registry.Dramatiq.Message
        STATUS_DONE = M.STATUS_DONE
        STATUS_FAILED = M.STATUS_FAILED
        try:
            m = M.get_instance_of(message)
            if m:
                m.update_status(
                    STATUS_FAILED if exception is not None else STATUS_DONE,
                    error=str(exception) if exception else None
                )
                registry.commit()
        except Exception as e:
            registry.rollback()
            m = M.get_instance_of(message)
            if m:
                m.update_status(M.STATUS_FAILED, error=str(e))
                registry.commit()

            raise e
        finally:
            registry.expire_all()

    def after_skip_message(self, broker, message):
        registry = RegistryManager.get(Configuration.get('db_name'))
        logger.debug("[after_skip_message] %s: update message(%s) status ",
                     id(registry.session), message.message_id)
        registry.rollback()
        M = registry.Dramatiq.Message
        m = M.get_instance_of(message)
        m.update_status(M.STATUS_SKIPED)
        registry.commit()

    def before_consumer_thread_shutdown(self, *args, **kwargs):
        registry = RegistryManager.get(Configuration.get('db_name'))
        logger.debug("[before_consumer_thread_shutdown] %s: %r %r",
                     id(registry.session), args, kwargs)
        registry.Session.remove()

    def before_worker_thread_shutdown(self, *args, **kwargs):
        registry = RegistryManager.get(Configuration.get('db_name'))
        logger.debug("[before_worker_thread_shutdown] %s: %r %r",
                     id(registry.session), args, kwargs)
        registry.Session.remove()

    def after_worker_shutdown(self, *args, **kwargs):
        registry = RegistryManager.get(Configuration.get('db_name'))
        logger.debug("[after_worker_shutdown] %s: %r %r",
                     id(registry.session), args, kwargs)
        registry.close()
