# This file is a part of the AnyBlok / Dramatiq project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from .testcase import DramatiqDBTestCase
from anyblok.column import Integer, String
from anyblok.environment import EnvironmentManager
from anyblok_dramatiq import (
    declare_actor_for,
    declare_actor_send_for,
    actor,
    actor_send,
    AnyBlokActor,
    AnyBlokActorException
)
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

    def test_declare_actor_send_for(self):
        registry = self.init_registry(add_in_registry)
        self.assertFalse(isinstance(registry.Task.add, AnyBlokActor))
        declare_actor_send_for(registry.Task.add)
        self.assertTrue(isinstance(registry.Task.add, AnyBlokActor))

    def test_declare_actor_send_for_twice(self):
        registry = self.init_registry(add_in_registry)
        declare_actor_send_for(registry.Task.add)
        with self.assertRaises(AnyBlokActorException):
            declare_actor_send_for(registry.Task.add)

    def test_declare_actor_send_for_with_on_another_than_class_method(self):
        registry = self.init_registry(add_in_registry)
        with self.assertRaises(AnyBlokActorException):
            declare_actor_send_for(registry.Task.add_without_class_method)

    def test_declare_actor_send_for_with_bad_queue_name(self):
        registry = self.init_registry(add_in_registry)
        with self.assertRaises(AnyBlokActorException):
            declare_actor_send_for(registry.Task.add, queue_name='12345')

    def test_declare_actor_send_for_with_bad_broker_option(self):
        registry = self.init_registry(add_in_registry)
        with self.assertRaises(AnyBlokActorException):
            declare_actor_send_for(
                registry.Task.add, bad_broker_options='12345')

    def test_decorator_actor(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Model)
            class Task:

                id = Integer(primary_key=True)

                @actor()
                def add(cls, val):
                    return val

        registry = self.init_registry(add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, Actor))
        self.assertEqual(registry.Task.add(1), 1)

    def test_decorator_actor_with_options(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Model)
            class Task:

                id = Integer(primary_key=True)

                @actor(queue_name="other", priority=1)
                def add(cls, val):
                    return val

        registry = self.init_registry(add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, Actor))
        self.assertEqual(registry.Task.add(1), 1)
        self.assertEqual(registry.Task.add.queue_name, "other")
        self.assertEqual(registry.Task.add.priority, 1)

    def test_decorator_actor_with_inherit_Model_1(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Model)
            class Task:

                id = Integer(primary_key=True)

                @actor()
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)  # noqa
            class Task:

                id = Integer(primary_key=True)

                @actor()
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry(add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, Actor))
        self.assertEqual(registry.Task.add(1), 2)

    def test_decorator_actor_with_inherit_Model_2(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Model)
            class Task:

                id = Integer(primary_key=True)

                @classmethod
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)  # noqa
            class Task:

                id = Integer(primary_key=True)

                @actor()
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry(add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, Actor))
        self.assertEqual(registry.Task.add(1), 2)

    def test_decorator_actor_with_inherit_Model_3(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Model)
            class Task:

                id = Integer(primary_key=True)

                @actor()
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)  # noqa
            class Task:

                id = Integer(primary_key=True)

                @classmethod
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry(add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, Actor))
        self.assertEqual(registry.Task.add(1), 2)

    def test_decorator_actor_with_inherit_Mixin_1(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Mixin)
            class MixinTest:

                id = Integer(primary_key=True)

                @actor()
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)
            class Task(Declarations.Mixin.MixinTest):

                id = Integer(primary_key=True)

                @actor()
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry(add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, Actor))
        self.assertEqual(registry.Task.add(1), 2)

    def test_decorator_actor_with_inherit_Mixin_2(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Mixin)
            class MixinTest:

                id = Integer(primary_key=True)

                @actor()
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)
            class Task(Declarations.Mixin.MixinTest):

                id = Integer(primary_key=True)

                @classmethod
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry(add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, Actor))
        self.assertEqual(registry.Task.add(1), 2)

    def test_decorator_actor_with_inherit_Mixin_3(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Mixin)
            class MixinTest:

                id = Integer(primary_key=True)

                @classmethod
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)
            class Task(Declarations.Mixin.MixinTest):

                id = Integer(primary_key=True)

                @actor()
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry(add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, Actor))
        self.assertEqual(registry.Task.add(1), 2)

    def test_decorator_actor_with_inherit_Core_1(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Core)
            class SqlBase:

                @actor()
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)  # noqa
            class Task:

                id = Integer(primary_key=True)

                @actor()
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry(add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, Actor))
        self.assertEqual(registry.Task.add(1), 2)

    def test_decorator_actor_with_inherit_Core_2(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Core)
            class SqlBase:

                @actor()
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)  # noqa
            class Task:

                id = Integer(primary_key=True)

                @classmethod
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry(add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, Actor))
        self.assertEqual(registry.Task.add(1), 2)

    def test_decorator_actor_with_inherit_Core_3(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Core)
            class SqlBase:

                @classmethod
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)  # noqa
            class Task:

                id = Integer(primary_key=True)

                @actor()
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry(add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, Actor))
        self.assertEqual(registry.Task.add(1), 2)

    def test_decorator_actor_send(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Model)
            class Task:

                id = Integer(primary_key=True)

                @actor_send()
                def add(cls, val):
                    return val

        registry = self.init_registry_with_bloks(('dramatiq',), add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, AnyBlokActor))
        self.assertFalse(EnvironmentManager.get('_postcommit_hook'))
        registry.Task.add(1)
        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.assertTrue(EnvironmentManager.get('_postcommit_hook'))

    def test_decorator_actor_send_with_options(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Model)
            class Task:

                id = Integer(primary_key=True)

                @actor_send(queue_name="other", priority=1)
                def add(cls, val):
                    return val

        registry = self.init_registry_with_bloks(('dramatiq',), add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, AnyBlokActor))
        self.assertFalse(EnvironmentManager.get('_postcommit_hook'))
        registry.Task.add(1)
        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.assertEqual(registry.Task.add.queue_name, "other")
        self.assertEqual(registry.Task.add.priority, 1)
        self.assertTrue(EnvironmentManager.get('_postcommit_hook'))

    def test_decorator_actor_send_with_inherit_Model_1(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Model)
            class Task:

                id = Integer(primary_key=True)

                @actor_send()
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)  # noqa
            class Task:

                id = Integer(primary_key=True)

                @actor_send()
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry_with_bloks(('dramatiq',), add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, AnyBlokActor))
        self.assertFalse(EnvironmentManager.get('_postcommit_hook'))
        registry.Task.add(1)
        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.assertTrue(EnvironmentManager.get('_postcommit_hook'))

    def test_decorator_actor_send_with_inherit_Model_2(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Model)
            class Task:

                id = Integer(primary_key=True)

                @classmethod
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)  # noqa
            class Task:

                id = Integer(primary_key=True)

                @actor_send()
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry_with_bloks(('dramatiq',), add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, AnyBlokActor))
        self.assertFalse(EnvironmentManager.get('_postcommit_hook'))
        registry.Task.add(1)
        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.assertTrue(EnvironmentManager.get('_postcommit_hook'))

    def test_decorator_actor_send_with_inherit_Model_3(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Model)
            class Task:

                id = Integer(primary_key=True)

                @actor_send()
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)  # noqa
            class Task:

                id = Integer(primary_key=True)

                @classmethod
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry_with_bloks(('dramatiq',), add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, AnyBlokActor))
        self.assertFalse(EnvironmentManager.get('_postcommit_hook'))
        registry.Task.add(1)
        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.assertTrue(EnvironmentManager.get('_postcommit_hook'))

    def test_decorator_actor_send_with_inherit_Mixin_1(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Mixin)
            class MixinTest:

                id = Integer(primary_key=True)

                @actor_send()
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)
            class Task(Declarations.Mixin.MixinTest):

                id = Integer(primary_key=True)

                @actor_send()
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry_with_bloks(('dramatiq',), add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, AnyBlokActor))
        self.assertFalse(EnvironmentManager.get('_postcommit_hook'))
        registry.Task.add(1)
        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.assertTrue(EnvironmentManager.get('_postcommit_hook'))

    def test_decorator_actor_send_with_inherit_Mixin_2(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Mixin)
            class MixinTest:

                id = Integer(primary_key=True)

                @actor_send()
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)
            class Task(Declarations.Mixin.MixinTest):

                id = Integer(primary_key=True)

                @classmethod
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry_with_bloks(('dramatiq',), add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, AnyBlokActor))
        self.assertFalse(EnvironmentManager.get('_postcommit_hook'))
        registry.Task.add(1)
        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.assertTrue(EnvironmentManager.get('_postcommit_hook'))

    def test_decorator_actor_send_with_inherit_Mixin_3(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Mixin)
            class MixinTest:

                id = Integer(primary_key=True)

                @classmethod
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)
            class Task(Declarations.Mixin.MixinTest):

                id = Integer(primary_key=True)

                @actor_send()
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry_with_bloks(('dramatiq',), add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, AnyBlokActor))
        self.assertFalse(EnvironmentManager.get('_postcommit_hook'))
        registry.Task.add(1)
        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.assertTrue(EnvironmentManager.get('_postcommit_hook'))

    def test_decorator_actor_send_with_inherit_Core_1(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Core)
            class SqlBase:

                @actor_send()
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)  # noqa
            class Task:

                id = Integer(primary_key=True)

                @actor_send()
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry_with_bloks(('dramatiq',), add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, AnyBlokActor))
        self.assertFalse(EnvironmentManager.get('_postcommit_hook'))
        registry.Task.add(1)
        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.assertTrue(EnvironmentManager.get('_postcommit_hook'))

    def test_decorator_actor_send_with_inherit_Core_2(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Core)
            class SqlBase:

                @actor_send()
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)  # noqa
            class Task:

                id = Integer(primary_key=True)

                @classmethod
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry_with_bloks(('dramatiq',), add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, AnyBlokActor))
        self.assertFalse(EnvironmentManager.get('_postcommit_hook'))
        registry.Task.add(1)
        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.assertTrue(EnvironmentManager.get('_postcommit_hook'))

    def test_decorator_actor_send_with_inherit_Core_3(self):

        def add_in_registry():

            from anyblok import Declarations

            @Declarations.register(Declarations.Core)
            class SqlBase:

                @classmethod
                def add(cls, val):
                    return val

            @Declarations.register(Declarations.Model)  # noqa
            class Task:

                id = Integer(primary_key=True)

                @actor_send()
                def add(cls, val):
                    return super(Task, cls).add(val) * 2

        registry = self.init_registry_with_bloks(('dramatiq',), add_in_registry)
        self.assertTrue(isinstance(registry.Task.add, AnyBlokActor))
        self.assertFalse(EnvironmentManager.get('_postcommit_hook'))
        registry.Task.add(1)
        self.assertEqual(registry.Dramatiq.Message.query().count(), 1)
        self.assertTrue(EnvironmentManager.get('_postcommit_hook'))
