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
from logging import getLogger

logger = getLogger(__name__)


class AnyBlokActorException(ValueError):
    """A ValueError exception for anyblok_dramatiq"""


def declare_actor_for(method, queue_name="default", priority=0, **options):
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

    if isinstance(method, Actor):
        raise AnyBlokActorException(
            "The actor %r is declared two time as an actor" % actor_name
        )

    def fn(*a, **kw):
        return method(*a, **kw)

    actor = Actor(
        fn, actor_name=actor_name,
        queue_name=queue_name,
        priority=priority,
        broker=broker,
        options=options,
    )
    setattr(Model, method.__name__, actor)


def actor(queue_name="default", priority=0, **options):
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


class ActorPlugin(ModelPluginBase):

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
