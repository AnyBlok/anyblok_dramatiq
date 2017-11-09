# This file is a part of the AnyBlok / Pyramid project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok_dramatiq.broker import prepare_broker


class DramatiqTestCase:

    def setUp(self):
        super(DramatiqTestCase, self).setUp()
        self.broker = prepare_broker(withmiddleware=True)
        self.broker.emit_after("process_boot")
        self.worker = None

    def tearDown(self):
        super(DramatiqTestCase, self).tearDown()
        self.broker.close()


class DramatiqDBTestCase(DramatiqTestCase, DBTestCase):
    pass
