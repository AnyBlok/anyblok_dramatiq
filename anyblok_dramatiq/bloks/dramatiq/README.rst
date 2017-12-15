.. This file is a part of the AnyBlok / Dramatiq project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Memento
~~~~~~~

An **actor** method is a classmethod who are executed by the dramatiq worker. AnyBlok define
two differente actor decorator:

* ``actor``: Works exactly as the dramatiq.actor decorator
* ``actor_send``: This actor call the send broker method by default

The actor decorator from anyblok must decorate only an AnyBlok Model, Mixin or Core


``actor``
`````````

The more basic actor::

    from anyblok_dramatiq import actor

    @register(Model)
    class MyModel:
        
        ...

        @actor()
        def actor_method(cls, *args, **kwargs)
            # do something
            ...


This use case is simple, you may:

* Call directly the actor_method and execute it::
      
      registry.MyModel.actor_method(, *a, **kw)

* Use the dramatiq functionnality without ``Model.Dramatiq.Message``::

      message = registry.MyModel.actor_method.send(*a, **kw)
      registry.Dramatiq.send2broker(message)

* Use the dramatiq functionnality with ``Model.Dramatiq.Message`` to get status and history::

      registry.Dramatiq.create_message(registry.MyModel.actor_method, *a, **kw)

  .. note::

      In this case the message will be send to dramatiq worker by the ``postcommit_hook`` of
      AnyBlok


``actor_send``
``````````````

The more basic actor::

    from anyblok_dramatiq import actor_send

    @register(Model)
    class MyModel:
        
        ...

        @actor_send()
        def actor_method(cls, *args, **kwargs)
            # do something
            ...


By default this decorator allow one case, use the dramatiq functionnality with ``Model.Dramatiq.Messag``::

    registry.MyModel.actor_method(*a, **kw)


The inheritance of AnyBlok allow to overwrite all classmethod to transform them by an actor easily.

In the case where you want execute directly the actor you have to use the context manager ``call_directly_the_actor_send``::

    from anyblok_dramatiq import call_directly_the_actor_send

    with call_directly_the_actor_send():
        registry.MyModel.actor_method(*a, **kw)

