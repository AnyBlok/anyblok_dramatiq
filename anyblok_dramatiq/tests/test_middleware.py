# This file is a part of the AnyBlok / Dramatiq project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from .testcase import DramatiqDBTestCase
from uuid import uuid4


class MockMessage:

    def __init__(self, message_id):
        self.message_id = message_id


class TestMiddleWare(DramatiqDBTestCase):

    def test_before_enqueue_without_delay(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('dramatiq',))
        message_id = uuid4()
        message = registry.Dramatiq.Message.insert(id=message_id, message={})
        self.assertEqual(
            message.status,
            registry.Dramatiq.Message.STATUS_NEW
        )
        self.assertEqual(len(message.histories), 1)
        self.broker.emit_before('enqueue', MockMessage(message_id), None)
        self.assertEqual(
            message.status,
            registry.Dramatiq.Message.STATUS_ENQUEUED
        )
        self.assertEqual(len(message.histories), 2)
        self.assertEqual(message.updated_at, message.histories[1].created_at)
        self.assertEqual(message.status, message.histories[1].status)

    def test_before_enqueue_with_delay(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('dramatiq',))
        message_id = uuid4()
        message = registry.Dramatiq.Message.insert(id=message_id, message={})
        self.assertEqual(
            message.status,
            registry.Dramatiq.Message.STATUS_NEW
        )
        self.assertEqual(len(message.histories), 1)
        self.broker.emit_before('enqueue', MockMessage(message_id), 1000)
        self.assertEqual(
            message.status,
            registry.Dramatiq.Message.STATUS_DELAYED
        )
        self.assertEqual(len(message.histories), 2)
        self.assertEqual(message.updated_at, message.histories[1].created_at)
        self.assertEqual(message.status, message.histories[1].status)

    def test_before_process_message(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('dramatiq',))
        message_id = uuid4()
        message = registry.Dramatiq.Message.insert(id=message_id, message={})
        self.assertEqual(
            message.status,
            registry.Dramatiq.Message.STATUS_NEW
        )
        self.assertEqual(len(message.histories), 1)
        self.broker.emit_before('process_message', MockMessage(message_id))
        self.assertEqual(
            message.status,
            registry.Dramatiq.Message.STATUS_RUNNING
        )
        self.assertEqual(len(message.histories), 2)
        self.assertEqual(message.updated_at, message.histories[1].created_at)
        self.assertEqual(message.status, message.histories[1].status)

    def test_after_process_message(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('dramatiq',))
        message_id = uuid4()
        message = registry.Dramatiq.Message.insert(id=message_id, message={})
        self.assertEqual(
            message.status,
            registry.Dramatiq.Message.STATUS_NEW
        )
        self.assertEqual(len(message.histories), 1)
        self.broker.emit_after('process_message', MockMessage(message_id))
        self.assertEqual(
            message.status,
            registry.Dramatiq.Message.STATUS_DONE
        )
        self.assertEqual(len(message.histories), 2)
        self.assertEqual(message.updated_at, message.histories[1].created_at)
        self.assertEqual(message.status, message.histories[1].status)

    def test_after_process_message_with_exception(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('dramatiq',))
        message_id = uuid4()
        message = registry.Dramatiq.Message.insert(
            id=message_id, message={})
        self.assertEqual(
            message.status,
            registry.Dramatiq.Message.STATUS_NEW
        )
        self.assertEqual(len(message.histories), 1)
        self.broker.emit_after('process_message', MockMessage(message_id),
                               exception=Exception('test'))
        self.assertEqual(
            message.status,
            registry.Dramatiq.Message.STATUS_FAILED
        )
        self.assertEqual(len(message.histories), 2)
        self.assertEqual(message.updated_at, message.histories[1].created_at)
        self.assertEqual(message.status, message.histories[1].status)

    def test_after_process_message_with_db_exception(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('dramatiq',))
        message_id = uuid4()
        message = registry.Dramatiq.Message.insert(id=message_id, message={})
        with self.assertRaises(Exception):
            # no query is available
            registry.Dramatiq.Message.insert(id=message_id)

        self.assertEqual(
            message.status,
            registry.Dramatiq.Message.STATUS_NEW
        )
        self.broker.emit_after('process_message', MockMessage(message_id))

    def test_after_skip_message_with(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('dramatiq',))
        message_id = uuid4()
        message = registry.Dramatiq.Message.insert(id=message_id, message={})
        self.assertEqual(
            message.status,
            registry.Dramatiq.Message.STATUS_NEW
        )
        self.broker.emit_after('skip_message', MockMessage(message_id))
        with self.assertRaises(Exception):
            # waiting rollback, dramatiq_message table doesn't exist
            registry.Dramatiq.Message.query().count()

    def test_before_consumer_thread_shutdown(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('dramatiq',))
        message_id = uuid4()
        registry.Dramatiq.Message.insert(id=message_id, message={})

        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.broker.emit_before('consumer_thread_shutdown')
        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)

    def test_before_worker_thread_shutdown(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('dramatiq',))
        message_id = uuid4()
        registry.Dramatiq.Message.insert(id=message_id, message={})

        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.broker.emit_before('worker_thread_shutdown')
        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)

    def test_after_worker_shutdown(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('dramatiq',))
        message_id = uuid4()
        registry.Dramatiq.Message.insert(id=message_id, message={})

        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.broker.emit_after('worker_shutdown')
        with self.assertRaises(Exception):
            # waiting rollback, dramatiq_message table doesn't exist
            registry.Dramatiq.Message.query().count()
