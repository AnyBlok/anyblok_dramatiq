.. This file is a part of the AnyBlok / Dramatiq project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. contents::

Code
====

**Actor**
---------

.. automodule:: anyblok_dramatiq.actor

.. autoexception:: AnyBlokActorException
    :members:
    :noindex:
    :show-inheritance:
    :inherited-members:

.. autoclass:: AnyBlokActor
    :members:
    :noindex:
    :show-inheritance:

.. autofunction:: declare_actor_for
    :noindex:

.. autofunction:: declare_actor_send_for
    :noindex:

.. autofunction:: actor
    :noindex:

.. autofunction:: actor_send
    :noindex:

.. autofunction:: call_directly_the_actor_send
    :noindex:

.. autoclass:: ActorPlugin
    :members:
    :noindex:
    :show-inheritance:

.. autoclass:: ActorSendPlugin
    :members:
    :noindex:
    :show-inheritance:


**Broker**
----------

.. automodule:: anyblok_dramatiq.broker

.. autofunction:: prepare_broker
    :noindex:


**Dramatiq middleware**
-----------------------

.. automodule:: anyblok_dramatiq.middleware

.. autoclass:: DramatiqMessageMiddleware
    :members:
    :noindex:
    :show-inheritance:


**Scripts**
-----------

.. automodule:: anyblok_dramatiq.scripts

.. autofunction:: worker_process
    :noindex:

.. autofunction:: dramatiq
    :noindex:
