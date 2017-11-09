# This file is a part of the AnyBlok / Dramatiq project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from .testcase import DramatiqDBTestCase


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
