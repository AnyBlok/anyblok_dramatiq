# This file is a part of the AnyBlok / Dramatiq api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import dramatiq
from dramatiq.actor import _queue_name_re, Actor


def declare_actor_for(Model, meth, queue_name="default",
                      priority=0, **options):
    db_name = Model.registry.db_name
    actor_name = db_name + ':' + Model.__registry_name__ + '=>' + meth
    if not _queue_name_re.fullmatch(queue_name):
        raise ValueError(
            "Queue names must start with a letter or an underscore followed "
            "by any number of letters, digits, dashes or underscores."
        )

    broker = dramatiq.get_broker()
    invalid_options = set(options) - broker.actor_options
    if invalid_options:
        raise ValueError(
            (
                "The following actor options are undefined: "
                "{%s}. Did you forget to add a middleware "
                "to your Broker?"
            ) % ', '.join(invalid_options)
        )

    real_function = getattr(Model, meth)

    if isinstance(real_function, Actor):
        raise ValueError(
            "The actor %r is declared two time as an actor" % actor_name
        )

    if not hasattr(real_function, '__self__'):
        raise ValueError(
            "The actor %r must be declared on a classmethod" % actor_name
        )

    def fn(*a, **kw):
        return real_function(*a, **kw)

    actor = Actor(
        fn, actor_name=actor_name,
        queue_name=queue_name,
        priority=priority,
        broker=broker,
        options=options,
    )
    setattr(Model, meth, actor)
