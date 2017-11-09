# This file is a part of the AnyBlok / Dramatiq project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from .testcase import DramatiqTestCase
from unittest import TestCase
from dramatiq import get_broker


class TestBroker(DramatiqTestCase, TestCase):

    def test_get_broker(self):
        self.assertIs(self.broker, get_broker())
