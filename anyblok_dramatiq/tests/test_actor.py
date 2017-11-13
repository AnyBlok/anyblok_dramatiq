# This file is a part of the AnyBlok / Dramatiq project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from .testcase import DramatiqDBTestCase
from anyblok.column import Integer, String
from anyblok_dramatiq import declare_actor_for, AnyBlokActorException
from dramatiq.actor import Actor


def add_in_registry():

    from anyblok import Declarations

    @Declarations.register(Declarations.Model)
    class Task:
        id = Integer(primary_key=True)
        name = String(nullable=False)

        @classmethod
        def add(cls, name):
            cls.insert(name=name)

        def add_without_class_method(self):
            pass


class TestActor(DramatiqDBTestCase):

    def test_declare_actor_for(self):
        registry = self.init_registry(add_in_registry)
        self.assertFalse(isinstance(registry.Task.add, Actor))
        declare_actor_for(registry.Task.add)
        self.assertTrue(isinstance(registry.Task.add, Actor))

    def test_declare_actor_for_twice(self):
        registry = self.init_registry(add_in_registry)
        declare_actor_for(registry.Task.add)
        with self.assertRaises(AnyBlokActorException):
            declare_actor_for(registry.Task.add)

    def test_declare_actor_for_with_on_another_than_class_method(self):
        registry = self.init_registry(add_in_registry)
        with self.assertRaises(AnyBlokActorException):
            declare_actor_for(registry.Task.add_without_class_method)

    def test_declare_actor_for_with_bad_queue_name(self):
        registry = self.init_registry(add_in_registry)
        with self.assertRaises(AnyBlokActorException):
            declare_actor_for(registry.Task.add, queue_name='12345')

    def test_declare_actor_for_with_bad_broker_option(self):
        registry = self.init_registry(add_in_registry)
        with self.assertRaises(AnyBlokActorException):
            declare_actor_for(registry.Task.add, bad_broker_options='12345')
