# This file is a part of the AnyBlok / Dramatiq api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import dramatiq
from dramatiq.actor import _queue_name_re, Actor
from anyblok.common import add_autodocs
from anyblok.model.plugins import ModelPluginBase
from anyblok.environment import EnvironmentManager
from contextlib import contextmanager
from logging import getLogger

logger = getLogger(__name__)


class AnyBlokActorException(ValueError):
    """A ValueError exception for anyblok_dramatiq"""


class AnyBlokActor(Actor):
    """Overload the dramatiq.actor.Actor class

    the goal is to allowthe decorator actor_send, this decorator
    use directly the method send

    """
    def __call__(self, *args, **kwargs):
        """Send to the broker or call directly the classmethod"""
        is_called_by_dramatiq_actor = EnvironmentManager.get(
            'is_called_by_dramatiq_actor', False)
        if is_called_by_dramatiq_actor:
            kwargs.pop('run_at', None)
            kwargs.pop('delay', None)
            return self.fn(*args, **kwargs)

        return self.send(*args, **kwargs)

    def send(self, *args, **kwargs):
        """Send to the broker"""
        return self.fn.registry.Dramatiq.create_message(
            self.fn.actor, *args, **kwargs)


def _declare_actor_for(ActorCls, method, queue_name="default", priority=0,
                       **options):
    if not hasattr(method, '__self__'):
        raise AnyBlokActorException(
            "The method %r must be declared as a classmethod" % method
        )

    Model = method.__self__
    db_name = Model.registry.db_name
    registry_name = Model.__registry_name__
    actor_name = db_name + ':' + registry_name + '=>' + method.__name__
    logger.info("Declare the actor : %r", actor_name)
    if not _queue_name_re.fullmatch(queue_name):
        raise AnyBlokActorException(
            "Queue names must start with a letter or an underscore followed "
            "by any number of letters, digits, dashes or underscores."
        )

    broker = dramatiq.get_broker()
    invalid_options = set(options) - broker.actor_options
    if invalid_options:
        raise AnyBlokActorException(
            (
                "The following actor options are undefined: "
                "{%s}. Did you forget to add a middleware "
                "to your Broker?"
            ) % ', '.join(invalid_options)
        )

    if isinstance(method, ActorCls):
        raise AnyBlokActorException(
            "The actor %r is declared two time as an actor" % actor_name
        )

    def fn(*a, **kw):
        return method(*a, **kw)

    setattr(fn, 'registry', Model.registry)
    setattr(fn, 'method', method)

    actor = ActorCls(
        fn, actor_name=actor_name,
        queue_name=queue_name,
        priority=priority,
        broker=broker,
        options=options,
    )
    setattr(fn, 'actor', actor)
    setattr(Model, method.__name__, actor)
    logger.debug('declare actor on "%s:%s"',
                 Model.__registry_name__, method.__name__)


def declare_actor_for(method, **kwargs):
    """Method to add anyblok_dramatiq.actor.actor decorator on the
    class method

    :param method: classmethod pointer
    :param _**kwargs: decorator kwargs
    """
    _declare_actor_for(Actor, method, **kwargs)


def declare_actor_send_for(method, **kwargs):
    """Method to add anyblok_dramatiq.actor.actor_send decorator on the
    class method

    :param method: classmethod pointer
    :param _**kwargs: decorator kwargs
    """
    _declare_actor_for(AnyBlokActor, method, **kwargs)


def actor(queue_name="default", priority=0, **options):
    """Decorator to get an Actor

    :param queue_name: name of the queue
    :param priority: priority of the actor
    :param _**options: options for actor
    """
    kwargs = {'queue_name': queue_name, 'priority': priority}
    kwargs.update(options)
    autodoc = """
        **actor** event call with positionnal argument %(kwargs)r
    """ % dict(kwargs=kwargs)

    def wrapper(method):
        add_autodocs(method, autodoc)
        method.is_a_dramatiq_actor = True
        method.kwargs = kwargs
        return classmethod(method)

    return wrapper


def actor_send(queue_name="default", priority=0, **options):
    """Decorator to get an AnyBlokActor

    :param queue_name: name of the queue
    :param priority: priority of the actor
    :param _**options: options for actor
    """
    kwargs = {'queue_name': queue_name, 'priority': priority}
    kwargs.update(options)
    autodoc = """
        **actor_send** event call with positionnal argument %(kwargs)r
    """ % dict(kwargs=kwargs)

    def wrapper(method):
        add_autodocs(method, autodoc)
        method.is_a_dramatiq_actor_send = True
        method.kwargs = kwargs
        return classmethod(method)

    return wrapper


@contextmanager
def call_directly_the_actor_send():
    """Context manager to call directly without use dramatiq"""
    try:
        EnvironmentManager.set('is_called_by_dramatiq_actor', True)
        yield
    finally:
        EnvironmentManager.set('is_called_by_dramatiq_actor', False)


class ActorPlugin(ModelPluginBase):
    """``anyblok.model.plugin`` to allow the build of the
    ``anyblok_dramatiq.actor``
    """

    def initialisation_tranformation_properties(self, properties,
                                                transformation_properties):
        """ Initialise the transform properties

        :param properties: the properties declared in the model
        :param new_type_properties: param to add in a new base if need
        """
        if 'dramatiq_actors' not in transformation_properties:
            transformation_properties['dramatiq_actors'] = {}

    def transform_base_attribute(self, attr, method, namespace, base,
                                 transformation_properties,
                                 new_type_properties):
        """ transform the attribute for the final Model

        :param attr: attribute name
        :param method: method pointer of the attribute
        :param namespace: the namespace of the model
        :param base: One of the base of the model
        :param transformation_properties: the properties of the model
        :param new_type_properties: param to add in a new base if need
        """
        if hasattr(method, 'is_a_dramatiq_actor'):
            if method.is_a_dramatiq_actor:
                if attr not in transformation_properties['dramatiq_actors']:
                    transformation_properties['dramatiq_actors'][attr] = {}

                transformation_properties['dramatiq_actors'][attr].update(
                    method.kwargs)

    def insert_in_bases(self, new_base, namespace, properties,
                        transformation_properties):
        """Insert in a base the overload

        :param new_base: the base to be put on front of all bases
        :param namespace: the namespace of the model
        :param properties: the properties declared in the model
        :param transformation_properties: the properties of the model
        """
        for actor in transformation_properties['dramatiq_actors']:

            def wrapper(*args, **kwargs):
                cls = args[0]
                return getattr(super(new_base, cls), actor)(*args[1:], **kwargs)

            wrapper.__name__ = actor
            setattr(new_base, actor, classmethod(wrapper))

    def after_model_construction(self, base, namespace,
                                 transformation_properties):
        """Do some action with the constructed Model

        :param base: the Model class
        :param namespace: the namespace of the model
        :param transformation_properties: the properties of the model
        """
        for actor in transformation_properties['dramatiq_actors']:
            method = getattr(base, actor)
            kwargs = transformation_properties['dramatiq_actors'][actor]
            declare_actor_for(method, **kwargs)


class ActorSendPlugin(ModelPluginBase):
    """``anyblok.model.plugin`` to allow the build of the
    ``anyblok_dramatiq.actor_send``
    """

    def initialisation_tranformation_properties(self, properties,
                                                transformation_properties):
        """ Initialise the transform properties

        :param properties: the properties declared in the model
        :param new_type_properties: param to add in a new base if need
        """
        if 'dramatiq_actors_send' not in transformation_properties:
            transformation_properties['dramatiq_actors_send'] = {}

    def transform_base_attribute(self, attr, method, namespace, base,
                                 transformation_properties,
                                 new_type_properties):
        """ transform the attribute for the final Model

        :param attr: attribute name
        :param method: method pointer of the attribute
        :param namespace: the namespace of the model
        :param base: One of the base of the model
        :param transformation_properties: the properties of the model
        :param new_type_properties: param to add in a new base if need
        """
        tp = transformation_properties
        if hasattr(method, 'is_a_dramatiq_actor_send'):
            if method.is_a_dramatiq_actor_send:
                if attr not in tp['dramatiq_actors_send']:
                    tp['dramatiq_actors_send'][attr] = {}

                tp['dramatiq_actors_send'][attr].update(method.kwargs)

    def insert_in_bases(self, new_base, namespace, properties,
                        transformation_properties):
        """Insert in a base the overload

        :param new_base: the base to be put on front of all bases
        :param namespace: the namespace of the model
        :param properties: the properties declared in the model
        :param transformation_properties: the properties of the model
        """
        for actor in transformation_properties['dramatiq_actors_send']:

            def wrapper(*args, **kwargs):
                cls = args[0]
                return getattr(super(new_base, cls), actor)(*args[1:], **kwargs)

            wrapper.__name__ = actor
            setattr(new_base, actor, classmethod(wrapper))

    def after_model_construction(self, base, namespace,
                                 transformation_properties):
        """Do some action with the constructed Model

        :param base: the Model class
        :param namespace: the namespace of the model
        :param transformation_properties: the properties of the model
        """
        for actor in transformation_properties['dramatiq_actors_send']:
            method = getattr(base, actor)
            kwargs = transformation_properties['dramatiq_actors_send'][actor]
            declare_actor_send_for(method, **kwargs)
