# This file is a part of the AnyBlok / Dramatiq project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from .testcase import DramatiqDBTestCase
from uuid import uuid4
from anyblok.environment import EnvironmentManager


class TestMessage(DramatiqDBTestCase):

    blok_entry_points = ('bloks', 'test_bloks')

    def test_create_message(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_dramatiq_1',))
        message = registry.Dramatiq.create_message(
            registry.Task.add, name='test')
        self.assertEqual(message.kwargs, dict(name='test'))
        query = registry.Dramatiq.Message.query()
        query = query.filter_by(id=message.message_id)
        self.assertEqual(query.count(), 1)
        message = query.one()
        self.assertEqual(message.status, registry.Dramatiq.Message.STATUS_NEW)
        self.assertEqual(len(message.histories), 1)
        self.assertEqual(message.histories[0].created_at, message.updated_at)
        self.assertEqual(message.histories[0].status, message.status)

    def test_create_message_add_postcommit_hook(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_dramatiq_1',))
        self.assertFalse(EnvironmentManager.get('_postcommit_hook'))
        registry.Dramatiq.create_message(registry.Task.add, name='test')
        self.assertTrue(EnvironmentManager.get('_postcommit_hook'))

    def test_create_2_message(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_dramatiq_1',))
        registry.Dramatiq.create_message(registry.Task.add, name='test')
        registry.Dramatiq.create_message(registry.Task.add, name='test')

    def test_update_message(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_dramatiq_1',))
        message = registry.Dramatiq.create_message(
            registry.Task.add, name='test')
        self.assertEqual(message.kwargs, dict(name='test'))
        query = registry.Dramatiq.Message.query()
        query = query.filter_by(id=message.message_id)
        message = query.one()
        self.assertEqual(message.status, registry.Dramatiq.Message.STATUS_NEW)
        message.update_status(registry.Dramatiq.Message.STATUS_DONE)
        self.assertEqual(message.status, registry.Dramatiq.Message.STATUS_DONE)
        self.assertEqual(len(message.histories), 2)
        self.assertEqual(message.histories[1].created_at, message.updated_at)
        self.assertEqual(message.histories[1].status, message.status)

    def test_message_unique_constraint(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_dramatiq_1',))
        uuid = uuid4()
        registry.Dramatiq.Message.insert(id=uuid, message={})
        with self.assertRaises(Exception):
            registry.Dramatiq.Message.insert(id=uuid)
