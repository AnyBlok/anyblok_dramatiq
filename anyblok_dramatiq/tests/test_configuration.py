# This file is a part of the AnyBlok / Dramatiq project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_dramatiq.config import (
    define_dramatiq_consumer,
    define_dramatiq_broker
)
from anyblok.tests.testcase import TestCase
from anyblok.tests.test_config import MockArgumentParser


class TestArgsParseOption(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestArgsParseOption, cls).setUpClass()
        cls.parser = MockArgumentParser()
        cls.group = cls.parser.add_argument_group('label')
        cls.configuration = {}
        cls.function = {
            'define_dramatiq_broker': define_dramatiq_broker,
            'define_dramatiq_consumer': define_dramatiq_consumer,
        }

    def test_define_dramatiq_consumer(self):
        self.function['define_dramatiq_consumer'](self.parser)

    def test_define_dramatiq_broker(self):
        self.function['define_dramatiq_broker'](self.parser)
